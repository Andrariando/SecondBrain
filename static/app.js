let loadedMemories = {};
let currentViewBeforeArticle = 'dashboard';

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('stats-container').innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${data.total}</div>
                <div class="stat-label">Total Memories</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.knowledge}</div>
                <div class="stat-label">Wiki Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.ideas}</div>
                <div class="stat-label">Ideas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.actions}</div>
                <div class="stat-label">Action Items</div>
            </div>
        `;
    } catch (e) {
        console.error("Error fetching stats:", e);
    }
}

function createMemoryCard(memory) {
    let sourceBadge = '';
    if (memory.source_doc) {
        sourceBadge = `<div style="font-size: 0.75rem; color: #94a3b8; margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border-color);">Source: ${memory.source_doc}</div>`;
    }
    
    return `
        <div class="memory-card" onclick="openArticle('${memory.id}')" data-title="${(memory.title || '').toLowerCase()}" data-content="${(memory.content || '').toLowerCase()}">
            <div class="memory-type">${memory.type.replace('_', ' ')}</div>
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
        const title = card.getAttribute('data-title');
        const content = card.getAttribute('data-content');
        if (title.includes(input) || content.includes(input)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

async function fetchMemories(type = null, containerId = 'recent-memories') {
    let url = '/api/memories';
    if (type) url += `?type=${type}`;
    
    try {
        const res = await fetch(url);
        const data = await res.json();
        
        // Cache them for the article view
        data.memories.forEach(m => {
            loadedMemories[m.id] = m;
        });

        const container = document.getElementById(containerId);
        container.innerHTML = data.memories.map(createMemoryCard).join('');
    } catch (e) {
        console.error("Error fetching memories:", e);
    }
}

function loadView(viewType) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    // Attempt to set active nav item based on viewType
    let targetNav = document.querySelector(`.nav-item[onclick="loadView('${viewType}')"]`);
    if(targetNav) targetNav.classList.add('active');

    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));

    if (viewType === 'dashboard') {
        document.getElementById('view-dashboard').classList.remove('hidden');
        fetchStats();
        fetchMemories(null, 'recent-memories');
    } else if (viewType === 'upload') {
        document.getElementById('view-upload').classList.remove('hidden');
    } else {
        document.getElementById('view-filtered').classList.remove('hidden');
        document.getElementById('filtered-title').innerText = viewType.replace('_', ' ');
        fetchMemories(viewType, 'filtered-memories');
    }
}

async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const statusEl = document.getElementById('upload-status');
    
    if (fileInput.files.length === 0) {
        statusEl.style.color = '#ef4444';
        statusEl.innerText = 'Please select a file first.';
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    statusEl.style.color = 'var(--text-secondary)';
    statusEl.innerText = 'Uploading and processing document with AI... This might take a few seconds.';
    
    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        statusEl.style.color = '#34d399';
        statusEl.innerText = data.message;
        fileInput.value = ''; 
    } catch (e) {
        console.error("Upload failed", e);
        statusEl.style.color = '#ef4444';
        statusEl.innerText = 'Upload failed.';
    }
}

// Full Article View Functions
function openArticle(id) {
    const memory = loadedMemories[id];
    if (!memory) return;

    // Track where we came from so back button works nicely
    document.querySelectorAll('.view-section').forEach(el => {
        if (!el.classList.contains('hidden') && el.id !== 'view-article') {
            currentViewBeforeArticle = el.id.replace('view-', '');
        }
    });

    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.getElementById('view-article').classList.remove('hidden');

    document.getElementById('article-type').innerText = memory.type.replace('_', ' ');
    
    let dateStr = "";
    if (memory.created_at) {
        dateStr = new Date(memory.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    }
    document.getElementById('article-date').innerText = dateStr;
    document.getElementById('article-title').innerText = memory.title;

    // Convert Markdown to HTML
    const htmlContent = marked.parse(memory.content);
    document.getElementById('article-body').innerHTML = htmlContent;

    // Handle PDF Embedding
    const pdfPane = document.getElementById('pdf-pane');
    const pdfIframe = document.getElementById('pdf-iframe');
    
    if (memory.source_doc && memory.source_doc.toLowerCase().endsWith('.pdf')) {
        pdfPane.classList.remove('hidden');
        pdfIframe.src = `/uploads/${memory.source_doc}`;
    } else {
        pdfPane.classList.add('hidden');
        pdfIframe.src = "";
    }
}

function closeArticle() {
    loadView(currentViewBeforeArticle);
}

// Initial load
fetchStats();
fetchMemories(null, 'recent-memories');
