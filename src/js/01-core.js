/* js/01-core.js: globals, data placeholders and shared helpers.
   The js/ files load in their numbered order (see index.html) and share one global scope,
   so code that runs at load time may only use what earlier files define.

   Map of the site script:
     Globals and helpers ...... GAME, NEWS, $, esc, emptyState (01-core)
     Pages .................... PAGES: home, tierlist, characters, guides, tools (02-pages)
     News, Patch Notes ........ PAGES.news, PAGES.patches, steamText (03-news)
     Start-up and routing ..... loadData, buildNav, showPage, the router (09-startup, loaded last) */

// Filled from data/game.json and data/steam-news.json at start-up (js/09-startup.js).
let GAME = {
  meta: {},
  SITE: { pages: [] },
  CHARACTERS: [],
  TIER_LIST: { tiers: [], lists: [] },
  GUIDES: [],
  TOOLS: [],
};
let NEWS = { posts: [], patches: [] };

// Every page renderer registers itself here: PAGES[pageId] = () => html string.
const PAGES = {};

const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
}

function emptyState(text) {
  return `<p class="empty">${esc(text)}</p>`;
}

function formatDate(iso) {
  const d = new Date(iso + 'T00:00:00Z');
  return isNaN(d)
    ? esc(iso)
    : d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
}
