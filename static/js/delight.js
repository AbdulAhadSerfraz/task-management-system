(function () {
  'use strict';

  var rm = window.matchMedia('(prefers-reduced-motion: reduce)');

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

  /* --- Completion celebration --- */
  var completedId = new URLSearchParams(window.location.search).get('completed');
  if (completedId) {
    var completedCard = document.querySelector('[data-task-id="' + completedId + '"]');
    if (completedCard && !rm.matches) {
      completedCard.classList.add('completing');
      var badge = completedCard.querySelector('.badge-green .ph-check');
      if (badge) {
        badge.style.animation = 'none';
        requestAnimationFrame(function () {
          badge.style.animation = '';
        });
      }
    }
  }

  /* --- Confetti on first task --- */
  var created = new URLSearchParams(window.location.search).get('created');
  if (created === '1' && !rm.matches) {
    var container = document.createElement('div');
    container.className = 'confetti-container';
    var colors = ['#111111', '#6B6B67', '#346538', '#9F2F2D', '#956400'];
    for (var c = 0; c < 48; c++) {
      var piece = document.createElement('div');
      piece.className = 'confetti-piece';
      piece.style.left = (Math.random() * 100) + '%';
      piece.style.top = '-10px';
      piece.style.background = colors[Math.floor(Math.random() * colors.length)];
      piece.style.width = (4 + Math.random() * 4) + 'px';
      piece.style.height = (4 + Math.random() * 4) + 'px';
      piece.style.animationDelay = (Math.random() * 0.6) + 's';
      piece.style.animationDuration = (1.2 + Math.random() * 0.8) + 's';
      piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '1px';
      container.appendChild(piece);
    }
    document.body.appendChild(container);
    setTimeout(function () {
      if (container.parentElement) container.remove();
    }, 2500);
  }

  /* --- Textarea auto-resize --- */
  var textareas = document.querySelectorAll('.form-textarea');
  for (var t = 0; t < textareas.length; t++) {
    (function (ta) {
      ta.classList.add('form-textarea-resize');
      function resize() {
        ta.style.height = 'auto';
        ta.style.height = ta.scrollHeight + 'px';
      }
      ta.addEventListener('input', resize);
      resize();
    })(textareas[t]);
  }

  /* --- Keyboard shortcut: Cmd+Enter / Ctrl+Enter to submit form --- */
  var formTextareas = document.querySelectorAll('form textarea');
  for (var k = 0; k < formTextareas.length; k++) {
    (function (ta) {
      ta.addEventListener('keydown', function (e) {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
          var form = ta.closest('form');
          if (form) {
            var submitBtn = form.querySelector('.btn-primary');
            if (submitBtn) submitBtn.click();
            else form.submit();
          }
        }
      });
    })(formTextareas[k]);
  }

  /* --- Scroll reveal via IntersectionObserver --- */
  if (!rm.matches && 'IntersectionObserver' in window) {
    var revealEls = document.querySelectorAll('.reveal');
    if (revealEls.length === 0) {
      var autoTargets = document.querySelectorAll('.task-card, .auth-card, .empty-state');
      for (var k2 = 0; k2 < autoTargets.length; k2++) {
        autoTargets[k2].classList.add('reveal');
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
