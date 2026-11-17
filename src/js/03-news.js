/* js/03-news.js: News and Patch Notes, from data/steam-news.json.
   That file is refreshed automatically from the official Steam announcements (tools/steam_news.py). */

PAGES.news = () => {
  if (!NEWS.posts.length) return emptyState('No announcements yet.');
  return NEWS.posts.map((p) => postCard(p, '')).join('');
};

PAGES.patches = () => {
  if (!NEWS.patches.length) return emptyState('No patch notes yet.');
  return NEWS.patches.map((p) => postCard(p, `<span class="badge">Ver. ${esc(p.version)}</span>`)).join('');
};

function postCard(post, badge) {
  return `<details class="card post"><summary><span class="post-date">${formatDate(post.date)}</span>${badge}<strong>${esc(post.title)}</strong></summary>
  <div class="post-body">${steamText(post.body)}</div>
  <p><a href="${esc(post.url)}" target="_blank" rel="noopener">Read on Steam</a></p></details>`;
}

// Steam posts use BBCode. Escape everything first, then turn the few safe tags into HTML; images and videos are dropped.
function steamText(body) {
  let html = esc(body)
    .replace(/\[img[^\]]*\][\s\S]*?\[\/img\]/gi, '')
    .replace(/\[previewyoutube[^\]]*\][\s\S]*?\[\/previewyoutube\]/gi, '')
    .replace(/\{STEAM_CLAN_IMAGE\}\S*/g, '')
    .replace(/\[(\/?)(b|i|u)\]/gi, '<$1$2>')
    .replace(/\[(\/?)h[1-6]\]/gi, (m, close) => (close ? '</h3>' : '<h3>'))
    .replace(/\[hr\]\[\/hr\]|\[hr\]/gi, '<hr>')
    .replace(/\[(\/?)(list|olist)\]/gi, (m, close, tag) => `<${close}${tag === 'olist' ? 'ol' : 'ul'}>`)
    .replace(/\[\*\]/g, '<li>')
    .replace(
      /\[url=(?:&quot;)?(https:\/\/[^\]\s]+?)(?:&quot;)?\]([\s\S]*?)\[\/url\]/gi,
      '<a href="$1" target="_blank" rel="noopener">$2</a>',
    )
    .replace(/\[\/?[a-z0-9]+(?:=[^\]]*)?\]/gi, '');
  return html
    .replace(/(<\/h3>|<hr>|<\/?ul>|<\/?ol>)\s*\n/g, '$1')
    .replace(/\n{2,}/g, '<br><br>')
    .replace(/\n/g, '<br>');
}
