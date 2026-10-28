(() => {
  'use strict';
  const storage = {
    get(key) { try { return JSON.parse(localStorage.getItem(key)); } catch (_) { return null; } },
    set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* Reading works without storage. */ } }
  };
  const validProgress = (book, value) => value && Number.isInteger(value.chapter) && value.chapter >= 0 && value.chapter <= 50 &&
    value.path === `/novels/${book}/${String(value.chapter).padStart(3, '0')}/`;
  document.querySelectorAll('[data-novel-resume]').forEach(link => {
    const book = link.dataset.novelResume;
    const progress = storage.get(`novel:${book}:progress`);
    if (!validProgress(book, progress)) return;
    link.href = `${progress.path}#novel-resume`;
    link.textContent = `继续阅读 · ${progress.title || `第${progress.chapter}章`}`;
    link.hidden = false;
  });
  const reader = document.querySelector('.novel-reader');
  if (!reader) return;
  const book = reader.dataset.novel;
  const key = `novel:${book}:progress`;
  let font = Number(storage.get('novel:font-size')) || 18;
  const setFont = value => {
    font = Math.min(26, Math.max(16, value));
    reader.style.setProperty('--novel-font-size', `${font}px`);
    document.querySelector('#novel-font-size').textContent = font;
    storage.set('novel:font-size', font);
  };
  setFont(font);
  reader.querySelectorAll('[data-font]').forEach(button => button.addEventListener('click', () => {
    setFont(button.dataset.font === 'reset' ? 18 : font + Number(button.dataset.font));
  }));
  reader.querySelector('[data-novel-theme]').addEventListener('click', () => {
    document.querySelector('#color-toggle-btn')?.click();
  });
  const previous = storage.get(key);
  if (location.hash === '#novel-resume' && validProgress(book, previous) && previous.path === location.pathname) {
    window.addEventListener('load', () => {
      requestAnimationFrame(() => {
        const height = Math.max(0, document.documentElement.scrollHeight - innerHeight);
        window.scrollTo({ top: Math.min(1, Math.max(0, Number(previous.ratio) || 0)) * height, behavior: 'instant' });
      });
    }, { once: true });
  }
  const save = () => {
    const height = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    storage.set(key, { chapter: Number(reader.dataset.chapter), title: reader.dataset.title, path: location.pathname,
      ratio: Math.min(1, Math.max(0, window.scrollY / height)) });
  };
  // Do not overwrite the stored scroll position before a requested resume has restored it.
  if (location.hash !== '#novel-resume') save();
  let timer;
  window.addEventListener('scroll', () => { clearTimeout(timer); timer = setTimeout(save, 200); }, { passive: true });
  window.addEventListener('pagehide', save);
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') save(); });
})();
