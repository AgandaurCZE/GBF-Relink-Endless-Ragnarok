/* js/06-guides.js: the Guides list and each guide's own page at /guides/<id>.

   GUIDES[] {id, title, summary, updated?, blocks?: [...]}
   A guide with blocks gets its own page (drawn by js/04-blocks.js); one without is listed as coming soon.
   A guide with three or more titled blocks shows a contents list that jumps to each. */

function guideRoute(g) {
  return 'guides/' + g.id;
}

PAGES.guides = () => {
  if (!GAME.GUIDES.length) return emptyState('Guides are coming soon.');
  return `<div class="grid guides">${GAME.GUIDES.map((g) => {
    const inner = `<h2>${esc(g.title)}</h2><p>${esc(g.summary)}</p>${g.blocks?.length ? '' : '<p class="muted">Coming soon</p>'}`;
    return g.blocks?.length
      ? `<a class="card shortcut" href="${esc(guideRoute(g))}" data-route="${esc(guideRoute(g))}">${inner}</a>`
      : `<div class="card">${inner}</div>`;
  }).join('')}</div>`;
};

PAGES.guide = (page) => {
  const g = page.guide;
  const titled = g.blocks.filter((b) => b.title);
  const contents =
    titled.length >= 3
      ? `<nav class="card contents" aria-label="Contents"><strong>Contents</strong><ol>${titled
          .map(
            (b) =>
              `<li><a href="#${esc(anchorId(b.title))}" data-anchor="${esc(anchorId(b.title))}">${esc(b.title)}</a></li>`,
          )
          .join('')}</ol></nav>`
      : '';
  const meta = g.updated ? `<p class="muted">Updated ${formatDate(g.updated)}</p>` : '';
  return `<a class="back-link" href="guides" data-route="guides">← All guides</a>${g.summary ? `<p>${esc(g.summary)}</p>` : ''}${meta}${contents}<article class="guide-body">${blocksHtml(g.blocks)}</article>`;
};

// Contents links scroll to their section without leaving the page; a #section in the address opens there.
document.addEventListener('click', (event) => {
  const link = event.target.closest('a[data-anchor]');
  if (!link) return;
  event.preventDefault();
  document.getElementById(link.dataset.anchor)?.scrollIntoView({ behavior: 'smooth' });
  history.replaceState(null, '', '#' + link.dataset.anchor);
});

function guideScroll() {
  const id = decodeURIComponent(location.hash.slice(1));
  if (id) document.getElementById(id)?.scrollIntoView();
}
