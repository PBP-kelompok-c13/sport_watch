// shop/static/shop/js/toast.js
(function () {
  const el = document.getElementById('toast');
  const text = document.getElementById('toast-text');

  // If toast container isn't on the page, provide a no-op.
  if (!el || !text) {
    window.showToast = function () {};
    return;
  }

  // Set background color based on type
  function setStyle(type) {
    el.classList.remove('bg-green-600','bg-blue-600','bg-red-600','bg-yellow-600','text-white');
    el.classList.add('text-white');
    switch ((type || 'info').toLowerCase()) {
      case 'success': el.classList.add('bg-green-600'); break;
      case 'error':   el.classList.add('bg-red-600');   break;
      case 'warning': el.classList.add('bg-yellow-600');break;
      default:        el.classList.add('bg-blue-600');  // info
    }
  }

  let hideTimer;

  window.showToast = function (message, type = 'info', durationMs = 1800) {
    try {
      setStyle(type);
      text.textContent = message || '';

      // Show: unhide then remove opacity/translate for the transition
      el.classList.remove('hidden');
      // next frame so transition runs
      requestAnimationFrame(() => {
        el.classList.remove('opacity-0', 'translate-y-5');
      });

      // Reset previous timer
      clearTimeout(hideTimer);
      hideTimer = setTimeout(() => {
        // Hide with transition, then set hidden
        el.classList.add('opacity-0', 'translate-y-5');
        setTimeout(() => el.classList.add('hidden'), 300);
      }, durationMs);
    } catch (err) {
      console.error('Toast error:', err);
    }
  };
})();
