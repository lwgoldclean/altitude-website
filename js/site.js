/* Mobile navigation toggle. */
document.addEventListener('DOMContentLoaded', function () {
  var button = document.querySelector('[data-menu-button]');
  var panel  = document.querySelector('[data-menu-panel]');
  if (!button || !panel) return;

  button.addEventListener('click', function () {
    var open = panel.classList.toggle('hidden') === false;
    button.setAttribute('aria-expanded', String(open));
  });
});
