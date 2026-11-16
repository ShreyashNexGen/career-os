// CareerOS Client-Side SPA Controller & Strategy Suite

let currentUser = null;
let currentTab = 'pipeline';
let currentDocSubTab = 'visual';
let allRadarJobs = [];
let radarJobsMap = {};
let vaultDocsMap = {};
let activeGeneratedPackage = null;
let allApplicationsMap = {};
let activeDetailAppId = null;

// Attach persisted JWT automatically for workspace switching
const _origFetch = window.fetch.bind(window);
window.fetch = function(input, init = {}) {
  const tok = localStorage.getItem('careeros_token');
  if (tok && typeof input === 'string' && input.startsWith('/api/')) {
    init = Object.assign({}, init);
    init.headers = Object.assign({}, init.headers || {}, { 'Authorization': `Bearer ${tok}` });
  }
  return _origFetch(input, init);
};

document.addEventListener('DOMContentLoaded', async () => {
  await initUser();
  await loadStats();
  await loadApplications();
  await loadMomentum();
  await loadProfile();
  await loadSettings();
  loadRadarJobs();
  calculateSalary();
  loadDedicatedPrepKit('ViralMe', 'Backend Software Engineer');
});

// --- Tab Navigation ---
function switchTab(tabId) {
  currentTab = tabId;
  const tabs = ['pipeline', 'tailor', 'radar', 'dsa', 'sysdesign', 'corecs', 'prep', 'ai-search', 'salary', 'vault', 'profile', 'settings'];
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
  const bnavTabs = ['pipeline', 'radar', 'dsa', 'sysdesign', 'prep'];
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
    radar: 'Job Radar & LinkedIn Fresh-Jobs Sniper',
    dsa: 'Top 200 DSA Pattern Hub (Python & C++)',
    sysdesign: 'System Design Made Easy & Case Studies',
    corecs: 'Backend Core CS Rapid-Fire Sheet',
    prep: 'Technical Interview Strategy & Grill Suite',
    salary: 'Salary Benchmark & ESOP Calculator',
    vault: 'Document & CV Archive Vault',
    profile: 'Candidate Master Profile',
    settings: 'Free AI Engine & DB Settings'
  };
  const subtitles = {
    pipeline: 'Compact Kanban, full JD details, and 3-day follow-up tracker',
    tailor: 'Generate tailored ATS resumes, cover letters, outreach DMs, and interview prep',
    radar: 'Live Greenhouse ATS boards, curated Indian startups & 1-click LinkedIn sniper',
    dsa: '15 core patterns, 30-second recognition tricks, Python/C++ solutions & AI Tutor',
    sysdesign: 'Visual building blocks + 8 HLD/LLD case studies with AI Staff review',
    corecs: 'SQL Window functions, DBMS MVCC/ACID, OS locks & HTTP/JWT internals',
    prep: 'Mock Interview Grill Mode, domain blueprints, technical Q&As & STAR stories',
    salary: 'Expected market CTC, stock options, and word-for-word negotiation scripts',
    vault: 'Historical vault of all generated documents and LaTeX sources',
    'ai-search': 'Full-capability AI Copilot with multi-turn chat history • ₹1L+/mo Remote Focus',
    profile: 'Single source of truth used by the AI tailoring engine',
    settings: 'Groq / Gemini AI keys & persistent Supabase setup guide'
  };

  document.getElementById('page-title').innerText = titles[tabId] || (tabId === 'ai-search' ? 'Universal AI Assistant' : 'CareerOS');
  document.getElementById('page-subtitle').innerText = subtitles[tabId] || '';

  if (tabId === 'pipeline') loadApplications();
  if (tabId === 'vault') loadVaultDocuments();
  if (tabId === 'prep' && !currentPrepData) loadDedicatedPrepKit();
  if (tabId === 'dsa' && allDsaProblems.length === 0) loadDsaHub();
  if (tabId === 'sysdesign' && !sysDesignLoaded) loadSysDesignHub();
  if (tabId === 'corecs' && coreCsTopics.length === 0) loadCoreCsHub();
  if (tabId === 'ai-search') loadAiChatSessions();
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
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('careeros_token', data.access_token);
      location.reload();
    }
  } else if (choice === "1") {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email: 'shreyashshukla7398554573@gmail.com', password: 'admin123' })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('careeros_token', data.access_token);
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

    Object.values(cols).forEach(c => { if (c) c.innerHTML = ''; });
    const counts = { discovered: 0, drafted: 0, applied: 0, interview: 0, offer: 0 };
    allApplicationsMap = {};
    const followUpDue = [];

    apps.forEach(app => {
      allApplicationsMap[app.id] = app;
      const statusKey = (app.status === 'hired') ? 'offer' : (cols[app.status] ? app.status : 'discovered');
      counts[statusKey] = (counts[statusKey] || 0) + 1;
      
      const fitBadgeClass = app.fit_score >= 85 
        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
        : (app.fit_score >= 70 ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30');

      const createdDate = new Date(app.created_at);
      const diffDays = Math.floor((new Date() - createdDate) / (1000 * 60 * 60 * 24));
      const daysText = diffDays === 0 ? "Today" : `${diffDays}d ago`;
      const showFollowUpBadge = (app.status === 'applied' && diffDays >= 3);
      if (showFollowUpBadge) followUpDue.push({ app, diffDays });

      const card = document.createElement('div');
      card.className = 'glass-card rounded-xl p-2.5 space-y-2 border border-slate-700/60 hover:border-blue-500/60 hover:shadow-lg hover:shadow-blue-500/10 transition-all cursor-pointer';
      card.onclick = (e) => {
        if (e.target.closest('select') || e.target.closest('button') || e.target.closest('a')) return;
        openAppDetailModal(app.id);
      };
      
      card.innerHTML = `
        <div class="flex items-center justify-between gap-1.5">
          <div class="flex items-center gap-1.5 min-w-0">
            <span class="w-5 h-5 rounded-md bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-[10px] uppercase shrink-0">
              ${(app.company || 'C')[0]}
            </span>
            <div class="font-bold text-white text-xs truncate">${app.company}</div>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded-full border ${fitBadgeClass} font-bold shrink-0">
            ${app.fit_score}%
          </span>
        </div>

        <div class="flex items-center justify-between gap-2 text-[11px]">
          <span class="font-medium text-slate-300 truncate">${app.role}</span>
          <span class="text-[9px] text-slate-500 font-mono shrink-0">${daysText}</span>
        </div>

        ${showFollowUpBadge ? '<div class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold inline-block">3d+ Follow-Up Due</div>' : ''}

        <div class="pt-1.5 border-t border-slate-800/70 flex items-center justify-between text-[10px] gap-1">
          <select onchange="handleStatusChange(${app.id}, this.value)" class="bg-slate-950 border border-slate-800 text-[10px] text-slate-300 rounded-lg px-1.5 py-1 focus:outline-none focus:border-blue-500 transition min-w-0 max-w-[92px]">
            <option value="discovered" ${app.status === 'discovered' ? 'selected' : ''}>Discovered</option>
            <option value="drafted" ${app.status === 'drafted' ? 'selected' : ''}>Drafted</option>
            <option value="applied" ${app.status === 'applied' ? 'selected' : ''}>Applied</option>
            <option value="interview" ${app.status === 'interview' ? 'selected' : ''}>Interview</option>
            <option value="offer" ${app.status === 'offer' ? 'selected' : ''}>Offer</option>
            <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>Rejected</option>
          </select>
          
          <div class="flex items-center gap-1 shrink-0">
            <button onclick="openAppDetailModal(${app.id})" title="View Full JD & Notes" class="text-sky-400 hover:text-sky-300 text-[11px] p-1 rounded bg-sky-950/40 border border-sky-500/30 transition">
              <i class="fa-solid fa-expand"></i>
            </button>
            <button onclick="openInterviewModalById(${app.id})" title="Interview Prep Kit" class="text-purple-400 hover:text-purple-300 text-[11px] p-1 rounded bg-purple-950/50 border border-purple-500/30 transition">
              <i class="fa-solid fa-brain"></i>
            </button>
            <button onclick="deleteApp(${app.id})" title="Remove" class="text-slate-500 hover:text-rose-400 text-[11px] p-1 rounded transition">
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
          <div class="h-36 border-2 border-dashed border-slate-800/80 rounded-xl flex flex-col items-center justify-center p-4 text-center select-none my-auto">
            <i class="fa-regular fa-folder-open text-slate-700 text-lg mb-1.5"></i>
            <span class="text-[11px] text-slate-500 font-medium">No roles in this stage</span>
            <span class="text-[10px] text-slate-600 mt-0.5">Move or add jobs here</span>
          </div>
        `;
      }
      const countEl = document.getElementById(`col-count-${k}`);
      if (countEl) countEl.innerText = counts[k];
    });

    // Update 3-Day Follow-Up Banner
    const fuBanner = document.getElementById('followup-queue-banner');
    if (fuBanner) {
      if (followUpDue.length > 0) {
        fuBanner.classList.remove('hidden');
        document.getElementById('followup-queue-count').innerText = `${followUpDue.length} Due`;
        document.getElementById('followup-queue-names').innerText =
          `Ready for polite Day 3+ bump: ${followUpDue.map(x => `${x.app.company} (${x.diffDays}d)`).join(', ')}`;
        document.getElementById('followup-queue-actions').innerHTML = followUpDue.slice(0, 3).map(x => `
          <button onclick="copyFollowUpByAppId(${x.app.id})" class="px-2.5 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-[11px] font-semibold transition">
            <i class="fa-regular fa-copy"></i> DM ${x.app.company}
          </button>
        `).join('');
      } else {
        fuBanner.classList.add('hidden');
      }
    }

    loadStats();
    loadMomentum();
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
  exportDiv.style.left = '0';
  exportDiv.style.top = '0';
  exportDiv.style.width = '794px'; // 210mm in pixels at 96 DPI
  exportDiv.style.maxHeight = '1120px'; // Exact 1-Page A4 height bound
  exportDiv.style.overflow = 'hidden';
  exportDiv.style.boxSizing = 'border-box';
  exportDiv.style.padding = '18px 24px';
  exportDiv.style.background = '#ffffff';
  exportDiv.style.color = '#0f172a';
  exportDiv.style.zIndex = '-9999';
  exportDiv.style.opacity = '1';
  exportDiv.style.pointerEvents = 'none';
  document.body.appendChild(exportDiv);

  const opt = {
    margin: [0, 0, 0, 0],
    filename: filename,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true, letterRendering: true, scrollY: 0, backgroundColor: '#ffffff' },
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

// --- Job Radar (Multi-ATS + Sniper + Pagination) ---
let radarCurrentPage = 1;
const radarPageSize = 24;
let currentFilteredRadarJobs = [];

function launchLinkedInSniper() {
  const role = document.getElementById('sniper-role')?.value || 'Remote Contract Backend Engineer Node.js Python';
  const loc = document.getElementById('sniper-loc')?.value || 'Remote';
  const workType = document.getElementById('sniper-work-type')?.value || 'contract';
  const time = document.getElementById('sniper-time')?.value || 'r86400';
  const easy = document.getElementById('sniper-easy-apply')?.checked ?? true;
  const under10 = (document.getElementById('sniper-under-10')?.checked || document.getElementById('sniper-early')?.checked) ?? true;

  let url = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(role)}&location=${encodeURIComponent(loc)}&sortBy=DD`;
  if (time && time !== 'all') {
    url += `&f_TPR=${time}`;
  }
  if (workType === 'contract') {
    url += '&f_JT=C%2CF&f_WRA=true';
  } else if (workType === 'part_time') {
    url += '&f_JT=P&f_WRA=true';
  } else if (workType === 'full_time') {
    url += '&f_JT=F&f_WRA=true';
  }
  if (loc === 'Remote') {
    url += '&f_WT=2'; // 100% Remote filter code
  }
  if (easy) {
    url += '&f_LF=f_AL';
  }
  if (under10) {
    url += '&f_EA=true';
  }
  window.open(url, '_blank');
  showToast(`Launched LinkedIn Live Sniper for ${role}!`);
}

function setRadarWorkTypeQuickFilter(wt) {
  const sel = document.getElementById('radar-filter-work-type');
  if (sel) sel.value = wt;

  ['remote-contract', 'part-time', 'remote-all', 'direct-ats', 'all'].forEach(k => {
    const p = document.getElementById(`pill-wt-${k}`);
    if (!p) return;
    const match = (k === 'remote-contract' && wt === 'remote_contract') ||
                  (k === 'part-time' && wt === 'part_time') ||
                  (k === 'remote-all' && wt === 'remote_all') ||
                  (k === 'direct-ats' && wt === 'direct_ats') ||
                  (k === 'all' && wt === 'all');
    if (match) {
      p.className = 'px-3 py-1 rounded-xl bg-emerald-600 text-white border border-emerald-500 text-xs font-bold shrink-0 transition flex items-center gap-1.5 shadow-md shadow-emerald-600/30';
    } else {
      p.className = 'px-3 py-1 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium shrink-0 transition flex items-center gap-1.5';
    }
  });

  applyRadarFilters();
}

async function loadRadarJobs() {
  const grid = document.getElementById('radar-jobs-grid');
  grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-16 text-xs font-mono text-slate-400"><i class="fa-solid fa-spinner animate-spin text-emerald-400 text-xl mb-2 block"></i> Scanning live Greenhouse, Ashby & Lever ATS endpoints + verified tech hubs...</div>';

  try {
    const res = await fetch('/api/radar/jobs?query=all&limit=250');
    if (!res.ok) throw new Error();
    const data = await res.json();
    allRadarJobs = Array.isArray(data) ? data : (data.jobs || []);
    radarCurrentPage = 1;
    applyRadarFilters();
  } catch (e) {
    grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-12 text-xs text-rose-400">Error loading radar jobs.</div>';
  }
}

function applyRadarFilters() {
  const query = (document.getElementById('radar-search')?.value || '').trim().toLowerCase();
  const workType = (document.getElementById('radar-filter-work-type')?.value || 'all').toLowerCase();
  const sourceFilter = (document.getElementById('radar-filter-source')?.value || 'all').toLowerCase();
  const compType = (document.getElementById('radar-filter-company')?.value || 'all').toLowerCase();
  const salRange = (document.getElementById('radar-filter-salary')?.value || 'all').toLowerCase();
  const loc = (document.getElementById('radar-filter-loc')?.value || 'all').toLowerCase();
  const role = (document.getElementById('radar-filter-role')?.value || 'all').toLowerCase();
  const sort = document.getElementById('radar-filter-sort')?.value || 'score';

  currentFilteredRadarJobs = allRadarJobs.filter(j => {
    // Work Type filter (remote_contract, part_time, remote_all, direct_ats)
    if (workType !== 'all') {
      const wt = (j.work_type || '').toLowerCase();
      const titleL = (j.title || '').toLowerCase();
      const badgeL = (j.source_badge || '').toLowerCase();
      const locL = (j.location || '').toLowerCase();
      const salL = (j.salary || '').toLowerCase();

      if (workType === 'remote_contract') {
        const isRc = wt === 'remote_contract' || titleL.includes('contract') || badgeL.includes('contract') ||
                     (locL.includes('remote') && (titleL.includes('contract') || salL.includes('$') || salL.includes('mo')));
        if (!isRc) return false;
      } else if (workType === 'part_time') {
        const isPt = wt === 'part_time' || titleL.includes('part') || badgeL.includes('part-time');
        if (!isPt) return false;
      } else if (workType === 'remote_all') {
        const isRem = locL.includes('remote') || locL.includes('worldwide') || locL.includes('global') || wt === 'remote_contract' || wt === 'part_time';
        if (!isRem) return false;
      } else if (workType === 'direct_ats') {
        if (!j.is_direct) return false;
      }
    }

    // Direct ATS vs Portal source filter
    if (sourceFilter !== 'all') {
      if (sourceFilter === 'direct_ats' && !j.is_direct) return false;
      if (sourceFilter === 'portal' && j.is_direct) return false;
    }

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
      if (loc === 'bengaluru' && !jLoc.includes('bengaluru') && !jLoc.includes('bangalore')) return false;
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
    currentFilteredRadarJobs.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
  } else if (sort === 'direct') {
    currentFilteredRadarJobs.sort((a, b) => (b.is_direct ? 1 : 0) - (a.is_direct ? 1 : 0) || (b.match_score || 0) - (a.match_score || 0));
  } else if (sort === 'company') {
    currentFilteredRadarJobs.sort((a, b) => (a.company || '').localeCompare(b.company || ''));
  }

  // Update badge count
  const countBadge = document.getElementById('radar-count-badge');
  if (countBadge) countBadge.innerText = `${currentFilteredRadarJobs.length} Active Jobs`;

  renderRadarPaginated();
}

function changeRadarPage(delta) {
  const totalPages = Math.max(1, Math.ceil(currentFilteredRadarJobs.length / radarPageSize));
  const newPage = radarCurrentPage + delta;
  if (newPage >= 1 && newPage <= totalPages) {
    radarCurrentPage = newPage;
    renderRadarPaginated();
    const grid = document.getElementById('radar-jobs-grid');
    if (grid) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function renderRadarPaginated() {
  const total = currentFilteredRadarJobs.length;
  const totalPages = Math.max(1, Math.ceil(total / radarPageSize));
  if (radarCurrentPage > totalPages) radarCurrentPage = totalPages;
  if (radarCurrentPage < 1) radarCurrentPage = 1;

  const start = (radarCurrentPage - 1) * radarPageSize;
  const pageSlice = currentFilteredRadarJobs.slice(start, start + radarPageSize);

  // Update pagination info
  const infoEl = document.getElementById('radar-page-info');
  if (infoEl) {
    infoEl.innerText = total === 0 ? 'Showing 0 jobs' : `Showing jobs ${start + 1}-${Math.min(start + radarPageSize, total)} of ${total} verified`;
  }
  const pillEl = document.getElementById('radar-cur-page-pill');
  if (pillEl) {
    pillEl.innerText = `Page ${radarCurrentPage} / ${totalPages}`;
  }
  const btnPrev = document.getElementById('btn-radar-prev');
  if (btnPrev) btnPrev.disabled = (radarCurrentPage <= 1);
  const btnNext = document.getElementById('btn-radar-next');
  if (btnNext) btnNext.disabled = (radarCurrentPage >= totalPages);

  renderRadarGrid(pageSlice);
}

function renderRadarGrid(jobs) {
  const grid = document.getElementById('radar-jobs-grid');
  grid.innerHTML = '';

  if (jobs.length === 0) {
    grid.innerHTML = '<div class="col-span-1 md:col-span-3 text-center py-16 text-slate-500 text-xs">No matching jobs found with current filters. Try resetting search!</div>';
    return;
  }

  jobs.forEach(job => {
    radarJobsMap[String(job.id)] = job;
    const card = document.createElement('div');
    card.className = 'glass-card rounded-2xl p-5 flex flex-col justify-between hover:border-emerald-500/50 hover:shadow-lg hover:shadow-emerald-500/10 transition-all';
    
    const tagsHtml = (job.tags || []).slice(0, 4).map(t => `<span class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300 border border-slate-700/60">${t}</span>`).join('');

    const compTypeBadge = job.company_type === 'startup' ? '<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 font-bold uppercase">Startup</span>' :
                          (job.company_type === 'mnc' ? '<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 font-bold uppercase">Tier-1 MNC</span>' :
                          '<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 font-bold uppercase">Cloud/DevTools</span>');

    let sourceBadge = '';
    const badgeText = job.source_badge || '';
    if (badgeText.includes('Remote Contract') || (job.tags && job.tags.includes('Remote Contract'))) {
      sourceBadge = '<span class="text-[9px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/25 text-emerald-300 border border-emerald-500/50 font-bold flex items-center gap-1 shrink-0"><i class="fa-solid fa-fire text-amber-400"></i> Remote Contract • ₹1L+/mo</span>';
    } else if (badgeText.includes('Part-Time') || (job.tags && job.tags.includes('Part-Time Remote'))) {
      sourceBadge = '<span class="text-[9px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold flex items-center gap-1 shrink-0"><i class="fa-solid fa-clock text-cyan-400"></i> Part-Time Remote</span>';
    } else if (job.is_direct) {
      sourceBadge = '<span class="text-[9px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold flex items-center gap-1 shrink-0"><i class="fa-solid fa-bolt text-emerald-400"></i> Direct ATS Form</span>';
    } else {
      sourceBadge = '<span class="text-[9px] font-mono px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30 font-medium shrink-0">Official Portal</span>';
    }

    const jobUrl = job.url || `https://www.google.com/search?q=${encodeURIComponent(job.company + ' careers')}`;

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between gap-2 mb-2.5">
          <div class="flex items-center gap-1.5">
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">${job.match_score}% Match</span>
            ${compTypeBadge}
          </div>
          ${sourceBadge}
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
          <a href="${jobUrl}" target="_blank" class="px-2.5 py-1.5 rounded-xl ${job.is_direct ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm' : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'} text-[11px] font-semibold transition flex items-center gap-1.5" title="${job.is_direct ? 'Direct to Official ATS Submission Form' : 'Direct to Official Career Portal'}">
            ${job.is_direct ? '<i class="fa-solid fa-bolt text-amber-300"></i> 1-Click Form' : '<i class="fa-solid fa-arrow-up-right-from-square text-sky-400"></i> Portal'}
          </a>
          <button onclick="tailorFromRadarById('${encodeURIComponent(String(job.id))}')" class="px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-semibold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-300"></i> Tailor Pack
          </button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function tailorFromRadarById(encodedId) {
  const job = radarJobsMap[decodeURIComponent(encodedId)];
  if (!job) return;
  tailorFromRadar(job);
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
function openInterviewModalById(appId) {
  const app = allApplicationsMap[appId];
  const company = app ? app.company : 'Target Company';
  const role = app ? app.role : 'Software Engineer';
  return openInterviewModal(appId, company, role);
}

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
      vaultDocsMap[d.id] = d;
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
    let d = vaultDocsMap[docId];
    if (!d) {
      const res = await fetch(`/api/documents/${docId}`);
      if (!res.ok) return;
      d = await res.json();
      vaultDocsMap[docId] = d;
    }
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
    exportDiv.style.left = '0';
    exportDiv.style.top = '0';
    exportDiv.style.width = '794px'; // 210mm in pixels at 96 DPI
    exportDiv.style.maxHeight = '1120px'; // Strict 1-Page A4 height
    exportDiv.style.overflow = 'hidden';
    exportDiv.style.boxSizing = 'border-box';
    exportDiv.style.padding = '18px 24px';
    exportDiv.style.background = '#ffffff';
    exportDiv.style.color = '#0f172a';
    exportDiv.style.zIndex = '-9999';
    exportDiv.style.opacity = '1';
    exportDiv.style.pointerEvents = 'none';
    document.body.appendChild(exportDiv);

    const filename = `Shreyash_Shukla_Resume_${(d.company || 'Role').replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;

    if (window.html2pdf) {
      try {
        await html2pdf().set({
          margin: [0, 0, 0, 0],
          filename: filename,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true, scrollY: 0, backgroundColor: '#ffffff' },
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
  a.download = `${activeModalDoc.company}_${activeModalDoc.role}.txt`;
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
    div.style.position = 'fixed';
    div.style.left = '-9999px';
    div.style.top = '0';
    div.style.width = '794px';
    document.body.appendChild(div);
    html2pdf().set({
      margin: [0, 0, 0, 0],
      filename: `${comp}_Technical_Interview_Kit.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).from(div).save().then(() => {
      showToast('Downloaded Interview Kit PDF!');
    }).finally(() => {
      if (div.parentNode) div.parentNode.removeChild(div);
    });
  } else {
    showToast('PDF ready.');
  }
}

// ==========================================
// MOBILE KANBAN SWITCHER & APPLICATION DETAILS
// ==========================================
function setMobileKanbanStage(stage) {
  const stages = ['discovered', 'drafted', 'applied', 'interview', 'offer'];
  stages.forEach(s => {
    const wrap = document.getElementById(`kanban-wrap-${s}`);
    if (wrap) {
      if (stage === 'all' || stage === s) wrap.classList.remove('hidden');
      else wrap.classList.add('hidden');
    }
    const pill = document.getElementById(`mstage-${s}`);
    if (pill) {
      pill.className = (stage === s)
        ? 'px-3 py-1.5 rounded-full bg-blue-600 text-white text-[11px] font-semibold shrink-0 transition'
        : 'px-3 py-1.5 rounded-full bg-slate-900 text-slate-300 border border-slate-800 text-[11px] font-medium shrink-0 transition';
    }
  });
  const allPill = document.getElementById('mstage-all');
  if (allPill) {
    allPill.className = (stage === 'all')
      ? 'px-3 py-1.5 rounded-full bg-blue-600 text-white text-[11px] font-semibold shrink-0 transition'
      : 'px-3 py-1.5 rounded-full bg-slate-900 text-slate-300 border border-slate-800 text-[11px] font-medium shrink-0 transition';
  }
}

function openAppDetailModal(appId) {
  const app = allApplicationsMap[appId];
  if (!app) return;
  activeDetailAppId = appId;

  document.getElementById('ad-fit-badge').innerText = `${app.fit_score}% Match`;
  document.getElementById('ad-company-title').innerText = `${app.company} — ${app.role}`;
  const created = new Date(app.created_at).toLocaleDateString();
  document.getElementById('ad-meta').innerText = `Stage: ${(app.status || 'discovered').toUpperCase()} • Added: ${created}`;

  const linkEl = document.getElementById('ad-open-link');
  if (app.job_url) {
    linkEl.href = app.job_url;
    linkEl.classList.remove('hidden');
  } else {
    linkEl.href = `https://www.google.com/search?q=${encodeURIComponent(app.company + ' careers')}`;
  }

  document.getElementById('ad-jd-box').innerText = app.jd_text || app.notes || 'No full JD saved yet. Use Tailor or Quick Import to attach the full description.';
  document.getElementById('ad-notes-input').value = app.notes || '';
  document.getElementById('ad-screen-q').value = '';
  document.getElementById('ad-screen-ans-wrap').classList.add('hidden');
  document.getElementById('app-detail-modal').classList.remove('hidden');
}

function closeAppDetailModal() {
  document.getElementById('app-detail-modal').classList.add('hidden');
  activeDetailAppId = null;
}

async function saveAppDetailNotes() {
  if (!activeDetailAppId) return;
  const notes = document.getElementById('ad-notes-input').value;
  try {
    const res = await fetch(`/api/applications/${activeDetailAppId}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ notes })
    });
    if (res.ok) {
      showToast('Application notes saved!');
      loadApplications();
    }
  } catch (e) {
    showToast('Error saving notes');
  }
}

function copyFollowUpByAppId(appId) {
  const app = allApplicationsMap[appId];
  if (!app) return;
  copyFollowUpTemplate(app.company, app.role);
}

function copyFollowUpTemplate(company, role) {
  const msg = `Hi [Hiring Manager/Recruiter],\n\nFollowing up politely on my application for the ${role} role at ${company}. With 2+ years building 250+ RESTful APIs in Node.js & Python and cutting SQL transaction latency by 35% via composite indexing, I'd love a brief chat on how I can contribute immediately to your backend systems.\n\nBest,\nShreyash Shukla\nhttps://linkedin.com/in/shuklashreyash`;
  navigator.clipboard.writeText(msg);
  showToast(`Copied 3-Day Follow-Up DM for ${company}!`);
}

function copyAppFollowUpDm() {
  const app = allApplicationsMap[activeDetailAppId];
  if (!app) return;
  copyFollowUpTemplate(app.company, app.role);
}

async function generateAppScreeningAnswer() {
  const app = allApplicationsMap[activeDetailAppId];
  const question = document.getElementById('ad-screen-q').value.trim();
  if (!app || !question) {
    showToast('Enter a screening question first.');
    return;
  }
  const btn = document.getElementById('btn-ad-screen');
  btn.disabled = true; btn.innerText = 'Thinking...';
  try {
    const res = await fetch('/api/ai/screening-answer', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        company: app.company,
        role: app.role,
        question,
        jd_text: app.jd_text || app.notes || ''
      })
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById('ad-screen-ans').innerText = data.answer;
      document.getElementById('ad-screen-ans-wrap').classList.remove('hidden');
      showToast(`Generated via ${data.provider}!`);
    }
  } catch (e) {
    showToast('Failed to generate screening answer');
  } finally {
    btn.disabled = false; btn.innerText = 'Generate Answer';
  }
}

// ==========================================
// DAILY MOMENTUM TRACKER
// ==========================================
function applyMomentumData(m) {
  const aEl = document.getElementById('mom-apps');
  const dEl = document.getElementById('mom-dsa');
  const sEl = document.getElementById('mom-design');
  if (aEl) aEl.innerText = `${m.apps_count}/3`;
  if (dEl) dEl.innerText = `${m.dsa_count}/2`;
  if (sEl) sEl.innerText = `${m.design_count}/1`;
}

async function loadMomentum() {
  try {
    const res = await fetch('/api/momentum');
    if (!res.ok) return;
    const m = await res.json();
    applyMomentumData(m);
  } catch (e) {}
}

async function bumpMomentum(metric) {
  try {
    const res = await fetch('/api/momentum', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ metric, delta: 1 })
    });
    if (res.ok) {
      const m = await res.json();
      applyMomentumData(m);
      showToast(`Momentum logged (+1 ${metric.toUpperCase()})!`);
    }
  } catch (e) {}
}

// ==========================================
// LINKEDIN SNIPER & QUICK JD IMPORT
// ==========================================
function toggleRadarMobileFilters() {
  const panel = document.getElementById('radar-filters-panel');
  if (panel) panel.classList.toggle('hidden');
}

function launchLinkedInSniper() {
  const keywords = document.getElementById('sniper-role')?.value || 'Backend Engineer Node.js Python';
  const loc = document.getElementById('sniper-loc')?.value || 'India';
  const tpr = document.getElementById('sniper-time')?.value || 'r86400';
  const easy = document.getElementById('sniper-easy-apply')?.checked;
  const early = document.getElementById('sniper-early')?.checked;

  let url = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(keywords)}&location=${encodeURIComponent(loc)}&f_TPR=${encodeURIComponent(tpr)}&sortBy=DD`;
  if (easy) url += '&f_AL=true';
  if (early) url += '&f_EA=true';

  window.open(url, '_blank');
  showToast('Opened LinkedIn Fresh-Jobs Sniper!');
}

function openQuickImportModal() {
  document.getElementById('quick-import-modal').classList.remove('hidden');
}

function closeQuickImportModal() {
  document.getElementById('quick-import-modal').classList.add('hidden');
}

async function saveQuickImportToKanban() {
  const company = document.getElementById('qi-company').value.trim() || 'LinkedIn Lead';
  const role = document.getElementById('qi-role').value.trim() || 'Backend Software Engineer';
  const job_url = document.getElementById('qi-url').value.trim();
  const jd_text = document.getElementById('qi-jd').value.trim();

  try {
    const res = await fetch('/api/applications', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        company,
        role,
        status: 'discovered',
        fit_score: 88,
        job_url: job_url || null,
        jd_text: jd_text || null,
        notes: 'Imported from LinkedIn / External Board'
      })
    });
    if (res.ok) {
      closeQuickImportModal();
      showToast(`Saved ${company} to Pipeline!`);
      loadApplications();
      switchTab('pipeline');
    }
  } catch (e) {
    showToast('Error importing application');
  }
}

function tailorQuickImport() {
  const company = document.getElementById('qi-company').value.trim() || 'Target Company';
  const role = document.getElementById('qi-role').value.trim() || 'Backend Software Engineer';
  const url = document.getElementById('qi-url').value.trim();
  const jd = document.getElementById('qi-jd').value.trim();

  document.getElementById('tailor-company').value = company;
  document.getElementById('tailor-role').value = role;
  document.getElementById('tailor-jd').value = (url ? `URL: ${url}\n\n` : '') + jd;
  closeQuickImportModal();
  switchTab('tailor');
}

// ==========================================
// TOP 200 DSA HUB (PYTHON & C++ + AI TUTOR)
// ==========================================
let allDsaProblems = [];
let dsaPatterns = [];
let activeDsaProblem = null;
let activeDsaLang = 'python';

async function loadDsaHub() {
  try {
    const res = await fetch('/api/dsa');
    if (!res.ok) return;
    const data = await res.json();
    allDsaProblems = data.problems || [];
    dsaPatterns = data.patterns || [];

    const patSelect = document.getElementById('dsa-filter-pattern');
    if (patSelect && patSelect.options.length <= 1) {
      dsaPatterns.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p;
        opt.innerText = p;
        patSelect.appendChild(opt);
      });
    }

    updateDsaProgressHeader(data.stats);
    applyDsaFilters();
  } catch (e) {
    console.error('Error loading DSA Hub:', e);
  }
}

function updateDsaProgressHeader(stats) {
  const solved = stats ? stats.solved : allDsaProblems.filter(p => p.status === 'solved').length;
  const revisit = stats ? stats.revisit : allDsaProblems.filter(p => p.status === 'revisit').length;
  const total = allDsaProblems.length || 200;

  const sEl = document.getElementById('dsa-solved-count');
  const rEl = document.getElementById('dsa-revisit-count');
  const barEl = document.getElementById('dsa-progress-bar');
  if (sEl) sEl.innerText = solved;
  if (rEl) rEl.innerText = revisit;
  if (barEl) barEl.style.width = `${Math.round((solved / total) * 100)}%`;
}

function filterDsaRevision() {
  document.getElementById('dsa-filter-status').value = 'revisit';
  applyDsaFilters();
}

function applyDsaFilters() {
  const q = (document.getElementById('dsa-search')?.value || '').trim().toLowerCase();
  const pat = document.getElementById('dsa-filter-pattern')?.value || 'all';
  const diff = document.getElementById('dsa-filter-diff')?.value || 'all';
  const st = document.getElementById('dsa-filter-status')?.value || 'all';

  const filtered = allDsaProblems.filter(p => {
    if (pat !== 'all' && p.pattern !== pat) return false;
    if (diff !== 'all' && p.difficulty !== diff) return false;
    if (st !== 'all' && p.status !== st) return false;
    if (q) {
      const hay = `${p.num} ${p.title} ${p.pattern} ${p.trick} ${(p.companies || []).join(' ')}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  renderDsaList(filtered);
}

function renderDsaList(list) {
  const container = document.getElementById('dsa-problems-list');
  if (!container) return;
  container.innerHTML = '';

  if (list.length === 0) {
    container.innerHTML = '<div class="p-8 text-center text-xs text-slate-500">No DSA problems match your filters. Try clearing filters!</div>';
    return;
  }

  list.forEach(p => {
    const diffCls = p.difficulty === 'Easy' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
      : (p.difficulty === 'Medium' ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' : 'text-rose-400 bg-rose-500/10 border-rose-500/20');
    const stBadge = p.status === 'solved'
      ? '<span class="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">Solved ✓</span>'
      : (p.status === 'revisit'
        ? '<span class="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[10px] font-bold">Revise ↻</span>'
        : '<span class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">Todo</span>');

    const row = document.createElement('div');
    row.className = 'p-3.5 sm:px-5 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:bg-slate-800/40 cursor-pointer transition';
    row.onclick = () => openDsaModal(p.id);
    row.innerHTML = `
      <div class="min-w-0 flex-1 space-y-1">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-[11px] font-mono text-slate-500 font-bold">#${p.num}</span>
          <span class="text-xs sm:text-sm font-bold text-white hover:text-cyan-300 transition">${p.title}</span>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded border ${diffCls}">${p.difficulty}</span>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-cyan-300 border border-slate-800">${p.pattern}</span>
        </div>
        <p class="text-[11px] text-slate-400 line-clamp-1"><strong class="text-amber-300/90">Trick:</strong> ${p.trick}</p>
      </div>
      <div class="flex items-center justify-between sm:justify-end gap-2 shrink-0">
        <div class="flex items-center gap-1">
          ${(p.companies || []).slice(0, 2).map(c => `<span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">${c}</span>`).join('')}
        </div>
        ${stBadge}
      </div>
    `;
    container.appendChild(row);
  });
}

function openDsaModal(problemId) {
  const p = allDsaProblems.find(x => x.id === problemId);
  if (!p) return;
  activeDsaProblem = p;

  document.getElementById('dsa-m-num').innerText = `#${p.num}`;
  document.getElementById('dsa-m-diff').innerText = p.difficulty;
  document.getElementById('dsa-m-comp').innerText = p.complexity;
  document.getElementById('dsa-m-title').innerText = p.title;
  document.getElementById('dsa-m-pattern').innerText = p.pattern;
  document.getElementById('dsa-m-lc').href = p.leetcode_url || `https://leetcode.com/problemset/all/?search=${encodeURIComponent(p.title)}`;
  const gfgEl = document.getElementById('dsa-m-gfg');
  if (gfgEl) {
    gfgEl.href = p.gfg_url || `https://www.geeksforgeeks.org/explore?page=1&search=${encodeURIComponent(p.title)}`;
  }
  document.getElementById('dsa-m-trick').innerText = p.trick;
  document.getElementById('dsa-m-intuition').innerText = p.intuition;
  const compEl = document.getElementById('dsa-m-complexity-text');
  if (compEl) compEl.innerText = p.complexity;
  document.getElementById('dsa-m-notes').value = p.notes || '';
  document.getElementById('dsa-ai-input').value = '';
  document.getElementById('dsa-ai-output').classList.add('hidden');

  // Answers are NOT shown directly - collapse solution until explicitly revealed
  const solContainer = document.getElementById('dsa-solution-container');
  const txtToggle = document.getElementById('text-dsa-sol');
  const iconToggle = document.getElementById('icon-dsa-sol');
  if (solContainer) solContainer.classList.add('hidden');
  if (txtToggle) txtToggle.innerText = 'Reveal Solution & Code (Python 3 & C++17)';
  if (iconToggle) iconToggle.className = 'fa-solid fa-eye';

  highlightDsaStatusButtons(p.status);
  switchDsaLang(activeDsaLang);
  document.getElementById('dsa-study-modal').classList.remove('hidden');
}

function toggleDsaSolution() {
  const solContainer = document.getElementById('dsa-solution-container');
  const txtToggle = document.getElementById('text-dsa-sol');
  const iconToggle = document.getElementById('icon-dsa-sol');
  if (!solContainer) return;
  const isHidden = solContainer.classList.contains('hidden');
  if (isHidden) {
    solContainer.classList.remove('hidden');
    if (txtToggle) txtToggle.innerText = 'Hide Solution Code';
    if (iconToggle) iconToggle.className = 'fa-solid fa-eye-slash';
  } else {
    solContainer.classList.add('hidden');
    if (txtToggle) txtToggle.innerText = 'Reveal Solution & Code (Python 3 & C++17)';
    if (iconToggle) iconToggle.className = 'fa-solid fa-eye';
  }
}

function closeDsaModal() {
  document.getElementById('dsa-study-modal').classList.add('hidden');
}

function switchDsaLang(lang) {
  activeDsaLang = lang;
  if (!activeDsaProblem) return;
  const codeEl = document.getElementById('dsa-m-code');
  const pyBtn = document.getElementById('dsa-lang-py');
  const cppBtn = document.getElementById('dsa-lang-cpp');

  if (lang === 'python') {
    codeEl.innerText = activeDsaProblem.python_code;
    pyBtn.className = 'px-3 py-1 rounded-lg bg-cyan-600 text-white text-xs font-semibold transition';
    cppBtn.className = 'px-3 py-1 rounded-lg text-slate-400 hover:text-white text-xs font-semibold transition';
  } else {
    codeEl.innerText = activeDsaProblem.cpp_code;
    cppBtn.className = 'px-3 py-1 rounded-lg bg-cyan-600 text-white text-xs font-semibold transition';
    pyBtn.className = 'px-3 py-1 rounded-lg text-slate-400 hover:text-white text-xs font-semibold transition';
  }
}

function highlightDsaStatusButtons(status) {
  ['todo', 'solved', 'revisit'].forEach(st => {
    const btn = document.getElementById(`dsa-st-${st}`);
    if (!btn) return;
    if (st === status) {
      const col = st === 'solved' ? 'bg-emerald-600 text-white border-emerald-500'
        : (st === 'revisit' ? 'bg-amber-600 text-white border-amber-500' : 'bg-blue-600 text-white border-blue-500');
      btn.className = `px-3 py-1 rounded-lg text-xs font-bold border transition ${col}`;
    } else {
      btn.className = 'px-3 py-1 rounded-lg text-xs font-semibold border border-slate-700 bg-slate-900 text-slate-400 hover:text-white transition';
    }
  });
}

async function setActiveDsaStatus(newStatus) {
  if (!activeDsaProblem) return;
  try {
    const res = await fetch('/api/learning/progress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ category: 'dsa', item_id: activeDsaProblem.id, status: newStatus })
    });
    if (res.ok) {
      activeDsaProblem.status = newStatus;
      highlightDsaStatusButtons(newStatus);
      updateDsaProgressHeader();
      applyDsaFilters();
      loadMomentum();
      showToast(`Marked #${activeDsaProblem.num} as ${newStatus}!`);
    }
  } catch (e) {
    showToast('Error saving DSA progress');
  }
}

async function saveActiveDsaNotes() {
  if (!activeDsaProblem) return;
  const notes = document.getElementById('dsa-m-notes').value;
  try {
    const res = await fetch('/api/learning/progress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ category: 'dsa', item_id: activeDsaProblem.id, status: activeDsaProblem.status, notes })
    });
    if (res.ok) {
      activeDsaProblem.notes = notes;
      showToast('DSA notes saved!');
    }
  } catch (e) {
    showToast('Error saving notes');
  }
}

async function askDsaAiTutor(mode) {
  if (!activeDsaProblem) return;
  const out = document.getElementById('dsa-ai-output');
  const userInput = document.getElementById('dsa-ai-input').value.trim();
  out.classList.remove('hidden');
  out.innerText = 'AI Tutor analyzing in ' + (activeDsaLang === 'cpp' ? 'C++17' : 'Python 3') + '...';

  try {
    const res = await fetch('/api/dsa/ai-tutor', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        problem_id: activeDsaProblem.id,
        title: activeDsaProblem.title,
        pattern: activeDsaProblem.pattern,
        language: activeDsaLang,
        mode,
        user_input: userInput
      })
    });
    if (res.ok) {
      const data = await res.json();
      out.innerText = `[Engine: ${data.provider.toUpperCase()}]\n\n${data.response}`;
    }
  } catch (e) {
    out.innerText = 'Error reaching AI Tutor.';
  }
}

// ==========================================
// SYSTEM DESIGN ACADEMY (HLD & LLD)
// ==========================================
let sysDesignLoaded = false;
let sdBlocks = [];
let sdCases = [];
let sdProgress = {};
let sdNotes = {};
let activeCaseStudy = null;
let activeSdCodeLang = 'python';

async function loadSysDesignHub() {
  try {
    const res = await fetch('/api/sysdesign');
    if (!res.ok) return;
    const data = await res.json();
    sdBlocks = data.building_blocks || [];
    sdCases = data.case_studies || [];
    sdProgress = data.progress || {};
    sdNotes = data.notes || {};
    sysDesignLoaded = true;

    renderSdBlocks();
    renderSdCasesSidebar();
    if (sdCases.length > 0) selectCaseStudy(sdCases[0].id);
  } catch (e) {
    console.error('Error loading System Design Academy:', e);
  }
}

function switchSysDesignSubtab(sub) {
  const bPanel = document.getElementById('sd-panel-blocks');
  const cPanel = document.getElementById('sd-panel-cases');
  const bBtn = document.getElementById('sd-sub-blocks');
  const cBtn = document.getElementById('sd-sub-cases');

  if (sub === 'blocks') {
    bPanel.classList.remove('hidden'); cPanel.classList.add('hidden');
    bBtn.className = 'px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold transition';
    cBtn.className = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white text-xs font-semibold transition';
  } else {
    cPanel.classList.remove('hidden'); bPanel.classList.add('hidden');
    cBtn.className = 'px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold transition';
    bBtn.className = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white text-xs font-semibold transition';
  }
}

function renderSdBlocks() {
  const container = document.getElementById('sd-panel-blocks');
  if (!container) return;
  container.innerHTML = sdBlocks.map(b => `
    <div class="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
      <div class="flex items-center justify-between gap-2">
        <h4 class="text-sm font-bold text-white">${b.title}</h4>
        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 shrink-0">${b.tag}</span>
      </div>
      <p class="text-xs text-amber-300/90 font-medium">${b.summary}</p>
      <p class="text-xs text-slate-300 leading-relaxed">${b.intuition}</p>
      <ul class="space-y-1 text-[11px] text-slate-400 list-disc pl-4">
        ${(b.key_rules || []).map(r => `<li>${r}</li>`).join('')}
      </ul>
      <pre class="bg-slate-950 p-3 rounded-xl border border-slate-800/80 text-[11px] font-mono text-emerald-300 overflow-x-auto custom-scroll">${b.diagram}</pre>
    </div>
  `).join('');
}

function renderSdCasesSidebar() {
  const sb = document.getElementById('sd-cases-sidebar');
  if (!sb) return;
  sb.innerHTML = sdCases.map(c => {
    const active = activeCaseStudy && activeCaseStudy.id === c.id;
    const studied = sdProgress[c.id] === 'solved';
    const typeCol = c.type === 'LLD' ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : 'bg-purple-500/15 text-purple-300 border-purple-500/30';
    return `
      <button onclick="selectCaseStudy('${c.id}')" class="w-full text-left p-3.5 rounded-xl border transition ${active ? 'bg-indigo-600/20 border-indigo-500' : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'}">
        <div class="flex items-center justify-between gap-2 mb-1">
          <span class="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${typeCol}">${c.type}</span>
          ${studied ? '<span class="text-[10px] text-emerald-400 font-bold">Studied ✓</span>' : ''}
        </div>
        <div class="text-xs font-bold text-white leading-snug">${c.title}</div>
      </button>
    `;
  }).join('');
}

function selectCaseStudy(caseId) {
  const c = sdCases.find(x => x.id === caseId);
  if (!c) return;
  activeCaseStudy = c;
  renderSdCasesSidebar();

  const detail = document.getElementById('sd-case-detail');
  const hasCode = Boolean(c.python_code || c.cpp_code);
  const studied = sdProgress[c.id] === 'solved';

  detail.innerHTML = `
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
      <div>
        <div class="flex flex-wrap items-center gap-1.5 mb-1">
          <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">${c.type} CASE STUDY</span>
          ${(c.companies || []).map(co => `<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">${co}</span>`).join('')}
        </div>
        <h4 class="text-base font-bold text-white">${c.title}</h4>
        <p class="text-[11px] font-mono text-emerald-400 mt-0.5">${c.scale}</p>
      </div>
      <button onclick="markSysDesignStudied('${c.id}')" class="px-3.5 py-1.5 rounded-xl text-xs font-bold border transition shrink-0 ${studied ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'}">
        ${studied ? 'Studied ✓' : 'Mark Studied'}
      </button>
    </div>

    <p class="text-xs text-slate-300 leading-relaxed">${c.summary}</p>

    <div>
      <span class="text-[11px] font-mono uppercase text-purple-400 font-bold block mb-1.5">Architecture Flow Diagram</span>
      <pre class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto custom-scroll">${c.diagram}</pre>
    </div>

    <div class="space-y-2">
      <span class="text-[11px] font-mono uppercase text-blue-400 font-bold block">End-to-End Walkthrough</span>
      <div class="space-y-2">
        ${(c.steps || []).map(s => `<div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80 text-xs text-slate-300 leading-relaxed">${s}</div>`).join('')}
      </div>
    </div>

    <div class="space-y-1.5">
      <span class="text-[11px] font-mono uppercase text-amber-400 font-bold block">Key Engineering Trade-Offs</span>
      <ul class="space-y-1.5 text-xs text-slate-300 list-disc pl-4">
        ${(c.tradeoffs || []).map(t => `<li>${t}</li>`).join('')}
      </ul>
    </div>

    ${hasCode ? `
      <div class="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden">
        <div class="flex items-center justify-between px-3 py-2 border-b border-slate-800 bg-slate-900/80">
          <div class="flex items-center gap-1.5">
            <button onclick="switchSdCodeLang('python')" id="sd-lang-py" class="px-3 py-1 rounded-lg bg-cyan-600 text-white text-xs font-semibold">Python OOP</button>
            <button onclick="switchSdCodeLang('cpp')" id="sd-lang-cpp" class="px-3 py-1 rounded-lg text-slate-400 hover:text-white text-xs font-semibold">C++17 OOP</button>
          </div>
          <button onclick="copyToClipboard('sd-case-code')" class="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
            <i class="fa-regular fa-copy"></i> Copy Code
          </button>
        </div>
        <pre id="sd-case-code" class="p-4 text-xs font-mono text-emerald-300 overflow-x-auto custom-scroll leading-relaxed"></pre>
      </div>
    ` : ''}

    <!-- Personal Engineering & Interview Notes -->
    <div class="glass-card rounded-xl p-4 border border-slate-800 space-y-2.5">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-slate-200 flex items-center gap-1.5">
          <i class="fa-solid fa-pen-to-square text-cyan-400"></i> My Personal Architecture & Interview Notes
        </span>
        <button onclick="saveSysDesignNotes('${c.id}')" class="px-3 py-1 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-semibold transition flex items-center gap-1">
          <i class="fa-solid fa-floppy-disk"></i> Save Notes
        </button>
      </div>
      <textarea id="sd-case-notes" rows="3" placeholder="Write personal failure modes, exact numbers (e.g. 100M DAU = 1150 QPS write), questions to ask the interviewer, or trade-offs..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 custom-scroll">${sdNotes[c.id] || ''}</textarea>
    </div>

    <!-- AI Staff Engineer Critique -->
    <div class="bg-indigo-950/20 border border-indigo-500/30 rounded-xl p-4 space-y-2.5">
      <span class="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
        <i class="fa-solid fa-user-tie"></i> AI Staff Engineer Design Review
      </span>
      <p class="text-[11px] text-slate-400">Describe how YOU would scale this or handle a bottleneck (e.g., hot keys, payment webhook retries, 10x spike):</p>
      <textarea id="sd-review-input" rows="3" placeholder="Propose your design decision or bottleneck fix..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"></textarea>
      <div class="flex justify-end">
        <button onclick="submitSysDesignReview()" id="btn-sd-review" class="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition">
          Get Staff Critique
        </button>
      </div>
      <pre id="sd-review-output" class="hidden bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs font-mono text-slate-200 whitespace-pre-wrap leading-relaxed"></pre>
    </div>
  `;

  if (hasCode) switchSdCodeLang(activeSdCodeLang);
}

async function saveSysDesignNotes(caseId) {
  const el = document.getElementById('sd-case-notes');
  if (!el) return;
  const notes = el.value;
  try {
    const res = await fetch('/api/learning/progress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ category: 'sysdesign', item_id: caseId, status: sdProgress[caseId] || 'todo', notes })
    });
    if (res.ok) {
      sdNotes[caseId] = notes;
      showToast('System Design notes saved!');
    }
  } catch (e) {
    showToast('Failed to save notes');
  }
}

function switchSdCodeLang(lang) {
  activeSdCodeLang = lang;
  if (!activeCaseStudy) return;
  const codeEl = document.getElementById('sd-case-code');
  const pyBtn = document.getElementById('sd-lang-py');
  const cppBtn = document.getElementById('sd-lang-cpp');
  if (!codeEl) return;
  if (lang === 'python') {
    codeEl.innerText = activeCaseStudy.python_code || '';
    if (pyBtn) pyBtn.className = 'px-3 py-1 rounded-lg bg-cyan-600 text-white text-xs font-semibold';
    if (cppBtn) cppBtn.className = 'px-3 py-1 rounded-lg text-slate-400 hover:text-white text-xs font-semibold';
  } else {
    codeEl.innerText = activeCaseStudy.cpp_code || '';
    if (cppBtn) cppBtn.className = 'px-3 py-1 rounded-lg bg-cyan-600 text-white text-xs font-semibold';
    if (pyBtn) pyBtn.className = 'px-3 py-1 rounded-lg text-slate-400 hover:text-white text-xs font-semibold';
  }
}

async function markSysDesignStudied(caseId) {
  const newStatus = sdProgress[caseId] === 'solved' ? 'todo' : 'solved';
  try {
    const res = await fetch('/api/learning/progress', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ category: 'sysdesign', item_id: caseId, status: newStatus })
    });
    if (res.ok) {
      sdProgress[caseId] = newStatus;
      selectCaseStudy(caseId);
      loadMomentum();
      showToast(newStatus === 'solved' ? 'Marked Case Study as Studied!' : 'Marked as Todo');
    }
  } catch (e) {}
}

async function submitSysDesignReview() {
  if (!activeCaseStudy) return;
  const proposal = document.getElementById('sd-review-input').value.trim();
  if (!proposal) { showToast('Enter your design proposal first.'); return; }
  const btn = document.getElementById('btn-sd-review');
  const out = document.getElementById('sd-review-output');
  btn.disabled = true; btn.innerText = 'Reviewing...';
  out.classList.remove('hidden'); out.innerText = 'Staff Engineer evaluating trade-offs...';

  try {
    const res = await fetch('/api/sysdesign/ai-review', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ case_id: activeCaseStudy.id, case_title: activeCaseStudy.title, user_design: proposal })
    });
    if (res.ok) {
      const data = await res.json();
      out.innerText = `[Engine: ${data.provider.toUpperCase()}]\n\n${data.review}`;
      loadMomentum();
    }
  } catch (e) {
    out.innerText = 'Failed to fetch AI review.';
  } finally {
    btn.disabled = false; btn.innerText = 'Get Staff Critique';
  }
}

// ==========================================
// CORE CS RAPID-FIRE SHEET
// ==========================================
let coreCsTopics = [];
let activeCoreCsCat = '';

async function loadCoreCsHub() {
  try {
    const res = await fetch('/api/corecs');
    if (!res.ok) return;
    const data = await res.json();
    coreCsTopics = data.topics || [];
    if (coreCsTopics.length > 0) {
      renderCoreCsCategory(coreCsTopics[0].category);
    }
  } catch (e) {
    console.error('Error loading Core CS:', e);
  }
}

function renderCoreCsCategory(catName) {
  activeCoreCsCat = catName;
  const pills = document.getElementById('corecs-cat-pills');
  const container = document.getElementById('corecs-items-container');
  if (pills) {
    pills.innerHTML = coreCsTopics.map(t => `
      <button onclick="renderCoreCsCategory('${t.category}')" class="px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${t.category === catName ? 'bg-rose-600 text-white border-rose-500' : 'bg-slate-900 text-slate-300 border-slate-800 hover:text-white'}">
        ${t.category}
      </button>
    `).join('');
  }
  const activeObj = coreCsTopics.find(t => t.category === catName);
  if (container && activeObj) {
    container.innerHTML = activeObj.items.map((item, idx) => `
      <details class="glass-card rounded-2xl p-4 sm:p-5 border border-slate-800 group" ${idx === 0 ? 'open' : ''}>
        <summary class="text-xs sm:text-sm font-bold text-white cursor-pointer list-none flex items-center justify-between gap-3">
          <span><span class="text-rose-400 font-mono mr-1.5">Q${idx+1}.</span>${item.q}</span>
          <i class="fa-solid fa-chevron-down text-slate-500 text-xs group-open:rotate-180 transition shrink-0"></i>
        </summary>
        <div class="mt-3 pt-3 border-t border-slate-800/80 space-y-3">
          <p class="text-xs text-slate-300 leading-relaxed">${item.a}</p>
          ${item.code ? `<pre class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto custom-scroll">${item.code}</pre>` : ''}
        </div>
      </details>
    `).join('');
  }
}

// ==========================================
// INTERACTIVE AI MOCK INTERVIEW GRILL MODE
// ==========================================
const GRILL_SEED_PROMPTS = [
  "Walk me through how you reduced SQL transaction latency by 35% at NexGen—what did EXPLAIN show before vs after, and how would you protect that endpoint from cache stampede under 10x traffic?",
  "Design a distributed Token Bucket rate limiter using Node.js and Redis that supports 50,000 req/sec without race conditions.",
  "Two simultaneous webhook calls arrive for the exact same payout transaction at Razorpay/ViralMe. How do you guarantee strictly one debit in SQL + Redis?",
  "Given an array of integers and K, explain how you pick between Sliding Window vs Prefix-Sum HashMap when negative numbers are allowed."
];

function resetGrillQuestion() {
  const idx = Math.floor(Math.random() * GRILL_SEED_PROMPTS.length);
  document.getElementById('grill-question').innerText = GRILL_SEED_PROMPTS[idx];
  document.getElementById('grill-answer').value = '';
  document.getElementById('grill-feedback-box').classList.add('hidden');
}

async function submitGrillAnswer() {
  const company = document.getElementById('prep-target-company')?.value || 'ViralMe';
  const role = document.getElementById('prep-target-role')?.value || 'Backend Software Engineer';
  const focus = document.getElementById('grill-focus')?.value || 'backend';
  const question = document.getElementById('grill-question').innerText;
  const user_answer = document.getElementById('grill-answer').value.trim();

  if (!user_answer) {
    showToast('Type your answer first!');
    return;
  }

  const btn = document.getElementById('btn-grill-submit');
  btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Evaluating...';

  try {
    const res = await fetch('/api/ai/mock-grill', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ company, role, question, user_answer, focus_area: focus })
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById('grill-score-badge').innerText = `Score: ${data.score}/10`;
      document.getElementById('grill-provider-tag').innerText = `Evaluated by ${(data.provider || 'AI').toUpperCase()}`;
      document.getElementById('grill-feedback-text').innerText = data.feedback;
      document.getElementById('grill-ideal-bullet').innerText = data.ideal_bullet;
      document.getElementById('grill-feedback-box').classList.remove('hidden');

      if (data.next_question) {
        document.getElementById('grill-question').innerText = data.next_question;
        document.getElementById('grill-answer').value = '';
      }
      showToast(`Graded ${data.score}/10 — Next follow-up loaded!`);
    }
  } catch (e) {
    showToast('Error grading answer.');
  } finally {
    btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Evaluate & Grill Next';
  }
}

// ==========================================
// UNIVERSAL AI ASSISTANT CLONE & CHAT CONTINUITY
// ==========================================
let aiChatSessions = [];
let activeAiChatSessionId = null;
let activeAiChatMessages = [];
let isAiChatSending = false;

function formatAiMarkdown(text) {
  if (!text) return '';
  let escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Fenced Code Blocks: ```lang ... ```
  escaped = escaped.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<div class="bg-slate-950 rounded-xl border border-slate-800 my-2 overflow-hidden">
      <div class="flex items-center justify-between px-3 py-1 bg-slate-900 border-b border-slate-800 text-[10px] font-mono text-slate-400">
        <span>${lang || 'CODE'}</span>
        <button onclick="copyCodeSnippet(this)" class="hover:text-white transition flex items-center gap-1">
          <i class="fa-regular fa-copy"></i> Copy
        </button>
      </div>
      <pre class="p-3 text-xs font-mono text-emerald-300 overflow-x-auto custom-scroll leading-relaxed"><code>${code.trim()}</code></pre>
    </div>`;
  });

  // Inline code `code`
  escaped = escaped.replace(/`([^`]+)`/g, '<code class="bg-slate-900 px-1.5 py-0.5 rounded text-amber-300 font-mono text-[11px] border border-slate-800">$1</code>');

  // Headers: ###, ##, #
  escaped = escaped.replace(/^### (.*$)/gim, '<h4 class="text-xs sm:text-sm font-bold text-indigo-300 mt-2 mb-1">$1</h4>');
  escaped = escaped.replace(/^## (.*$)/gim, '<h3 class="text-sm sm:text-base font-bold text-white mt-2.5 mb-1.5 border-b border-slate-800 pb-1">$1</h3>');
  escaped = escaped.replace(/^# (.*$)/gim, '<h2 class="text-base sm:text-lg font-bold text-white mt-3 mb-2">$1</h2>');

  // Bold **text**
  escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');

  // Bullet points
  escaped = escaped.replace(/^\s*[-*]\s+(.*$)/gim, '<li class="text-xs text-slate-300 ml-4 list-disc mb-1 leading-relaxed">$1</li>');

  // Line breaks
  escaped = escaped.replace(/\n\n/g, '<div class="h-2"></div>');

  return escaped;
}

function copyCodeSnippet(btn) {
  const codeEl = btn.closest('div').nextElementSibling?.querySelector('code');
  if (!codeEl) return;
  navigator.clipboard.writeText(codeEl.innerText).then(() => {
    btn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> Copied';
    setTimeout(() => { btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy'; }, 2000);
  });
}

async function loadAiChatSessions() {
  try {
    const res = await fetch('/api/ai/sessions');
    if (!res.ok) return;
    aiChatSessions = await res.json();
    renderAiChatSessionsList();

    if (aiChatSessions.length > 0) {
      if (!activeAiChatSessionId || !aiChatSessions.find(s => s.id === activeAiChatSessionId)) {
        selectAiChatSession(aiChatSessions[0].id);
      } else {
        selectAiChatSession(activeAiChatSessionId);
      }
    } else {
      startNewAiChat();
    }
  } catch (e) {
    console.error('Failed to load chat sessions:', e);
  }
}

function renderAiChatSessionsList() {
  const container = document.getElementById('ai-chat-threads-list');
  const countBadge = document.getElementById('ai-chat-thread-count');
  if (countBadge) countBadge.innerText = aiChatSessions.length;
  if (!container) return;

  if (aiChatSessions.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8 text-slate-500 text-xs font-mono">
        <i class="fa-regular fa-comments text-lg mb-1 block text-slate-600"></i>
        No conversations yet
      </div>`;
    return;
  }

  container.innerHTML = aiChatSessions.map(s => {
    const isActive = s.id === activeAiChatSessionId;
    return `
      <div onclick="selectAiChatSession(${s.id})" class="group flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-xs transition ${
        isActive 
          ? 'bg-indigo-600/25 border border-indigo-500/40 text-white font-semibold' 
          : 'bg-slate-950/60 hover:bg-slate-800/60 border border-slate-800/80 text-slate-300'
      }">
        <div class="flex items-center gap-2 min-w-0 pr-1">
          <i class="fa-regular fa-message text-[11px] ${isActive ? 'text-indigo-400' : 'text-slate-500'} shrink-0"></i>
          <span class="truncate text-[11px]">${s.title || 'New Conversation'}</span>
        </div>
        <button onclick="deleteAiChatSessionFromList(event, ${s.id})" title="Delete conversation" class="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-1 text-[11px] transition shrink-0">
          <i class="fa-regular fa-trash-can"></i>
        </button>
      </div>
    `;
  }).join('');
}

async function startNewAiChat() {
  try {
    const res = await fetch('/api/ai/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'New Conversation' })
    });
    if (!res.ok) return;
    const newSession = await res.json();
    aiChatSessions.unshift(newSession);
    renderAiChatSessionsList();
    selectAiChatSession(newSession.id);
    const input = document.getElementById('ai-chat-prompt-input');
    if (input) input.focus();
  } catch (e) {
    showToast('Failed to create new conversation');
  }
}

async function selectAiChatSession(sessionId) {
  activeAiChatSessionId = sessionId;
  renderAiChatSessionsList();

  const titleEl = document.getElementById('ai-chat-session-title');
  const container = document.getElementById('ai-chat-messages-container');
  const welcomeCard = document.getElementById('ai-chat-welcome-card');

  try {
    const res = await fetch(`/api/ai/sessions/${sessionId}`);
    if (!res.ok) return;
    const sessionData = await res.json();

    if (titleEl) titleEl.innerText = sessionData.title || 'CareerOS Universal Assistant';
    activeAiChatMessages = sessionData.messages || [];

    if (activeAiChatMessages.length === 0) {
      if (welcomeCard) welcomeCard.classList.remove('hidden');
      if (container) container.innerHTML = '';
    } else {
      if (welcomeCard) welcomeCard.classList.add('hidden');
      renderAiChatMessages(activeAiChatMessages);
    }
  } catch (e) {
    console.error('Failed to load session messages:', e);
  }
}

function renderAiChatMessages(messages) {
  const container = document.getElementById('ai-chat-messages-container');
  if (!container) return;

  container.innerHTML = messages.map(m => {
    if (m.role === 'user') {
      return `
        <div class="flex justify-end">
          <div class="max-w-[85%] sm:max-w-[75%] rounded-2xl p-3 sm:p-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs sm:text-sm shadow-md shadow-blue-600/15 leading-relaxed selection:bg-white/20 whitespace-pre-wrap">
            ${m.content}
          </div>
        </div>
      `;
    } else {
      const providerTag = (m.provider || 'AI').toUpperCase();
      return `
        <div class="flex items-start gap-2.5 sm:gap-3">
          <div class="w-7 h-7 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs shrink-0 mt-1 shadow-sm">
            <i class="fa-solid fa-sparkles"></i>
          </div>
          <div class="flex-1 glass-card rounded-2xl p-4 sm:p-5 border border-slate-800 space-y-2 text-xs sm:text-sm text-slate-200 leading-relaxed overflow-hidden">
            <div class="flex items-center justify-between pb-2 border-b border-slate-800/80 text-[10px] font-mono text-slate-400">
              <span class="flex items-center gap-1.5 text-emerald-400 font-bold">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> ${providerTag}
              </span>
              <button onclick="copyMessageContent(this)" class="hover:text-white transition flex items-center gap-1">
                <i class="fa-regular fa-copy"></i> Copy
              </button>
            </div>
            <div class="ai-msg-body space-y-1.5">${formatAiMarkdown(m.content)}</div>
          </div>
        </div>
      `;
    }
  }).join('');

  scrollChatToBottom();
}

function copyMessageContent(btn) {
  const body = btn.closest('.glass-card')?.querySelector('.ai-msg-body');
  if (!body) return;
  navigator.clipboard.writeText(body.innerText).then(() => {
    btn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> Copied';
    setTimeout(() => { btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy'; }, 2000);
  });
}

function scrollChatToBottom() {
  const wrap = document.getElementById('ai-chat-messages-wrap');
  if (wrap) {
    setTimeout(() => { wrap.scrollTop = wrap.scrollHeight; }, 50);
  }
}

async function sendAiChatMessage(customText = null) {
  if (isAiChatSending) return;

  const input = document.getElementById('ai-chat-prompt-input');
  const text = (customText || input?.value || '').trim();
  if (!text) return;

  if (input) input.value = '';

  if (!activeAiChatSessionId) {
    await startNewAiChat();
  }

  const welcomeCard = document.getElementById('ai-chat-welcome-card');
  if (welcomeCard) welcomeCard.classList.add('hidden');

  const container = document.getElementById('ai-chat-messages-container');
  
  // 1. Immediately append user bubble
  const userHtml = `
    <div class="flex justify-end">
      <div class="max-w-[85%] sm:max-w-[75%] rounded-2xl p-3 sm:p-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs sm:text-sm shadow-md shadow-blue-600/15 leading-relaxed whitespace-pre-wrap">
        ${text}
      </div>
    </div>
  `;
  if (container) container.innerHTML += userHtml;

  // 2. Append temporary thinking bubble
  const tempId = `temp-thinking-${Date.now()}`;
  const thinkingHtml = `
    <div id="${tempId}" class="flex items-start gap-2.5 sm:gap-3">
      <div class="w-7 h-7 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs shrink-0 mt-1">
        <i class="fa-solid fa-sparkles animate-pulse"></i>
      </div>
      <div class="flex-1 glass-card rounded-2xl p-4 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
        <i class="fa-solid fa-circle-notch animate-spin text-indigo-400"></i>
        <span>Synthesizing response with multi-turn context (Target: ₹1L+/Mo Remote)...</span>
      </div>
    </div>
  `;
  if (container) container.innerHTML += thinkingHtml;
  scrollChatToBottom();

  const providerSelect = document.getElementById('ai-chat-provider-select');
  const provider = providerSelect?.value || 'gemini';

  const sendBtn = document.getElementById('btn-ai-chat-send');
  if (sendBtn) sendBtn.disabled = true;
  isAiChatSending = true;

  try {
    const res = await fetch(`/api/ai/sessions/${activeAiChatSessionId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text, provider })
    });

    const thinkingEl = document.getElementById(tempId);
    if (thinkingEl) thinkingEl.remove();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Message failed');
    }

    const data = await res.json();
    const assistantMsg = data.assistant_message;
    const providerTag = (data.provider || 'AI').toUpperCase();

    // Update session title if changed
    if (data.session_title) {
      const titleEl = document.getElementById('ai-chat-session-title');
      if (titleEl) titleEl.innerText = data.session_title;
      const sessObj = aiChatSessions.find(s => s.id === activeAiChatSessionId);
      if (sessObj) sessObj.title = data.session_title;
      renderAiChatSessionsList();
    }

    // Append finalized assistant bubble
    const assistantHtml = `
      <div class="flex items-start gap-2.5 sm:gap-3">
        <div class="w-7 h-7 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs shrink-0 mt-1 shadow-sm">
          <i class="fa-solid fa-sparkles"></i>
        </div>
        <div class="flex-1 glass-card rounded-2xl p-4 sm:p-5 border border-slate-800 space-y-2 text-xs sm:text-sm text-slate-200 leading-relaxed overflow-hidden">
          <div class="flex items-center justify-between pb-2 border-b border-slate-800/80 text-[10px] font-mono text-slate-400">
            <span class="flex items-center gap-1.5 text-emerald-400 font-bold">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> ${providerTag}
            </span>
            <button onclick="copyMessageContent(this)" class="hover:text-white transition flex items-center gap-1">
              <i class="fa-regular fa-copy"></i> Copy
            </button>
          </div>
          <div class="ai-msg-body space-y-1.5">${formatAiMarkdown(assistantMsg.content)}</div>
        </div>
      </div>
    `;
    if (container) container.innerHTML += assistantHtml;
    scrollChatToBottom();

  } catch (e) {
    const thinkingEl = document.getElementById(tempId);
    if (thinkingEl) thinkingEl.remove();
    showToast('AI response error: ' + (e.message || 'Check connection'));
  } finally {
    isAiChatSending = false;
    if (sendBtn) sendBtn.disabled = false;
  }
}

function triggerQuickAiPrompt(text) {
  sendAiChatMessage(text);
}

async function deleteActiveChatSession() {
  if (!activeAiChatSessionId) return;
  if (!confirm('Delete this conversation history?')) return;

  try {
    const res = await fetch(`/api/ai/sessions/${activeAiChatSessionId}`, { method: 'DELETE' });
    if (res.ok) {
      aiChatSessions = aiChatSessions.filter(s => s.id !== activeAiChatSessionId);
      activeAiChatSessionId = null;
      loadAiChatSessions();
      showToast('Conversation deleted');
    }
  } catch (e) {
    showToast('Failed to delete conversation');
  }
}

async function deleteAiChatSessionFromList(e, sessionId) {
  e.stopPropagation();
  if (!confirm('Delete this conversation?')) return;

  try {
    const res = await fetch(`/api/ai/sessions/${sessionId}`, { method: 'DELETE' });
    if (res.ok) {
      aiChatSessions = aiChatSessions.filter(s => s.id !== sessionId);
      if (activeAiChatSessionId === sessionId) {
        activeAiChatSessionId = null;
        loadAiChatSessions();
      } else {
        renderAiChatSessionsList();
      }
      showToast('Conversation deleted');
    }
  } catch (e) {
    showToast('Failed to delete conversation');
  }
}

async function saveActiveChatToVault() {
  if (!activeAiChatSessionId) {
    showToast('No active conversation to save');
    return;
  }

  const container = document.getElementById('ai-chat-messages-container');
  if (!container || !container.innerText.trim()) {
    showToast('Conversation is empty');
    return;
  }

  const titleEl = document.getElementById('ai-chat-session-title');
  const title = (titleEl?.innerText || 'AI Assistant Conversation').slice(0, 100);

  try {
    const res = await fetch('/api/documents/custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        category: 'ai_conversation',
        content: `Conversation: ${title}\nDate: ${new Date().toLocaleString()}\n\n${container.innerText}`
      })
    });
    if (res.ok) {
      showToast('Saved conversation transcript to Document Vault!');
    } else {
      showToast('Failed to save to Document Vault');
    }
  } catch (e) {
    showToast('Error saving to vault');
  }
}

// Bind Enter key on prompt input
document.addEventListener('DOMContentLoaded', () => {
  const promptInput = document.getElementById('ai-chat-prompt-input');
  if (promptInput) {
    promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendAiChatMessage();
      }
    });
  }
});
