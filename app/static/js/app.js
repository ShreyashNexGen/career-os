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
  loadDedicatedPrepKit('ViralMe', 'Backend Software Engineer');
});

// --- Tab Navigation ---
function switchTab(tabId) {
  currentTab = tabId;
  const tabs = ['pipeline', 'tailor', 'radar', 'prep', 'salary', 'vault', 'profile', 'settings'];
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

  // Highlight Mobile Bottom Bar
  const bnavTabs = ['pipeline', 'tailor', 'radar', 'prep', 'vault'];
  bnavTabs.forEach(b => {
    const bBtn = document.getElementById(`bnav-${b}`);
    if (bBtn) {
      if (b === tabId) {
        bBtn.className = 'flex flex-col items-center gap-0.5 text-blue-500 text-[10px] font-semibold py-1 px-2 transition';
      } else {
        bBtn.className = 'flex flex-col items-center gap-0.5 text-slate-400 hover:text-white text-[10px] font-medium py-1 px-2 transition';
      }
    }
  });

  closeMobileSidebar();

  const titles = {
    pipeline: 'Applications Pipeline & Tracking',
    tailor: '1-Click AI Document Tailor',
    radar: 'Automated Job Radar (100+ Active Jobs)',
    prep: 'Technical Interview Strategy Suite',
    salary: 'Salary Benchmark & ESOP Calculator',
    vault: 'Document & CV Archive Vault',
    profile: 'Candidate Master Profile',
    settings: 'Free AI Engine Settings'
  };
  const subtitles = {
    pipeline: 'Track, tailor, and progress your active opportunities',
    tailor: 'Generate tailored ATS resumes, letters, outreach, and interview kits in seconds',
    radar: 'Scrapes live tech postings matching your skill profile',
    prep: 'Domain architecture blueprints, 10+ technical Q&As, and grounded STAR stories',
    salary: 'Expected market CTC, stock options, and word-for-word negotiation scripts',
    vault: 'Historical vault of all generated documents and LaTeX sources',
    profile: 'Single source of truth used by the AI tailoring engine',
    settings: 'Configure free Google Gemini or Groq API keys'
  };

  document.getElementById('page-title').innerText = titles[tabId] || 'CareerOS';
  document.getElementById('page-subtitle').innerText = subtitles[tabId] || '';

  if (tabId === 'pipeline') loadApplications();
  if (tabId === 'vault') loadVaultDocuments();
  if (tabId === 'prep' && !currentPrepData) loadDedicatedPrepKit();
}

function toggleMobileSidebar() {
  const drawer = document.getElementById('sidebar-drawer');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!drawer || !backdrop) return;
  const isClosed = drawer.classList.contains('-translate-x-full');
  if (isClosed) {
    drawer.classList.remove('-translate-x-full');
    backdrop.classList.remove('hidden');
  } else {
    closeMobileSidebar();
  }
}

function closeMobileSidebar() {
  const drawer = document.getElementById('sidebar-drawer');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (drawer) drawer.classList.add('-translate-x-full');
  if (backdrop) backdrop.classList.add('hidden');
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toast-msg');
  if (!toast || !toastMsg) return;
  toastMsg.innerText = msg;
  toast.classList.remove('translate-y-20', 'opacity-0', 'pointer-events-none');
  setTimeout(() => {
    toast.classList.add('translate-y-20', 'opacity-0', 'pointer-events-none');
  }, 2500);
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
    showToast(`Status updated to ${newStatus}!`);
  } catch (e) {
    showToast('Error updating status');
  }
}

async function deleteApp(appId) {
  if (!confirm('Remove this application?')) return;
  try {
    await fetch(`/api/applications/${appId}`, { method: 'DELETE' });
    loadApplications();
    showToast('Application removed');
  } catch (e) {
    showToast('Error deleting application');
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
    showToast(err.message || 'Error tailoring application');
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

// --- High-Fidelity PDF & Isolated Print Engine ---
function downloadResumePdf() {
  const container = document.getElementById('visual-resume-frame');
  if (!container || !container.innerHTML.trim()) {
    showToast('Please tailor an application first.');
    return;
  }
  showToast('Generating official PDF resume...');

  const company = (activeGeneratedPackage?.company_name || 'Shreyash_Shukla').replace(/[^a-zA-Z0-9_-]/g, '_');
  const filename = `Shreyash_Shukla_Resume_${company}.pdf`;

  // Attach temporary container to DOM so html2canvas computes valid layout & metrics
  const exportDiv = document.createElement('div');
  exportDiv.id = 'pdf-export-active-resume';
  exportDiv.innerHTML = container.innerHTML;
  exportDiv.style.position = 'fixed';
  exportDiv.style.left = '-9999px';
  exportDiv.style.top = '0';
  exportDiv.style.width = '794px'; // 210mm in pixels at 96 DPI
  exportDiv.style.padding = '32px 36px';
  exportDiv.style.background = '#ffffff';
  exportDiv.style.color = '#0f172a';
  exportDiv.style.zIndex = '-9999';
  document.body.appendChild(exportDiv);

  const opt = {
    margin: [0, 0, 0, 0],
    filename: filename,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true, letterRendering: true, scrollY: 0 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
  };

  if (window.html2pdf) {
    html2pdf().set(opt).from(exportDiv).save().then(() => {
      showToast('PDF downloaded successfully!');
    }).catch(err => {
      console.error('html2pdf error:', err);
      printVisualResume();
    }).finally(() => {
      if (exportDiv.parentNode) exportDiv.parentNode.removeChild(exportDiv);
    });
  } else {
    if (exportDiv.parentNode) exportDiv.parentNode.removeChild(exportDiv);
    printVisualResume();
  }
}

function printVisualResume() {
  const content = document.getElementById('visual-resume-frame')?.innerHTML || '';
  if (!content.trim()) {
    showToast('No resume content to print.');
    return;
  }
  const company = (activeGeneratedPackage?.company_name || 'Shreyash_Shukla').replace(/[^a-zA-Z0-9_-]/g, '_');
  printResumeHtml(content, company);
}

function printResumeHtml(contentHtml, companyName) {
  const comp = (companyName || 'Target').replace(/[^a-zA-Z0-9_-]/g, '_');
  const printWin = window.open('', '_blank', 'width=850,height=1000');
  if (!printWin) {
    showToast('Please allow popups to print/save resume.');
    return;
  }
  printWin.document.open();
  printWin.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Shreyash_Shukla_Resume_${comp}</title>
      <meta charset="utf-8">
      <style>
        @page { size: A4; margin: 12mm 14mm; }
        * { box-sizing: border-box; }
        html, body {
          margin: 0;
          padding: 0;
          background: #ffffff !important;
          color: #0f172a !important;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          font-size: 13px;
          line-height: 1.45;
        }
        @media print {
          body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        }
      </style>
    </head>
    <body>
      ${contentHtml}
      <script>
        window.onload = function() {
          window.focus();
          window.print();
          window.onafterprint = function() { window.close(); };
        };
      <\/script>
    </body>
    </html>
  `);
  printWin.document.close();
}

function downloadActiveDoc(ext) {
  if (!activeGeneratedPackage) {
    showToast('Please tailor an application first.');
    return;
  }
  if (ext === 'pdf') {
    downloadResumePdf();
    return;
  }
  const content = (ext === 'tex') ? activeGeneratedPackage.tailored_cv_latex : activeGeneratedPackage.tailored_cv_text;
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${activeGeneratedPackage.company_name}_Resume.${ext}`;
  a.click();
  showToast(`Downloaded .${ext} file!`);
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
  const compType = (document.getElementById('radar-filter-company')?.value || 'all').toLowerCase();
  const salRange = (document.getElementById('radar-filter-salary')?.value || 'all').toLowerCase();
  const loc = (document.getElementById('radar-filter-loc')?.value || 'all').toLowerCase();
  const role = (document.getElementById('radar-filter-role')?.value || 'all').toLowerCase();
  const sort = document.getElementById('radar-filter-sort')?.value || 'score';

  let filtered = allRadarJobs.filter(j => {
    // Search query
    if (query) {
      const match = `${j.title} ${j.company} ${j.location} ${(j.tags || []).join(' ')}`.toLowerCase();
      if (!match.includes(query)) return false;
    }

    // Company Type
    if (compType !== 'all') {
      if ((j.company_type || '').toLowerCase() !== compType) return false;
    }

    // Salary Range
    if (salRange !== 'all') {
      if ((j.salary_range || '').toLowerCase() !== salRange) return false;
    }

    // Location
    if (loc !== 'all') {
      const jLoc = (j.location || '').toLowerCase();
      if (loc === 'bengaluru' && !jLoc.includes('bengaluru')) return false;
      if (loc === 'delhi_ncr' && (!jLoc.includes('noida') && !jLoc.includes('gurgaon') && !jLoc.includes('delhi'))) return false;
      if (loc === 'remote_india' && (!jLoc.includes('remote') || jLoc.includes('global') || jLoc.includes('worldwide'))) return false;
      if (loc === 'global_remote' && (!jLoc.includes('worldwide') && !jLoc.includes('global') && !jLoc.includes('$'))) return false;
    }

    // Role
    if (role !== 'all') {
      const jTitle = (j.title || '').toLowerCase();
      if (role === 'backend' && !jTitle.includes('backend') && j.role_type !== 'backend') return false;
      if (role === 'fullstack' && !jTitle.includes('full') && j.role_type !== 'fullstack') return false;
      if (role === 'sde1' && j.level !== 'sde1') return false;
      if (role === 'sde2' && j.level !== 'sde2') return false;
    }

    return true;
  });

  // Sort
  if (sort === 'score') {
    filtered.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
  } else if (sort === 'company') {
    filtered.sort((a, b) => (a.company || '').localeCompare(b.company || ''));
  }

  // Update badge count
  const countBadge = document.getElementById('radar-count-badge');
  if (countBadge) countBadge.innerText = `${filtered.length} Active Jobs`;

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

    const compTypeBadge = job.company_type === 'startup' ? '<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 font-bold uppercase">Startup</span>' :
                          (job.company_type === 'mnc' ? '<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 font-bold uppercase">Tier-1 MNC</span>' :
                          '<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 font-bold uppercase">Cloud/DevTools</span>');

    const jobUrl = job.url || `https://www.google.com/search?q=${encodeURIComponent(job.company + ' careers')}`;

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between gap-2 mb-2.5">
          <div class="flex items-center gap-1.5">
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">${job.match_score}% Match</span>
            ${compTypeBadge}
          </div>
          <span class="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">${job.source}</span>
        </div>
        <a href="${jobUrl}" target="_blank" class="block group" title="Open official job posting">
          <h4 class="text-sm font-bold text-white group-hover:text-blue-400 mb-1 leading-snug transition flex items-center justify-between">
            <span>${job.title}</span>
            <i class="fa-solid fa-arrow-up-right-from-square text-[11px] text-slate-500 group-hover:text-blue-400 ml-1.5 shrink-0 opacity-70"></i>
          </h4>
        </a>
        <p class="text-xs font-semibold text-blue-400 mb-2">
          <a href="${jobUrl}" target="_blank" class="hover:underline">${job.company}</a>
          <span class="text-slate-500 font-normal">• ${job.location}</span>
        </p>
        <p class="text-[11px] text-slate-400 line-clamp-3 mb-3 leading-relaxed">${job.description}</p>
        <div class="flex flex-wrap gap-1 mb-4">${tagsHtml}</div>
      </div>
      <div class="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
        <span class="text-[10px] font-mono text-emerald-400 font-semibold">${job.salary || 'Competitive'}</span>
        <div class="flex items-center gap-1.5">
          <a href="${jobUrl}" target="_blank" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium transition flex items-center gap-1.5" title="Direct to Official Portal">
            <i class="fa-solid fa-arrow-up-right-from-square text-emerald-400"></i> Direct Apply
          </a>
          <button onclick='tailorFromRadar(${JSON.stringify(job).replace(/'/g, "&#39;")})' class="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-300"></i> Tailor Pack
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

let activeModalDoc = null;

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
      
      let actionsHtml = '';
      if (d.doc_type === 'cv') {
        actionsHtml = `
          <button onclick="previewDoc(${d.id})" class="text-blue-400 hover:text-blue-300 text-xs font-semibold mr-1.5 transition">Preview</button>
          <button onclick="downloadDocPdf(${d.id})" class="text-emerald-400 hover:text-emerald-300 text-xs font-semibold mr-1.5 transition"><i class="fa-solid fa-file-pdf"></i> PDF</button>
          <button onclick="downloadDoc(${d.id}, 'txt')" class="text-slate-400 hover:text-white text-xs font-mono mr-1.5 transition">.txt</button>
          <button onclick="downloadDoc(${d.id}, 'tex')" class="text-slate-400 hover:text-white text-xs font-mono transition">.tex</button>
        `;
      } else {
        actionsHtml = `
          <button onclick="previewDoc(${d.id})" class="text-blue-400 hover:text-blue-300 text-xs font-semibold mr-2 transition">Preview</button>
          <button onclick="downloadDoc(${d.id}, 'txt')" class="text-emerald-400 hover:text-emerald-300 text-xs font-semibold transition">Download</button>
        `;
      }

      tr.innerHTML = `
        <td class="py-3 px-4 text-slate-400 whitespace-nowrap">${new Date(d.created_at).toLocaleDateString()}</td>
        <td class="py-3 px-4 text-white font-bold whitespace-nowrap">${d.company}</td>
        <td class="py-3 px-4 text-slate-300">${d.role}</td>
        <td class="py-3 px-4 whitespace-nowrap"><span class="px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/30 uppercase text-[10px] font-bold">${d.doc_type}</span></td>
        <td class="py-3 px-4 text-right whitespace-nowrap">${actionsHtml}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
  }
}

async function previewDoc(docId) {
  try {
    const res = await fetch(`/api/documents/${docId}`);
    if (!res.ok) return;
    const d = await res.json();
    activeModalDoc = d;

    const modal = document.getElementById('doc-preview-modal');
    const badge = document.getElementById('doc-modal-badge');
    const title = document.getElementById('doc-modal-title');
    const sub = document.getElementById('doc-modal-sub');
    const body = document.getElementById('doc-modal-body');
    const btnPdf = document.getElementById('doc-modal-btn-pdf');
    const btnPrint = document.getElementById('doc-modal-btn-print');

    badge.innerText = d.doc_type.toUpperCase();
    title.innerText = `${d.company} — ${d.role}`;
    sub.innerText = `Generated on ${new Date(d.created_at).toLocaleString()}`;

    if (d.doc_type === 'cv') {
      btnPdf.classList.remove('hidden');
      btnPrint.classList.remove('hidden');
      if (d.html_text) {
        body.innerHTML = `
          <div class="bg-white text-slate-900 p-6 sm:p-10 rounded-2xl shadow-xl overflow-x-auto max-h-[70vh] custom-scroll" id="modal-resume-render">
            ${d.html_text}
          </div>
        `;
      } else {
        body.innerHTML = `<pre class="bg-slate-950 p-4 rounded-xl text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-[70vh] overflow-y-auto">${d.content_text}</pre>`;
      }
    } else if (d.doc_type === 'interview_prep') {
      btnPdf.classList.remove('hidden');
      btnPrint.classList.add('hidden');
      try {
        const prep = JSON.parse(d.content_text);
        let qHtml = (prep.questions || []).map((item, i) => `
          <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
            <div class="text-xs font-bold text-white"><span class="text-purple-400 font-mono">Q${i+1}:</span> ${item.question}</div>
            <p class="text-xs text-slate-300 font-mono mt-1.5 leading-relaxed">${item.answer}</p>
          </div>
        `).join('');

        let starHtml = (prep.star_stories || []).map(s => `
          <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1 text-xs">
            <div class="font-bold text-emerald-400">${s.title}</div>
            <div class="text-slate-400"><strong>Action:</strong> ${s.action}</div>
            <div class="text-slate-300"><strong>Result:</strong> ${s.result}</div>
          </div>
        `).join('');

        body.innerHTML = `
          <div class="space-y-4" id="modal-resume-render">
            <div>
              <span class="text-xs font-mono text-purple-400 font-bold uppercase block mb-1">System Design Blueprint</span>
              <pre class="bg-slate-950 p-4 rounded-xl text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">${prep.system_design || 'System architecture ready.'}</pre>
            </div>
            <div>
              <span class="text-xs font-mono text-purple-400 font-bold uppercase block mb-1">Predicted Technical Questions</span>
              <div class="space-y-2.5 max-h-60 overflow-y-auto custom-scroll">${qHtml}</div>
            </div>
            <div>
              <span class="text-xs font-mono text-emerald-400 font-bold uppercase block mb-1">Grounded Project STAR Stories</span>
              <div class="grid grid-cols-1 gap-2">${starHtml}</div>
            </div>
          </div>
        `;
      } catch (err) {
        body.innerHTML = `<pre class="bg-slate-950 p-4 rounded-xl text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-[70vh] overflow-y-auto">${d.content_text}</pre>`;
      }
    } else {
      btnPdf.classList.add('hidden');
      btnPrint.classList.add('hidden');
      body.innerHTML = `<pre class="bg-slate-950 p-5 rounded-xl text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-[70vh] overflow-y-auto">${d.content_text}</pre>`;
    }

    modal.classList.remove('hidden');
  } catch (e) {
    console.error(e);
  }
}

function closeDocPreviewModal() {
  document.getElementById('doc-preview-modal').classList.add('hidden');
}

async function downloadDocPdf(docId) {
  try {
    const res = await fetch(`/api/documents/${docId}`);
    if (!res.ok) return;
    const d = await res.json();
    showToast(`Generating ${d.company} PDF...`);

    const resumeHtml = d.html_text || `<div style="padding:24px; font-family:sans-serif; white-space:pre-wrap; color:#0f172a; background:#ffffff;">${d.content_text}</div>`;
    
    // Create temporary export container attached to document body
    const exportDiv = document.createElement('div');
    exportDiv.id = 'pdf-export-vault-temp';
    exportDiv.innerHTML = resumeHtml;
    exportDiv.style.position = 'fixed';
    exportDiv.style.left = '-9999px';
    exportDiv.style.top = '0';
    exportDiv.style.width = '794px'; // 210mm in pixels at 96 DPI
    exportDiv.style.padding = '32px 36px';
    exportDiv.style.background = '#ffffff';
    exportDiv.style.color = '#0f172a';
    exportDiv.style.zIndex = '-9999';
    document.body.appendChild(exportDiv);

    const filename = `Shreyash_Shukla_Resume_${(d.company || 'Role').replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;

    if (window.html2pdf) {
      try {
        await html2pdf().set({
          margin: [0, 0, 0, 0],
          filename: filename,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        }).from(exportDiv).save();
        showToast('PDF downloaded successfully!');
      } catch (err) {
        console.error('html2pdf generation error:', err);
        printResumeHtml(resumeHtml, d.company);
      } finally {
        if (exportDiv.parentNode) exportDiv.parentNode.removeChild(exportDiv);
      }
    } else {
      if (exportDiv.parentNode) exportDiv.parentNode.removeChild(exportDiv);
      printResumeHtml(resumeHtml, d.company);
    }
  } catch (e) {
    console.error(e);
    showToast('Failed to generate PDF');
  }
}

function downloadModalPdf() {
  if (!activeModalDoc) return;
  downloadDocPdf(activeModalDoc.id);
}

function printModalDoc() {
  if (!activeModalDoc) return;
  const content = document.getElementById('modal-resume-render')?.innerHTML || activeModalDoc.content_text;
  printResumeHtml(content, activeModalDoc.company);
}

function downloadModalTxt() {
  if (!activeModalDoc) return;
  const blob = new Blob([activeModalDoc.content_text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${activeModalDoc.company}_${activeModalDoc.role}.${activeModalDoc.latex_text ? 'tex' : 'txt'}`;
  a.click();
  showToast('Downloaded text file!');
}

function copyModalContent() {
  if (!activeModalDoc) return;
  navigator.clipboard.writeText(activeModalDoc.content_text);
  showToast('Copied document text to clipboard!');
}

async function downloadDoc(docId, ext = 'txt') {
  const res = await fetch(`/api/documents/${docId}`);
  if (res.ok) {
    const d = await res.json();
    const content = (ext === 'tex' && d.latex_text) ? d.latex_text : d.content_text;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${d.company}_${d.role}_${d.doc_type}.${ext}`;
    a.click();
    showToast(`Downloaded .${ext} file!`);
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
    showToast('Candidate profile updated successfully!');
  } catch (e) {
    showToast('Error saving profile');
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
    showToast('AI keys configured successfully!');
    initUser();
  } catch (e) {
    showToast('Error saving keys');
  }
}

function copyToClipboard(id) {
  const el = document.getElementById(id);
  const text = el ? (el.innerText || el.value) : '';
  navigator.clipboard.writeText(text);
  showToast('Copied to clipboard!');
}

function copyInterviewKit() {
  const sysDesign = document.getElementById('prep-page-system-design')?.innerText || document.getElementById('prep-system-design')?.innerText || '';
  const qElements = document.querySelectorAll('#prep-page-questions-list details, #prep-questions-list details');
  const questionsText = Array.from(qElements).map(d => d.innerText).join('\n\n');
  const starElements = document.querySelectorAll('#prep-page-star-stories > div, #prep-star-stories > div');
  const starText = Array.from(starElements).map(d => d.innerText).join('\n\n');
  const revText = document.getElementById('prep-page-reverse-questions')?.innerText || document.getElementById('prep-reverse-questions')?.innerText || '';

  const text = `
=== TECHNICAL INTERVIEW PREPARATION STRATEGY ===

=== SYSTEM DESIGN BLUEPRINT ===
${sysDesign}

=== EXPECTED TECHNICAL QUESTIONS & MODEL ANSWERS ===
${questionsText}

=== PROJECT STAR STORIES ===
${starText}

=== REVERSE QUESTIONS TO ASK ===
${revText}
  `;
  navigator.clipboard.writeText(text.trim());
  showToast('Full interview cheat sheet copied!');
}

// --- Dedicated Interview Prep Suite Engine ---
let currentPrepData = null;

async function loadDedicatedPrepKit(company, role) {
  const comp = company || document.getElementById('prep-target-company')?.value || 'ViralMe';
  const r = role || document.getElementById('prep-target-role')?.value || 'Backend Software Engineer';

  try {
    // 1. Instant deterministic kit from endpoint
    const instantRes = await fetch(`/api/prep/instant?company=${encodeURIComponent(comp)}&role=${encodeURIComponent(r)}`);
    if (instantRes.ok) {
      const prepDoc = await instantRes.json();
      currentPrepData = prepDoc;
      renderDedicatedPrepPage(comp, r, prepDoc);
      showToast(`Interview strategy loaded for ${comp}!`);
      return;
    }
  } catch (e) {
    console.warn('Instant prep endpoint skipped, checking vault...', e);
  }

  try {
    // 2. Try finding existing prep document
    const resDocs = await fetch('/api/documents');
    let prepDoc = null;
    if (resDocs.ok) {
      const docs = await resDocs.json();
      const matched = docs.find(d => d.doc_type === 'interview_prep' && d.company.toLowerCase() === comp.toLowerCase());
      if (matched) {
        try { prepDoc = JSON.parse(matched.content_text); } catch (e) {}
      }
    }

    if (prepDoc) {
      currentPrepData = prepDoc;
      renderDedicatedPrepPage(comp, r, prepDoc);
      showToast(`Interview strategy loaded for ${comp}!`);
    }
  } catch (e) {
    console.error('Error loading prep kit:', e);
    showToast('Failed to load prep kit.');
  }
}

function renderDedicatedPrepPage(company, role, prep) {
  const tagEl = document.getElementById('prep-domain-tag');
  const sysEl = document.getElementById('prep-page-system-design');
  const countEl = document.getElementById('prep-q-count');
  const qList = document.getElementById('prep-page-questions-list');
  const starContainer = document.getElementById('prep-page-star-stories');
  const revList = document.getElementById('prep-page-reverse-questions');

  if (tagEl) tagEl.innerText = `${company} Systems`;
  if (sysEl) sysEl.innerText = prep.system_design || 'System architecture ready.';
  if (countEl) countEl.innerText = `${(prep.questions || []).length} Questions`;

  if (qList) {
    qList.innerHTML = '';
    (prep.questions || []).forEach((item, idx) => {
      qList.innerHTML += `
        <details class="bg-slate-950 p-4 rounded-xl border border-slate-800/80 group">
          <summary class="text-xs font-semibold text-white cursor-pointer list-none flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <span class="text-purple-400 font-mono font-bold shrink-0">Q${idx+1}.</span>
              <span>${item.question}</span>
            </div>
            <i class="fa-solid fa-chevron-down text-slate-500 text-[10px] group-open:rotate-180 transition shrink-0"></i>
          </summary>
          <div class="mt-3 pt-3 border-t border-slate-800/80">
            <span class="text-[10px] font-mono uppercase text-emerald-400 font-bold block mb-1">Ideal Model Answer & Architectural Rationale:</span>
            <p class="text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">${item.answer}</p>
          </div>
        </details>
      `;
    });
  }

  if (starContainer) {
    starContainer.innerHTML = '';
    (prep.star_stories || []).forEach(st => {
      starContainer.innerHTML += `
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
          <div class="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
            <i class="fa-solid fa-star text-[10px]"></i> ${st.title}
          </div>
          <div class="text-[11px] text-slate-400 space-y-1 leading-snug">
            <div><strong class="text-slate-300 font-mono">Action:</strong> ${st.action}</div>
            <div><strong class="text-slate-300 font-mono">Result:</strong> ${st.result}</div>
          </div>
        </div>
      `;
    });
  }

  if (revList) {
    revList.innerHTML = '';
    (prep.reverse_questions || []).forEach(rq => {
      revList.innerHTML += `<li>${rq}</li>`;
    });
  }
}

function setPrepTarget(company, role) {
  const compInput = document.getElementById('prep-target-company');
  const roleInput = document.getElementById('prep-target-role');
  if (compInput) compInput.value = company;
  if (roleInput) roleInput.value = role;
  loadDedicatedPrepKit(company, role);
}

function downloadInterviewKitTxt() {
  if (!currentPrepData) {
    showToast('No prep kit loaded yet.');
    return;
  }
  const comp = document.getElementById('prep-target-company')?.value || 'Tech_Company';
  const text = `
=== ${comp.toUpperCase()} TECHNICAL INTERVIEW STRATEGY SUITE ===
Target: Backend Software Engineer | Candidate: Shreyash Shukla

=== SYSTEM DESIGN BLUEPRINT ===
${currentPrepData.system_design}

=== TECHNICAL QUESTIONS & MODEL ANSWERS ===
${(currentPrepData.questions || []).map((q, i) => `[Q${i+1}] ${q.question}\nANSWER: ${q.answer}\n`).join('\n')}

=== PROJECT STAR STORIES (REAL PRODUCTION IMPACT) ===
${(currentPrepData.star_stories || []).map(s => `[STORY] ${s.title}\nSituation: ${s.situation}\nTask: ${s.task}\nAction: ${s.action}\nResult: ${s.result}\n`).join('\n')}

=== HIGH-LEVERAGE REVERSE QUESTIONS TO ASK ===
${(currentPrepData.reverse_questions || []).map((r, i) => `${i+1}. ${r}`).join('\n')}
  `;

  const blob = new Blob([text.trim()], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${comp}_Interview_Prep_Strategy.txt`;
  a.click();
  showToast('Downloaded cheat sheet .txt');
}

function downloadInterviewKitPdf() {
  if (!currentPrepData) {
    showToast('No prep kit loaded yet.');
    return;
  }
  const comp = document.getElementById('prep-target-company')?.value || 'Tech_Company';
  showToast(`Generating ${comp} Interview Kit PDF...`);

  const div = document.createElement('div');
  div.style.padding = '14mm 16mm';
  div.style.background = '#ffffff';
  div.style.color = '#0f172a';
  div.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  div.style.fontSize = '12px';
  div.style.lineHeight = '1.45';

  let qHtml = (currentPrepData.questions || []).map((q, i) => `
    <div style="margin-bottom: 12px; page-break-inside: avoid;">
      <div style="font-weight: 700; color: #1e3a8a;">Q${i+1}: ${q.question}</div>
      <div style="font-size: 11px; color: #334155; margin-top: 3px;">${q.answer}</div>
    </div>
  `).join('');

  let starHtml = (currentPrepData.star_stories || []).map(s => `
    <div style="margin-bottom: 10px; page-break-inside: avoid; background: #f8fafc; padding: 8px; border-left: 3px solid #10b981;">
      <div style="font-weight: 700; color: #047857;">${s.title}</div>
      <div style="font-size: 11px; color: #334155; margin-top: 2px;"><strong>Action:</strong> ${s.action}</div>
      <div style="font-size: 11px; color: #334155;"><strong>Result:</strong> ${s.result}</div>
    </div>
  `).join('');

  div.innerHTML = `
    <div style="text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 8px; margin-bottom: 14px;">
      <h1 style="font-size: 20pt; margin: 0; color: #1e3a8a;">${comp} Technical Interview Strategy</h1>
      <p style="margin: 4px 0 0; color: #64748b; font-size: 10pt;">Candidate: Shreyash Shukla | Target: Backend Software Engineer</p>
    </div>

    <h2 style="font-size: 13pt; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 2px; margin-top: 14px;">1. System Design Blueprint</h2>
    <pre style="background: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 10px; font-family: monospace; white-space: pre-wrap; line-height: 1.4;">${currentPrepData.system_design}</pre>

    <h2 style="font-size: 13pt; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 2px; margin-top: 14px;">2. Top Technical Questions & Model Answers</h2>
    ${qHtml}

    <h2 style="font-size: 13pt; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 2px; margin-top: 14px;">3. Grounded STAR Project Stories</h2>
    ${starHtml}
  `;

  if (window.html2pdf) {
    html2pdf().set({
      margin: [0, 0, 0, 0],
      filename: `${comp}_Technical_Interview_Kit.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).from(div).save().then(() => {
      showToast('Downloaded Interview Kit PDF!');
    });
  } else {
    showToast('PDF ready.');
  }
}
