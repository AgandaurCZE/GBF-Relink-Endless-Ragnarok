/* js/02-pages.js: Home, Tier List, Characters, Guides and Tools.
   Each page reads its content from data/game.json; none of the content lives in this file. */

// ===== Home
PAGES.home = () => {
  const cards = GAME.SITE.pages
    .filter((p) => p.id !== 'home')
    .map(
      (p) =>
        `<a class="card shortcut" href="${esc(p.route)}" data-route="${esc(p.route)}"><strong>${esc(p.label)}</strong></a>`,
    )
    .join('');
  return `<section class="intro"><p>A fan-made guide to <strong>Granblue Fantasy: Relink - Endless Ragnarok</strong>: tier list, character guides and tools.</p></section>
  <div class="grid shortcuts">${cards}</div>`;
};

// ===== Tier list: TIER_LIST.tiers (order, colours) and TIER_LIST.ratings (character name -> tier)
PAGES.tierlist = () => {
  const { tiers, ratings } = GAME.TIER_LIST;
  if (!tiers.length || !Object.keys(ratings).length) return emptyState('The tier list is coming soon.');
  const byName = Object.fromEntries(GAME.CHARACTERS.map((c) => [c.name, c]));
  return tiers
    .map((tier) => {
      const names = Object.keys(ratings).filter((n) => ratings[n] === tier.name);
      const chips = names.map((n) => characterChip(byName[n] || { name: n })).join('');
      return `<div class="tier-row"><div class="tier-label" style="--tier:${esc(tier.color)}">${esc(tier.name)}</div><div class="tier-items">${chips}</div></div>`;
    })
    .join('');
};

// ===== Characters: CHARACTERS[] {name, image, element, role}
PAGES.characters = () => {
  if (!GAME.CHARACTERS.length) return emptyState('Characters are coming soon.');
  return `<div class="grid characters">${GAME.CHARACTERS.map(characterChip).join('')}</div>`;
};

function characterChip(c) {
  const img = c.image ? `<img src="${esc(c.image)}" alt="" loading="lazy">` : '';
  return `<div class="card character">${img}<strong>${esc(c.name)}</strong></div>`;
}

// ===== Guides: GUIDES[] {id, title, summary}
PAGES.guides = () => {
  if (!GAME.GUIDES.length) return emptyState('Guides are coming soon.');
  return GAME.GUIDES.map(
    (g) => `<article class="card"><h2>${esc(g.title)}</h2><p>${esc(g.summary)}</p></article>`,
  ).join('');
};

// ===== Tools: TOOLS[] {id, title, summary}
PAGES.tools = () => {
  if (!GAME.TOOLS.length) return emptyState('Tools are coming soon.');
  return GAME.TOOLS.map((t) => `<article class="card"><h2>${esc(t.title)}</h2><p>${esc(t.summary)}</p></article>`).join(
    '',
  );
};
