// CareerOS Client-Side SPA Controller

let currentUser = null;
let currentTab = 'pipeline';
let currentDocSubTab = 'cv';

document.addEventListener('DOMContentLoaded', async () => {
  await initUser();
  await loadStats();
  await loadApplications();
  await loadProfile();
  await loadSettings();
  loadRadarJobs();
});

// --- Tab Navigation ---
function switchTab(tabId) {
  currentTab = tabId;
  const tabs = ['pipeline', 'tailor', 'radar', 'vault', 'profile', 'settings'];
  tabs.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    const navBtn = document.getElementById(`nav-${t}`);
    if (el) el.classList.toggle('hidden', t !== tabId);
    if (navBtn) {
      if (t === tabId) {
        navBtn.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-blue-600 text-white font-semibold transition shadow-sm';
      } else {
        navBtn.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition';
      }
    }
  });

  const titles = {
    pipeline: 'Applications Pipeline & Tracking',
    tailor: '1-Click AI Document Tailor',
    radar: 'Automated Job Radar & Discovery',
    vault: 'Document & CV Archive Vault',
    profile: 'Candidate Master Profile',
    settings: 'Free AI Engine Settings'
  };
  const subtitles = {
    pipeline: 'Track, tailor, and progress your active opportunities',
    tailor: 'Generate tailored ATS resumes, letters, and cold DMs in seconds',
    radar: 'Scrapes live tech postings matching your skill profile',
    vault: 'Historical vault of all generated documents and LaTeX sources',
    profile: 'Single source of truth used by the AI tailoring engine',
    settings: 'Configure free Google Gemini or Groq API keys'
  };

  document.getElementById('page-title').innerText = titles[tabId] || 'CareerOS';
  document.getElementById('page-subtitle').innerText = subtitles[tabId] || '';

  if (tabId === 'pipeline') loadApplications();
  if (tabId === 'vault') loadVaultDocuments();
}

function switchDocSubTab(subTab) {
  currentDocSubTab = subTab;
  const subTabs = ['cv', 'cl', 'dm', 'latex'];
  subTabs.forEach(s => {
    const el = document.getElementById(`doc-subtab-${s}`);
    const btn = document.getElementById(`subtab-btn-${s}`);
    if (el) el.classList.toggle('hidden', s !== subTab);
    if (btn) {
      if (s === subTab) {
        btn.className = 'px-5 py-3 text-white border-b-2 border-blue-500 font-semibold shrink-0';
      } else {
        btn.className = 'px-5 py-3 hover:text-white text-slate-400 shrink-0';
      }
    }
  });
}

// --- User Initialization & Switching ---
async function initUser() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      currentUser = await res.json();
      document.getElementById('user-display-name').innerText = currentUser.full_name;
      document.getElementById('user-display-email').innerText = currentUser.email;
      
      const initials = currentUser.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
      document.getElementById('user-avatar').innerText = initials || 'US';
      
      document.getElementById('sidebar-ai-mode').innerText = currentUser.has_gemini_key ? 'Gemini Pro' : (currentUser.has_groq_key ? 'Groq Fast' : 'Gemini (Free)');
    }
  } catch (e) {
    console.error('Error fetching user:', e);
  }
}

async function switchUserModal() {
  const choice = prompt("Multi-User SaaS Demo:\nEnter '1' for Shreyash Shukla (Primary)\nEnter '2' for Alex Friend (Friend Workspace):", "1");
  if (choice === "2") {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email: 'friend@example.com', password: 'demo123' })
    });
    if (res.ok) {
      location.reload();
    }
  } else if (choice === "1") {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email: 'shreyashshukla7398554573@gmail.com', password: 'admin123' })
    });
    if (res.ok) {
      location.reload();
    }
  }
}

// --- Load Pipeline Stats ---
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const stats = await res.json();
    document.getElementById('kpi-total').innerText = stats.total_applications;
    document.getElementById('kpi-drafted').innerText = stats.status_counts['drafted'] || 0;
    document.getElementById('kpi-interview').innerText = stats.status_counts['interview'] || 0;
    document.getElementById('kpi-fit').innerText = `${stats.avg_fit_score}%`;
  } catch (e) {
    console.error('Error loading stats:', e);
  }
}

// --- Applications Kanban Board ---
async function loadApplications() {
  try {
    const res = await fetch('/api/applications');
    if (!res.ok) return;
    const apps = await res.json();

    const cols = {
      discovered: document.getElementById('col-discovered'),
      drafted: document.getElementById('col-drafted'),
      applied: document.getElementById('col-applied'),
      interview: document.getElementById('col-interview'),
      offer: document.getElementById('col-offer')
    };

    // Reset columns
    Object.values(cols).forEach(c => { if (c) c.innerHTML = ''; });
    const counts = { discovered: 0, drafted: 0, applied: 0, interview: 0, offer: 0 };

    apps.forEach(app => {
      const statusKey = (app.status === 'hired') ? 'offer' : (cols[app.status] ? app.status : 'discovered');
      counts[statusKey] = (counts[statusKey] || 0) + 1;
      
      const fitBadgeClass = app.fit_score >= 85 
        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
        : (app.fit_score >= 70 ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30');

      const card = document.createElement('div');
      card.className = 'glass-card rounded-xl p-3.5 space-y-2.5 border border-slate-700/60 hover:border-blue-500/60 hover:shadow-lg hover:shadow-blue-500/10 transition-all';
      
      card.innerHTML = `
        <div class="flex items-center justify-between gap-1.5">
          <div class="flex items-center gap-2 min-w-0">
            <span class="w-6 h-6 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-xs uppercase shrink-0">
              ${(app.company || 'C')[0]}
            </span>
            <div class="font-bold text-white text-xs truncate max-w-[130px]">${app.company}</div>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-full border ${fitBadgeClass} font-bold shrink-0">
            ${app.fit_score}%
          </span>
        </div>

        <div class="text-[11px] font-medium text-slate-300 leading-snug line-clamp-1">${app.role}</div>

        ${app.notes ? `<div class="text-[10px] text-slate-400 italic line-clamp-2 leading-relaxed bg-slate-950/40 p-2 rounded-lg border border-slate-800/40">${app.notes}</div>` : ''}

        <div class="pt-2 border-t border-slate-800/70 flex items-center justify-between text-[10px] gap-2">
          <select onchange="handleStatusChange(${app.id}, this.value)" class="bg-slate-950 border border-slate-800 text-[10px] text-slate-300 rounded-lg px-2 py-1 focus:outline-none focus:border-blue-500 transition">
            <option value="discovered" ${app.status === 'discovered' ? 'selected' : ''}>Discovered</option>
            <option value="drafted" ${app.status === 'drafted' ? 'selected' : ''}>Drafted</option>
            <option value="applied" ${app.status === 'applied' ? 'selected' : ''}>Applied</option>
            <option value="interview" ${app.status === 'interview' ? 'selected' : ''}>Interview</option>
            <option value="offer" ${app.status === 'offer' ? 'selected' : ''}>Offer</option>
            <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>Rejected</option>
          </select>
          <button onclick="deleteApp(${app.id})" title="Remove" class="text-slate-500 hover:text-rose-400 text-xs p-1 rounded transition">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      `;
      if (cols[statusKey]) cols[statusKey].appendChild(card);
    });

    // Render Clean Empty States for empty columns
    Object.keys(cols).forEach(k => {
      const colEl = cols[k];
      if (colEl && counts[k] === 0) {
        colEl.innerHTML = `
          <div class="h-36 border-2 border-dashed border-slate-800/80 rounded-xl flex flex-col items-center justify-center p-4 text-center select-none">
            <i class="fa-regular fa-folder-open text-slate-700 text-xl mb-1.5"></i>
            <span class="text-[11px] text-slate-500 font-medium">No roles in this stage</span>
          </div>
        `;
      }
      const countEl = document.getElementById(`col-count-${k}`);
      if (countEl) countEl.innerText = counts[k];
    });

    loadStats();
  } catch (e) {
    console.error('Error loading applications:', e);
  }
}

async function handleStatusChange(appId, newStatus) {
  try {
    await fetch(`/api/applications/${appId}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ status: newStatus })
    });
    loadApplications();
  } catch (e) {
    alert('Error updating status');
  }
}

async function deleteApp(appId) {
  if (!confirm('Remove this application?')) return;
  try {
    await fetch(`/api/applications/${appId}`, { method: 'DELETE' });
    loadApplications();
  } catch (e) {
    alert('Error deleting application');
  }
}

// --- 1-Click AI Tailor Handler ---
async function handleTailorSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-tailor-generate');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Generating with AI...';

  const company = document.getElementById('tailor-company').value.trim();
  const role = document.getElementById('tailor-role').value.trim();
  const jd = document.getElementById('tailor-jd').value.trim();
  const provider = document.getElementById('tailor-provider').value;

  try {
    const res = await fetch('/api/tailor', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        company_name: company,
        role_title: role,
        job_description: jd,
        provider: provider
      })
    });

    if (!res.ok) throw new Error('Failed to generate tailored application');
    const data = await res.json();

    // Render results
    document.getElementById('res-score').innerText = `${data.fit_score} / 100 (${data.fit_score >= 80 ? 'Strong Match' : 'Moderate Match'})`;
    document.getElementById('res-target-role').innerText = `${data.role_title} @ ${data.company_name}`;
    document.getElementById('res-summary').innerText = data.fit_summary;

    const chipsEl = document.getElementById('res-skills-chips');
    chipsEl.innerHTML = '';
    (data.matching_skills || []).forEach(s => {
      chipsEl.innerHTML += `<span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"><i class="fa-solid fa-check text-[10px]"></i> ${s}</span>`;
    });

    document.getElementById('res-cv-content').innerText = data.tailored_cv_text;
    document.getElementById('res-cl-content').innerText = data.tailored_cover_letter;
    document.getElementById('res-dm-content').innerText = `--- LINKEDIN INMAIL ---\n${data.outreach_linkedin_dm}\n\n--- COLD EMAIL ---\n${data.outreach_cold_email}`;
    document.getElementById('res-latex-content').innerText = data.tailored_cv_latex;

    document.getElementById('tailor-results').classList.remove('hidden');
    document.getElementById('tailor-results').scrollIntoView({ behavior: 'smooth' });
    loadApplications();
  } catch (err) {
    alert(err.message || 'Error tailoring application');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Generate Tailored Assets';
  }
}

// --- Job Radar ---
async function loadRadarJobs() {
  const grid = document.getElementById('radar-jobs-grid');
  grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-12 text-xs font-mono text-slate-400"><i class="fa-solid fa-spinner animate-spin text-emerald-400 text-lg mb-2 block"></i> Scanning live tech developer feeds...</div>';
  const query = document.getElementById('radar-query-input').value.trim() || 'backend';

  try {
    const res = await fetch(`/api/radar/jobs?query=${encodeURIComponent(query)}&limit=12`);
    if (!res.ok) throw new Error();
    const jobs = await res.json();

    grid.innerHTML = '';
    jobs.forEach(job => {
      const card = document.createElement('div');
      card.className = 'glass-card rounded-2xl p-5 flex flex-col justify-between hover:border-emerald-500/50 hover:shadow-lg hover:shadow-emerald-500/10 transition-all';
      card.innerHTML = `
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">${job.match_score}% Match</span>
            <span class="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">${job.source}</span>
          </div>
          <h4 class="text-sm font-bold text-white mb-1 leading-snug">${job.title}</h4>
          <p class="text-xs font-semibold text-blue-400 mb-2">${job.company} <span class="text-slate-500 font-normal">• ${job.location}</span></p>
          <p class="text-[11px] text-slate-400 line-clamp-3 mb-4 leading-relaxed">${job.description}</p>
        </div>
        <div class="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
          <span class="text-[10px] font-mono text-slate-300 font-semibold">${job.salary || 'Competitive'}</span>
          <button onclick='tailorFromRadar(${JSON.stringify(job).replace(/'/g, "&#39;")})' class="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-300"></i> Tailor & Apply
          </button>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-8 text-xs text-rose-400">Error loading radar jobs.</div>';
  }
}

function tailorFromRadar(job) {
  document.getElementById('tailor-company').value = job.company;
  document.getElementById('tailor-role').value = job.title;
  document.getElementById('tailor-jd').value = `${job.title} at ${job.company}\nLocation: ${job.location}\n\nDescription:\n${job.description}`;
  switchTab('tailor');
}

// --- Document Vault ---
async function loadVaultDocuments() {
  const tbody = document.getElementById('vault-table-body');
  try {
    const res = await fetch('/api/documents');
    if (!res.ok) return;
    const docs = await res.json();

    tbody.innerHTML = '';
    if (docs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-slate-500">No generated documents yet. Use 1-Click Tailor to create some!</td></tr>';
      return;
    }

    docs.forEach(d => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-800/40 transition';
      tr.innerHTML = `
        <td class="py-3 px-4 text-slate-400">${new Date(d.created_at).toLocaleDateString()}</td>
        <td class="py-3 px-4 text-white font-bold">${d.company}</td>
        <td class="py-3 px-4 text-slate-300">${d.role}</td>
        <td class="py-3 px-4"><span class="px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 uppercase text-[10px] font-bold">${d.doc_type}</span></td>
        <td class="py-3 px-4 text-right">
          <button onclick="previewDoc(${d.id})" class="text-blue-400 hover:text-blue-300 text-xs font-semibold mr-2 transition">Preview</button>
          <button onclick="downloadDoc(${d.id})" class="text-emerald-400 hover:text-emerald-300 text-xs font-semibold transition">Download</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
  }
}

async function previewDoc(docId) {
  const res = await fetch(`/api/documents/${docId}`);
  if (res.ok) {
    const d = await res.json();
    alert(`[${d.doc_type.toUpperCase()}] for ${d.company}:\n\n` + d.content_text.substring(0, 600) + '...');
  }
}

async function downloadDoc(docId) {
  const res = await fetch(`/api/documents/${docId}`);
  if (res.ok) {
    const d = await res.json();
    const content = d.latex_text || d.content_text;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${d.company}_${d.role}_${d.doc_type}.${d.latex_text ? 'tex' : 'txt'}`;
    a.click();
  }
}

// --- Profile & Settings Handlers ---
async function loadProfile() {
  try {
    const res = await fetch('/api/profile');
    if (!res.ok) return;
    const p = await res.json();
    document.getElementById('prof-headline').value = p.headline || '';
    document.getElementById('prof-location').value = p.location || '';
    document.getElementById('prof-phone').value = p.phone || '';
    document.getElementById('prof-linkedin').value = p.linkedin_url || '';
    document.getElementById('prof-github').value = p.github_url || '';
    document.getElementById('prof-portfolio').value = p.portfolio_url || '';
    document.getElementById('prof-skills').value = p.skills_json || '';
  } catch (e) {
    console.error(e);
  }
}

async function handleProfileSave(e) {
  e.preventDefault();
  const payload = {
    headline: document.getElementById('prof-headline').value,
    location: document.getElementById('prof-location').value,
    phone: document.getElementById('prof-phone').value,
    linkedin_url: document.getElementById('prof-linkedin').value,
    github_url: document.getElementById('prof-github').value,
    portfolio_url: document.getElementById('prof-portfolio').value,
    skills_json: document.getElementById('prof-skills').value
  };
  try {
    await fetch('/api/profile', {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    alert('Candidate profile updated successfully!');
  } catch (e) {
    alert('Error saving profile');
  }
}

async function loadSettings() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const u = await res.json();
      if (u.has_gemini_key) document.getElementById('key-gemini').placeholder = '•••••••• (Active Free Key)';
      if (u.has_groq_key) document.getElementById('key-groq').placeholder = '•••••••• (Active Free Key)';
    }
  } catch (e) {}
}

async function handleKeysSave(e) {
  e.preventDefault();
  const gemini = document.getElementById('key-gemini').value.trim();
  const groq = document.getElementById('key-groq').value.trim();
  try {
    await fetch('/api/settings/keys', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        gemini_api_key: gemini || null,
        groq_api_key: groq || null,
        preferred_ai: gemini ? 'gemini' : (groq ? 'groq' : 'offline')
      })
    });
    alert('AI keys configured! Your searches will now be accelerated by free AI.');
    initUser();
  } catch (e) {
    alert('Error saving keys');
  }
}

function copyToClipboard(id) {
  const text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text);
  alert('Copied to clipboard!');
}
