/* School Dashboard front end: plain JS, no build step. */
"use strict";

// ------------------------------------------------------------------ icons
const ICONS = {
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
  list: '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m3.5 6 1 1 2-2M3.5 12l1 1 2-2M3.5 18l1 1 2-2"/>',
  calendar: '<rect x="3" y="4.5" width="18" height="16.5" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/>',
  plug: '<path d="M9 2v5M15 2v5"/><path d="M6 7h12v4a6 6 0 0 1-12 0z"/><path d="M12 17v5"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
  refresh: '<path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5M3 21v-5h5"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  alert: '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17.5v.01"/>',
  flame: '<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-2 2-5 5-5 8a7 7 0 0 0 7 7z"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  trophy: '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/>',
  upload: '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>',
  text: '<path d="M4 6h16M4 12h16M4 18h10"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  video: '<rect x="2.5" y="6" width="13" height="12" rx="2.5"/><path d="m15.5 10.5 6-3.5v10l-6-3.5"/>',
  paper: '<path d="M6 2.5h8l4 4v15H6z"/><path d="M14 2.5v4h4"/>',
  tool: '<path d="M14.7 6.3a4 4 0 0 0 5 5L21 13l-8 8-3-3 8-8-1.3-1.3a4 4 0 0 0-5-5z"/><path d="M3 21l6-6"/>',
  quiz: '<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="m8 9 1.5 1.5L12 8M8 15l1.5 1.5L12 14M14 9.5h3M14 15.5h3"/>',
  chat: '<path d="M21 12a8 8 0 0 1-11.6 7.1L3 21l1.9-6.4A8 8 0 1 1 21 12z"/>',
  book: '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v17H6.5A2.5 2.5 0 0 0 4 21.5z"/><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>',
  flask: '<path d="M9 2.5h6M10 2.5v6L4.5 19a2 2 0 0 0 1.8 2.5h11.4a2 2 0 0 0 1.8-2.5L14 8.5v-6"/><path d="M7 15h10"/>',
  pen: '<path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/><path d="m14 6 3 3"/>',
  slides: '<rect x="2.5" y="3.5" width="19" height="13" rx="2"/><path d="M12 16.5V21M8 21h8"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
  calc: '<rect x="5" y="2.5" width="14" height="19" rx="2.5"/><path d="M8.5 7h7M8.5 12h.01M12 12h.01M15.5 12h.01M8.5 16h.01M12 16h.01M15.5 16h.01"/>',
  cards: '<rect x="3" y="6" width="13" height="15" rx="2"/><path d="M8 3h11a2 2 0 0 1 2 2v12"/>',
  file: '<path d="M6 2.5h8l4 4v15H6z"/><path d="M9 12h6M9 16h6"/>',
  sparkles: '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
  external: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 19V7.5A1.5 1.5 0 0 1 5.5 6H10"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  eyeoff: '<path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8"/><path d="M9.9 5.1A10 10 0 0 1 12 5c6 0 10 7 10 7a17 17 0 0 1-3.2 3.9M6.6 6.6C3.9 8.3 2 12 2 12s4 7 10 7a9.6 9.6 0 0 0 5.4-1.6"/>',
  eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  left: '<path d="m15 6-6 6 6 6"/>',
  right: '<path d="m9 6 6 6-6 6"/>',
  download: '<path d="M12 4v12M7 11l5 5 5-5"/><path d="M4 20h16"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  lightbulb: '<path d="M9 18h6M10 21.5h4"/><path d="M12 2.5a6.5 6.5 0 0 0-4 11.6c.6.5 1 1.3 1 2.1V17h6v-.8c0-.8.4-1.6 1-2.1a6.5 6.5 0 0 0-4-11.6z"/>',
  flag: '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  star: '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
  question: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01"/>',
  play: '<path d="M7 4v16l13-8z"/>',
};
const icon = (name, cls = "") => `<svg class="icon ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ICONS.file}</svg>`;
const hydrateIcons = (root = document) => root.querySelectorAll("i[data-icon]").forEach(el => { el.innerHTML = icon(el.dataset.icon); });

const CAT_ICON = { essay: "pen", lab: "flask", presentation: "slides", project: "layers", quiz: "quiz", discussion: "chat",
  reading: "book", problem_set: "calc", media: "video", vocab: "cards", general: "file" };
const SUB_ICON = { upload: "upload", text: "text", url: "link", media: "video", paper: "paper", external_tool: "tool",
  quiz: "quiz", discussion: "chat", annotation: "edit", none: "x", unknown: "external" };
const PLATFORM_STYLE = {
  canvas: { color: "#e3242b", letter: "C" }, schoology: { color: "#0677bf", letter: "S" }, moodle: { color: "#f98012", letter: "M" },
  ical: { color: "#7c3aed", letter: "" }, demo: { color: "#10b981", letter: "" }, manual: { color: "#64748b", letter: "" },
};
const PALETTE = ["#6366f1", "#ec4899", "#14b8a6", "#f59e0b", "#8b5cf6", "#0ea5e9", "#ef4444", "#22c55e", "#f97316", "#a855f7", "#06b6d4", "#84cc16"];

// ------------------------------------------------------------------ state & helpers
const S = { status: null, assignments: [], connections: [], settings: {}, plan: null, filter: "open", course: "", q: "",
  weekStart: 0, schedMode: null, openId: null };

const $ = (sel, root = document) => root.querySelector(sel);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function api(method, path, body) {
  const res = await fetch(path, { method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
  const data = res.headers.get("content-type")?.includes("json") ? await res.json() : await res.text();
  if (!res.ok) throw new Error((data && data.detail) || `Request failed (${res.status})`);
  return data;
}

function toast(msg, kind = "") {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.textContent = msg;
  $("#toasts").appendChild(el);
  setTimeout(() => el.remove(), kind === "error" ? 6000 : 3200);
}

async function busy(btn, fn) {
  btn?.classList.add("loading");
  if (btn) btn.disabled = true;
  try { return await fn(); }
  catch (e) { toast(e.message, "error"); }
  finally { btn?.classList.remove("loading"); if (btn) btn.disabled = false; }
}

function colorFor(course) {
  let h = 0;
  for (const ch of course || "") h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return PALETTE[h % PALETTE.length];
}
const courseChip = c => c ? `<span class="chip" style="color:${colorFor(c)};background:${colorFor(c)}1f"><span class="dot"></span>${esc(c)}</span>` : "";

const isDone = a => a.status === "done" || ["submitted", "graded"].includes(a.platform_status);
const isOpen = a => !isDone(a) && a.status !== "hidden";
const minutesLabel = m => !m ? "" : m < 60 ? `${m} min` : `${Math.floor(m / 60)}h${m % 60 ? ` ${m % 60}m` : ""}`;

const startOfDay = d => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
const dayDiff = (a, b) => Math.round((startOfDay(a) - startOfDay(b)) / 86400000);
const fmtTime = d => d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const fmtDay = d => d.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });

function dueText(iso) {
  if (!iso) return "No due date";
  const d = new Date(iso), diff = dayDiff(d, new Date());
  if (diff === 0) return `Today ${fmtTime(d)}`;
  if (diff === 1) return `Tomorrow ${fmtTime(d)}`;
  if (diff === -1) return `Yesterday ${fmtTime(d)}`;
  if (diff > 1 && diff < 7) return `${d.toLocaleDateString([], { weekday: "long" })} ${fmtTime(d)}`;
  return `${fmtDay(d)} · ${fmtTime(d)}`;
}
function relText(iso) {
  if (!iso) return "";
  const ms = new Date(iso) - new Date(), h = Math.abs(ms) / 3600000;
  const s = h < 1 ? `${Math.max(1, Math.round(h * 60))} min` : h < 48 ? `${Math.round(h)}h` : `${Math.round(h / 24)} days`;
  return ms < 0 ? `${s} ago` : `in ${s}`;
}
function dueClass(a) {
  if (!a.due_at || isDone(a)) return "";
  const h = (new Date(a.due_at) - new Date()) / 3600000;
  return h < 0 ? "overdue" : h < 36 ? "soon" : "";
}
function bucket(a) {
  if (!a.due_at) return "none";
  const d = new Date(a.due_at), now = new Date();
  if (d < now && !isDone(a)) return "overdue";
  const diff = dayDiff(d, now);
  if (diff <= 0) return "today";
  if (diff === 1) return "tomorrow";
  if (diff < 7) return "week";
  return "later";
}
function statusChip(a) {
  if (a.platform_status === "graded") return `<span class="chip chip-green">${icon("check")}Graded</span>`;
  if (a.platform_status === "submitted") return `<span class="chip chip-green">${icon("check")}Submitted</span>`;
  if (a.status === "done") return `<span class="chip chip-green">${icon("check")}Done</span>`;
  if (a.platform_status === "missing") return `<span class="chip chip-red">Missing</span>`;
  if (a.status === "in_progress") return `<span class="chip chip-blue">In progress</span>`;
  if (a.status === "hidden") return `<span class="chip">Hidden</span>`;
  return "";
}
const sourceName = a => a.source_kind === "manual" ? "Added by me" : a.source_name;

// ------------------------------------------------------------------ data
async function loadAll() {
  const [status, assignments, connections] = await Promise.all([api("GET", "/api/status"), api("GET", "/api/assignments"), api("GET", "/api/connections")]);
  S.status = status; S.settings = status.settings; S.assignments = assignments; S.connections = connections;
  applyTheme();
  try { S.plan = await api("GET", "/api/schedule"); } catch { S.plan = null; }
  updateChrome();
}
async function reloadAssignments() {
  S.assignments = await api("GET", "/api/assignments");
  try { S.plan = await api("GET", "/api/schedule"); } catch { /* keep the old plan */ }
  updateChrome();
}
function updateChrome() {
  const open = S.assignments.filter(isOpen);
  const urgent = open.filter(a => a.due_at && (new Date(a.due_at) - new Date()) < 86400000 * 2).length;
  $("#badge-todo").textContent = urgent || "";
  const syncs = S.connections.map(c => c.last_sync).filter(Boolean).sort();
  $("#last-sync").textContent = syncs.length ? `Synced ${relText(syncs[syncs.length - 1].replace(" ", "T"))}` : "";
}
function applyTheme() {
  const t = localStorage.getItem("theme") || "auto";
  if (t === "auto") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.dataset.theme = t;
}

// ------------------------------------------------------------------ routing
const VIEWS = { dashboard: renderDashboard, assignments: renderAssignments, schedule: renderSchedule, connections: renderConnections, settings: renderSettings };
function currentView() { const v = location.hash.slice(1).split("?")[0]; return VIEWS[v] ? v : "dashboard"; }
function render() {
  const v = currentView();
  document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("active", a.dataset.view === v));
  VIEWS[v]();
  hydrateIcons($("#main"));
}
window.addEventListener("hashchange", () => { render(); $("#main").focus({ preventScroll: true }); window.scrollTo(0, 0); });

// ------------------------------------------------------------------ shared pieces
function rowHTML(a, opts = {}) {
  const done = isDone(a);
  const cat = a.category || "general", color = colorFor(a.course);
  return `<div class="row ${done ? "done" : ""}" data-open="${a.id}">
    <button class="check ${done ? "on" : ""}" data-toggle="${a.id}" title="${done ? "Mark not done" : "Mark done"}" aria-label="Toggle done">${icon("check")}</button>
    <div class="cat-icon" style="background:${color}1a;color:${color}">${icon(CAT_ICON[cat] || "file")}</div>
    <div class="row-main">
      <div class="row-title">${esc(a.title)}</div>
      <div class="row-meta">${courseChip(a.course)}${statusChip(a)}${a.priority === "high" ? `<span class="chip chip-amber">${icon("star")}Priority</span>` : ""}
        ${opts.source ? `<span>${esc(sourceName(a))}</span>` : ""}</div>
    </div>
    <div class="row-side">
      <div class="due ${dueClass(a)}">${esc(dueText(a.due_at))}</div>
      <div class="muted small est">${a.due_at && !done ? esc(relText(a.due_at)) + " · " : ""}${esc(minutesLabel(a.est_minutes || a.suggested_minutes))}</div>
    </div>
  </div>`;
}
function bindRows(root) {
  root.querySelectorAll("[data-toggle]").forEach(b => b.addEventListener("click", async ev => {
    ev.stopPropagation();
    const a = S.assignments.find(x => x.id === +b.dataset.toggle);
    const next = isDone(a) ? "todo" : "done";
    if (["submitted", "graded"].includes(a.platform_status) && next === "todo") return toast("Your platform says this was submitted.");
    await busy(null, async () => {
      await api("PATCH", `/api/assignments/${a.id}`, { status: next });
      await reloadAssignments();
      render();
      if (next === "done") toast("Nice work! Marked done.");
    });
  }));
  root.querySelectorAll("[data-open]").forEach(r => r.addEventListener("click", () => openAssignment(+r.dataset.open)));
}

function emptyConnect() {
  return `<div class="card card-pad empty">
    ${icon("plug")}
    <h3>Connect your school platform</h3>
    <p>Link Canvas, Schoology, Moodle or any platform with a calendar feed (Google Classroom, Blackboard, Brightspace…) and your assignments show up here.</p>
    <div class="actions" style="justify-content:center">
      <button class="btn btn-primary" data-connect="canvas">${icon("plus")}Connect Canvas</button>
      <button class="btn" data-connect="schoology">${icon("plus")}Connect Schoology</button>
      <a class="btn" href="#connections">More platforms</a>
      <button class="btn btn-ghost" data-connect="demo">${icon("play")}Try with sample data</button>
    </div>
  </div>`;
}
function bindConnectButtons(root) {
  root.querySelectorAll("[data-connect]").forEach(b => b.addEventListener("click", () => connectModal(b.dataset.connect)));
}

// ------------------------------------------------------------------ dashboard
function renderDashboard() {
  const main = $("#main");
  const all = S.assignments.filter(a => a.status !== "hidden");
  const open = all.filter(isOpen);
  const now = new Date();
  const overdue = open.filter(a => a.due_at && new Date(a.due_at) < now);
  const today = open.filter(a => a.due_at && new Date(a.due_at) >= now && dayDiff(new Date(a.due_at), now) === 0);
  const week = open.filter(a => a.due_at && new Date(a.due_at) >= now && dayDiff(new Date(a.due_at), now) < 7);
  const weekAll = all.filter(a => a.due_at && Math.abs(dayDiff(new Date(a.due_at), now)) < 7);
  const doneWeek = weekAll.filter(isDone).length;
  const pct = weekAll.length ? Math.round(doneWeek / weekAll.length * 100) : 0;
  const hour = now.getHours();
  const hello = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  const name = S.settings.student_name ? `, ${esc(S.settings.student_name)}` : "";
  const workLeft = open.filter(a => a.due_at && dayDiff(new Date(a.due_at), now) < 7)
    .reduce((s, a) => s + Math.max(0, (a.est_minutes || a.suggested_minutes || 0) - (a.progress_minutes || 0)), 0);

  let headline = "You're all caught up. 🎉";
  if (overdue.length) headline = `${overdue.length} overdue ${overdue.length === 1 ? "item needs" : "items need"} attention first.`;
  else if (today.length) headline = `${today.length} due today. You've got this.`;
  else if (week.length) headline = `${week.length} due in the next 7 days, about ${minutesLabel(workLeft)} of work.`;

  const upNext = open.slice().sort((a, b) => (a.due_at || "9") < (b.due_at || "9") ? -1 : 1).slice(0, 8);

  main.innerHTML = `
    <div class="hero">
      <div class="hero-row">
        <div>
          <div class="small" style="opacity:.85;font-weight:600">${esc(now.toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" }))}</div>
          <h1>${hello}${name}</h1>
          <p>${headline}</p>
          <div class="actions">
            <a class="btn btn-sm" href="#schedule" style="background:rgba(255,255,255,.18);border-color:transparent;color:#fff">${icon("calendar")}My plan</a>
            <button class="btn btn-sm" id="hero-sync" style="background:rgba(255,255,255,.18);border-color:transparent;color:#fff">${icon("refresh")}Sync now</button>
          </div>
        </div>
        <div class="ring" style="--p:${pct}" title="Completed this week"><span>${pct}%<small>this week</small></span></div>
      </div>
    </div>
    ${S.connections.length ? "" : emptyConnect()}
    <div class="stats">
      ${statCard("red", "flame", overdue.length, "Overdue", "overdue")}
      ${statCard("amber", "clock", today.length, "Due today", "today")}
      ${statCard("blue", "target", week.length, "Next 7 days", "week")}
      ${statCard("green", "trophy", doneWeek, "Done this week", "done")}
    </div>
    <div class="grid grid-dash">
      <div class="stack">
        <div class="card">
          <div class="card-head"><h2>Up next</h2><a href="#assignments" class="small">View all →</a></div>
          <div class="card-body list" id="upnext">${upNext.length ? upNext.map(a => rowHTML(a)).join("") :
            `<div class="empty">${icon("trophy")}<h3>Nothing on your list</h3><p>Sync, or add something yourself.</p></div>`}</div>
        </div>
        <div class="card">
          <div class="card-head"><h2>Workload, next 7 days</h2><span class="muted small">${minutesLabel(workLeft) || "0 min"} left</span></div>
          <div class="card-body">${workloadChart(open)}</div>
        </div>
      </div>
      <div class="stack">
        <div class="card">
          <div class="card-head"><h2>Today's plan</h2><a href="#schedule" class="small">Schedule →</a></div>
          <div class="card-body">${todayPlan()}</div>
        </div>
        ${S.plan && S.plan.warnings.filter(w => w.severity === "high").length ? `<div class="card">
          <div class="card-head"><h2>Heads up</h2></div>
          <div class="card-body">${warningsHTML(S.plan.warnings.filter(w => w.severity === "high").slice(0, 4))}</div></div>` : ""}
        <div class="card">
          <div class="card-head"><h2>Classes</h2></div>
          <div class="card-body">${coursesHTML(all)}</div>
        </div>
      </div>
    </div>`;
  bindRows(main);
  bindConnectButtons(main);
  main.querySelectorAll("[data-stat]").forEach(el => el.addEventListener("click", () => {
    S.filter = el.dataset.stat === "done" ? "done" : el.dataset.stat === "overdue" ? "overdue" : "open";
    location.hash = "assignments";
  }));
  main.querySelectorAll("[data-plan]").forEach(el => el.addEventListener("click", () => openAssignment(+el.dataset.plan)));
  bindWarnings(main);
  $("#hero-sync").addEventListener("click", e => syncAll(e.currentTarget));
}
function statCard(color, ic, num, label, key) {
  return `<div class="card stat ${color}" data-stat="${key}" role="button" tabindex="0">
    <div class="stat-icon">${icon(ic)}</div><div><div class="stat-num">${num}</div><div class="stat-label">${label}</div></div></div>`;
}
function workloadChart(open) {
  const days = [];
  const planned = {};
  (S.plan?.per_day || []).forEach(d => { planned[d.date] = d.minutes; });
  for (let i = 0; i < 7; i++) {
    const d = startOfDay(new Date()); d.setDate(d.getDate() + i);
    const items = open.filter(a => a.due_at && dayDiff(new Date(a.due_at), d) === 0);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    days.push({ d, count: items.length, plan: planned[key] || 0 });
  }
  const maxPlan = Math.max(60, ...days.map(x => x.plan));
  return `<div class="bars">${days.map((x, i) => `<div class="bar" title="${x.count} due · ${minutesLabel(x.plan) || "nothing"} planned">
      <span class="bar-num">${x.count || ""}</span>
      <div class="bar-col" style="height:${Math.max(4, x.plan / maxPlan * 100)}%"><div class="seg-plan" style="height:100%"></div></div>
      <span class="bar-label ${i === 0 ? "today" : ""}">${i === 0 ? "Today" : x.d.toLocaleDateString([], { weekday: "short" })}</span>
    </div>`).join("")}</div>
    <div class="legend"><span><i style="background:var(--accent)"></i>Planned study time</span><span><b style="color:var(--text-2)">#</b> items due</span></div>`;
}
function todayPlan() {
  if (!S.plan) return `<div class="muted">No plan yet.</div>`;
  const today = S.plan.blocks.filter(b => dayDiff(new Date(b.start), new Date()) === 0);
  if (!today.length) {
    const next = S.plan.blocks[0];
    return `<div class="empty" style="padding:14px">${icon("calendar")}<h3>Nothing planned for today</h3>
      <p>${next ? `Next session: <b>${esc(fmtDay(new Date(next.start)))} ${esc(fmtTime(new Date(next.start)))}</b>, ${esc(next.title)}` : "Add free time in Schedule to get a plan."}</p></div>`;
  }
  return today.map(b => `<div class="plan-item" data-plan="${b.assignment_id}">
      <div class="plan-time">${esc(fmtTime(new Date(b.start)))}<small>${esc(minutesLabel(b.minutes))}</small></div>
      <div class="plan-bar" style="background:${colorFor(b.course)}"></div>
      <div class="plan-body"><div class="t">${esc(b.title)}</div><div class="muted small">${esc(b.course)}${b.parts > 1 ? ` · part ${b.part} of ${b.parts}` : ""}</div></div>
    </div>`).join("");
}
function coursesHTML(all) {
  const by = {};
  all.forEach(a => { const c = a.course || "Other"; (by[c] ||= { total: 0, done: 0, open: 0 }); by[c].total++; if (isDone(a)) by[c].done++; else by[c].open++; });
  const rows = Object.entries(by).sort((a, b) => b[1].open - a[1].open);
  if (!rows.length) return `<div class="muted">Your classes appear here after syncing.</div>`;
  return rows.map(([c, v]) => `<div class="course-row">
      <span class="chip" style="color:${colorFor(c)};background:${colorFor(c)}1f;padding:4px"><span class="dot"></span></span>
      <span class="name">${esc(c)}</span><span class="muted small">${v.open} to do</span>
      <div class="progress" title="${v.done}/${v.total} done"><span style="width:${v.total ? v.done / v.total * 100 : 0}%;background:${colorFor(c)}"></span></div>
    </div>`).join("");
}
function warningsHTML(ws) {
  return ws.map(w => `<div class="warn-item ${w.severity}" data-warn="${w.assignment_id}">${icon("alert")}
      <div><b>${esc(w.title)}</b><div class="muted small">${esc(w.message)}</div></div></div>`).join("");
}
function bindWarnings(root) {
  root.querySelectorAll("[data-warn]").forEach(el => el.addEventListener("click", () => openAssignment(+el.dataset.warn)));
}

// ------------------------------------------------------------------ assignments
function renderAssignments() {
  const main = $("#main");
  const courses = [...new Set(S.assignments.map(a => a.course).filter(Boolean))].sort();
  const q = S.q.toLowerCase();
  let items = S.assignments.filter(a => {
    if (S.course && a.course !== S.course) return false;
    if (q && !(`${a.title} ${a.course}`.toLowerCase().includes(q))) return false;
    switch (S.filter) {
      case "open": return isOpen(a);
      case "overdue": return isOpen(a) && a.due_at && new Date(a.due_at) < new Date();
      case "in_progress": return isOpen(a) && a.status === "in_progress";
      case "done": return isDone(a) && a.status !== "hidden";
      case "hidden": return a.status === "hidden";
      default: return a.status !== "hidden";
    }
  });
  const groups = [["overdue", "Overdue"], ["today", "Today"], ["tomorrow", "Tomorrow"], ["week", "This week"], ["later", "Later"], ["none", "No due date"]];
  const byBucket = {};
  items.forEach(a => { (byBucket[bucket(a)] ||= []).push(a); });
  if (S.filter === "done") Object.values(byBucket).forEach(l => l.reverse());
  const filters = [["open", "To do"], ["overdue", "Overdue"], ["in_progress", "In progress"], ["done", "Done"], ["all", "All"], ["hidden", "Hidden"]];

  main.innerHTML = `
    <div class="page-head">
      <div><h1>Assignments</h1><div class="sub">${S.assignments.filter(isOpen).length} to do across ${courses.length} ${courses.length === 1 ? "class" : "classes"}</div></div>
      <div class="page-actions"><button class="btn" id="add-manual">${icon("plus")}Add assignment</button>
        <button class="btn btn-primary" id="sync-here">${icon("refresh")}Sync</button></div>
    </div>
    <div class="toolbar">
      <div class="search">${icon("search")}<input id="q" placeholder="Search assignments…" value="${esc(S.q)}"></div>
      <select id="course-filter"><option value="">All classes</option>${courses.map(c => `<option ${c === S.course ? "selected" : ""}>${esc(c)}</option>`).join("")}</select>
    </div>
    <div class="seg" id="filters">${filters.map(([k, l]) => `<button data-f="${k}" class="${S.filter === k ? "on" : ""}">${l}</button>`).join("")}</div>
    <div id="groups">
      ${!S.connections.length && !S.assignments.length ? `<div style="margin-top:18px">${emptyConnect()}</div>` : ""}
      ${items.length ? groups.filter(([k]) => byBucket[k]).map(([k, label]) => `
        <div class="group-title ${k === "overdue" ? "red" : ""}">${label}<span class="count">${byBucket[k].length}</span></div>
        <div class="card list" style="padding:4px 6px">${byBucket[k].map(a => rowHTML(a, { source: true })).join("")}</div>`).join("")
        : S.assignments.length ? `<div class="card empty" style="margin-top:18px">${icon("search")}<h3>Nothing here</h3><p>Try another filter.</p></div>` : ""}
    </div>`;
  bindRows(main);
  bindConnectButtons(main);
  $("#filters").addEventListener("click", e => { const f = e.target.dataset?.f; if (f) { S.filter = f; renderAssignments(); hydrateIcons(main); } });
  $("#course-filter").addEventListener("change", e => { S.course = e.target.value; renderAssignments(); hydrateIcons(main); });
  const qi = $("#q");
  qi.addEventListener("input", e => { S.q = e.target.value; renderAssignments(); hydrateIcons(main); const n = $("#q"); n.focus(); n.setSelectionRange(n.value.length, n.value.length); });
  $("#add-manual").addEventListener("click", () => manualModal());
  $("#sync-here").addEventListener("click", e => syncAll(e.currentTarget));
}

// ------------------------------------------------------------------ assignment drawer
function closeDrawer() {
  $("#drawer").classList.remove("open");
  $("#drawer").setAttribute("aria-hidden", "true");
  $("#drawer-backdrop").hidden = true;
  S.openId = null;
}
$("#drawer-backdrop").addEventListener("click", closeDrawer);
document.addEventListener("keydown", e => { if (e.key === "Escape") { if (!$("#modal-backdrop").hidden) closeModal(); else closeDrawer(); } });

async function openAssignment(id) {
  S.openId = id;
  const drawer = $("#drawer");
  drawer.innerHTML = `<div class="drawer-body"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div>`;
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  $("#drawer-backdrop").hidden = false;
  try { drawAssignment(await api("GET", `/api/assignments/${id}`)); }
  catch (e) { toast(e.message, "error"); closeDrawer(); }
}

function drawAssignment(a) {
  const drawer = $("#drawer"), g = a.guide, done = isDone(a);
  const total = a.est_minutes || g.est_minutes, prog = Math.min(total, a.progress_minutes || 0);
  const manual = a.source_kind === "manual";
  const platformLabel = (S.status.platforms.find(p => p.kind === a.source_kind)?.label || a.source_name || "platform").replace(" (any platform)", "");
  const desc = a.description || "";
  const coach = a.ai_coach;
  drawer.innerHTML = `
    <div class="drawer-head">
      <div class="top">
        <div style="display:flex;gap:6px;flex-wrap:wrap">${courseChip(a.course)}<span class="chip chip-accent">${icon(CAT_ICON[a.category] || "file")}${esc(a.category_label)}</span>${statusChip(a)}</div>
        <button class="btn btn-ghost btn-sm" id="d-close" aria-label="Close">${icon("x")}</button>
      </div>
      <h2>${esc(a.title)}</h2>
      <div class="facts">
        <span class="due ${dueClass(a)}">${icon("clock")}${esc(dueText(a.due_at))}${a.due_at && !done ? ` (${esc(relText(a.due_at))})` : ""}</span>
        ${a.points != null ? `<span>${icon("star")}${esc(+a.points)} pts</span>` : ""}
        <span>${icon("plug")}${esc(sourceName(a))}</span>
      </div>
      <div class="actions">
        <div class="seg" id="d-status">${[["todo", "To do"], ["in_progress", "In progress"], ["done", "Done"]].map(([k, l]) =>
          `<button data-s="${k}" class="${(a.status === k || (k === "done" && done)) ? "on" : ""}">${l}</button>`).join("")}</div>
        <button class="btn btn-sm ${a.priority === "high" ? "btn-primary" : ""}" id="d-prio" title="Prioritize in the schedule">${icon("star")}${a.priority === "high" ? "Priority" : "Prioritize"}</button>
        ${a.url ? `<a class="btn btn-sm" href="${esc(a.url)}" target="_blank" rel="noopener">${icon("external")}Open in ${esc(platformLabel)}</a>` : ""}
      </div>
    </div>
    <div class="drawer-body">
      <div class="card card-pad section">
        <h3>${icon("clock")}Time</h3>
        <div class="time-box">
          <div class="progress"><span style="width:${total ? prog / total * 100 : 0}%"></span></div>
          <span class="small muted">${minutesLabel(prog) || "0 min"} of</span>
          <input type="number" min="5" step="5" id="d-est" value="${total}" aria-label="Estimated minutes"><span class="small muted">min</span>
        </div>
        <div class="actions" style="margin-top:10px">
          <span class="small muted">Log time:</span>
          ${[15, 30, 45, 60].map(m => `<button class="btn btn-sm" data-log="${m}">+${m}m</button>`).join("")}
          ${prog ? `<button class="btn btn-sm btn-ghost" data-log="${-prog}">Reset</button>` : ""}
        </div>
      </div>

      <div class="card card-pad section">
        <h3>${icon("file")}What to do</h3>
        ${desc ? `<div class="desc ${desc.length > 1400 ? "clamp" : ""}" id="d-desc">${desc}</div>
          ${desc.length > 1400 ? `<button class="btn btn-sm btn-ghost" id="d-more">Show all</button>` : ""}`
          : `<p class="muted" style="margin:0">No instructions came with this item${a.url ? `. Open it in ${esc(platformLabel)} for details.` : "."}</p>`}
        ${a.allowed_extensions?.length ? `<p class="small muted" style="margin:10px 0 0">Allowed files: ${a.allowed_extensions.map(e => "." + esc(e)).join(", ")}</p>` : ""}
      </div>

      <div class="card card-pad section">
        <h3>${icon("upload")}How to submit</h3>
        <div class="sub-cards">${g.submission.map(s => `<div class="sub-card"><div class="ic">${icon(SUB_ICON[s.type] || "external")}</div>
          <div><b>${esc(s.label)}</b><p>${esc(s.how)}</p></div></div>`).join("")}</div>
        ${a.url ? `<div class="actions"><a class="btn btn-primary btn-sm" href="${esc(a.url)}" target="_blank" rel="noopener">${icon("external")}Go to submission page</a></div>` : ""}
      </div>

      <div class="card card-pad section" id="d-coach">${coachHTML(coach)}</div>

      <div class="card card-pad section">
        <h3>${icon("list")}Game plan <span class="muted small" style="font-weight:500">· about ${minutesLabel(g.est_minutes)}</span></h3>
        <ol class="steps">${g.steps.map(s => `<li><div><span class="st">${esc(s.title)}</span><span class="sm">${minutesLabel(s.minutes)}</span><div class="sd">${esc(s.detail)}</div></div></li>`).join("")}</ol>
      </div>

      <div class="card card-pad section">
        <h3>${icon("lightbulb")}Tips</h3>
        <ul class="tips">${g.tips.map(t => `<li>${icon("lightbulb")}<span>${esc(t)}</span></li>`).join("")}</ul>
        <h3 style="margin-top:16px">${icon("check")}Before you submit</h3>
        <ul class="tips check-list">${g.checklist.map(t => `<li>${icon("check")}<span>${esc(t)}</span></li>`).join("")}</ul>
      </div>

      <div class="card card-pad section">
        <h3>${icon("edit")}My notes</h3>
        <textarea id="d-notes" placeholder="Ideas, questions for the teacher, group roles…">${esc(a.notes)}</textarea>
      </div>

      <div class="actions">
        ${manual ? `<button class="btn btn-sm" id="d-edit">${icon("edit")}Edit</button><button class="btn btn-sm btn-danger" id="d-del">${icon("trash")}Delete</button>`
          : a.status === "hidden" ? `<button class="btn btn-sm" id="d-unhide">${icon("eye")}Show again</button>`
          : `<button class="btn btn-sm btn-ghost" id="d-hide" title="Hide things that aren't real assignments (e.g. class meetings from a calendar feed)">${icon("eyeoff")}Hide from my list</button>`}
      </div>
    </div>`;

  const patch = async body => {
    const updated = await api("PATCH", `/api/assignments/${a.id}`, body);
    await reloadAssignments();
    render();
    if (S.openId === a.id) drawAssignment(updated);
    return updated;
  };
  $("#d-close").addEventListener("click", closeDrawer);
  $("#d-status").addEventListener("click", e => {
    const s = e.target.dataset?.s;
    if (!s) return;
    if (s !== "done" && ["submitted", "graded"].includes(a.platform_status)) return toast(`${platformLabel} says this was already submitted.`);
    busy(null, () => patch({ status: s }).then(() => s === "done" && toast("Marked done. 🎉")));
  });
  $("#d-prio").addEventListener("click", () => busy(null, () => patch({ priority: a.priority === "high" ? "normal" : "high" })));
  $("#d-est").addEventListener("change", e => busy(null, () => patch({ est_minutes: Math.max(5, +e.target.value || 0) })));
  drawer.querySelectorAll("[data-log]").forEach(b => b.addEventListener("click", () => busy(b, async () => {
    const updated = await api("POST", `/api/assignments/${a.id}/progress`, { minutes: +b.dataset.log });
    await reloadAssignments(); render(); drawAssignment(updated);
    if (+b.dataset.log > 0) toast(updated.work_left ? `Logged. About ${minutesLabel(updated.work_left)} to go.` : "That's the estimate done. Ready to submit?");
  })));
  $("#d-more")?.addEventListener("click", e => { $("#d-desc").classList.remove("clamp"); e.target.remove(); });
  $("#d-notes").addEventListener("change", e => busy(null, async () => { await api("PATCH", `/api/assignments/${a.id}`, { notes: e.target.value }); toast("Notes saved."); }));
  $("#d-hide")?.addEventListener("click", () => busy(null, async () => { await patch({ status: "hidden" }); toast("Hidden. Find it under the Hidden filter."); closeDrawer(); }));
  $("#d-unhide")?.addEventListener("click", () => busy(null, () => patch({ status: "todo" })));
  $("#d-del")?.addEventListener("click", () => {
    if (!confirm("Delete this assignment?")) return;
    busy(null, async () => { await api("DELETE", `/api/assignments/${a.id}`); await reloadAssignments(); render(); closeDrawer(); toast("Deleted."); });
  });
  $("#d-edit")?.addEventListener("click", () => manualModal(a));
  bindCoach(a);
}

function coachHTML(c) {
  const ai = S.status?.ai;
  if (!c) {
    return `<h3>${icon("sparkles")}AI study coach</h3>
      <p class="muted" style="margin:0 0 12px">Get a plain-English breakdown of what's being asked, the requirements, step-by-step plan, tips and what to ask your teacher. It coaches; it won't do the work for you.</p>
      <button class="btn btn-ai" id="d-ai">${icon("sparkles")}Coach me on this</button>
      ${ai && !ai.configured ? `<p class="small muted" style="margin:10px 0 0">Needs a Claude API key on the computer running the app (set <code>ANTHROPIC_API_KEY</code>). The game plan and tips below work without it.</p>` : ""}`;
  }
  const list = (items, cls = "", ic = "lightbulb") => items?.length ? `<ul class="tips ${cls}">${items.map(t => `<li>${icon(ic)}<span>${esc(t)}</span></li>`).join("")}</ul>` : "";
  return `<div class="ai-box">
      <h3 style="margin:0">${icon("sparkles")}AI study coach <span class="muted small" style="font-weight:500">· about ${minutesLabel(c.estimated_minutes)}</span></h3>
      <p style="margin:10px 0 0">${esc(c.summary)}</p>
      ${c.requirements?.length ? `<h4>Requirements</h4>${list(c.requirements, "check-list", "check")}` : ""}
      <h4>Steps</h4>
      <ol class="steps">${c.steps.map(s => `<li><div><span class="st">${esc(s.title)}</span><span class="sm">${minutesLabel(s.minutes)}</span><div class="sd">${esc(s.detail)}</div></div></li>`).join("")}</ol>
      <h4>Tips</h4>${list(c.tips)}
      ${c.pitfalls?.length ? `<h4>Avoid</h4>${list(c.pitfalls, "warn", "alert")}` : ""}
      ${c.submission_checklist?.length ? `<h4>Before you submit</h4>${list(c.submission_checklist, "check-list", "check")}` : ""}
      ${c.questions_for_teacher?.length ? `<h4>Worth asking your teacher</h4>${list(c.questions_for_teacher, "", "question")}` : ""}
      <div class="actions"><button class="btn btn-sm" id="d-ai">${icon("refresh")}Coach again</button>
        <button class="btn btn-sm btn-ghost" id="d-ai-est">Use ${minutesLabel(c.estimated_minutes)} as my estimate</button></div>
    </div>`;
}
function bindCoach(a) {
  $("#d-ai")?.addEventListener("click", e => busy(e.currentTarget, async () => {
    const updated = await api("POST", `/api/assignments/${a.id}/coach`);
    await reloadAssignments();
    if (S.openId === a.id) drawAssignment(updated);
  }));
  $("#d-ai-est")?.addEventListener("click", () => busy(null, async () => {
    const updated = await api("PATCH", `/api/assignments/${a.id}`, { est_minutes: a.ai_coach.estimated_minutes });
    await reloadAssignments(); render(); drawAssignment(updated); toast("Estimate updated; the schedule now uses it.");
  }));
}

// ------------------------------------------------------------------ modals
function openModal(html) {
  $("#modal").innerHTML = html;
  $("#modal-backdrop").hidden = false;
  hydrateIcons($("#modal"));
  setTimeout(() => $("#modal").querySelector("input, select, textarea")?.focus(), 30);
}
function closeModal() { $("#modal-backdrop").hidden = true; $("#modal").innerHTML = ""; }
$("#modal-backdrop").addEventListener("click", e => { if (e.target.id === "modal-backdrop") closeModal(); });

function logo(kind, size = 44) {
  const st = PLATFORM_STYLE[kind] || PLATFORM_STYLE.manual;
  const inner = st.letter || icon(kind === "ical" ? "calendar" : kind === "demo" ? "play" : "edit");
  return `<div class="logo" style="background:${st.color};width:${size}px;height:${size}px">${inner}</div>`;
}

function connectModal(kind, conn) {
  const p = S.status.platforms.find(x => x.kind === kind);
  if (!p) return;
  if (kind === "demo" && !conn) {
    return busy(null, async () => {
      const r = await api("POST", "/api/connections", { kind: "demo", config: {} });
      await loadAll(); render(); toast(`Loaded ${r.sync.total} sample assignments.`);
    });
  }
  const cfg = conn?.config || {};
  const fields = p.fields.map(f => {
    const val = f.secret ? "" : (cfg[f.key] ?? "");
    const ph = f.secret && conn?.secrets_set?.includes(f.key) ? "Saved. Leave blank to keep it" : (f.placeholder || "");
    if (f.type === "select") {
      return `<label class="field">${esc(f.label)}<select name="${f.key}">${f.options.map(o => `<option ${o === val ? "selected" : ""}>${esc(o)}</option>`).join("")}</select></label>`;
    }
    return `<label class="field">${esc(f.label)}<input name="${f.key}" type="${f.type === "password" ? "password" : "text"}" autocomplete="off" spellcheck="false" value="${esc(val)}" placeholder="${esc(ph)}"></label>`;
  }).join("");
  openModal(`
    <div class="modal-head"><div style="display:flex;gap:12px;align-items:center">${logo(kind, 40)}<div><h2>${conn ? "Edit" : "Connect"} ${esc(p.label)}</h2><div class="muted small">${esc(p.detail)}</div></div></div>
      <button class="btn btn-ghost btn-sm" data-close>${icon("x")}</button></div>
    <form class="form" id="conn-form">
      <div class="help">${p.help}</div>
      <label class="field">Name (optional)<input name="_name" value="${esc(conn?.name || "")}" placeholder="${esc(kind === "ical" ? "e.g. Google Classroom – Chemistry" : p.label)}"></label>
      ${fields}
      <div class="error-box hidden" id="conn-err"></div>
      <p class="small muted" style="margin:0">Your token/key is stored only on the computer running this app and is only sent to ${esc(p.label.replace(" (any platform)", ""))}.</p>
      <div class="modal-foot"><button type="button" class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" id="conn-save">${icon("check")}${conn ? "Save & sync" : "Test & connect"}</button></div>
    </form>`);
  $("#modal").querySelectorAll("[data-close]").forEach(b => b.addEventListener("click", closeModal));
  $("#conn-form").addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(e.target), config = {};
    for (const [k, v] of fd.entries()) if (k !== "_name") config[k] = v;
    const btn = $("#conn-save"), err = $("#conn-err");
    err.classList.add("hidden");
    btn.classList.add("loading"); btn.disabled = true;
    try {
      const r = conn ? await api("PATCH", `/api/connections/${conn.id}`, { name: fd.get("_name"), config })
                     : await api("POST", "/api/connections", { kind, name: fd.get("_name"), config });
      closeModal();
      await loadAll(); render();
      toast(`${r.connection.name}: ${r.sync.total} items synced${r.sync.added ? ` (${r.sync.added} new)` : ""}.`);
    } catch (ex) {
      err.textContent = ex.message; err.classList.remove("hidden");
    } finally { btn.classList.remove("loading"); btn.disabled = false; }
  });
}

function toLocalInput(iso) {
  if (!iso) return "";
  const d = new Date(iso), p = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}
function manualModal(a) {
  const courses = [...new Set(S.assignments.map(x => x.course).filter(Boolean))].sort();
  const subs = [["upload", "File upload"], ["text", "Text entry"], ["url", "Link"], ["paper", "On paper / in class"], ["quiz", "Online quiz"], ["discussion", "Discussion"], ["media", "Recording"], ["unknown", "Not sure"]];
  const descText = a ? (new DOMParser().parseFromString(a.description || "", "text/html").body.innerText || "") : "";
  openModal(`
    <div class="modal-head"><h2>${a ? "Edit assignment" : "Add an assignment"}</h2><button class="btn btn-ghost btn-sm" data-close>${icon("x")}</button></div>
    <form class="form" id="man-form">
      <label class="field">Title<input name="title" required value="${esc(a?.title || "")}" placeholder="e.g. Chapter 5 worksheet"></label>
      <div class="field-row">
        <label class="field">Class<input name="course" list="course-list" value="${esc(a?.course || "")}" placeholder="e.g. Chemistry"></label>
        <label class="field">Due<input name="due_at" type="datetime-local" value="${toLocalInput(a?.due_at)}"></label>
      </div>
      <datalist id="course-list">${courses.map(c => `<option value="${esc(c)}">`).join("")}</datalist>
      <label class="field">Instructions<textarea name="description" placeholder="What do you need to do?">${esc(descText)}</textarea></label>
      <div class="field-row">
        ${a ? "" : `<label class="field">How is it submitted?<select name="submission">${subs.map(([k, l]) => `<option value="${k}">${l}</option>`).join("")}</select></label>`}
        <label class="field">Estimated minutes<input name="est_minutes" type="number" min="5" step="5" value="${a?.est_minutes || ""}" placeholder="Auto"></label>
        <label class="field">Link (optional)<input name="url" value="${esc(a?.url || "")}" placeholder="https://"></label>
      </div>
      <div class="error-box hidden" id="man-err"></div>
      <div class="modal-foot"><button type="button" class="btn" data-close>Cancel</button><button class="btn btn-primary">${icon("check")}${a ? "Save" : "Add"}</button></div>
    </form>`);
  $("#modal").querySelectorAll("[data-close]").forEach(b => b.addEventListener("click", closeModal));
  $("#man-form").addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const due = fd.get("due_at") ? new Date(fd.get("due_at")).toISOString() : null;
    const body = { title: fd.get("title"), course: fd.get("course"), due_at: due, description: fd.get("description"),
      url: fd.get("url"), est_minutes: fd.get("est_minutes") ? +fd.get("est_minutes") : null };
    if (!a) body.submission_types = [fd.get("submission")];
    try {
      const saved = a ? await api("PATCH", `/api/assignments/${a.id}`, body) : await api("POST", "/api/assignments", body);
      closeModal();
      await loadAll(); render();
      if (a) drawAssignment(saved); else toast("Added.");
    } catch (ex) { const err = $("#man-err"); err.textContent = ex.message; err.classList.remove("hidden"); }
  });
}

// ------------------------------------------------------------------ connections
function renderConnections() {
  const main = $("#main");
  const plats = S.status.platforms;
  main.innerHTML = `
    <div class="page-head"><div><h1>Connections</h1><div class="sub">Link every platform your classes use. Everything syncs into one list.</div></div>
      ${S.connections.length ? `<div class="page-actions"><button class="btn btn-primary" id="sync-here">${icon("refresh")}Sync all</button></div>` : ""}</div>
    ${S.connections.length ? `<div class="card" style="margin-bottom:22px">
      <div class="card-head"><h2>Connected</h2></div>
      ${S.connections.map(c => `<div class="conn">
        ${logo(c.kind, 38)}
        <div class="info"><b>${esc(c.name)}</b>
          <span class="muted small">${esc(c.config.account || "")}${c.config.account ? " · " : ""}${c.item_count} items · ${c.last_sync ? `synced ${esc(relText(c.last_sync))}` : "never synced"}</span>
          ${c.last_error ? `<div class="error-box" style="margin-top:6px">${esc(c.last_error)}</div>` : ""}</div>
        ${c.kind === "manual" ? `<span class="muted small">Added by you</span>` : `
        <button class="btn btn-sm" data-sync="${c.id}">${icon("refresh")}Sync</button>
        ${c.kind !== "demo" ? `<button class="btn btn-sm btn-ghost" data-edit="${c.id}">${icon("edit")}Edit</button>` : ""}`}
        <button class="btn btn-sm btn-ghost btn-danger" data-remove="${c.id}" title="Remove">${icon("trash")}</button>
      </div>`).join("")}</div>` : ""}
    <h2 style="margin:0 0 12px">${S.connections.length ? "Add another" : "Choose your platform"}</h2>
    <div class="platforms">${plats.filter(p => p.kind !== "demo" || !S.connections.some(c => c.kind === "demo")).map(p => `
      <div class="card platform">${logo(p.kind)}<h3>${esc(p.label)}</h3><p>${esc(p.detail)}</p>
        <button class="btn ${p.kind === "demo" ? "" : "btn-primary"}" data-connect="${p.kind}">${icon(p.kind === "demo" ? "play" : "plus")}${p.kind === "demo" ? "Load sample data" : "Connect"}</button></div>`).join("")}
      <div class="card platform">${logo("manual")}<h3>Add by hand</h3><p>Paper handouts, things your teacher said in class, or anything not online.</p>
        <button class="btn" id="add-manual">${icon("plus")}Add assignment</button></div>
    </div>
    <p class="muted small" style="margin-top:18px">Using Google Classroom, Blackboard, Brightspace (D2L), Teams or PowerSchool? Choose <b>Calendar feed</b>; the form shows where to find the link for each one.</p>`;
  bindConnectButtons(main);
  $("#add-manual").addEventListener("click", () => manualModal());
  $("#sync-here")?.addEventListener("click", e => syncAll(e.currentTarget));
  main.querySelectorAll("[data-sync]").forEach(b => b.addEventListener("click", () => busy(b, async () => {
    const r = await api("POST", `/api/connections/${b.dataset.sync}/sync`);
    await loadAll(); render(); toast(`${r.connection.name}: ${r.sync.total} items (${r.sync.added} new).`);
  }).finally(async () => { await loadAll(); render(); })));
  main.querySelectorAll("[data-edit]").forEach(b => b.addEventListener("click", () => {
    const c = S.connections.find(x => x.id === +b.dataset.edit); connectModal(c.kind, c);
  }));
  main.querySelectorAll("[data-remove]").forEach(b => b.addEventListener("click", () => {
    const c = S.connections.find(x => x.id === +b.dataset.remove);
    if (!confirm(`Remove ${c.name}? Its assignments (and your notes on them) will be removed from the dashboard.`)) return;
    busy(b, async () => { await api("DELETE", `/api/connections/${c.id}`); await loadAll(); render(); toast("Removed."); });
  }));
}

async function syncAll(btn) {
  if (!S.connections.length) { location.hash = "connections"; return; }
  await busy(btn, async () => {
    const r = await api("POST", "/api/sync");
    await loadAll(); render();
    const bad = r.results.filter(x => !x.ok);
    if (bad.length) toast(`${bad.map(x => x.name).join(", ")}: ${bad[0].error}`, "error");
    else toast(`Synced ${r.results.reduce((s, x) => s + (x.total || 0), 0)} items.`);
  });
}

// ------------------------------------------------------------------ schedule
function renderSchedule() {
  const main = $("#main"), plan = S.plan;
  if (S.schedMode === null) S.schedMode = window.matchMedia("(max-width: 760px)").matches ? "list" : "week";
  const hi = plan ? plan.warnings.filter(w => w.severity === "high") : [];
  main.innerHTML = `
    <div class="page-head"><div><h1>Schedule</h1>
      <div class="sub">${plan ? `${minutesLabel(plan.total_minutes) || "0 min"} of study planned over the next ${plan.days} days, earliest deadlines first.` : ""}</div></div>
      <div class="page-actions">
        <div class="seg" id="mode"><button data-m="week" class="${S.schedMode === "week" ? "on" : ""}">Week</button><button data-m="list" class="${S.schedMode === "list" ? "on" : ""}">List</button></div>
        <button class="btn" id="rebuild">${icon("refresh")}Rebuild</button>
        <a class="btn" href="/api/schedule.ics" download>${icon("download")}Export to calendar</a>
      </div></div>
    ${plan && plan.warnings.length ? `<div class="card" style="margin-bottom:18px"><div class="card-head"><h2>${hi.length ? "Needs attention" : "Notes"}</h2></div>
      <div class="card-body">${warningsHTML(plan.warnings)}</div></div>` : ""}
    <div id="sched-view"></div>
    <div class="card" style="margin-top:18px" id="avail-card"></div>`;
  $("#mode").addEventListener("click", e => { const m = e.target.dataset?.m; if (m) { S.schedMode = m; renderSchedule(); hydrateIcons(main); } });
  $("#rebuild").addEventListener("click", e => busy(e.currentTarget, async () => { S.plan = await api("GET", "/api/schedule"); renderSchedule(); hydrateIcons(main); toast("Plan rebuilt."); }));
  bindWarnings(main);
  if (!plan || !plan.blocks.length) {
    $("#sched-view").innerHTML = `<div class="card empty">${icon("calendar")}<h3>${S.assignments.filter(isOpen).length ? "No study time fits yet" : "Nothing to schedule"}</h3>
      <p>${S.assignments.filter(isOpen).length ? "Add free time below and the plan fills in automatically." : "Connect a platform or add assignments, then come back."}</p></div>`;
  } else if (S.schedMode === "list") {
    $("#sched-view").innerHTML = agendaHTML(plan);
  } else {
    $("#sched-view").innerHTML = `<div class="cal-wrap">${weekHTML(plan)}</div><div class="agenda-only">${agendaHTML(plan)}</div>`;
    $("#wk-prev")?.addEventListener("click", () => { S.weekStart = Math.max(0, S.weekStart - 7); renderSchedule(); hydrateIcons(main); });
    $("#wk-next")?.addEventListener("click", () => { S.weekStart = Math.min(plan.days - 1, S.weekStart + 7); renderSchedule(); hydrateIcons(main); });
  }
  main.querySelectorAll("[data-blk]").forEach(el => el.addEventListener("click", () => openAssignment(+el.dataset.blk)));
  main.querySelectorAll("[data-did]").forEach(b => b.addEventListener("click", ev => {
    ev.stopPropagation();
    busy(b, async () => {
      await api("POST", `/api/assignments/${b.dataset.did}/progress`, { minutes: +b.dataset.min });
      await reloadAssignments(); renderSchedule(); hydrateIcons(main); toast("Logged. Plan updated.");
    });
  }));
  availabilityEditor();
}

function weekHTML(plan) {
  const start = startOfDay(new Date()); start.setDate(start.getDate() + S.weekStart);
  const days = [...Array(7)].map((_, i) => { const d = new Date(start); d.setDate(d.getDate() + i); return d; });
  const avail = S.settings.availability || {};
  const toMin = t => { const [h, m] = t.split(":").map(Number); return h * 60 + m; };
  let lo = 24 * 60, hiM = 0;
  Object.values(avail).flat().forEach(w => { lo = Math.min(lo, toMin(w[0])); hiM = Math.max(hiM, toMin(w[1])); });
  plan.blocks.forEach(b => { const s = new Date(b.start), e = new Date(b.end); lo = Math.min(lo, s.getHours() * 60 + s.getMinutes()); hiM = Math.max(hiM, e.getHours() * 60 + e.getMinutes() || 1440); });
  if (lo >= hiM) { lo = 15 * 60; hiM = 21 * 60; }
  lo = Math.floor(lo / 60) * 60; hiM = Math.min(24 * 60, Math.ceil(hiM / 60) * 60);
  const PX = 1.15, height = (hiM - lo) * PX;
  const y = d => ((d.getHours() * 60 + d.getMinutes()) - lo) * PX;
  const inRange = d => y(d) >= 0 && y(d) <= height;
  const wd = d => String((d.getDay() + 6) % 7);
  const dueItems = S.assignments.filter(a => isOpen(a) && a.due_at);
  const dateKey = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const perDay = Object.fromEntries((plan.per_day || []).map(x => [x.date, x.minutes]));
  const now = new Date();
  const hours = [];
  for (let m = lo; m <= hiM; m += 60) hours.push(m);
  const label = m => new Date(2000, 0, 1, Math.floor(m / 60), m % 60).toLocaleTimeString([], { hour: "numeric" });
  return `<div class="card" style="overflow:hidden">
    <div class="card-head"><h2>${esc(days[0].toLocaleDateString([], { month: "long", day: "numeric" }))} – ${esc(days[6].toLocaleDateString([], { month: "long", day: "numeric" }))}</h2>
      <div class="week-nav"><button class="btn btn-sm" id="wk-prev" ${S.weekStart <= 0 ? "disabled" : ""}>${icon("left")}</button>
        <button class="btn btn-sm" id="wk-next" ${S.weekStart + 7 >= plan.days ? "disabled" : ""}>${icon("right")}</button></div></div>
    <div class="cal-body"><div class="cal">
      <div class="cal-head"></div>
      ${days.map(d => `<div class="cal-head ${dayDiff(d, now) === 0 ? "today" : ""}"><div class="dn">${esc(d.toLocaleDateString([], { weekday: "short" }))}</div>
        <div class="dd">${d.getDate()}</div><div class="mins">${perDay[dateKey(d)] ? minutesLabel(perDay[dateKey(d)]) : "&nbsp;"}</div>
        ${(() => { const off = dueItems.filter(a => dayDiff(new Date(a.due_at), d) === 0 && !inRange(new Date(a.due_at)));
          return off.length ? `<div class="dues" title="${esc(off.map(a => `${a.title} (${fmtTime(new Date(a.due_at))})`).join("\n"))}">${off.length} due ${off.length === 1 ? esc(fmtTime(new Date(off[0].due_at))) : ""}</div>` : ""; })()}</div>`).join("")}
      <div class="cal-times" style="height:${height}px">${hours.map(m => `<span style="top:${(m - lo) * PX}px">${label(m)}</span>`).join("")}</div>
      ${days.map(d => {
        const free = (avail[wd(d)] || []).map(w => `<div class="free" style="top:${(toMin(w[0]) - lo) * PX}px;height:${(toMin(w[1]) - toMin(w[0])) * PX}px"></div>`).join("");
        const busyH = (S.settings.busy || []).filter(b => b.date === dateKey(d)).map(b =>
          `<div class="busy" style="top:${(toMin(b.start) - lo) * PX}px;height:${(toMin(b.end) - toMin(b.start)) * PX}px">${esc(b.label || "Busy")}</div>`).join("");
        const blks = plan.blocks.filter(b => dayDiff(new Date(b.start), d) === 0).map(b => {
          const s = new Date(b.start), e = new Date(b.end), h = Math.max(22, (e - s) / 60000 * PX);
          return `<div class="blk" data-blk="${b.assignment_id}" style="top:${y(s)}px;height:${h}px;background:${colorFor(b.course)}" title="${esc(b.title)} · ${esc(fmtTime(s))}–${esc(fmtTime(e))}">
            <b>${esc(b.title)}</b>${h > 34 ? `<small>${esc(fmtTime(s))} · ${minutesLabel(b.minutes)}${b.parts > 1 ? ` · ${b.part}/${b.parts}` : ""}</small>` : ""}</div>`;
        }).join("");
        const dues = dueItems.filter(a => dayDiff(new Date(a.due_at), d) === 0 && inRange(new Date(a.due_at))).map(a => {
          const t = new Date(a.due_at), top = Math.max(8, y(t));
          return `<div class="due-flag" style="top:${top}px" title="Due: ${esc(a.title)}"><span>Due: ${esc(a.title)}</span></div>`;
        }).join("");
        const nowLine = dayDiff(d, now) === 0 && y(now) >= 0 && y(now) <= height ? `<div class="now-line" style="top:${y(now)}px"></div>` : "";
        return `<div class="cal-col ${dayDiff(d, now) === 0 ? "today" : ""}" style="height:${height}px">
          ${hours.map(m => `<div class="hour" style="top:${(m - lo) * PX}px"></div>`).join("")}${free}${busyH}${dues}${blks}${nowLine}</div>`;
      }).join("")}
    </div></div></div>`;
}

function agendaHTML(plan) {
  const byDay = {};
  plan.blocks.forEach(b => { const k = startOfDay(new Date(b.start)).toISOString(); (byDay[k] ||= []).push(b); });
  const now = new Date();
  return Object.entries(byDay).map(([k, blocks]) => {
    const d = new Date(k), diff = dayDiff(d, now);
    const name = diff === 0 ? "Today" : diff === 1 ? "Tomorrow" : d.toLocaleDateString([], { weekday: "long" });
    const total = blocks.reduce((s, b) => s + b.minutes, 0);
    return `<div class="agenda-day"><h3>${esc(name)} <span class="muted">${esc(d.toLocaleDateString([], { month: "short", day: "numeric" }))} · ${minutesLabel(total)}</span></h3>
      ${blocks.map(b => `<div class="agenda-blk" data-blk="${b.assignment_id}">
        <span class="bar" style="background:${colorFor(b.course)}"></span>
        <div class="tm">${esc(fmtTime(new Date(b.start)))}<div class="muted small" style="font-weight:500">${minutesLabel(b.minutes)}</div></div>
        <div class="bd"><b>${esc(b.title)}</b><span class="muted small">${esc(b.course)}${b.parts > 1 ? ` · part ${b.part} of ${b.parts}` : ""}${b.due_at ? ` · due ${esc(dueText(b.due_at))}` : ""}</span></div>
        ${diff <= 0 ? `<button class="btn btn-sm" data-did="${b.assignment_id}" data-min="${b.minutes}" title="Log this session as done">${icon("check")}Did it</button>` : ""}
      </div>`).join("")}</div>`;
  }).join("");
}

function availabilityEditor() {
  const card = $("#avail-card");
  const s = JSON.parse(JSON.stringify(S.settings));
  const names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const draw = () => {
    card.innerHTML = `
      <div class="card-head"><h2>When can you work?</h2><button class="btn btn-primary btn-sm" id="av-save">${icon("check")}Save & rebuild</button></div>
      <div class="card-body">
        <p class="muted small" style="margin-top:0">Your free time each week. The planner only schedules study sessions inside these windows.</p>
        ${names.map((n, i) => `<div class="avail-day"><b>${n}</b><div class="wins">
          ${(s.availability[String(i)] || []).map((w, j) => `<div class="win">
            <input type="time" value="${w[0]}" data-d="${i}" data-j="${j}" data-k="0"><span class="muted">to</span>
            <input type="time" value="${w[1]}" data-d="${i}" data-j="${j}" data-k="1">
            <button class="btn btn-sm btn-ghost" data-rm="${i}:${j}" title="Remove">${icon("x")}</button></div>`).join("") || `<span class="muted small">Day off</span>`}
          <div><button class="btn btn-sm btn-ghost" data-add="${i}">${icon("plus")}Add time</button></div></div></div>`).join("")}
        <div class="field-row" style="margin-top:14px">
          <label class="field">Session length (min)<input type="number" min="20" max="180" step="5" data-num="block_minutes" value="${s.block_minutes}"></label>
          <label class="field">Break between (min)<input type="number" min="0" max="60" step="5" data-num="break_minutes" value="${s.break_minutes}"></label>
          <label class="field">Max study per day (min)<input type="number" min="20" max="900" step="10" data-num="max_minutes_per_day" value="${s.max_minutes_per_day}"></label>
          <label class="field">Finish early by (hours)<input type="number" min="0" max="72" step="1" data-num="buffer_hours" value="${s.buffer_hours}"></label>
          <label class="field">Plan ahead (days)<input type="number" min="3" max="60" step="1" data-num="horizon_days" value="${s.horizon_days}"></label>
        </div>
        <h3 style="margin:18px 0 8px">Busy times</h3>
        <p class="muted small" style="margin-top:0">Practice, work, appointments: one-off times to keep free.</p>
        ${(s.busy || []).map((b, j) => `<div class="win" style="margin-bottom:6px">
          <input type="date" value="${b.date}" data-busy="${j}" data-f="date" style="width:150px">
          <input type="time" value="${b.start}" data-busy="${j}" data-f="start"><span class="muted">to</span>
          <input type="time" value="${b.end}" data-busy="${j}" data-f="end">
          <input value="${esc(b.label || "")}" placeholder="Label" data-busy="${j}" data-f="label" style="width:150px">
          <button class="btn btn-sm btn-ghost" data-rmbusy="${j}">${icon("x")}</button></div>`).join("")}
        <button class="btn btn-sm" id="add-busy">${icon("plus")}Add busy time</button>
      </div>`;
    hydrateIcons(card);
    card.querySelectorAll("input[data-d]").forEach(inp => inp.addEventListener("change", () => { s.availability[inp.dataset.d][+inp.dataset.j][+inp.dataset.k] = inp.value; }));
    card.querySelectorAll("[data-rm]").forEach(b => b.addEventListener("click", () => { const [d, j] = b.dataset.rm.split(":"); s.availability[d].splice(+j, 1); draw(); }));
    card.querySelectorAll("[data-add]").forEach(b => b.addEventListener("click", () => { (s.availability[b.dataset.add] ||= []).push(["16:00", "18:00"]); draw(); }));
    card.querySelectorAll("[data-num]").forEach(inp => inp.addEventListener("change", () => { s[inp.dataset.num] = +inp.value; }));
    card.querySelectorAll("[data-busy]").forEach(inp => inp.addEventListener("change", () => { s.busy[+inp.dataset.busy][inp.dataset.f] = inp.value; }));
    card.querySelectorAll("[data-rmbusy]").forEach(b => b.addEventListener("click", () => { s.busy.splice(+b.dataset.rmbusy, 1); draw(); }));
    $("#add-busy").addEventListener("click", () => {
      const d = new Date(), p = n => String(n).padStart(2, "0");
      (s.busy ||= []).push({ date: `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`, start: "17:00", end: "19:00", label: "" }); draw();
    });
    $("#av-save").addEventListener("click", e => busy(e.currentTarget, async () => {
      for (const k of Object.keys(s.availability)) {
        for (const w of s.availability[k]) if (w[0] >= w[1]) throw new Error(`${names[+k]}: start time must be before end time.`);
      }
      S.settings = await api("PUT", "/api/settings", { availability: s.availability, busy: s.busy, block_minutes: s.block_minutes,
        break_minutes: s.break_minutes, max_minutes_per_day: s.max_minutes_per_day, buffer_hours: s.buffer_hours, horizon_days: s.horizon_days });
      S.plan = await api("GET", "/api/schedule");
      renderSchedule(); hydrateIcons($("#main")); toast("Saved. Plan rebuilt.");
    }));
  };
  draw();
}

// ------------------------------------------------------------------ settings
function renderSettings() {
  const main = $("#main"), ai = S.status.ai, theme = localStorage.getItem("theme") || "auto";
  const zones = typeof Intl.supportedValuesOf === "function" ? Intl.supportedValuesOf("timeZone") : [S.settings.timezone || "UTC"];
  main.innerHTML = `
    <div class="page-head"><div><h1>Settings</h1></div></div>
    <div class="grid" style="max-width:720px">
      <div class="card card-pad form">
        <h2>You</h2>
        <label class="field">Your first name (for the greeting)<input id="s-name" value="${esc(S.settings.student_name || "")}"></label>
        <label class="field">Time zone<select id="s-tz">${zones.map(z => `<option ${z === S.settings.timezone ? "selected" : ""}>${esc(z)}</option>`).join("")}</select></label>
        <div><span class="field" style="display:block;margin-bottom:6px;font-weight:600;font-size:13.5px;color:var(--text-2)">Appearance</span>
          <div class="seg" id="s-theme">${[["auto", "Auto"], ["light", "Light"], ["dark", "Dark"]].map(([k, l]) => `<button data-t="${k}" class="${theme === k ? "on" : ""}">${l}</button>`).join("")}</div></div>
        <div><button class="btn btn-primary" id="s-save">${icon("check")}Save</button></div>
      </div>
      <div class="card card-pad">
        <h2 style="margin-bottom:8px">${icon("sparkles")} AI study coach</h2>
        ${ai.configured ? `<p class="chip chip-green" style="margin:0 0 8px">${icon("check")}Connected (${esc(ai.model)})</p>
          <p class="muted" style="margin:0">Open any assignment and press <b>Coach me on this</b>.</p>`
          : `<p class="muted" style="margin:0">Optional. To turn it on, get an API key from <a href="https://platform.claude.com" target="_blank" rel="noopener">platform.claude.com</a>,
             set <code>ANTHROPIC_API_KEY</code> on the computer running this app, and restart it. Everything else works without it.</p>`}
      </div>
      <div class="card card-pad">
        <h2 style="margin-bottom:8px">Privacy</h2>
        <p class="muted" style="margin:0">Everything (assignments, notes and your platform tokens) is stored in a file on the computer running this app
          (<code>data/schoolboard.db</code>). Tokens are only sent to the platform they belong to. The AI coach sends one assignment's details to Claude when you ask for coaching.</p>
      </div>
    </div>`;
  $("#s-theme").addEventListener("click", e => {
    const t = e.target.dataset?.t; if (!t) return;
    localStorage.setItem("theme", t); applyTheme();
    main.querySelectorAll("#s-theme button").forEach(b => b.classList.toggle("on", b.dataset.t === t));
  });
  $("#s-save").addEventListener("click", e => busy(e.currentTarget, async () => {
    S.settings = await api("PUT", "/api/settings", { student_name: $("#s-name").value.trim(), timezone: $("#s-tz").value });
    S.plan = await api("GET", "/api/schedule");
    toast("Saved.");
  }));
}

// ------------------------------------------------------------------ boot
$("#sync-all").addEventListener("click", e => syncAll(e.currentTarget));
(async function boot() {
  hydrateIcons();
  $("#main").innerHTML = `<div class="skeleton" style="height:140px"></div><div class="skeleton"></div><div class="skeleton"></div>`;
  try {
    await loadAll();
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (!S.settings.timezone && tz) {
      S.settings = await api("PUT", "/api/settings", { timezone: tz });
      S.plan = await api("GET", "/api/schedule");
    }
    render();
    // Refresh from the platforms in the background when the last sync is over 30 minutes old.
    const last = S.connections.map(c => c.last_sync).filter(Boolean).sort().pop();
    if (S.connections.some(c => !["manual", "demo"].includes(c.kind)) && (!last || Date.now() - new Date(last) > 30 * 60000)) {
      api("POST", "/api/sync").then(async () => { await loadAll(); render(); }).catch(() => {});
    }
  } catch (e) {
    $("#main").innerHTML = `<div class="card empty">${icon("alert")}<h3>Couldn't load the dashboard</h3><p>${esc(e.message)}</p></div>`;
  }
})();
