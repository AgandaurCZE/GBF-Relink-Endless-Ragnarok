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
  return GAME.SITE.pages.find((p) => p.route === route) || GAME.SITE.pages[0];
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
  document.querySelectorAll('.nav-item').forEach((a) => a.classList.toggle('active', a.dataset.page === page.id));
  $('pageTitle').textContent = page.id === 'home' ? GAME.SITE.title : page.label;
  $('pageMeta').textContent = GAME.meta.patch ? `Game version ${GAME.meta.patch}` : '';
  $('pageBody').innerHTML = (PAGES[page.id] || (() => emptyState('Coming soon.')))();
  document.title =
    page.id === 'home' ? `${GAME.SITE.title} | Tier list, guides, tools` : `${page.label} | ${GAME.SITE.title}`;
  setMenu(false);
}

function go(route) {
  history.pushState(null, '', APP_ROOT + route);
  showPage(pageForPath(location.pathname));
  window.scrollTo(0, 0);
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

loadData()
  .then(() => {
    buildNav();
    showPage(pageForPath(location.pathname));
  })
  .catch((error) => {
    console.error(error);
    $('pageBody').innerHTML = emptyState('The guide data could not be loaded. Please reload the page.');
  });
