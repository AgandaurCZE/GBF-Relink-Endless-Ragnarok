/* js/02-pages.js: Home, Tier List, Characters and Tools (Guides: js/06-guides.js).
   Each page reads its content from data/game.json; none of the content lives in this file. */

// ===== Home: a dashboard. Each section shows only when it has something to show.
PAGES.home = () => {
  const patch = NEWS.patches[0];
  const seen = lastSeen('patches');
  const version = GAME.meta.patch ? `<span class="badge">Game version ${esc(GAME.meta.patch)}</span>` : '';
  const hero = `<section class="hero"><div><p class="hero-kicker">Fan-made guide</p>
    <p class="hero-text">Tier list, character guides and tools for <strong>Granblue Fantasy: Relink - Endless Ragnarok</strong>.</p>${version}</div></section>`;
  const latest = patch
    ? `<a class="card shortcut latest" href="patch-notes#${esc(postAnchor(patch))}" data-route="patch-notes#${esc(postAnchor(patch))}">
      <span class="muted">Latest patch</span>${seen && patch.date > seen ? '<span class="badge new">New</span>' : ''}
      <strong>${esc(patch.title)}</strong><span class="post-date">${formatDate(patch.date)}</span></a>`
    : '';
  const news = NEWS.posts.slice(0, 3);
  const newsList = news.length
    ? `<section class="card"><h2>News</h2><ul class="link-list">${news
        .map(
          (p) =>
            `<li><a href="news#${esc(postAnchor(p))}" data-route="news#${esc(postAnchor(p))}"><span class="post-date">${formatDate(p.date)}</span>${esc(p.title)}</a></li>`,
        )
        .join('')}</ul><a href="news" data-route="news">All news →</a></section>`
    : '';
  const recent = [
    ...GAME.GUIDES.filter((g) => g.updated && g.blocks?.length).map((g) => ({
      kind: 'Guide',
      title: g.title,
      date: g.updated,
      route: guideRoute(g),
    })),
    ...GAME.CHARACTERS.filter((c) => c.updated && c.slug).map((c) => ({
      kind: 'Character',
      title: c.name,
      date: c.updated,
      route: characterRoute(c),
    })),
  ]
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .slice(0, 6);
  const recentList = recent.length
    ? `<section class="card"><h2>Recently updated</h2><ul class="link-list">${recent
        .map(
          (r) =>
            `<li><a href="${esc(r.route)}" data-route="${esc(r.route)}"><span class="post-date">${formatDate(r.date)}</span><span class="muted">${r.kind}</span> ${esc(r.title)}</a></li>`,
        )
        .join('')}</ul></section>`
    : '';
  const portraits = GAME.CHARACTERS.filter((c) => c.image && c.slug).slice(0, 12);
  const roster = portraits.length
    ? `<section><h2 class="section-title">Characters</h2><div class="roster">${portraits.map(characterChip).join('')}</div></section>`
    : '';
  const cards = GAME.SITE.pages
    .filter((p) => p.id !== 'home')
    .map(
      (p) =>
        `<a class="card shortcut" href="${esc(p.route)}" data-route="${esc(p.route)}"><strong>${esc(p.label)}</strong></a>`,
    )
    .join('');
  return `${hero}${latest}<div class="dashboard">${recentList}${newsList}</div>${roster}
  <h2 class="section-title">Explore</h2><div class="grid shortcuts">${cards}</div>`;
};

// ===== Tier list: TIER_LIST.tiers [{name, color}] (best first) and TIER_LIST.lists [{id, label, about?, updated?,
// rows: {tier name: [character names, in order]}}]. Several lists show as tabs; /tierlist#<list id> opens one.
PAGES.tierlist = () => {
  const { tiers, lists } = GAME.TIER_LIST;
  const shown = lists.filter((l) => Object.values(l.rows || {}).some((names) => names.length));
  if (!tiers.length || !shown.length) return emptyState('The tier list is coming soon.');
  const tabs =
    shown.length > 1
      ? `<div class="profile-tabs" role="tablist">${shown
          .map(
            (l) =>
              `<button type="button" class="profile-tab tier-tab" role="tab" data-list="${esc(l.id)}" aria-selected="false">${esc(l.label)}</button>`,
          )
          .join('')}</div>`
      : '';
  return (
    tabs +
    shown
      .map((l) => `<section class="tier-list" data-list="${esc(l.id)}" hidden>${tierListHtml(l, tiers)}</section>`)
      .join('')
  );
};

function tierListHtml(list, tiers) {
  const byName = Object.fromEntries(GAME.CHARACTERS.map((c) => [c.name, c]));
  const head = `${list.about ? `<p>${esc(list.about)}</p>` : ''}${list.updated ? `<p class="muted">Updated ${formatDate(list.updated)}</p>` : ''}`;
  const rows = tiers
    .map((tier) => {
      const chips = (list.rows[tier.name] || []).map((n) => characterChip(byName[n] || { name: n })).join('');
      return `<div class="tier-row"><div class="tier-label" style="--tier:${esc(tier.color)}">${esc(tier.name)}</div><div class="tier-items">${chips}</div></div>`;
    })
    .join('');
  return head + rows;
}

// Called after the Tier List is drawn: show the list named in the address, or the first one.
function tierTabs() {
  const sections = [...document.querySelectorAll('.tier-list')];
  if (!sections.length) return;
  const show = (id, record) => {
    const target = sections.find((s) => s.dataset.list === id) || sections[0];
    sections.forEach((s) => (s.hidden = s !== target));
    document
      .querySelectorAll('.tier-tab')
      .forEach((b) => b.setAttribute('aria-selected', String(b.dataset.list === target.dataset.list)));
    if (record) history.replaceState(null, '', '#' + target.dataset.list);
  };
  document.querySelectorAll('.tier-tab').forEach((b) => b.addEventListener('click', () => show(b.dataset.list, true)));
  show(decodeURIComponent(location.hash.slice(1)), false);
}

// ===== Characters: CHARACTERS[] {name, slug, image, tabs} (each character's own page: js/04-characters.js)
PAGES.characters = () => {
  if (!GAME.CHARACTERS.length) return emptyState('Characters are coming soon.');
  return `<div class="grid characters">${GAME.CHARACTERS.map(characterChip).join('')}</div>`;
};

function characterChip(c) {
  const img = c.image ? `<img src="${esc(c.image)}" alt="" loading="lazy">` : '';
  if (!c.slug) return `<div class="card character">${img}<strong>${esc(c.name)}</strong></div>`;
  const route = characterRoute(c);
  return `<a class="card character shortcut" href="${esc(route)}" data-route="${esc(route)}">${img}<strong>${esc(c.name)}</strong></a>`;
}

// ===== Tools: TOOLS[] {id, title, summary}
PAGES.tools = () => {
  if (!GAME.TOOLS.length) return emptyState('Tools are coming soon.');
  return GAME.TOOLS.map((t) => `<article class="card"><h2>${esc(t.title)}</h2><p>${esc(t.summary)}</p></article>`).join(
    '',
  );
};
