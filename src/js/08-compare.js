/* js/08-compare.js: Compare. Two or three characters side by side, from the `stats` blocks in their tabs
   (a stat is matched by its block title and label, so "Stats › HP" lines up across characters).
   The choice is kept in the address: /compare#katalina,io. Rows whose values differ are marked. */

function statsOf(c) {
  const rows = new Map();
  for (const tab of c.tabs || [])
    for (const b of tab.blocks || [])
      if (b.type === 'stats') for (const item of b.items) rows.set(`${b.title || ''}\u0000${item.label}`, item.value);
  return rows;
}

PAGES.compare = () => {
  const pool = GAME.CHARACTERS.filter((c) => c.slug && statsOf(c).size);
  if (pool.length < 2) return emptyState('Comparisons are coming soon.');
  return `<p>Pick two or three characters to see their stats side by side.</p>
  <div class="compare-pickers">${[0, 1, 2]
    .map(
      (i) =>
        `<label class="picker"><span class="muted">${i === 2 ? 'Third (optional)' : i === 0 ? 'First' : 'Second'}</span><select data-slot="${i}">${
          i === 2 ? '<option value="">None</option>' : ''
        }${pool.map((c) => `<option value="${esc(c.slug)}">${esc(c.name)}</option>`).join('')}</select></label>`,
    )
    .join('')}</div><div id="compareTable"></div>`;
};

function compareShown() {
  const pool = GAME.CHARACTERS.filter((c) => c.slug && statsOf(c).size);
  const selects = [...document.querySelectorAll('.compare-pickers select')];
  if (!selects.length) return;
  const wanted = decodeURIComponent(location.hash.slice(1)).split(',');
  const fallback = [pool[0].slug, pool[1].slug, ''];
  selects.forEach((s, i) => (s.value = pool.some((c) => c.slug === wanted[i]) ? wanted[i] : fallback[i]));
  const draw = (record) => {
    const chosen = [...new Set(selects.map((s) => s.value).filter(Boolean))].map((slug) =>
      pool.find((c) => c.slug === slug),
    );
    if (record) history.replaceState(null, '', '#' + chosen.map((c) => c.slug).join(','));
    const stats = chosen.map(statsOf);
    const keys = [...new Set(stats.flatMap((s) => [...s.keys()]))];
    let group = null;
    const rows = keys
      .map((key) => {
        const [title, label] = key.split('\u0000');
        const values = stats.map((s) => s.get(key) ?? '–');
        const head =
          title !== group ? `<tr class="compare-group"><th colspan="${chosen.length + 1}">${esc(title)}</th></tr>` : '';
        group = title;
        const differs = new Set(values).size > 1 ? ' class="differs"' : '';
        return `${head}<tr${differs}><th scope="row">${esc(label)}</th>${values.map((v) => `<td>${esc(v)}</td>`).join('')}</tr>`;
      })
      .join('');
    const heads = chosen
      .map(
        (c) =>
          `<th scope="col"><a href="${esc(characterRoute(c))}" data-route="${esc(characterRoute(c))}">${esc(c.name)}</a></th>`,
      )
      .join('');
    $('compareTable').innerHTML =
      `<div class="table-wrap"><table class="compare"><thead><tr><th></th>${heads}</tr></thead><tbody>${rows}</tbody></table></div>`;
  };
  selects.forEach((s) => s.addEventListener('change', () => draw(true)));
  draw(false);
}
