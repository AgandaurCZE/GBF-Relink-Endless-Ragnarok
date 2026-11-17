/* js/05-search.js: the search box in the menu. Searches page names, characters (name, summary, tab text),
   guides, tools and the Steam news and patch notes (title and text); results replace the page until the box is cleared or a result is opened. */

function searchItems() {
  const items = GAME.SITE.pages.map((p) => ({ kind: 'Page', title: p.label, route: p.route, text: '' }));
  for (const c of GAME.CHARACTERS) {
    const text = (c.tabs || []).flatMap((t) => (t.blocks || []).map((b) => JSON.stringify(b))).join(' ');
    items.push({
      kind: 'Character',
      title: c.name,
      route: c.slug ? characterRoute(c) : 'characters',
      text: `${c.summary || ''} ${text}`,
    });
  }
  for (const g of GAME.GUIDES) items.push({ kind: 'Guide', title: g.title, route: 'guides', text: g.summary || '' });
  for (const t of GAME.TOOLS) items.push({ kind: 'Tool', title: t.title, route: 'tools', text: t.summary || '' });
  const plain = (body) => String(body).replace(/\[[^\]]*\]/g, ' ');
  for (const p of NEWS.patches)
    items.push({ kind: 'Patch notes', title: p.title, route: 'patch-notes', text: plain(p.body) });
  for (const p of NEWS.posts) items.push({ kind: 'News', title: p.title, route: 'news', text: plain(p.body) });
  return items;
}

function showSearch(query) {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!words.length || query.trim().length < 2) return showPage(pageForPath(location.pathname));
  const found = searchItems().filter((i) => words.every((w) => `${i.title} ${i.text}`.toLowerCase().includes(w)));
  found.sort(
    (a, b) =>
      words.every((w) => b.title.toLowerCase().includes(w)) - words.every((w) => a.title.toLowerCase().includes(w)),
  );
  $('pageTitle').textContent = 'Search';
  $('pageBody').innerHTML = found.length
    ? `<p class="muted">${found.length} result${found.length === 1 ? '' : 's'}</p>` +
      found
        .slice(0, 50)
        .map(
          (i) =>
            `<a class="card shortcut result" href="${esc(i.route || './')}" data-route="${esc(i.route)}"><span class="muted">${esc(i.kind)}</span> <strong>${esc(i.title)}</strong></a>`,
        )
        .join('')
    : emptyState('Nothing found.');
}
