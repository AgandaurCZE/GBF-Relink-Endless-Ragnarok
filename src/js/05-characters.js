/* js/05-characters.js: each character's own page at /characters/<slug>, with tabs.

   CHARACTERS[] {name, slug, image, summary, tabs: [{id, label, blocks: [...]}]}
   The blocks are drawn by js/04-blocks.js. The open tab is kept in the address (#skills),
   so a link can point at one tab. */

function characterRoute(c) {
  return 'characters/' + c.slug;
}

PAGES.character = (page) => {
  const c = page.character;
  const tabs = c.tabs || [];
  const img = c.image ? `<img class="profile-image" src="${esc(c.image)}" alt="">` : '';
  const summary = c.summary ? `<p>${esc(c.summary)}</p>` : '';
  const buttons = tabs
    .map(
      (t) =>
        `<button type="button" class="profile-tab" role="tab" data-tab="${esc(t.id)}" aria-selected="false">${esc(t.label)}</button>`,
    )
    .join('');
  const panels = tabs
    .map(
      (t) =>
        `<section class="profile-panel" role="tabpanel" data-tab="${esc(t.id)}" hidden>${t.blocks?.length ? blocksHtml(t.blocks) : emptyState('More coming soon.')}</section>`,
    )
    .join('');
  const body = tabs.length
    ? `<div class="profile-tabs" role="tablist">${buttons}</div>${panels}`
    : emptyState('More coming soon.');
  return `<a class="back-link" href="characters" data-route="characters">← All characters</a>
  <div class="profile-head">${img}<div>${summary}</div></div>${body}${mentionsHtml(c)}`;
};

// Official posts that name this character (or one of its `aliases`), newest first: patches, then news.
function mentions(c) {
  const names = [c.name, ...(c.aliases || [])].map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const re = new RegExp(`(^|[^\\p{L}\\p{N}])(${names.join('|')})(?![\\p{L}\\p{N}])`, 'iu');
  return [...NEWS.patches, ...NEWS.posts].filter((p) => re.test(p.title) || re.test(p.body));
}

function mentionsHtml(c) {
  const found = mentions(c);
  if (!found.length) return '';
  const items = found
    .slice(0, 12)
    .map((p) => {
      const route = (p.version ? 'patch-notes#' : 'news#') + postAnchor(p);
      const tag = p.version ? `<span class="badge">Ver. ${esc(p.version)}</span>` : '';
      return `<li><a href="${esc(route)}" data-route="${esc(route)}"><span class="post-date">${formatDate(p.date)}</span>${tag}${esc(p.title)}</a></li>`;
    })
    .join('');
  return `<section class="card mentions"><h2>In the official patch notes and news</h2><ul>${items}</ul></section>`;
}

function characterTabs(c) {
  const tabs = c.tabs || [];
  if (!tabs.length) return;
  const show = (id, record) => {
    const tab = tabs.find((t) => t.id === id) || tabs[0];
    document
      .querySelectorAll('.profile-tab')
      .forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === tab.id)));
    document.querySelectorAll('.profile-panel').forEach((p) => (p.hidden = p.dataset.tab !== tab.id));
    if (record) history.replaceState(null, '', '#' + tab.id);
  };
  document
    .querySelectorAll('.profile-tab')
    .forEach((b) => b.addEventListener('click', () => show(b.dataset.tab, true)));
  show(decodeURIComponent(location.hash.slice(1)), false);
}
