/* js/03-news.js: News and Patch Notes, from data/steam-news.json.
   That file is refreshed automatically from the official Steam announcements (tools/steam_news.py).
   Every post has its own link: /patch-notes#v2-0-6, /news#post-<id>. Patch Notes opens the newest patch,
   or the one in the link. Posts newer than the visitor's last look at that page are marked "New"
   (remembered in this browser only). */

const postAnchor = (post) => (post.version ? 'v' + post.version.replace(/\./g, '-') : 'post-' + post.id);

PAGES.news = () => {
  if (!NEWS.posts.length) return emptyState('No announcements yet.');
  const seen = lastSeen('news');
  return NEWS.posts.map((p) => postCard(p, '', seen)).join('');
};

PAGES.patches = () => {
  if (!NEWS.patches.length) return emptyState('No patch notes yet.');
  const seen = lastSeen('patches');
  return NEWS.patches.map((p) => postCard(p, `<span class="badge">Ver. ${esc(p.version)}</span>`, seen)).join('');
};

function postCard(post, badge, seen) {
  const fresh = seen && post.date > seen ? '<span class="badge new">New</span>' : '';
  const anchor = postAnchor(post);
  return `<details class="card post" id="${esc(anchor)}"><summary><span class="post-date">${formatDate(post.date)}</span>${badge}${fresh}<strong>${esc(post.title)}</strong></summary>
  <div class="post-body">${steamText(post.body)}</div>
  <p class="post-links"><a href="${esc(post.url)}" target="_blank" rel="noopener">Read on Steam</a><button type="button" class="copy-link" data-copy="${esc(anchor)}">Copy link</button></p></details>`;
}

// The date of the newest post the visitor saw on this page last time ("" on a first visit: nothing is marked).
function lastSeen(list) {
  try {
    return localStorage.getItem('seen-' + list) || '';
  } catch {
    return '';
  }
}

// Called after News or Patch Notes is drawn: open the linked post (or the newest patch), then remember what was seen.
function postsShown(pageId) {
  const posts = pageId === 'patches' ? NEWS.patches : NEWS.posts;
  const wanted = decodeURIComponent(location.hash.slice(1));
  const target =
    (wanted && document.getElementById(wanted)) || (pageId === 'patches' && document.querySelector('.post'));
  if (target) {
    if (!wanted) target.dataset.auto = '1'; // opened for the visitor: keep the address as it is
    target.open = true;
    if (wanted) target.scrollIntoView();
  }
  try {
    if (posts.length) localStorage.setItem('seen-' + pageId, posts[0].date);
  } catch {}
}

document.addEventListener(
  'toggle',
  (event) => {
    const post = event.target;
    if (!post.classList?.contains('post') || !post.open) return;
    if (post.dataset.auto) return delete post.dataset.auto;
    history.replaceState(null, '', '#' + post.id);
  },
  true,
);

document.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-copy]');
  if (!button) return;
  const url = location.href.split('#')[0] + '#' + button.dataset.copy;
  try {
    await navigator.clipboard.writeText(url);
    button.textContent = 'Link copied';
  } catch {
    button.textContent = url;
  }
  setTimeout(() => (button.textContent = 'Copy link'), 2000);
});

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
