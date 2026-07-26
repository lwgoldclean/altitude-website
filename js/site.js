/* Mobile navigation toggle. */
document.addEventListener('DOMContentLoaded', function () {
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
});

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
