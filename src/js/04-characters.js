/* js/04-characters.js: each character's own page at /characters/<slug>, with tabs.

   CHARACTERS[] {name, slug, image, summary, tabs: [{id, label, blocks: [...]}]}
   A block is one of (docs/DATA_REFERENCE.md has the details):
     {type: "text",  title?, text}                       a paragraph; blank lines start a new paragraph
     {type: "list",  title?, items: [text, ...]}         a bulleted list
     {type: "table", title?, columns: [...], rows: [[...], ...]}
     {type: "stats", title?, items: [{label, value}, ...]}   label and value pairs in a grid
   The open tab is kept in the address (#skills), so a link can point at one tab. */

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
        `<section class="profile-panel" role="tabpanel" data-tab="${esc(t.id)}" hidden>${blocksHtml(t.blocks || [])}</section>`,
    )
    .join('');
  const body = tabs.length
    ? `<div class="profile-tabs" role="tablist">${buttons}</div>${panels}`
    : emptyState('More coming soon.');
  return `<a class="back-link" href="characters" data-route="characters">← All characters</a>
  <div class="profile-head">${img}<div>${summary}</div></div>${body}`;
};

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

function blocksHtml(blocks) {
  return blocks.map(blockHtml).join('');
}

function blockHtml(b) {
  const title = b.title ? `<h3>${esc(b.title)}</h3>` : '';
  if (b.type === 'text')
    return `<div class="block">${title}${String(b.text)
      .split(/\n{2,}/)
      .map((p) => `<p>${esc(p).replace(/\n/g, '<br>')}</p>`)
      .join('')}</div>`;
  if (b.type === 'list')
    return `<div class="block">${title}<ul>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul></div>`;
  if (b.type === 'table') {
    const head = b.columns.map((c) => `<th>${esc(c)}</th>`).join('');
    const rows = b.rows.map((r) => `<tr>${r.map((v) => `<td>${esc(v)}</td>`).join('')}</tr>`).join('');
    return `<div class="block">${title}<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div></div>`;
  }
  if (b.type === 'stats')
    return `<div class="block">${title}<dl class="stats">${b.items
      .map((i) => `<div><dt>${esc(i.label)}</dt><dd>${esc(i.value)}</dd></div>`)
      .join('')}</dl></div>`;
  return '';
}
