// ===== ZTG Security Dashboard =====

const API = {
    stats: '/api/stats/',
    requests: '/api/requests/',
    threats: '/api/threats/',
    traffic: '/api/traffic/',
    threatBreakdown: '/api/threat-breakdown/',
    topIps: '/api/top-ips/',
    blockedIps: '/api/blocked-ips/',
    blockIp: '/api/block-ip/',
    unblockIp: (id) => `/api/unblock-ip/${id}/`,
    resolveThreat: (id) => `/api/resolve-threat/${id}/`,
};

let trafficChart = null;
let threatChart = null;
let currentPage = 0;
const PAGE_SIZE = 30;
let autoRefreshInterval = null;


// ===== init =====

document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupBlockForm();
    setupPagination();
    loadOverview();
    startAutoRefresh();

    document.getElementById('refreshBtn').addEventListener('click', refreshCurrentSection);
});


// ===== navigation =====

function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;

            // update active nav
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // update active section
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(`section-${section}`).classList.add('active');

            // update title
            const titles = { overview: 'Overview', requests: 'Request Logs', threats: 'Threats', blocked: 'Blocked IPs' };
            document.getElementById('pageTitle').textContent = titles[section] || 'Dashboard';

            // load data for the section
            loadSection(section);

            // close mobile sidebar
            document.getElementById('sidebar').classList.remove('open');
        });
    });

    // mobile menu
    document.getElementById('menuToggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });
}

function loadSection(section) {
    switch (section) {
        case 'overview': loadOverview(); break;
        case 'requests': loadRequests(); break;
        case 'threats': loadThreats(); break;
        case 'blocked': loadBlockedIps(); break;
    }
}

function refreshCurrentSection() {
    const active = document.querySelector('.nav-item.active');
    if (active) loadSection(active.dataset.section);
    updateTimestamp();
}


// ===== overview =====

async function loadOverview() {
    await Promise.all([
        loadStats(),
        loadTrafficChart(),
        loadThreatBreakdownChart(),
        loadTopIps(),
        loadThreatFeed(),
    ]);
}

async function loadStats() {
    try {
        const data = await fetchJSON(API.stats);
        animateNumber('statRequests', data.total_requests);
        animateNumber('statBlocked', data.blocked_ips);
        animateNumber('statViolations', data.rate_violations);
        animateNumber('statThreats', data.active_threats);

        // trend
        const trendEl = document.getElementById('trendRequests');
        if (data.requests_prev_hour > 0) {
            const change = ((data.requests_last_hour - data.requests_prev_hour) / data.requests_prev_hour * 100).toFixed(0);
            if (change > 0) {
                trendEl.textContent = `↑ ${change}% vs last hour`;
                trendEl.className = 'stat-trend up';
            } else if (change < 0) {
                trendEl.textContent = `↓ ${Math.abs(change)}% vs last hour`;
                trendEl.className = 'stat-trend down';
            } else {
                trendEl.textContent = '→ same as last hour';
                trendEl.className = 'stat-trend';
            }
        } else {
            trendEl.textContent = `${data.requests_last_hour} in last hour`;
            trendEl.className = 'stat-trend';
        }
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

function animateNumber(elementId, target) {
    const el = document.getElementById(elementId);
    const start = parseInt(el.textContent) || 0;
    const duration = 500;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + (target - start) * eased).toLocaleString();
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}


// ===== traffic chart =====

async function loadTrafficChart() {
    try {
        const data = await fetchJSON(API.traffic);
        const labels = data.results.map(d => {
            const date = new Date(d.hour);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        });
        const values = data.results.map(d => d.count);

        const ctx = document.getElementById('trafficChart').getContext('2d');

        if (trafficChart) trafficChart.destroy();

        const gradient = ctx.createLinearGradient(0, 0, 0, 260);
        gradient.addColorStop(0, 'rgba(129, 140, 248, 0.3)');
        gradient.addColorStop(1, 'rgba(129, 140, 248, 0)');

        trafficChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Requests',
                    data: values,
                    borderColor: '#818cf8',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: '#818cf8',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1a1f35',
                        borderColor: '#2a2f45',
                        borderWidth: 1,
                        titleColor: '#e2e8f0',
                        bodyColor: '#94a3b8',
                        cornerRadius: 8,
                        padding: 10,
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(42, 47, 69, 0.5)', drawBorder: false },
                        ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 8 },
                    },
                    y: {
                        grid: { color: 'rgba(42, 47, 69, 0.5)', drawBorder: false },
                        ticks: { color: '#64748b', font: { size: 10 } },
                        beginAtZero: true,
                    }
                },
                interaction: { intersect: false, mode: 'index' },
            }
        });
    } catch (err) {
        console.error('Failed to load traffic chart:', err);
    }
}


// ===== threat breakdown chart =====

async function loadThreatBreakdownChart() {
    try {
        const data = await fetchJSON(API.threatBreakdown);

        if (data.results.length === 0) {
            document.getElementById('threatChart').parentElement.innerHTML =
                '<div class="empty-state"><div class="empty-state-icon">✅</div><p class="empty-state-text">No threats detected</p></div>';
            return;
        }

        const labels = data.results.map(d => formatThreatType(d.type));
        const values = data.results.map(d => d.count);
        const colors = ['#818cf8', '#f87171', '#fbbf24', '#34d399', '#fb7185'];

        const ctx = document.getElementById('threatChart').getContext('2d');
        if (threatChart) threatChart.destroy();

        threatChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.slice(0, values.length),
                    borderColor: '#1a1f35',
                    borderWidth: 3,
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            padding: 12,
                            usePointStyle: true,
                            pointStyleWidth: 8,
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1a1f35',
                        borderColor: '#2a2f45',
                        borderWidth: 1,
                        titleColor: '#e2e8f0',
                        bodyColor: '#94a3b8',
                        cornerRadius: 8,
                    }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load threat chart:', err);
    }
}


// ===== top ips =====

async function loadTopIps() {
    try {
        const data = await fetchJSON(API.topIps);
        const body = document.getElementById('topIpsBody');

        if (data.results.length === 0) {
            body.innerHTML = '<tr><td colspan="3"><div class="empty-state"><p class="empty-state-text">No request data yet</p></div></td></tr>';
            return;
        }

        const max = data.results[0]?.count || 1;
        body.innerHTML = data.results.map(ip => `
            <tr>
                <td style="font-family: monospace; font-size: 0.8rem;">${escapeHtml(ip.ip)}</td>
                <td>${ip.count.toLocaleString()}</td>
                <td><div class="ip-bar-wrap"><div class="ip-bar" style="width: ${(ip.count / max * 100)}%"></div></div></td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Failed to load top IPs:', err);
    }
}


// ===== threat feed =====

async function loadThreatFeed() {
    try {
        const data = await fetchJSON(API.threats + '?limit=10');
        const feed = document.getElementById('threatFeed');

        if (data.results.length === 0) {
            feed.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✅</div><p class="empty-state-text">No threats detected</p></div>';
            return;
        }

        feed.innerHTML = data.results.map(t => `
            <div class="threat-item severity-border-${t.severity}">
                <div class="threat-item-content">
                    <div class="threat-item-header">
                        <span class="severity-badge severity-${t.severity}">${t.severity}</span>
                        <span class="threat-type">${formatThreatType(t.threat_type)}</span>
                        <span class="threat-time">${timeAgo(t.timestamp)}</span>
                    </div>
                    <p class="threat-desc">${escapeHtml(t.description)}</p>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Failed to load threat feed:', err);
    }
}


// ===== request logs =====

async function loadRequests() {
    try {
        const offset = currentPage * PAGE_SIZE;
        const data = await fetchJSON(`${API.requests}?limit=${PAGE_SIZE}&offset=${offset}`);
        const body = document.getElementById('requestsBody');

        if (data.results.length === 0) {
            body.innerHTML = '<tr><td colspan="5"><div class="empty-state"><div class="empty-state-icon">📋</div><p class="empty-state-text">No requests logged yet</p></div></td></tr>';
            return;
        }

        body.innerHTML = data.results.map(r => `
            <tr>
                <td>${formatTime(r.timestamp)}</td>
                <td><span class="method-badge method-${r.method}">${r.method}</span></td>
                <td style="font-family: monospace; font-size: 0.8rem; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(r.path)}</td>
                <td><span class="status-badge-code status-${getStatusClass(r.status_code)}">${r.status_code}</span></td>
                <td style="font-family: monospace; font-size: 0.8rem;">${escapeHtml(r.ip_address)}</td>
            </tr>
        `).join('');

        // pagination
        const totalPages = Math.ceil(data.total / PAGE_SIZE);
        document.getElementById('pageInfo').textContent = `Page ${currentPage + 1} of ${totalPages || 1}`;
        document.getElementById('prevPage').disabled = currentPage === 0;
        document.getElementById('nextPage').disabled = currentPage >= totalPages - 1;
    } catch (err) {
        console.error('Failed to load requests:', err);
    }
}

function setupPagination() {
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 0) { currentPage--; loadRequests(); }
    });
    document.getElementById('nextPage').addEventListener('click', () => {
        currentPage++;
        loadRequests();
    });
}


// ===== threats table =====

async function loadThreats() {
    try {
        const data = await fetchJSON(API.threats + '?limit=50');
        const body = document.getElementById('threatsBody');

        if (data.results.length === 0) {
            body.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">✅</div><p class="empty-state-text">No threats detected</p></div></td></tr>';
            return;
        }

        body.innerHTML = data.results.map(t => `
            <tr>
                <td>${formatTime(t.timestamp)}</td>
                <td>${formatThreatType(t.threat_type)}</td>
                <td><span class="severity-badge severity-${t.severity}">${t.severity}</span></td>
                <td style="font-family: monospace; font-size: 0.8rem;">${escapeHtml(t.ip_address)}</td>
                <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(t.description)}</td>
                <td>${t.is_resolved
                    ? '<span style="color: var(--success); font-size: 0.75rem;">✓ Resolved</span>'
                    : `<button class="btn-success btn-sm" onclick="resolveThreat(${t.id})">Resolve</button>`
                }</td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Failed to load threats:', err);
    }
}

async function resolveThreat(id) {
    try {
        await fetchJSON(API.resolveThreat(id), { method: 'POST' });
        showToast('Threat marked as resolved', 'success');
        loadThreats();
        loadStats();
    } catch (err) {
        showToast('Failed to resolve threat', 'error');
    }
}


// ===== blocked ips =====

async function loadBlockedIps() {
    try {
        const data = await fetchJSON(API.blockedIps);
        const body = document.getElementById('blockedBody');

        if (data.results.length === 0) {
            body.innerHTML = '<tr><td colspan="4"><div class="empty-state"><div class="empty-state-icon">🚫</div><p class="empty-state-text">No blocked IPs</p></div></td></tr>';
            return;
        }

        body.innerHTML = data.results.map(ip => `
            <tr>
                <td style="font-family: monospace; font-size: 0.85rem;">${escapeHtml(ip.ip_address)}</td>
                <td>${escapeHtml(ip.reason)}</td>
                <td>${formatTime(ip.blocked_at)}</td>
                <td><button class="btn-danger btn-sm" onclick="unblockIp(${ip.id})">Unblock</button></td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Failed to load blocked IPs:', err);
    }
}

function setupBlockForm() {
    const form = document.getElementById('blockForm');
    const showBtn = document.getElementById('showBlockForm');
    const cancelBtn = document.getElementById('cancelBlockBtn');
    const blockBtn = document.getElementById('blockIpBtn');

    showBtn.addEventListener('click', () => form.classList.remove('hidden'));
    cancelBtn.addEventListener('click', () => {
        form.classList.add('hidden');
        document.getElementById('blockIpInput').value = '';
        document.getElementById('blockReasonInput').value = '';
    });

    blockBtn.addEventListener('click', async () => {
        const ip = document.getElementById('blockIpInput').value.trim();
        const reason = document.getElementById('blockReasonInput').value.trim() || 'Manually blocked';

        if (!ip) { showToast('Enter an IP address', 'error'); return; }

        try {
            await fetchJSON(API.blockIp, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip_address: ip, reason }),
            });
            showToast(`${ip} blocked successfully`, 'success');
            form.classList.add('hidden');
            document.getElementById('blockIpInput').value = '';
            document.getElementById('blockReasonInput').value = '';
            loadBlockedIps();
            loadStats();
        } catch (err) {
            showToast('Failed to block IP', 'error');
        }
    });
}

async function unblockIp(id) {
    try {
        await fetchJSON(API.unblockIp(id), { method: 'POST' });
        showToast('IP unblocked', 'success');
        loadBlockedIps();
        loadStats();
    } catch (err) {
        showToast('Failed to unblock IP', 'error');
    }
}


// ===== auto refresh =====

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        refreshCurrentSection();
    }, 30000); // every 30 seconds
}

function updateTimestamp() {
    document.getElementById('lastUpdated').textContent = 'Updated just now';
}


// ===== helpers =====

async function fetchJSON(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function formatTime(iso) {
    const d = new Date(iso);
    return d.toLocaleString([], {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

function timeAgo(iso) {
    const seconds = Math.floor((Date.now() - new Date(iso)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

function formatThreatType(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getStatusClass(code) {
    if (code < 300) return '2xx';
    if (code < 400) return '3xx';
    if (code < 500) return '4xx';
    return '5xx';
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function showToast(message, type = 'success') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = type === 'success' ? `✓ ${message}` : `✕ ${message}`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
