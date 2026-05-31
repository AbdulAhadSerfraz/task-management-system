(function () {
  'use strict';

  /* --- Auto-dismiss flash alerts --- */
  var alerts = document.querySelectorAll('.alert');
  for (var i = 0; i < alerts.length; i++) {
    (function (alert) {
      setTimeout(function () {
        if (alert.parentElement) alert.remove();
      }, 4500);
    })(alerts[i]);
  }

  /* --- Stagger card animation indices --- */
  var cards = document.querySelectorAll('.task-card');
  for (var j = 0; j < cards.length; j++) {
    cards[j].style.setProperty('--card-index', j);
  }

  /* --- Scroll reveal via IntersectionObserver --- */
  function isReduceMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  if (!isReduceMotion() && 'IntersectionObserver' in window) {
    var revealEls = document.querySelectorAll('.reveal');
    if (revealEls.length === 0) {
      /* auto-reveal task cards and auth card */
      var autoTargets = document.querySelectorAll('.task-card, .auth-card, .empty-state');
      for (var k = 0; k < autoTargets.length; k++) {
        autoTargets[k].classList.add('reveal');
      }
      revealEls = document.querySelectorAll('.reveal');
    }

    var observer = new IntersectionObserver(function (entries) {
      for (var m = 0; m < entries.length; m++) {
        if (entries[m].isIntersecting) {
          entries[m].target.classList.add('visible');
          observer.unobserve(entries[m].target);
        }
      }
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    for (var n = 0; n < revealEls.length; n++) {
      observer.observe(revealEls[n]);
    }
  }
})();
