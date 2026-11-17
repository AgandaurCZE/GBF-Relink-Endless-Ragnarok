/* js/04-blocks.js: content blocks, shared by character tabs and guides (docs/DATA_REFERENCE.md, "Blocks").
     {type: "text",  title?, text}                            paragraphs; a blank line starts a new one
     {type: "list",  title?, items: [text, ...]}              a bulleted list
     {type: "table", title?, columns: [...], rows: [[...]]}   a table that scrolls sideways on phones
     {type: "stats", title?, items: [{label, value}, ...]}    label and value pairs in a grid
     {type: "note",  title?, text, tone?: "tip" | "warning"}  a highlighted box
     {type: "image", src, alt, caption?}                      a picture from assets/, full width
   Everything is escaped: HTML in the data shows as text. */

function blocksHtml(blocks) {
  return blocks.map(blockHtml).join('');
}

function blockHtml(b) {
  const title = b.title ? `<h3 id="${esc(anchorId(b.title))}">${esc(b.title)}</h3>` : '';
  if (b.type === 'text') return `<div class="block">${title}${paragraphs(b.text)}</div>`;
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
  if (b.type === 'note')
    return `<aside class="block note note-${b.tone === 'warning' ? 'warning' : 'tip'}">${title}${paragraphs(b.text)}</aside>`;
  if (b.type === 'image')
    return `<figure class="block figure"><img src="${esc(b.src)}" alt="${esc(b.alt)}" loading="lazy">${b.caption ? `<figcaption>${esc(b.caption)}</figcaption>` : ''}</figure>`;
  return '';
}

function paragraphs(text) {
  return String(text)
    .split(/\n{2,}/)
    .map((p) => `<p>${esc(p).replace(/\n/g, '<br>')}</p>`)
    .join('');
}

// An id for a block title, so a guide's contents can link to it: "Early game" -> "early-game".
function anchorId(text) {
  return String(text)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}
