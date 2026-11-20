/* Keep the complete page readable without JavaScript. */
(() => {
  const cover = document.querySelector('.portfolio-cover img');
  if (cover) {
    const fallback = () => {
      const src = cover.dataset.fallback;
      if (src && !cover.dataset.fallbackTried) {
        cover.dataset.fallbackTried = 'true';
        cover.src = src;
      } else { cover.hidden = true; }
    };
    cover.addEventListener('error', fallback);
    if (cover.complete && cover.naturalWidth === 0) fallback();
  }
  const menu = document.querySelector('.chapter-nav');
  if (menu) {
    menu.addEventListener('click', e => { if (e.target.closest('a')) menu.open = false; });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); } });
    document.addEventListener('click', e => { if (menu.open && !menu.contains(e.target)) menu.open = false; });
  }
})();
