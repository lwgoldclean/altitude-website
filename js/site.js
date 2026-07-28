/* Mobile navigation toggle. */
document.addEventListener('DOMContentLoaded', function () {
  // First: the stat tiles start hidden, so nothing further down this
  // handler should be able to strand them that way.
  initStatCards();

  var button = document.querySelector('[data-menu-button]');
  var panel  = document.querySelector('[data-menu-panel]');
  if (button && panel) {
    button.addEventListener('click', function () {
      var open = panel.classList.toggle('hidden') === false;
      button.setAttribute('aria-expanded', String(open));
    });
  }

  Array.prototype.forEach.call(
    document.querySelectorAll('[data-quote-form]'),
    initQuoteForm
  );

  initQuoteDisclosure();
  initHeroVideo();
});

/* The four hero proof points carry the pitch, so they arrive in sequence
   rather than as a block of flat type, and any figure among them counts up
   to its value. The markup ships with .stats-armed so the tiles never flash
   in before this runs; the .js class set in the head means an unscripted
   document never hides them in the first place. */
function initStatCards() {
  var list = document.querySelector('[data-stats]');
  if (!list) return;

  var cards = list.querySelectorAll('.stat-card');
  if (!cards.length) return;

  var still = window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function reveal() {
    Array.prototype.forEach.call(cards, function (card, index) {
      window.setTimeout(function () {
        card.classList.add('is-revealed');
        countUp(card.querySelector('[data-count-to]'), still);
      }, still ? 0 : index * 110);
    });
  }

  // The row sits in the hero, so this normally fires straight away; the
  // observer is here so it still behaves if the page opens part-scrolled.
  if (still || !('IntersectionObserver' in window)) {
    reveal();
    return;
  }

  var watcher = new IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      if (!entries[i].isIntersecting) continue;
      watcher.disconnect();
      reveal();
      return;
    }
  }, { threshold: 0.35 });

  watcher.observe(list);
}

/* Counts 0 → target, eased out so the number settles instead of stopping
   dead on the last frame. */
function countUp(figure, still) {
  if (!figure) return;

  var target = parseFloat(figure.getAttribute('data-count-to'));
  var suffix = figure.getAttribute('data-count-suffix') || '';
  if (isNaN(target)) return;

  if (still || !window.requestAnimationFrame) {
    figure.textContent = target + suffix;
    return;
  }

  var duration = 1250;
  var started  = null;

  function frame(now) {
    if (started === null) started = now;
    var progress = Math.min((now - started) / duration, 1);
    var eased    = 1 - Math.pow(1 - progress, 3);
    figure.textContent = Math.round(target * eased) + suffix;
    if (progress < 1) window.requestAnimationFrame(frame);
  }

  figure.textContent = '0' + suffix;
  window.requestAnimationFrame(frame);
}

/* The hero video is decorative. Where autoplay is refused — iOS Low Power
   Mode, Android Data Saver — the browser is left showing a frozen first
   frame under its own play button, which reads as broken. Rather than leave
   that, drop the element and let the navy .hero-bg gradient stand in, which
   is what it is there for. */
function initHeroVideo() {
  var video = document.querySelector('.hero-video');
  if (!video) return;

  // iOS honours the muted *property*; the attribute alone is not always
  // enough for an unattended play() to be permitted.
  video.muted = true;
  video.setAttribute('muted', '');

  var started = video.play();
  if (!started || typeof started.catch !== 'function') return;   // older browsers

  started.catch(function () {
    video.parentNode && video.parentNode.removeChild(video);
  });
}

/* The enquiry form is collapsed on phones only. The markup ships with `open`
   so that a visitor without JavaScript still gets a working form; this closes
   it below the lg breakpoint and re-opens it if the viewport grows. */
function initQuoteDisclosure() {
  var panel = document.querySelector('[data-quote-disclosure]');
  if (!panel) return;

  var wide = window.matchMedia('(min-width: 1024px)');

  function sync() {
    panel.open = wide.matches;
  }
  sync();

  if (wide.addEventListener) {
    wide.addEventListener('change', sync);
  } else if (wide.addListener) {
    wide.addListener(sync);          // Safari < 14
  }

  // The sticky action bar points at the form; make sure tapping it reveals
  // the fields rather than scrolling to a collapsed summary.
  Array.prototype.forEach.call(
    document.querySelectorAll('[data-open-quote]'),
    function (trigger) {
      trigger.addEventListener('click', function () {
        panel.open = true;
      });
    }
  );
}

/* Enquiry forms submit in the background so the visitor stays on the page.
   The endpoint is the form's own action, which points at the Cloudflare Worker
   in worker/ — that Worker holds the Resend key, which must never be in the
   page source. Until it is deployed the action still reads REPLACE_WITH_...,
   and the form says so rather than pretending to send. */
function initQuoteForm(form) {
  var status = form.querySelector('[data-form-status]');
  var button = form.querySelector('button[type="submit"]');
  var label  = form.querySelector('[data-submit-label]');
  if (!status || !button || !label) return;

  var idleLabel = label.textContent;

  function show(message, kind) {
    status.textContent = message;
    status.className = 'text-sm r-md px-4 py-3 ' + (
      kind === 'ok'
        ? 'bg-emerald-50 text-emerald-900 border border-emerald-200'
        : 'bg-rose-50 text-rose-900 border border-rose-200'
    );
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    var endpoint = form.getAttribute('action') || '';
    if (endpoint.indexOf('REPLACE_WITH') !== -1) {
      show('This form is not yet connected. Please call 0432 008 830 and we will take your enquiry directly.', 'error');
      return;
    }

    button.disabled = true;
    label.textContent = 'Submitting…';
    status.className = 'hidden';

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Accept': 'application/json' },
      body: new FormData(form)
    })
      .then(function (response) { return response.json(); })
      .then(function (result) {
        if (result && result.success) {
          form.reset();
          show('Enquiry received. We will respond within two business days — sooner if you have flagged it as urgent.', 'ok');
        } else {
          show('That did not send. Please call 0432 008 830 and we will take the details directly.', 'error');
        }
      })
      .catch(function () {
        show('That did not send — check your connection, or call 0432 008 830.', 'error');
      })
      .then(function () {
        button.disabled = false;
        label.textContent = idleLabel;
      });
  });
}
