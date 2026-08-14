/**
 * Semcod Engine Landing Page & Auto 24h Cache Engine
 */

let appState = {
  projects: {},
  filteredProjects: [],
  selectedCategory: 'all',
  selectedTag: null,
  searchQuery: '',
  activeView: 'grid',
  activeModalProject: null,
  activeModalTab: 'task',
  cyGraph: null,
  cacheInfo: { lastUpdated: null, source: 'Local Cache', ttlHours: 24 }
};

document.addEventListener('DOMContentLoaded', async () => {
  await loadProjectData();
  setupEventListeners();
  renderMetrics();
  renderTagsCloud();
  renderProjectsGrid();
  renderDependencyMatrix();
  initCytoscapeGraph();

  setInterval(checkAutomaticCacheRefresh, 60000);
});

async function loadProjectData() {
  const LOCAL_CACHE_KEY = 'semcod_github_daily_cache_v1';
  const CACHE_TTL_MS = 24 * 60 * 60 * 1000;

  updateSyncStatusIndicator('syncing', 'Ładowanie automatycznego cache...');

  try {
    let cacheData = null;
    const stored = localStorage.getItem(LOCAL_CACHE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        const age = Date.now() - new Date(parsed.last_updated).getTime();
        if (age < CACHE_TTL_MS) {
          cacheData = parsed;
        }
      } catch (e) {}
    }

    if (!cacheData) {
      const resp = await fetch('projects_cache.json?t=' + Date.now());
      if (!resp.ok) throw new Error('Nie można pobrać pliku projects_cache.json');
      cacheData = await resp.json();
      localStorage.setItem(LOCAL_CACHE_KEY, JSON.stringify(cacheData));
    }

    appState.projects = cacheData.projects || {};
    appState.cacheInfo.lastUpdated = cacheData.last_updated;

    processTags();
    updateCacheCountdown();
    filterProjects();

  } catch (err) {
    updateSyncStatusIndicator('error', 'Błąd auto-cache');
  }
}

function checkAutomaticCacheRefresh() {
  const LOCAL_CACHE_KEY = 'semcod_github_daily_cache_v1';
  const CACHE_TTL_MS = 24 * 60 * 60 * 1000;
  const stored = localStorage.getItem(LOCAL_CACHE_KEY);
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      const age = Date.now() - new Date(parsed.last_updated).getTime();
      if (age >= CACHE_TTL_MS) {
        localStorage.removeItem(LOCAL_CACHE_KEY);
        loadProjectData();
        return;
      }
    } catch (e) {}
  }
  updateCacheCountdown();
}

function updateCacheCountdown() {
  if (!appState.cacheInfo.lastUpdated) return;
  const CACHE_TTL_MS = 24 * 60 * 60 * 1000;
  const ageMs = Date.now() - new Date(appState.cacheInfo.lastUpdated).getTime();
  const remainingMs = Math.max(0, CACHE_TTL_MS - ageMs);
  const hoursLeft = Math.floor(remainingMs / (1000 * 60 * 60));
  const minsLeft = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60));
  updateSyncStatusIndicator('success', `Auto-Cache GitHub: Następne odświeżenie za ${hoursLeft}h ${minsLeft}m`);
}

function updateSyncStatusIndicator(type, message) {
  const dot = document.getElementById('cache-status-dot');
  const text = document.getElementById('cache-status-text');
  if (text) text.textContent = message;
  if (dot) {
    dot.style.backgroundColor = type === 'syncing' ? '#f59e0b' : (type === 'error' ? '#f43f5e' : '#10b981');
  }
}

function processTags() {
  appState.tags = {};
  Object.values(appState.projects).forEach(p => {
    if (p.tags && Array.isArray(p.tags)) {
      p.tags.forEach(tag => { appState.tags[tag] = (appState.tags[tag] || 0) + 1; });
    }
  });
}

function filterProjects() {
  const query = appState.searchQuery.toLowerCase().trim();
  appState.filteredProjects = Object.values(appState.projects).filter(p => {
    if (appState.selectedTag && (!p.tags || !p.tags.includes(appState.selectedTag))) return false;
    if (query) {
      const matchName = p.name.toLowerCase().includes(query);
      const matchId = p.id.toLowerCase().includes(query);
      const matchTask = p.task && p.task.toLowerCase().includes(query);
      return matchName || matchId || matchTask;
    }
    return true;
  });
  renderProjectsGrid();
}

function renderMetrics() {
  document.getElementById('metric-total-repos').textContent = Object.keys(appState.projects).length;
  let totalDeps = 0;
  Object.values(appState.projects).forEach(p => { totalDeps += (p.dependencies ? p.dependencies.length : 0); });
  document.getElementById('metric-total-deps').textContent = totalDeps;
  document.getElementById('metric-total-tags').textContent = Object.keys(appState.tags).length;
}

function renderTagsCloud() {
  const container = document.getElementById('tag-cloud-container');
  if (!container) return;
  const sortedTags = Object.entries(appState.tags).sort((a, b) => b[1] - a[1]);
  let html = `<button class="tag-pill ${!appState.selectedTag ? 'active' : ''}" onclick="selectTag(null)">Wszystkie tagi <span class="tag-count">${Object.keys(appState.projects).length}</span></button>`;
  sortedTags.forEach(([tag, count]) => {
    const isActive = appState.selectedTag === tag ? 'active' : '';
    html += `<button class="tag-pill ${isActive}" onclick="selectTag('${tag}')">#${tag} <span class="tag-count">${count}</span></button>`;
  });
  container.innerHTML = html;
}

function selectTag(tag) {
  appState.selectedTag = appState.selectedTag === tag ? null : tag;
  renderTagsCloud();
  filterProjects();
}

function renderProjectsGrid() {
  const container = document.getElementById('projects-grid-container');
  if (!container) return;
  let html = '';
  appState.filteredProjects.forEach(p => {
    const tagsHtml = (p.tags || []).map(t => `<span class="card-tag" onclick="event.stopPropagation(); selectTag('${t}')">#${t}</span>`).join(' ');
    const depsPills = (p.dependencies || []).map(d => `<span class="dep-pill" onclick="event.stopPropagation(); openProjectModal('${d}')">${d}</span>`).join(' ');
    const usedByPills = (p.used_by || []).map(u => `<span class="dep-pill" style="background: rgba(16,185,129,0.15); color: #10b981;" onclick="event.stopPropagation(); openProjectModal('${u}')">${u}</span>`).join(' ');

    html += `
      <div class="project-card" onclick="openProjectModal('${p.id}')">
        <div>
          <div class="card-header">
            <span class="category-badge">${p.category}</span>
            <span class="status-badge">${p.status}</span>
          </div>
          <h3 class="project-title">${p.name}</h3>
          <div class="task-box">
            <span class="task-label"><i class="fas fa-bullseye"></i> Zadanie Projektu:</span>
            ${p.task}
          </div>
          <div class="card-tags">${tagsHtml}</div>
          <div class="dependencies-summary">
            ${p.dependencies && p.dependencies.length > 0 ? `<div class="dep-row"><strong>Wymaga:</strong> ${depsPills}</div>` : ''}
            ${p.used_by && p.used_by.length > 0 ? `<div class="dep-row"><strong>Używany przez:</strong> ${usedByPills}</div>` : ''}
          </div>
        </div>
        <div class="card-footer">
          <div class="github-stats">
            <span>⭐ ${p.stars || 0}</span>
            <span>🍴 ${p.forks || 0}</span>
            <span>${p.language || 'Python'}</span>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); openProjectModal('${p.id}')">Szczegóły & README <i class="fas fa-arrow-right"></i></button>
        </div>
      </div>
    `;
  });
  container.innerHTML = html;
}

function initCytoscapeGraph() {
  const container = document.getElementById('cy');
  if (!container) return;
  const elements = [];
  Object.values(appState.projects).forEach(p => {
    elements.push({ data: { id: p.id, label: p.id, color: '#a855f7' } });
  });
  Object.values(appState.projects).forEach(p => {
    (p.dependencies || []).forEach(targetId => {
      if (appState.projects[targetId]) elements.push({ data: { id: `${p.id}->${targetId}`, source: p.id, target: targetId } });
    });
  });
  appState.cyGraph = cytoscape({
    container: container,
    elements: elements,
    style: [
      { selector: 'node', style: { 'background-color': 'data(color)', 'label': 'data(label)', 'color': '#fff', 'font-size': '12px', 'font-weight': 'bold', 'text-valign': 'center', 'text-halign': 'center', 'width': '65px', 'height': '65px', 'text-outline-color': '#090d16', 'text-outline-width': '3px' } },
      { selector: 'edge', style: { 'width': 2, 'line-color': 'rgba(99,102,241,0.4)', 'target-arrow-color': 'rgba(99,102,241,0.8)', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier' } }
    ],
    layout: { name: 'cose', animate: true }
  });
  appState.cyGraph.on('tap', 'node', function(evt){ openProjectModal(evt.target.id()); });
}

function resetGraphLayout() { if (appState.cyGraph) appState.cyGraph.layout({ name: 'cose', animate: true }).run(); }

function renderDependencyMatrix() {
  const container = document.getElementById('matrix-table-container');
  if (!container) return;
  let html = `<table style="width:100%; border-collapse:collapse; font-size:0.85rem;"><thead><tr style="background:rgba(30,41,59,0.8);"><th style="padding:0.75rem;">Projekt</th><th style="padding:0.75rem;">Zadanie Projektu</th><th style="padding:0.75rem;">Wymaga</th><th style="padding:0.75rem;">Używany przez</th></tr></thead><tbody>`;
  Object.values(appState.projects).forEach(p => {
    html += `<tr><td style="padding:0.75rem; font-weight:bold;"><a href="javascript:void(0)" onclick="openProjectModal('${p.id}')">${p.name}</a></td><td style="padding:0.75rem;">${p.task}</td><td style="padding:0.75rem;">${(p.dependencies||[]).join(', ')||'-'}</td><td style="padding:0.75rem;">${(p.used_by||[]).join(', ')||'-'}</td></tr>`;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;
}

function openProjectModal(projId) {
  const p = appState.projects[projId];
  if (!p) return;
  appState.activeModalProject = p;
  appState.activeModalTab = 'task';
  document.getElementById('modal-project-name').textContent = p.name;
  document.getElementById('modal-project-cat').textContent = p.category;
  document.getElementById('modal-github-link').href = p.github_url;
  renderModalTabContent();
  document.getElementById('project-modal-backdrop').classList.add('open');
}

function closeProjectModal() { document.getElementById('project-modal-backdrop').classList.remove('open'); }
function switchModalTab(tabName) {
  appState.activeModalTab = tabName;
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabName));
  renderModalTabContent();
}

function renderModalTabContent() {
  const body = document.getElementById('modal-body-content');
  const p = appState.activeModalProject;
  if (!body || !p) return;
  if (appState.activeModalTab === 'task') {
    body.innerHTML = `<div style="background:rgba(15,23,42,0.8); padding:1.5rem; border-radius:12px;"><h3 style="color:${config['accent_primary']}; margin-bottom:0.5rem;"><i class="fas fa-bullseye"></i> Zadanie Projektu:</h3><p style="font-size:1.1rem; line-height:1.6;">${p.task}</p></div>`;
  } else if (appState.activeModalTab === 'readme') {
    body.innerHTML = window.marked && p.readme ? `<div class="markdown-body">${marked.parse(p.readme)}</div>` : `<pre>${escapeHtml(p.readme||'Brak README.md')}</pre>`;
  } else if (appState.activeModalTab === 'deps') {
    body.innerHTML = `<h4>Wymaga:</h4><p>${(p.dependencies||[]).join(', ')||'Brak'}</p><h4 style="margin-top:1rem;">Używany przez:</h4><p>${(p.used_by||[]).join(', ')||'Brak'}</p>`;
  }
}

function switchView(viewName) {
  appState.activeView = viewName;
  document.querySelectorAll('.view-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.view === viewName));
  document.getElementById('projects-grid-container').style.display = viewName === 'grid' ? 'grid' : 'none';
  document.getElementById('graph-view-wrapper').style.display = viewName === 'graph' ? 'block' : 'none';
  document.getElementById('matrix-view-wrapper').style.display = viewName === 'matrix' ? 'block' : 'none';
  if (viewName === 'graph' && appState.cyGraph) setTimeout(() => { appState.cyGraph.resize(); resetGraphLayout(); }, 100);
}

function setupEventListeners() {
  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.addEventListener('input', e => { appState.searchQuery = e.target.value; filterProjects(); });
}
function resetFilters() { appState.searchQuery = ''; appState.selectedTag = null; filterProjects(); }
function escapeHtml(str) { return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
