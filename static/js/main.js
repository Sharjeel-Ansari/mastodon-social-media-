/* ── Vibe Social — main.js ───────────── */

// Mobile sidebar
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Focus new post textarea (called from "New Post" button)
function focusNewPost() {
  const ta = document.getElementById('postContent');
  if (ta) {
    ta.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => ta.focus(), 300);
  }
}

// Post menu toggle
function toggleMenu(postId) {
  const menu = document.getElementById('menu-' + postId);
  document.querySelectorAll('.post-menu-dropdown.open').forEach(m => { if (m !== menu) m.classList.remove('open'); });
  menu.classList.toggle('open');
}
document.addEventListener('click', e => {
  if (!e.target.closest('.post-menu'))
    document.querySelectorAll('.post-menu-dropdown.open').forEach(m => m.classList.remove('open'));
});

// ── Image Preview ──────────────────────
let selectedImageFile = null;
document.addEventListener('DOMContentLoaded', () => {
  const inp = document.getElementById('postImageInput');
  if (inp) inp.addEventListener('change', function() {
    const file = this.files[0];
    if (!file) return;
    selectedImageFile = file;
    const reader = new FileReader();
    reader.onload = ev => {
      document.getElementById('previewImg').src = ev.target.result;
      document.getElementById('mediaPreview').style.display = 'flex';
    };
    reader.readAsDataURL(file);
  });
});
function clearMedia() {
  selectedImageFile = null;
  const inp = document.getElementById('postImageInput');
  if (inp) inp.value = '';
  document.getElementById('mediaPreview').style.display = 'none';
}

// ── Create Post ────────────────────────
async function submitPost() {
  const content = document.getElementById('postContent').value.trim();
  if (!content) { showToast('Please write something first!', 'error'); return; }
  const formData = new FormData();
  formData.append('content', content);
  if (selectedImageFile) formData.append('image', selectedImageFile);
  try {
    const res = await fetch('/posts/create/', {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('postContent').value = '';
      clearMedia();
      prependPost(data);
      showToast('Post published!');
    }
  } catch { showToast('Something went wrong.', 'error'); }
}

function prependPost(data) {
  const container = document.getElementById('posts-container');
  const empty = container.querySelector('.empty-feed');
  if (empty) empty.remove();
  container.insertAdjacentHTML('afterbegin', `
    <article class="post-card" id="post-${data.post_id}" data-post-id="${data.post_id}">
      <div class="post-header">
        <a href="/profile/${data.author}/" class="post-author">
          <img src="${data.avatar}" alt="${data.author}" class="avatar-md"/>
          <div>
            <span class="author-name">${data.author}</span>
            <span class="author-handle">@${data.author} · just now</span>
          </div>
        </a>
        <div class="post-menu">
          <button class="post-menu-btn" onclick="toggleMenu(${data.post_id})">···</button>
          <div class="post-menu-dropdown" id="menu-${data.post_id}">
            <button onclick="deletePost(${data.post_id})">🗑 Delete Post</button>
          </div>
        </div>
      </div>
      <div class="post-content"><p>${escapeHtml(data.content)}</p></div>
      <div class="post-actions">
        <button class="action-btn comment-btn" onclick="openComments(${data.post_id})">
          <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
          <span id="comment-count-${data.post_id}">0</span>
        </button>
        <button class="action-btn repost-btn" onclick="sharePost(${data.post_id})">
          <svg viewBox="0 0 24 24"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>
        </button>
        <button class="action-btn like-btn" onclick="toggleLike(${data.post_id}, this)" id="like-btn-${data.post_id}">
          <svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
          <span id="like-count-${data.post_id}">0</span>
        </button>
        <button class="action-btn bookmark-btn">
          <svg viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
        </button>
      </div>
    </article>`);
}

// ── Delete Post ─────────────────────────
async function deletePost(postId) {
  if (!confirm('Delete this post?')) return;
  try {
    const res = await fetch(`/posts/${postId}/delete/`, {
      method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' },
    });
    const data = await res.json();
    if (data.success) {
      const card = document.getElementById('post-' + postId);
      card.style.transition = 'opacity .25s';
      card.style.opacity = '0';
      setTimeout(() => card.remove(), 250);
      showToast('Post deleted.');
    }
  } catch { showToast('Error.', 'error'); }
}

// ── Toggle Like ──────────────────────────
async function toggleLike(postId, btn) {
  try {
    const res = await fetch(`/posts/${postId}/like/`, {
      method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN },
    });
    const data = await res.json();
    btn.classList.toggle('liked', data.liked);
    document.getElementById('like-count-' + postId).textContent = data.count;
  } catch {}
}

// ── Comment Modal ────────────────────────
function openComments(postId) {
  currentPostId.value = postId;
  const modal = document.getElementById('commentModal');
  if (!modal) return;
  modal.style.display = 'flex';
  const list = document.getElementById('modalCommentsList');
  list.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:20px">Loading...</p>';
  fetch(`/posts/${postId}/`)
    .then(r => r.text())
    .then(html => {
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const items = doc.querySelectorAll('.comment-item');
      list.innerHTML = '';
      if (!items.length) {
        list.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:20px">No comments yet.</p>';
      } else {
        items.forEach(c => list.appendChild(c.cloneNode(true)));
      }
    });
}
function closeModal() {
  const modal = document.getElementById('commentModal');
  if (modal) modal.style.display = 'none';
  const list = document.getElementById('modalCommentsList');
  if (list) list.innerHTML = '';
  const inp = document.getElementById('modalCommentInput');
  if (inp) inp.value = '';
  if (typeof currentPostId !== 'undefined') currentPostId.value = null;
}
document.addEventListener('click', e => {
  const modal = document.getElementById('commentModal');
  if (modal && e.target === modal) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
  if (e.key === 'Enter' && e.target.id === 'modalCommentInput') submitComment();
});

async function submitComment() {
  const input = document.getElementById('modalCommentInput');
  const content = input.value.trim();
  const postId = typeof currentPostId !== 'undefined' ? currentPostId.value : null;
  if (!content || !postId) return;
  try {
    const res = await fetch(`/posts/${postId}/comment/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': CSRF_TOKEN },
      body: `content=${encodeURIComponent(content)}`,
    });
    const data = await res.json();
    if (data.success) {
      input.value = '';
      const list = document.getElementById('modalCommentsList');
      const placeholder = list.querySelector('p');
      if (placeholder) placeholder.remove();
      list.insertAdjacentHTML('beforeend', `
        <div class="comment-item" id="comment-${data.comment_id}">
          <img src="${data.avatar}" class="avatar-sm" alt=""/>
          <div class="comment-body">
            <div class="comment-header">
              <span class="comment-author">${data.author}</span>
              <span class="comment-time">${data.created_at}</span>
            </div>
            <p class="comment-text">${escapeHtml(data.content)}</p>
          </div>
        </div>`);
      list.scrollTop = list.scrollHeight;
      const countEl = document.getElementById('comment-count-' + postId);
      if (countEl) countEl.textContent = data.count;
    }
  } catch {}
}

async function deleteComment(commentId) {
  if (!confirm('Delete comment?')) return;
  try {
    const res = await fetch(`/comments/${commentId}/delete/`, { method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN } });
    const data = await res.json();
    if (data.success) document.getElementById('comment-' + commentId)?.remove();
  } catch {}
}

// ── Follow ────────────────────────────────
async function toggleFollow(username, btn) {
  try {
    const res = await fetch(`/users/${username}/follow/`, {
      method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN },
    });
    const data = await res.json();
    if (btn.classList.contains('btn-follow')) {
      btn.textContent = data.following ? 'Following' : 'Follow';
      btn.classList.toggle('following', data.following);
      const countEl = document.getElementById('follower-count');
      if (countEl) countEl.textContent = data.count;
    } else {
      btn.textContent = data.following ? 'Following' : 'Follow';
      btn.classList.toggle('following-sm', data.following);
    }
    showToast(data.following ? `Following @${username}` : `Unfollowed @${username}`);
  } catch {}
}

// ── Share ─────────────────────────────────
function sharePost(postId) {
  const url = `${location.origin}/posts/${postId}/`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => showToast('Link copied!'));
  }
}

// ── Toast ─────────────────────────────────
function showToast(msg, type = 'success') {
  document.querySelector('.toast')?.remove();
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  t.style.cssText = `position:fixed;bottom:24px;right:24px;background:${type==='error'?'#EF4444':'#111827'};color:#fff;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:600;z-index:9999;box-shadow:0 4px 16px rgba(0,0,0,.15);animation:toastIn .25s ease`;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity .25s'; setTimeout(()=>t.remove(),250); }, 3000);
}
const s = document.createElement('style');
s.textContent = '@keyframes toastIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}';
document.head.appendChild(s);

// ── Helpers ───────────────────────────────
function escapeHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Auto-resize textareas
document.querySelectorAll('textarea').forEach(ta => {
  ta.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
  });
});
