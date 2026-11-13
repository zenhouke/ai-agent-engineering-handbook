const nav = document.querySelector('.sidebar');
const toggle = document.querySelector('.menu-button');
const search = document.querySelector('#lesson-search');
const empty = document.querySelector('#empty-search');
let searchExpansion = null;

function closeMenu() {
  nav.classList.remove('is-open');
  toggle.setAttribute('aria-expanded', 'false');
}
toggle.addEventListener('click', () => {
  const open = !nav.classList.contains('is-open');
  nav.classList.toggle('is-open', open);
  toggle.setAttribute('aria-expanded', String(open));
  if (open) search.focus();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && nav.classList.contains('is-open')) {
    closeMenu();
    toggle.focus();
  }
});
nav.addEventListener('click', (event) => {
  if (event.target.closest('a') && matchMedia('(max-width:760px)').matches) closeMenu();
});
document.addEventListener('click', (event) => {
  if (!nav.contains(event.target) && !toggle.contains(event.target)) closeMenu();
});
search.addEventListener('input', () => {
  const query = search.value.trim().toLocaleLowerCase();
  if (query && searchExpansion === null) {
    searchExpansion = new Map([...nav.querySelectorAll('[data-section], [data-group]')].map((group) => [group, group.open]));
  }
  let count = 0;
  nav.querySelectorAll('[data-lesson]').forEach((item) => {
    const match = item.dataset.title.toLocaleLowerCase().includes(query);
    item.hidden = !match;
    if (match) count++;
  });
  nav.querySelectorAll('[data-section], [data-group]').forEach((group) => {
    group.hidden = !group.querySelector('[data-lesson]:not([hidden])');
    if (query) group.open = true;
    else if (searchExpansion) group.open = searchExpansion.get(group);
  });
  if (!query) searchExpansion = null;
  empty.hidden = count > 0;
});

// The stable lesson key is shared across language editions. Storage is optional.
const completion = document.querySelector('[data-complete]');
let learned = new Set();
try {
  const stored = JSON.parse(localStorage.getItem('ai-handbook-learned') || '[]');
  if (Array.isArray(stored)) learned = new Set(stored.filter((item) => typeof item === 'string'));
} catch { /* Reading still works when storage is unavailable or corrupted. */ }
function showProgress() {
  if (completion) {
    const active = learned.has(completion.dataset.complete);
    completion.textContent = active ? completion.dataset.done : completion.dataset.pending;
    completion.setAttribute('aria-pressed', String(active));
  }
  const progress = document.querySelector('[data-progress]');
  const validKeys = [...nav.querySelectorAll('[data-lesson]')].map((item) => item.dataset.lesson);
  progress.textContent = `${progress.dataset.progress}: ${validKeys.filter((key) => learned.has(key)).length} / ${validKeys.length}`;
}
completion?.addEventListener('click', () => {
  const key = completion.dataset.complete;
  learned.has(key) ? learned.delete(key) : learned.add(key);
  try { localStorage.setItem('ai-handbook-learned', JSON.stringify([...learned])); } catch { /* Session-only fallback. */ }
  showProgress();
});
showProgress();

// Scroll only the fixed navigation pane; preserve document position and focus.
const currentLesson = nav.querySelector('a[aria-current="page"]');
if (currentLesson && matchMedia('(min-width:761px)').matches) {
  const linkBox = currentLesson.getBoundingClientRect();
  const navBox = nav.getBoundingClientRect();
  if (linkBox.bottom > navBox.bottom) nav.scrollTop += linkBox.bottom - navBox.bottom + 32;
}

// Keep the current section link visible without moving focus or scrolling the document.
const sections = document.querySelectorAll('article h2[id], article h3[id]');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      document.querySelectorAll('.toc a').forEach((link) => {
        link.removeAttribute('aria-current');
        if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
      });
    }
  }, { rootMargin: '-80px 0px -65% 0px' });
  sections.forEach((section) => observer.observe(section));
}
