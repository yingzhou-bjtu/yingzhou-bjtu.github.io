(function () {
  'use strict';

  var btn = document.getElementById('back-to-top');
  var masthead = document.querySelector('.masthead');
  if (!btn && !masthead) return;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function onScroll() {
    if (btn) btn.classList.toggle('is-visible', window.scrollY > 420);
    if (masthead) masthead.classList.toggle('is-scrolled', window.scrollY > 10);
  }

  if (btn) {
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
