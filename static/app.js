let loadedMemories = {};
let currentViewBeforeArticle = 'dashboard';

// Live clock in header
function updateClock() {
    const el = document.getElementById('header-time');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
        + '  •  ' + now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// ---- Stats ----
async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        const icons = { total: '🧠', knowledge: '📚', ideas: '💡', actions: '✅', chat: '💬' };
        document.getElementById('stats-container').innerHTML = `
            <div class="stat-card"><div class="stat-value">${data.total}</div><div class="stat-label">Total Memories</div></div>
            <div class="stat-card"><div class="stat-value">${data.knowledge}</div><div class="stat-label">Wiki Articles</div></div>
            <div class="stat-card"><div class="stat-value">${data.ideas}</div><div class="stat-label">Ideas</div></div>
            <div class="stat-card"><div class="stat-value">${data.actions}</div><div class="stat-label">Action Items</div></div>
        `;
    } catch (e) { console.error("Error fetching stats:", e); }
}

// ---- Memory Cards ----
function getTypeClass(type) {
    const map = { knowledge: 'knowledge', action_item: 'action_item', idea: 'idea', chat: 'chat' };
    return map[type] || type;
}
function getTypeLabel(type) {
    const map = { knowledge: '📚 Knowledge', action_item: '✅ Action Item', idea: '💡 Idea', chat: '💬 Chat' };
    return map[type] || type.replace('_', ' ');
}

function createMemoryCard(memory, index) {
    const typeClass = getTypeClass(memory.type);
    const typeLabel = getTypeLabel(memory.type);
    const delay = Math.min(index * 60, 500);

    let sourceBadge = '';
    if (memory.source_doc) {
        sourceBadge = `<div class="memory-source">📄 ${memory.source_doc}</div>`;
    }

    return `
        <div class="memory-card" data-type="${memory.type}"
             onclick="openArticle('${memory.id}')"
             data-title="${(memory.title || '').toLowerCase()}"
             data-content="${(memory.content || '').toLowerCase()}"
             style="animation-delay: ${delay}ms">
            <div class="memory-type ${typeClass}">${typeLabel}</div>
            <h3 class="memory-title">${memory.title}</h3>
            <div class="memory-content">${memory.content}</div>
            ${sourceBadge}
        </div>
    `;
}

function filterMemories() {
    const input = document.getElementById('search-input').value.toLowerCase();
    const cards = document.querySelectorAll('#filtered-memories .memory-card');
    cards.forEach(card => {
        const match = card.getAttribute('data-title').includes(input) ||
                      card.getAttribute('data-content').includes(input);
        card.style.display = match ? 'flex' : 'none';
    });
}

async function fetchMemories(type = null, containerId = 'recent-memories') {
    let url = '/api/memories';
    if (type) url += `?type=${type}`;
    try {
        const res = await fetch(url);
        const data = await res.json();
        data.memories.forEach(m => { loadedMemories[m.id] = m; });
        const container = document.getElementById(containerId);
        container.innerHTML = data.memories.map((m, i) => createMemoryCard(m, i)).join('');
    } catch (e) { console.error("Error fetching memories:", e); }
}

// ---- Navigation ----
const viewSubtitles = {
    knowledge: 'Browse your AI-summarized knowledge articles',
    action_item: 'Track tasks and pending action items',
    idea: 'Explore your captured ideas',
    chat: 'Review your WhatsApp conversation history',
};

function loadView(viewType) {
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const navEl = document.getElementById(`nav-${viewType}`);
    if (navEl) navEl.classList.add('active');

    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));

    if (viewType === 'dashboard') {
        document.getElementById('view-dashboard').classList.remove('hidden');
        fetchStats();
        fetchMemories(null, 'recent-memories');
    } else if (viewType === 'upload') {
        document.getElementById('view-upload').classList.remove('hidden');
    } else {
        document.getElementById('view-filtered').classList.remove('hidden');
        document.getElementById('filtered-title').innerText =
            viewType.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
        document.getElementById('filtered-subtitle').innerText =
            viewSubtitles[viewType] || 'Browse your memories';
        fetchMemories(viewType, 'filtered-memories');
    }
}

// ---- Upload ----
async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const statusEl = document.getElementById('upload-status');
    if (fileInput.files.length === 0) {
        statusEl.style.color = '#f87171';
        statusEl.innerText = 'Please select a file first.';
        return;
    }
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    statusEl.style.color = 'var(--text-secondary)';
    statusEl.innerText = '⏳ Uploading and processing with AI… This might take a few seconds.';
    try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await res.json();
        statusEl.style.color = '#34d399';
        statusEl.innerText = '✅ ' + data.message;
        fileInput.value = '';
    } catch (e) {
        statusEl.style.color = '#f87171';
        statusEl.innerText = '❌ Upload failed. Please try again.';
    }
}

// ---- Article View ----
function openArticle(id) {
    const memory = loadedMemories[id];
    if (!memory) return;

    // Remember which view we came from
    document.querySelectorAll('.view-section').forEach(el => {
        if (!el.classList.contains('hidden') && el.id !== 'view-article') {
            currentViewBeforeArticle = el.id.replace('view-', '');
        }
    });

    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.getElementById('view-article').classList.remove('hidden');

    const typeClass = getTypeClass(memory.type);
    const typeLabel = getTypeLabel(memory.type);
    document.getElementById('article-type').className = `memory-type ${typeClass}`;
    document.getElementById('article-type').innerText = typeLabel;

    let dateStr = '';
    if (memory.created_at) {
        dateStr = new Date(memory.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    }
    document.getElementById('article-date').innerText = dateStr;
    document.getElementById('article-title').innerText = memory.title;

    // Render markdown
    document.getElementById('article-body').innerHTML = marked.parse(memory.content);

    // Fetch semantic related pages
    if (memory.type === 'knowledge') {
        fetch(`/api/memories/${id}/related`)
            .then(res => res.json())
            .then(data => {
                if (data.related && data.related.length > 0) {
                    const relatedHtml = `
                        <div class="related-section">
                            <div class="related-title">🔗 Connected Knowledge</div>
                            <div class="related-tags">
                                ${data.related.map(r => `<div class="related-tag" onclick="openArticle('${r.id}')">📄 ${r.title}</div>`).join('')}
                            </div>
                        </div>`;
                    document.getElementById('article-body').innerHTML += relatedHtml;
                }
            })
            .catch(err => console.error("Error fetching related:", err));
    }

    // Handle PDF embed
    const pdfPane = document.getElementById('pdf-pane');
    const pdfIframe = document.getElementById('pdf-iframe');
    if (memory.source_doc && memory.source_doc.toLowerCase().endsWith('.pdf')) {
        pdfPane.classList.remove('hidden');
        pdfIframe.src = `/uploads/${memory.source_doc}`;
    } else {
        pdfPane.classList.add('hidden');
        pdfIframe.src = '';
    }
}

function closeArticle() {
    loadView(currentViewBeforeArticle);
}

// ---- Initial Load ----
fetchStats();
fetchMemories(null, 'recent-memories');
