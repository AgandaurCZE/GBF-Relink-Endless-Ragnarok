/* js/09-startup.js: data loading, navigation and clean-URL routing. Loaded last.
   Every page has its own path (SITE.pages[].route). tools/build_routes.py generates a copy of index.html
   for each path under routes/, so GitHub Pages serves a real page at every address. */

const APP_ROOT = new URL('.', document.baseURI).pathname;

async function loadJson(path) {
  const response = await fetch(path, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return response.json();
}

async function loadData() {
  const [game, news] = await Promise.all([loadJson('data/game.json'), loadJson('data/steam-news.json')]);
  GAME = game;
  NEWS = news;
}

function pageForPath(pathname) {
  const route = decodeURIComponent(pathname.startsWith(APP_ROOT) ? pathname.slice(APP_ROOT.length) : '').replace(
    /\/+$/,
    '',
  );
  const character = GAME.CHARACTERS.find((c) => c.slug && characterRoute(c) === route);
  if (character) return { id: 'character', nav: 'characters', label: character.name, character };
  const guide = GAME.GUIDES.find((g) => g.blocks?.length && guideRoute(g) === route);
  if (guide) return { id: 'guide', nav: 'guides', label: guide.title, guide };
  return GAME.SITE.pages.find((p) => p.route === route) || { id: 'notfound', label: 'Page not found' };
}

function buildNav() {
  let group = null;
  let html = '';
  for (const page of GAME.SITE.pages) {
    if (page.group && page.group !== group) html += `<div class="nav-group">${esc(page.group)}</div>`;
    group = page.group;
    html += `<a class="nav-item" href="${esc(page.route || './')}" data-route="${esc(page.route)}" data-page="${esc(page.id)}">${esc(page.label)}</a>`;
  }
  $('navList').innerHTML = html;
}

function showPage(page) {
  document
    .querySelectorAll('.nav-item')
    .forEach((a) => a.classList.toggle('active', a.dataset.page === (page.nav || page.id)));
  $('pageTitle').textContent = page.id === 'home' ? GAME.SITE.title : page.label;
  $('pageMeta').textContent = GAME.meta.patch && page.id !== 'home' ? `Game version ${GAME.meta.patch}` : ''; // Home shows it in its banner
  $('pageBody').innerHTML = (PAGES[page.id] || (() => emptyState('Coming soon.')))(page);
  document.title =
    page.id === 'home' ? `${GAME.SITE.title} | Tier list, guides, tools` : `${page.label} | ${GAME.SITE.title}`;
  setMenu(false);
  if (page.id === 'character') characterTabs(page.character);
  if (page.id === 'guide') guideScroll();
  if (page.id === 'news' || page.id === 'patches') postsShown(page.id);
}

function go(route) {
  history.pushState(null, '', APP_ROOT + route);
  $('search').value = '';
  window.scrollTo(0, 0);
  showPage(pageForPath(location.pathname));
}

function setMenu(open) {
  $('mobileMenu').setAttribute('aria-expanded', String(open));
  $('mainNavigation').classList.toggle('is-open', open);
  $('menuBackdrop').hidden = !open;
}

document.addEventListener('click', (event) => {
  const link = event.target.closest('a[data-route]');
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.button !== 0) return;
  event.preventDefault();
  go(link.dataset.route);
});
window.addEventListener('popstate', () => showPage(pageForPath(location.pathname)));
$('mobileMenu').addEventListener('click', () => setMenu(!$('mainNavigation').classList.contains('is-open')));
$('menuBackdrop').addEventListener('click', () => setMenu(false));
$('search').addEventListener('input', () => showSearch($('search').value));

// Keyboard: "/" jumps to the search box from anywhere (unless typing), Esc clears it and closes the phone menu.
document.addEventListener('keydown', (event) => {
  const typing =
    /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
  if (event.key === '/' && !typing && !event.ctrlKey && !event.metaKey && !event.altKey) {
    event.preventDefault();
    if (window.matchMedia('(max-width: 800px)').matches) setMenu(true);
    $('search').focus();
  } else if (event.key === 'Escape') {
    if ($('search').value) {
      $('search').value = '';
      showSearch('');
    }
    if (document.activeElement === $('search')) $('search').blur();
    setMenu(false);
  }
});

// Light / dark: follows the system until the visitor picks one; the choice is remembered in this browser.
const currentTheme = () =>
  document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
function themeLabel() {
  $('themeBtn').textContent = currentTheme() === 'light' ? '☾ Dark mode' : '☀ Light mode';
  document.querySelector('meta[name="theme-color"]').content = currentTheme() === 'light' ? '#f3f6fb' : '#0b1424';
}
$('themeBtn').addEventListener('click', () => {
  const next = currentTheme() === 'light' ? 'dark' : 'light';
  document.documentElement.dataset.theme = next;
  try {
    localStorage.setItem('theme', next);
  } catch {}
  themeLabel();
});
themeLabel();

// Installable app (sw.js, manifest.webmanifest): offline reading of pages already opened, and an "Install app"
// button where the browser offers installing.
if ('serviceWorker' in navigator)
  navigator.serviceWorker.register(APP_ROOT + 'sw.js', { scope: APP_ROOT }).catch(() => {});
let installPrompt = null;
window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  installPrompt = event;
  $('installBtn').hidden = false;
});
$('installBtn').addEventListener('click', async () => {
  if (!installPrompt) return;
  installPrompt.prompt();
  await installPrompt.userChoice.catch(() => {});
  installPrompt = null;
  $('installBtn').hidden = true;
});

// "Back to top" appears once the page is scrolled down a screen.
window.addEventListener(
  'scroll',
  () => {
    $('toTop').hidden = window.scrollY < window.innerHeight;
  },
  { passive: true },
);
$('toTop').addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  $('pageBody').focus({ preventScroll: true });
});

// Shown for an address that is no page (GitHub Pages serves 404.html, generated by tools/build_routes.py).
PAGES.notfound = () =>
  `${emptyState('There is no page at this address.')}<p><a href="./" data-route="">Go to the home page</a></p>`;

loadData()
  .then(() => {
    buildNav();
    if (GAME.meta.updated) $('dataDate').textContent = `Guide updated ${formatDate(GAME.meta.updated)}.`;
    showPage(pageForPath(location.pathname));
  })
  .catch((error) => {
    console.error(error);
    $('pageBody').innerHTML = emptyState('The guide data could not be loaded. Please reload the page.');
  });
