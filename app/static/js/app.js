// CareerOS Client-Side SPA Controller & Strategy Suite

let currentUser = null;
let currentTab = 'pipeline';
let currentDocSubTab = 'visual';
let allRadarJobs = [];
let activeGeneratedPackage = null;

document.addEventListener('DOMContentLoaded', async () => {
  await initUser();
  await loadStats();
  await loadApplications();
  await loadProfile();
  await loadSettings();
  loadRadarJobs();
  calculateSalary();
});

// --- Tab Navigation ---
function switchTab(tabId) {
  currentTab = tabId;
  const tabs = ['pipeline', 'tailor', 'radar', 'salary', 'vault', 'profile', 'settings'];
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
    radar: 'Automated Job Radar (100+ Active Jobs)',
    salary: 'Salary Benchmark & ESOP Calculator',
    vault: 'Document & CV Archive Vault',
    profile: 'Candidate Master Profile',
    settings: 'Free AI Engine Settings'
  };
  const subtitles = {
    pipeline: 'Track, tailor, and progress your active opportunities',
    tailor: 'Generate tailored ATS resumes, letters, outreach, and interview kits in seconds',
    radar: 'Scrapes live tech postings matching your skill profile',
    salary: 'Expected market CTC, stock options, and word-for-word negotiation scripts',
    vault: 'Historical vault of all generated documents and LaTeX sources',
    profile: 'Single source of truth used by the AI tailoring engine',
    settings: 'Configure free Google Gemini or Groq API keys'
  };

  document.getElementById('page-title').innerText = titles[tabId] || 'CareerOS';
  document.getElementById('page-subtitle').innerText = subtitles[tabId] || '';

  if (tabId === 'pipeline') loadApplications();
  if (tabId === 'vault') loadVaultDocuments();
}

// --- Subtab Navigation for Tailor Results ---
function switchDocSubTab(subTab) {
  currentDocSubTab = subTab;
  const subTabs = ['visual', 'cv', 'cl', 'outreach', 'interview', 'latex'];
  subTabs.forEach(s => {
    const el = document.getElementById(`doc-subtab-${s}`);
    const btn = document.getElementById(`subtab-btn-${s}`);
    if (el) el.classList.toggle('hidden', s !== subTab);
    if (btn) {
      if (s === subTab) {
        btn.className = 'px-5 py-3 text-white border-b-2 border-blue-500 font-semibold shrink-0 flex items-center gap-1.5';
      } else {
        btn.className = 'px-5 py-3 hover:text-white text-slate-400 shrink-0 flex items-center gap-1.5';
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
      document.getElementById('user-avatar').innerText = initials || 'SS';
      
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
    if (res.ok) location.reload();
  } else if (choice === "1") {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email: 'shreyashshukla7398554573@gmail.com', password: 'admin123' })
    });
    if (res.ok) location.reload();
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

    Object.values(cols).forEach(c => { if (c) c.innerHTML = ''; });
    const counts = { discovered: 0, drafted: 0, applied: 0, interview: 0, offer: 0 };

    apps.forEach(app => {
      const statusKey = (app.status === 'hired') ? 'offer' : (cols[app.status] ? app.status : 'discovered');
      counts[statusKey] = (counts[statusKey] || 0) + 1;
      
      const fitBadgeClass = app.fit_score >= 85 
        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
        : (app.fit_score >= 70 ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30');

      // Calculate days elapsed
      const createdDate = new Date(app.created_at);
      const diffDays = Math.floor((new Date() - createdDate) / (1000 * 60 * 60 * 24));
      const daysText = diffDays === 0 ? "Today" : `${diffDays}d ago`;

      const showFollowUpBadge = (app.status === 'applied' && diffDays >= 4);

      const card = document.createElement('div');
      card.className = 'glass-card rounded-xl p-3.5 space-y-2.5 border border-slate-700/60 hover:border-blue-500/60 hover:shadow-lg hover:shadow-blue-500/10 transition-all';
      
      card.innerHTML = `
        <div class="flex items-center justify-between gap-1.5">
          <div class="flex items-center gap-2 min-w-0">
            <span class="w-6 h-6 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-xs uppercase shrink-0">
              ${(app.company || 'C')[0]}
            </span>
            <div class="font-bold text-white text-xs truncate max-w-[125px]">${app.company}</div>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-full border ${fitBadgeClass} font-bold shrink-0">
            ${app.fit_score}%
          </span>
        </div>

        <div class="text-[11px] font-medium text-slate-300 leading-snug line-clamp-1">${app.role}</div>

        <div class="flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>Added: ${daysText}</span>
          ${showFollowUpBadge ? '<span class="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">Follow-Up Ready</span>' : ''}
        </div>

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
          
          <div class="flex items-center gap-1.5">
            <button onclick="openInterviewModal(${app.id}, '${app.company.replace(/'/g, "\\'")}', '${app.role.replace(/'/g, "\\'")}')" title="Interview Prep Kit" class="text-purple-400 hover:text-purple-300 text-xs px-1.5 py-0.5 rounded bg-purple-950/50 border border-purple-500/30 transition">
              <i class="fa-solid fa-brain"></i> Prep
            </button>
            <button onclick="deleteApp(${app.id})" title="Remove" class="text-slate-500 hover:text-rose-400 text-xs p-1 rounded transition">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </div>
      `;
      if (cols[statusKey]) cols[statusKey].appendChild(card);
    });

    Object.keys(cols).forEach(k => {
      const colEl = cols[k];
      if (colEl && counts[k] === 0) {
        colEl.innerHTML = `
          <div class="h-32 border-2 border-dashed border-slate-800/80 rounded-xl flex flex-col items-center justify-center p-4 text-center select-none">
            <i class="fa-regular fa-folder-open text-slate-700 text-lg mb-1"></i>
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
  btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Generating Full Strategy Package...';

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
    activeGeneratedPackage = data;

    // Render results
    document.getElementById('res-score').innerText = `${data.fit_score} / 100 (${data.fit_score >= 85 ? 'Strong Match' : 'Good Match'})`;
    document.getElementById('res-target-role').innerText = `${data.role_title} @ ${data.company_name}`;
    document.getElementById('res-summary').innerText = data.fit_summary;

    const chipsEl = document.getElementById('res-skills-chips');
    chipsEl.innerHTML = '';
    (data.matching_skills || []).forEach(s => {
      chipsEl.innerHTML += `<span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"><i class="fa-solid fa-check text-[10px]"></i> ${s}</span>`;
    });

    // Subtab 1: Visual Resume
    if (data.tailored_cv_html) {
      document.getElementById('visual-resume-frame').innerHTML = data.tailored_cv_html;
    }

    // Subtab 2: Plain Text ATS
    document.getElementById('res-cv-content').innerText = data.tailored_cv_text;

    // Subtab 3: Cover Letter
    document.getElementById('res-cl-content').innerText = data.tailored_cover_letter;

    // Subtab 4: Cold Outreach Pack
    document.getElementById('res-cold-email-content').innerText = data.outreach_cold_email;
    document.getElementById('res-connection-note').innerText = data.outreach_connection_note || "Hi! Saw your opening. Built 250+ APIs, cut SQL latency by 35% with Redis, rank #28 on GFG. Would love to connect!";
    document.getElementById('res-linkedin-dm').innerText = data.outreach_linkedin_dm;
    document.getElementById('res-followup-1').innerText = data.outreach_followup_1 || "";
    document.getElementById('res-followup-2').innerText = data.outreach_followup_2 || "";

    // Set mailto link
    const subjectMatch = data.outreach_cold_email.match(/Subject:\s*(.*)/i);
    const subject = subjectMatch ? subjectMatch[1] : `${role} Application - Shreyash Shukla`;
    const body = data.outreach_cold_email.replace(/Subject:.*\n+/i, '');
    document.getElementById('btn-mailto-link').href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    // Subtab 5: Interview Prep Kit
    if (data.interview_prep) {
      renderInterviewPrep(data.interview_prep);
    }

    // Subtab 6: LaTeX
    document.getElementById('res-latex-content').innerText = data.tailored_cv_latex;

    document.getElementById('tailor-results').classList.remove('hidden');
    document.getElementById('tailor-results').scrollIntoView({ behavior: 'smooth' });
    loadApplications();
  } catch (err) {
    alert(err.message || 'Error tailoring application');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Generate Complete Job Pack';
  }
}

function renderInterviewPrep(prep) {
  // System Design Blueprint
  document.getElementById('prep-system-design').innerText = prep.system_design || "System design architecture ready.";

  // Questions List
  const qList = document.getElementById('prep-questions-list');
  qList.innerHTML = '';
  (prep.questions || []).forEach((item, idx) => {
    qList.innerHTML += `
      <details class="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80 group">
        <summary class="text-xs font-semibold text-white cursor-pointer list-none flex items-center justify-between gap-2">
          <span><span class="text-purple-400 font-mono font-bold mr-1.5">Q${idx+1}.</span> ${item.question}</span>
          <i class="fa-solid fa-chevron-down text-slate-500 text-[10px] group-open:rotate-180 transition"></i>
        </summary>
        <p class="text-xs text-slate-300 mt-2.5 pt-2 border-t border-slate-800 leading-relaxed font-mono">${item.answer}</p>
      </details>
    `;
  });

  // STAR Stories
  const starContainer = document.getElementById('prep-star-stories');
  starContainer.innerHTML = '';
  (prep.star_stories || []).forEach(st => {
    starContainer.innerHTML += `
      <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
        <div class="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
          <i class="fa-solid fa-star text-[10px]"></i> ${st.title}
        </div>
        <div class="text-[11px] text-slate-400 space-y-1 leading-snug">
          <div><strong class="text-slate-300 font-mono">Situation:</strong> ${st.situation}</div>
          <div><strong class="text-slate-300 font-mono">Task:</strong> ${st.task}</div>
          <div><strong class="text-slate-300 font-mono">Action:</strong> ${st.action}</div>
          <div><strong class="text-slate-300 font-mono">Result:</strong> ${st.result}</div>
        </div>
      </div>
    `;
  });

  // Reverse Questions
  const revList = document.getElementById('prep-reverse-questions');
  revList.innerHTML = '';
  (prep.reverse_questions || []).forEach(rq => {
    revList.innerHTML += `<li>${rq}</li>`;
  });
}

function printVisualResume() {
  window.print();
}

function downloadActiveDoc(ext) {
  if (!activeGeneratedPackage) return;
  const content = (ext === 'tex') ? activeGeneratedPackage.tailored_cv_latex : activeGeneratedPackage.tailored_cv_text;
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${activeGeneratedPackage.company_name}_Resume.${ext}`;
  a.click();
}

// --- Job Radar (100+ Jobs) ---
async function loadRadarJobs() {
  const grid = document.getElementById('radar-jobs-grid');
  grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-16 text-xs font-mono text-slate-400"><i class="fa-solid fa-spinner animate-spin text-emerald-400 text-xl mb-2 block"></i> Scanning live developer feeds and verified Indian tech hubs...</div>';

  try {
    const res = await fetch('/api/radar/jobs?query=all&limit=150');
    if (!res.ok) throw new Error();
    allRadarJobs = await res.json();
    applyRadarFilters();
  } catch (e) {
    grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-12 text-xs text-rose-400">Error loading radar jobs.</div>';
  }
}

function applyRadarFilters() {
  const query = (document.getElementById('radar-search').value || '').trim().toLowerCase();
  const loc = document.getElementById('radar-filter-loc').value;
  const role = document.getElementById('radar-filter-role').value;
  const sort = document.getElementById('radar-filter-sort').value;

  let filtered = allRadarJobs.filter(j => {
    // Search query
    if (query) {
      const match = `${j.title} ${j.company} ${j.location} ${(j.tags || []).join(' ')}`.toLowerCase();
      if (!match.includes(query)) return false;
    }

    // Location
    if (loc !== 'all') {
      const jLoc = j.location.toLowerCase();
      if (loc === 'bengaluru' && !jLoc.includes('bengaluru')) return false;
      if (loc === 'delhi_ncr' && (!jLoc.includes('noida') && !jLoc.includes('gurgaon') && !jLoc.includes('delhi'))) return false;
      if (loc === 'remote_india' && (!jLoc.includes('remote') || jLoc.includes('global') || jLoc.includes('worldwide'))) return false;
      if (loc === 'global_remote' && (!jLoc.includes('worldwide') && !jLoc.includes('global') && !jLoc.includes('$') && !jLoc.includes('€'))) return false;
    }

    // Role
    if (role !== 'all') {
      if (role === 'backend' && !j.title.toLowerCase().includes('backend') && j.role_type !== 'backend') return false;
      if (role === 'fullstack' && !j.title.toLowerCase().includes('full') && j.role_type !== 'fullstack') return false;
      if (role === 'sde1' && j.level !== 'sde1') return false;
      if (role === 'sde2' && j.level !== 'sde2') return false;
    }

    return true;
  });

  // Sort
  if (sort === 'score') {
    filtered.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
  } else if (sort === 'company') {
    filtered.sort((a, b) => a.company.localeCompare(b.company));
  }

  // Update badge count
  document.getElementById('radar-count-badge').innerText = `${filtered.length} Active Jobs`;

  renderRadarGrid(filtered);
}

function renderRadarGrid(jobs) {
  const grid = document.getElementById('radar-jobs-grid');
  grid.innerHTML = '';

  if (jobs.length === 0) {
    grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-16 text-slate-500 text-xs">No matching jobs found with current filters. Try resetting search!</div>';
    return;
  }

  jobs.forEach(job => {
    const card = document.createElement('div');
    card.className = 'glass-card rounded-2xl p-5 flex flex-col justify-between hover:border-emerald-500/50 hover:shadow-lg hover:shadow-emerald-500/10 transition-all';
    
    const tagsHtml = (job.tags || []).slice(0, 4).map(t => `<span class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300 border border-slate-700/60">${t}</span>`).join('');

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between gap-2 mb-2">
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">${job.match_score}% Match</span>
          <span class="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">${job.source}</span>
        </div>
        <h4 class="text-sm font-bold text-white mb-1 leading-snug">${job.title}</h4>
        <p class="text-xs font-semibold text-blue-400 mb-2">${job.company} <span class="text-slate-500 font-normal">• ${job.location}</span></p>
        <p class="text-[11px] text-slate-400 line-clamp-3 mb-3 leading-relaxed">${job.description}</p>
        <div class="flex flex-wrap gap-1 mb-4">${tagsHtml}</div>
      </div>
      <div class="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
        <span class="text-[10px] font-mono text-emerald-400 font-semibold">${job.salary || 'Competitive'}</span>
        <div class="flex items-center gap-1.5">
          ${job.url ? `<a href="${job.url}" target="_blank" class="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-900 border border-slate-800 text-xs" title="Open Official Link"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>` : ''}
          <button onclick='tailorFromRadar(${JSON.stringify(job).replace(/'/g, "&#39;")})' class="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-300"></i> Tailor & Apply
          </button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function tailorFromRadar(job) {
  document.getElementById('tailor-company').value = job.company;
  document.getElementById('tailor-role').value = job.title;
  document.getElementById('tailor-jd').value = `${job.title} at ${job.company}\nLocation: ${job.location}\nSalary: ${job.salary || ''}\n\nKey Responsibilities & Requirements:\n${job.description}`;
  switchTab('tailor');
}

// --- Interactive Salary Calculator ---
async function calculateSalary() {
  const exp = document.getElementById('sal-exp').value;
  const loc = document.getElementById('sal-loc').value;
  const tier = document.getElementById('sal-tier').value;

  try {
    const res = await fetch('/api/salary-benchmark', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        role: "Backend Software Engineer",
        experience_years: parseFloat(exp),
        location: loc,
        company_tier: tier
      })
    });
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById('sal-out-base').innerText = `${data.base_min} - ${data.base_max}`;
    document.getElementById('sal-out-bonus').innerText = data.bonus_estimate;
    document.getElementById('sal-out-esop').innerText = data.esop_estimate;
    document.getElementById('sal-out-total').innerText = data.total_ctc_range;
    document.getElementById('sal-out-script').innerText = data.negotiation_script;
  } catch (e) {
    console.error(e);
  }
}

// --- Application Details & Interview Prep Modal ---
async function openInterviewModal(appId, company, role) {
  const modal = document.getElementById('global-modal');
  const title = document.getElementById('modal-title');
  const subtitle = document.getElementById('modal-subtitle');
  const body = document.getElementById('modal-body');

  title.innerHTML = `<i class="fa-solid fa-brain text-purple-400"></i> ${company} — Technical Strategy`;
  subtitle.innerText = `Target Role: ${role}`;
  body.innerHTML = '<div class="text-center py-10 font-mono text-xs text-slate-400"><i class="fa-solid fa-spinner animate-spin text-purple-400 text-lg mb-2 block"></i> Loading strategic interview prep kit...</div>';
  modal.classList.remove('hidden');

  try {
    const res = await fetch(`/api/applications/${appId}/prep`);
    if (!res.ok) throw new Error();
    const prep = await res.json();

    let qHtml = (prep.questions || []).map((item, i) => `
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
        <div class="text-xs font-bold text-white"><span class="text-purple-400 font-mono">Q${i+1}:</span> ${item.question}</div>
        <p class="text-[11px] text-slate-300 font-mono mt-1 leading-relaxed">${item.answer}</p>
      </div>
    `).join('');

    let starHtml = (prep.star_stories || []).map(s => `
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1 text-[11px]">
        <div class="font-bold text-emerald-400">${s.title}</div>
        <div class="text-slate-400"><strong>Action:</strong> ${s.action}</div>
        <div class="text-slate-300"><strong>Result:</strong> ${s.result}</div>
      </div>
    `).join('');

    body.innerHTML = `
      <div class="space-y-4">
        <div>
          <span class="text-xs font-mono text-purple-400 font-bold uppercase block mb-1.5">System Design Blueprint</span>
          <pre class="bg-slate-950 p-3 rounded-xl text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">${prep.system_design || 'System architecture ready.'}</pre>
        </div>

        <div>
          <span class="text-xs font-mono text-purple-400 font-bold uppercase block mb-1.5">Top Predicted Technical Questions</span>
          <div class="space-y-2 max-h-60 overflow-y-auto custom-scroll">${qHtml}</div>
        </div>

        <div>
          <span class="text-xs font-mono text-emerald-400 font-bold uppercase block mb-1.5">Your STAR Project Stories</span>
          <div class="grid grid-cols-1 gap-2">${starHtml}</div>
        </div>
      </div>
    `;
  } catch (e) {
    body.innerHTML = '<div class="text-center py-8 text-xs text-rose-400">Failed to load interview prep.</div>';
  }
}

function closeModal() {
  document.getElementById('global-modal').classList.add('hidden');
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
    alert(`[${d.doc_type.toUpperCase()}] for ${d.company}:\n\n` + d.content_text.substring(0, 800) + '...');
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

function copyInterviewKit() {
  const text = `
=== TECHNICAL INTERVIEW PREPARATION STRATEGY ===

${document.getElementById('prep-system-design').innerText}

=== EXPECTED TECHNICAL QUESTIONS & MODEL ANSWERS ===
${Array.from(document.querySelectorAll('#prep-questions-list details')).map(d => d.innerText).join('\n\n')}

=== PROJECT STAR STORIES ===
${Array.from(document.querySelectorAll('#prep-star-stories > div')).map(d => d.innerText).join('\n\n')}

=== REVERSE QUESTIONS TO ASK ===
${document.getElementById('prep-reverse-questions').innerText}
  `;
  navigator.clipboard.writeText(text.trim());
  alert('Full interview cheat sheet copied to clipboard!');
}
