"use strict";

const state = { token: "", mode: "general", conversationId: null, documents: [], archives: [], generating: false, shuttingDown: false };
const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => [...document.querySelectorAll(selector)];

function readToken() {
  const params = new URLSearchParams(location.hash.slice(1));
  state.token = params.get("token") || sessionStorage.getItem("sws-token") || "";
  if (state.token) sessionStorage.setItem("sws-token", state.token);
  history.replaceState(null, "", `${location.pathname}${location.search}`);
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-SWS-Token", state.token);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const body = await response.json(); message = body.error || message; } catch (_) {}
    throw new Error(message);
  }
  return response;
}

function showNotice(message, kind = "warning") {
  const element = qs("#global-message");
  element.textContent = message;
  element.classList.remove("hidden");
  if (kind === "temporary") setTimeout(() => element.classList.add("hidden"), 4500);
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return "Unknown";
  const units = ["B", "KiB", "MiB", "GiB", "TiB"];
  let value = bytes, index = 0;
  while (value >= 1024 && index < units.length - 1) { value /= 1024; index += 1; }
  return `${value.toFixed(index < 2 ? 0 : 2)} ${units[index]}`;
}

function setSection(name) {
  const titles = { chat: ["PRIVATE LOCAL AI", "AI Chat"], library: ["OFFLINE REFERENCE COLLECTION", "Knowledge Library"], documents: ["YOUR PRIVATE FILES", "Document Search"], maps: ["REGIONAL MAP DATA", "Offline Maps"], guides: ["PORTABLE REFERENCE FILES", "Guides"], settings: ["LOCAL PREFERENCES", "Settings"], status: ["READINESS CHECK", "System Status"] };
  qsa(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.section === name));
  qsa(".section").forEach((section) => section.classList.toggle("active", section.id === `section-${name}`));
  qs("#section-eyebrow").textContent = titles[name][0];
  qs("#section-title").textContent = titles[name][1];
}

function createButton(label, className, handler) {
  const button = document.createElement("button");
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
}

function renderDocuments() {
  const list = qs("#document-list");
  const filter = qs("#document-filter").value.trim().toLowerCase();
  list.replaceChildren();
  const items = state.documents.filter((item) => item.filename.toLowerCase().includes(filter));
  if (!items.length) { list.append(emptyRow(state.documents.length ? "No filenames match your search." : "No documents have been added.")); return; }
  items.forEach((item) => {
    const row = document.createElement("div"); row.className = "resource-row";
    const copy = document.createElement("div");
    const title = document.createElement("h4"); title.textContent = item.filename;
    const tag = document.createElement("span"); tag.className = `tag ${item.status === "ready" ? "" : "bad"}`; tag.textContent = item.status;
    title.append(tag);
    const meta = document.createElement("div"); meta.className = "resource-meta";
    meta.textContent = item.status === "ready" ? `${formatBytes(item.size_bytes)} | ${item.chunk_count} searchable passages${item.page_count ? ` | ${item.page_count} pages` : ""}` : item.message;
    copy.append(title, meta);
    const actions = document.createElement("div"); actions.className = "resource-actions";
    actions.append(
      createButton("Open", "button ghost", () => openDocument(item.id)),
      createButton("Remove", "button danger", () => removeDocument(item.id, item.filename))
    );
    row.append(copy, actions); list.append(row);
  });
}

function emptyRow(message) { const row = document.createElement("div"); row.className = "resource-row"; const text = document.createElement("div"); text.className = "resource-meta"; text.textContent = message; row.append(text); return row; }

async function loadDocuments() { const response = await api("/api/documents"); state.documents = await response.json(); renderDocuments(); }
async function openDocument(id) { try { await api(`/api/documents/${id}/open`, { method: "POST" }); } catch (error) { showNotice(error.message); } }
async function removeDocument(id, filename) { if (!confirm(`Remove ${filename} from the CacheNorth document store and index?`)) return; try { await api(`/api/documents/${id}`, { method: "DELETE" }); await loadDocuments(); } catch (error) { showNotice(error.message); } }

async function watchJob(jobId) {
  const card = qs("#index-progress"); card.classList.remove("hidden");
  while (true) {
    const response = await api(`/api/jobs/${jobId}`); const job = await response.json();
    qs("#progress-message").textContent = job.message; qs("#progress-percent").textContent = `${job.percent}%`; qs("#progress-fill").style.width = `${job.percent}%`;
    if (job.state === "complete" || job.state === "error") { if (job.error) showNotice(job.error); setTimeout(() => card.classList.add("hidden"), 900); return; }
    await new Promise((resolve) => setTimeout(resolve, 350));
  }
}

async function addDocuments(files) {
  for (const file of files) {
    const jobId = crypto.randomUUID(); const form = new FormData(); form.append("file", file);
    const watcher = watchJob(jobId);
    try { await api("/api/documents/add", { method: "POST", headers: { "X-SWS-Job": jobId }, body: form }); } catch (error) { showNotice(error.message); }
    await watcher;
  }
  await loadDocuments(); await loadStatus();
}

async function rebuildIndex() {
  const jobId = crypto.randomUUID(); const watcher = watchJob(jobId);
  try { await api("/api/documents/rebuild", { method: "POST", headers: { "X-SWS-Job": jobId } }); } catch (error) { showNotice(error.message); }
  await watcher; await loadDocuments();
}

async function refreshDocuments() {
  const jobId = crypto.randomUUID(); const watcher = watchJob(jobId);
  try {
    const response = await api("/api/documents/refresh", { method: "POST", headers: { "X-SWS-Job": jobId } });
    const data = await response.json(); const result = data.result;
    showNotice(`Documents refreshed: ${result.added} added, ${result.updated} updated, ${result.removed} removed, ${result.duplicates} duplicates skipped${result.errors ? `, ${result.errors} errors` : ""}.`, "temporary");
  } catch (error) { showNotice(error.message); }
  await watcher; await loadDocuments(); await loadStatus();
}

function messageElement(role, content, sources = []) {
  const wrapper = document.createElement("article"); wrapper.className = `message ${role}`;
  const label = document.createElement("div"); label.className = "message-label"; label.textContent = role === "user" ? "YOU" : "CACHENORTH";
  const bubble = document.createElement("div"); bubble.className = "bubble"; bubble.textContent = content;
  wrapper.append(label, bubble);
  if (sources.length) {
    const group = document.createElement("div"); group.className = "source-group";
    sources.forEach((source) => {
      const card = document.createElement("div"); card.className = "source-card";
      const heading = document.createElement("strong"); heading.textContent = `${source.filename}${source.page_number ? ` - page ${source.page_number}` : ""}`;
      const passage = document.createElement("p"); passage.textContent = source.passage;
      card.append(heading, passage, createButton("Open original", "button ghost", () => openDocument(source.document_id))); group.append(card);
    });
    wrapper.append(group);
  }
  return wrapper;
}

function clearEmptyChat() { const empty = qs("#messages .empty-state"); if (empty) empty.remove(); }
function scrollMessages() { const messages = qs("#messages"); messages.scrollTop = messages.scrollHeight; }
function setGenerating(value) { state.generating = value; qs("#send-message").disabled = value; qs("#stop-generation").classList.toggle("hidden", !value); qs("#generation-state").textContent = value ? "Generating locally" : "Ready"; }

function shouldSendOnKeydown(event) {
  return event.key === "Enter" && !event.shiftKey && !event.isComposing && !event.repeat;
}

async function sendChat(event) {
  event.preventDefault(); if (state.generating) return;
  const input = qs("#message-input"); const question = input.value.trim(); if (!question) return;
  clearEmptyChat(); qs("#messages").append(messageElement("user", question)); input.value = ""; setGenerating(true); scrollMessages();
  const assistant = messageElement("assistant", ""); const bubble = assistant.querySelector(".bubble"); qs("#messages").append(assistant);
  try {
    const response = await api("/api/chat", { method: "POST", body: JSON.stringify({ message: question, mode: state.mode, conversation_id: state.conversationId }) });
    if ((response.headers.get("content-type") || "").includes("application/json")) {
      const result = await response.json(); state.conversationId = result.conversation_id; bubble.textContent = result.answer; return;
    }
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = "", sources = [];
    while (true) {
      const { value, done } = await reader.read(); buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const lines = buffer.split("\n"); buffer = lines.pop() || "";
      for (const line of lines) { if (!line) continue; const eventData = JSON.parse(line); if (eventData.conversation_id) state.conversationId = eventData.conversation_id; if (eventData.sources) sources = eventData.sources; if (eventData.context?.history_omitted) showNotice(`${eventData.context.history_omitted} older message${eventData.context.history_omitted === 1 ? " was" : "s were"} not sent to the AI to fit the ${eventData.context.size.toLocaleString()}-token context. The full conversation remains saved.`, "temporary"); if (eventData.delta) bubble.textContent += eventData.delta; if (eventData.error) throw new Error(eventData.error); }
      scrollMessages(); if (done) break;
    }
    if (sources.length) { const fresh = messageElement("assistant", bubble.textContent, sources); assistant.replaceWith(fresh); }
  } catch (error) { bubble.textContent = `Error: ${error.message}`; }
  finally { setGenerating(false); scrollMessages(); await loadChats().catch(() => {}); }
}

async function stopGeneration() { try { await api("/api/chat/stop", { method: "POST" }); } catch (error) { showNotice(error.message); } }
function newChat() { state.conversationId = null; qs("#conversation-list").value = ""; qs("#messages").innerHTML = '<div class="empty-state"><img src="/assets/cache-north-logo.png" alt=""><p class="eyebrow">WELCOME TO CACHENORTH</p><h3>Ask privately. Work offline.</h3><p>Enter a question below, or choose Ask Documents for answers supported by files you add.</p></div>'; }
function setMode(mode) { state.mode = mode; qsa(".mode-button").forEach((button) => button.classList.toggle("active", button.dataset.mode === mode)); qs("#chat-mode-note").textContent = mode === "documents" ? "Answers use indexed passages. Verified source cards appear beneath the response." : "General answers come from the local AI model and may contain mistakes."; newChat(); }

async function loadChats() {
  const response = await api("/api/chats"); const chats = await response.json(); const select = qs("#conversation-list"); const selected = state.conversationId || "";
  select.replaceChildren(new Option("Current conversation", ""));
  chats.forEach((chat) => select.append(new Option(`${chat.mode === "documents" ? "Documents" : "General"}: ${chat.title}`, chat.id)));
  select.value = selected;
}

async function loadConversation(id) {
  if (!id) { newChat(); return; }
  const listResponse = await api("/api/chats"); const chats = await listResponse.json(); const chat = chats.find((item) => item.id === id);
  const response = await api(`/api/chats/${id}`); const messages = await response.json();
  state.conversationId = id; state.mode = chat?.mode || "general";
  qsa(".mode-button").forEach((button) => button.classList.toggle("active", button.dataset.mode === state.mode));
  qs("#chat-mode-note").textContent = state.mode === "documents" ? "Answers use indexed passages. Verified source cards appear beneath the response." : "General answers come from the local AI model and may contain mistakes.";
  qs("#messages").replaceChildren(...messages.map((item) => messageElement(item.role, item.content, item.sources || []))); scrollMessages();
}

async function clearHistory() {
  if (!confirm("Permanently clear every saved CacheNorth conversation from this drive?")) return;
  try { await api("/api/chats", { method: "DELETE" }); newChat(); await loadChats(); showNotice("Saved conversations cleared.", "temporary"); } catch (error) { showNotice(error.message); }
}

function renderResourceList(selector, items, type) {
  const list = qs(selector); list.replaceChildren(); if (!items.length) { list.append(emptyRow(`No ${type} files were found.`)); return; }
  items.forEach((item) => { const row = document.createElement("div"); row.className = "resource-row"; const copy = document.createElement("div"); const title = document.createElement("h4"); title.textContent = item.title || item.name; const meta = document.createElement("div"); meta.className = "resource-meta"; const details = [item.name, item.category, item.date, formatBytes(item.size_bytes)].filter(Boolean); meta.textContent = details.join(" | "); copy.append(title, meta); row.append(copy); if (["map", "archive", "guide"].includes(type)) { const actions = document.createElement("div"); actions.className = "resource-actions"; const label = type === "archive" ? "Open in Kiwix" : type === "map" ? "Open map" : "Open PDF"; actions.append(createButton(label, "button ghost", () => type === "archive" ? openKiwix(item.name) : type === "map" ? openMaps(item.name) : openGuide(item))); row.append(actions); } list.append(row); });
}

function renderLibrary() { const filter = qs("#library-filter").value.trim().toLowerCase(); const items = state.archives.filter((item) => [item.title, item.name, item.category, item.date].some((value) => String(value || "").toLowerCase().includes(filter))); renderResourceList("#archive-list", items, "archive"); }
async function loadLibrary() { const response = await api("/api/library"); const data = await response.json(); state.archives = data.archives; qs("#library-summary").innerHTML = `<strong>${data.available ? "Kiwix is ready" : "Kiwix viewer is missing"}</strong><span>${data.archives.length} knowledge source${data.archives.length === 1 ? "" : "s"}</span>`; qs("#open-kiwix").disabled = !data.available; renderLibrary(); }
async function openKiwix(filename = null) { try { await api("/api/library/open", { method: "POST", body: JSON.stringify({ filename }) }); } catch (error) { showNotice(error.message); } }
async function loadMaps() { const response = await api("/api/maps"); const data = await response.json(); qs("#maps-summary").innerHTML = `<strong>${data.available ? "Portable map viewer is available" : "Portable map viewer is pending"}</strong><span>${data.files.length} map file${data.files.length === 1 ? "" : "s"}</span>`; qs("#open-maps").disabled = !data.available; renderResourceList("#map-list", data.files, "map"); }
async function openMaps(filename = null) { try { await api("/api/maps/open", { method: "POST", body: JSON.stringify({ filename }) }); } catch (error) { showNotice(error.message); } }
async function openHelp(item) { try { await api("/api/help/open", { method: "POST", body: JSON.stringify({ item }) }); } catch (error) { showNotice(error.message); } }
async function loadGuides() { const response = await api("/api/guides"); const data = await response.json(); qs("#guides-summary").innerHTML = `<strong>Portable PDF guides</strong><span>${data.files.length} file${data.files.length === 1 ? "" : "s"}</span>`; renderResourceList("#guide-list", data.files, "guide"); }
async function openGuide(item) { try { await api("/api/guides/open", { method: "POST", body: JSON.stringify({ filename: item.name, location: item.location }) }); } catch (error) { showNotice(error.message); } }
async function openFolder(folder) { try { await api("/api/folders/open", { method: "POST", body: JSON.stringify({ folder }) }); } catch (error) { showNotice(error.message); } }

async function loadModels() {
  const response = await api("/api/models"); const data = await response.json(); const list = qs("#model-list"); list.replaceChildren();
  qs("#model-summary").innerHTML = `<strong>${data.mode === "automatic" ? "Automatic selection" : "Manual selection"}</strong><span>${data.selected || "No compatible model"}</span>`;
  if (!data.models.length) { list.append(emptyRow("No GGUF models were found.")); return; }
  data.models.forEach((item) => {
    const row = document.createElement("div"); row.className = `resource-row ${item.name === data.selected ? "selected" : ""}`;
    const copy = document.createElement("div"); const title = document.createElement("h4"); title.textContent = item.title;
    const tag = document.createElement("span"); tag.className = `tag ${["unsupported", "too-large"].includes(item.status) ? "bad" : ""}`; tag.textContent = item.status; title.append(tag);
    const meta = document.createElement("div"); meta.className = "resource-meta"; meta.textContent = `${item.name} | ${item.size_label || "Unknown size"} | ${item.quantization || "Unknown quantization"} | ${formatBytes(item.estimated_memory_bytes)} estimated memory | ${item.reason}`; copy.append(title, meta);
    const actions = document.createElement("div"); actions.className = "resource-actions"; const button = createButton(item.name === data.selected ? "Selected" : "Load model", "button ghost", () => loadModel(item.name)); button.disabled = item.name === data.selected || ["unsupported", "too-large"].includes(item.status); actions.append(button); row.append(copy, actions); list.append(row);
  });
}
async function loadModel(filename) { try { const response = await api("/api/models/load", { method: "POST", body: JSON.stringify({ filename }) }); const data = await response.json(); watchJob(data.job_id).then(() => Promise.all([loadModels(), loadStatus()])); } catch (error) { showNotice(error.message); } }
async function restoreModel() { try { await api("/api/models/automatic", { method: "POST" }); await loadModels(); showNotice("Automatic model selection restored. The selected model will load at the next AI restart.", "temporary"); } catch (error) { showNotice(error.message); } }
async function refreshAll() { const button = qs("#refresh-all"); button.disabled = true; const jobId = crypto.randomUUID(); const watcher = watchJob(jobId); try { const response = await api("/api/refresh-all", { method: "POST", headers: { "X-SWS-Job": jobId } }); const data = await response.json(); await watcher; await Promise.all([loadDocuments(), loadLibrary(), loadMaps(), loadGuides(), loadModels(), loadStatus()]); showNotice(`Refresh complete: ${data.result.models} models, ${data.result.archives} archives, ${data.result.maps} maps, and ${data.result.guides} guides found.`, "temporary"); } catch (error) { showNotice(error.message); await watcher.catch(() => {}); } finally { button.disabled = false; } }

function statusCard(label, value, detail) { const card = document.createElement("div"); card.className = "status-card"; const a = document.createElement("div"); a.className = "label"; a.textContent = label; const b = document.createElement("div"); b.className = "value"; b.textContent = value; const c = document.createElement("div"); c.className = "detail"; c.textContent = detail; card.append(a,b,c); return card; }
async function loadStatus() {
  try {
    const response = await api("/api/status"); const data = await response.json(); const engine = data.engine;
    qs("#engine-label").textContent = engine.message; qs("#engine-dot").className = `dot ${engine.state === "running" ? "ready" : engine.state === "starting" ? "pending" : "error"}`;
    const banner = qs("#readiness-banner"); banner.className = `readiness-banner ${data.offline_ready ? "ready" : "error"}`; banner.querySelector("strong").textContent = data.offline_ready ? "Core offline resources are ready" : "Setup needs attention"; banner.querySelector("span").textContent = data.offline_ready ? "Local-only services" : data.blockers.join(" | ");
    const engineMode = engine.state === "running" ? accelerationLabel(engine.acceleration) : engine.message;
    qs("#status-grid").replaceChildren(
      statusCard("AI Engine", engine.state === "running" ? "Running" : engine.state === "starting" ? "Loading" : "Unavailable", `${engineMode}${engine.threads ? ` | ${engine.threads} CPU threads` : ""}`),
      statusCard(data.storage.label, formatBytes(data.storage.free_bytes), `${formatBytes(data.storage.total_bytes)} total`),
      statusCard("Offline Library", `${data.library.archives} archives`, `${data.documents.ready} indexed document${data.documents.ready === 1 ? "" : "s"}`),
      statusCard("Offline Maps", `${data.maps.files} detected`, data.maps.available ? "Viewer ready" : "Viewer unavailable")
    );
    const computer = qs("#computer-panel"); computer.replaceChildren();
    const heading = document.createElement("h3"); heading.textContent = "This Computer";
    const list = document.createElement("dl");
    [["Processor", data.system.cpu], ["Installed RAM", formatBytes(data.system.ram_total_bytes)], ["Graphics", data.system.gpus.length ? data.system.gpus.join(", ") : "No graphics adapter reported"]].forEach(([term, value]) => { const dt = document.createElement("dt"); dt.textContent = term; const dd = document.createElement("dd"); dd.textContent = value; list.append(dt, dd); });
    computer.append(heading, list);
    const storage = qs("#storage-panel"); storage.replaceChildren(); const storageHeading = document.createElement("h3"); storageHeading.textContent = "Storage Breakdown"; const storageList = document.createElement("dl"); storageList.className = "storage-list"; Object.entries(data.storage.categories || {}).forEach(([name, bytes]) => { const wrapper = document.createElement("div"); const dt = document.createElement("dt"); dt.textContent = name; const dd = document.createElement("dd"); dd.textContent = formatBytes(bytes); wrapper.append(dt, dd); storageList.append(wrapper); }); storage.append(storageHeading, storageList); (data.storage.warnings || []).forEach((warning) => showNotice(warning));
    qs("#advanced-status-grid").replaceChildren(
      statusCard("Model", engine.model || "No model detected", engine.last_generation?.completed ? `Last response: ${engine.last_generation.tokens_per_second ? engine.last_generation.tokens_per_second.toFixed(1) + " tokens/s | " : ""}${engine.last_generation.seconds.toFixed(1)}s total | first text ${engine.last_generation.time_to_first_token_seconds.toFixed(1)}s` : (engine.backend || "stopped")),
      statusCard("CPU Profile", data.system.cpu_mode, `${data.system.logical_processors} logical processors`),
      statusCard("Context Limit", `${(data.system.context_running || data.system.context_size).toLocaleString()} tokens`, data.system.context_requested ? `Requested ${data.system.context_requested.toLocaleString()} (${data.system.context_mode === "manual" ? "manual" : "automatic"})${data.system.context_fallback ? " — fell back to a safe size" : ""}` : data.system.memory_profile),
      statusCard("Storage Path", data.storage.kind, data.storage.path),
      statusCard("Document Passages", data.documents.chunks.toLocaleString(), `${data.documents.ready} ready`),
      statusCard("Windows", data.system.architecture, data.system.windows)
    );
  } catch (error) { qs("#engine-label").textContent = "Dashboard connection error"; qs("#engine-dot").className = "dot error"; }
}

const MODE_NAMES = { cpu: "CPU", auto_vulkan: "Automatic GPU", manual_vulkan: "Manual GPU" };

function accelerationLabel(acceleration) {
  if (!acceleration || acceleration.actual === "stopped" || acceleration.actual === "starting") return "Starting";
  if (acceleration.actual === "gpu") return `GPU mode: ${acceleration.device || "Vulkan device"}${acceleration.layers ? ` (${acceleration.layers[0]}/${acceleration.layers[1]} layers)` : ""}`;
  return acceleration.fallback || acceleration.reason ? "CPU mode (GPU unavailable)" : "CPU mode";
}

function describeAcceleration(settings) {
  const status = settings.acceleration_status || {};
  const parts = [`Selected: ${MODE_NAMES[settings.acceleration_mode] || "CPU"}.`];
  if (status.actual === "gpu" || status.actual === "cpu") parts.push(`Running: ${accelerationLabel(status)}.`);
  if (status.reason) parts.push(status.reason);
  else if (settings.vulkan_failure?.message) parts.push(`Last GPU issue on this computer: ${settings.vulkan_failure.message}`);
  if (settings.smart_app_control === "on" && settings.acceleration_mode !== "cpu") parts.push("Windows Smart App Control is on. It may block CacheNorth's unsigned GPU component; CPU mode is unaffected.");
  return parts.join(" ");
}

async function loadSettings() {
  const response = await api("/api/settings");
  const settings = await response.json();
  qs("#acceleration-mode").value = settings.acceleration_mode || "cpu";
  const device = qs("#vulkan-device"); device.replaceChildren();
  // Vulkan device numbers recorded from a real engine start are authoritative; Windows adapter order may differ.
  if (settings.vulkan_devices?.length) settings.vulkan_devices.forEach((item) => device.append(new Option(`${item.index}: ${item.name}`, item.index)));
  else if (settings.graphics_devices?.length) settings.graphics_devices.forEach((item) => device.append(new Option(`${item.index}: ${item.name} (numbering confirmed after first GPU start)`, item.index)));
  else device.append(new Option("No graphics devices reported by Windows", ""));
  if (settings.vulkan_device !== null && settings.vulkan_device !== undefined) device.value = String(settings.vulkan_device);
  updateAccelerationControls();
  qs("#acceleration-status").textContent = describeAcceleration(settings);
  renderContext(settings.context);
}

let contextReport = null;
const formatMiB = (mib) => (mib === null || mib === undefined ? "unknown" : mib >= 1024 ? `${(mib / 1024).toFixed(1)} GB` : `${mib} MB`);
const LEVEL_TEXT = { fits: "fits", tight: "tight fit", exceeds: "may exceed memory", unknown: "memory unknown" };

function renderContext(report) {
  contextReport = report;
  const select = qs("#context-size");
  select.replaceChildren();
  if (!report) { select.append(new Option("Automatic (recommended)", "auto")); qs("#context-estimate").textContent = "Context estimates appear once a model is available."; return; }
  select.append(new Option(`Automatic (recommended) — ${report.automatic_size.toLocaleString()} tokens now`, "auto"));
  report.options.forEach((item) => {
    const option = new Option(`${(item.size / 1024)}K tokens — ${item.supported ? LEVEL_TEXT[item.level] : "not supported by this model"}`, item.size);
    option.disabled = !item.supported;
    select.append(option);
  });
  select.value = String(report.choice);
  const running = report.running || {};
  const parts = [];
  if (running.actual) parts.push(`Running: ${running.actual.toLocaleString()} tokens${running.requested && running.requested !== running.actual ? ` (requested ${running.requested.toLocaleString()})` : ""}.`);
  if (running.reason) parts.push(running.reason);
  else if (report.failure?.message) parts.push(`Last context issue on this computer: ${report.failure.message}`);
  qs("#context-status").textContent = parts.join(" ");
  updateContextControls();
}

function updateContextControls() {
  const report = contextReport;
  if (!report) return;
  const value = qs("#context-size").value;
  const size = value === "auto" ? report.automatic_size : Number(value);
  const item = report.options.find((option) => option.size === size);
  const gpu = report.backend_for_estimate === "gpu";
  qs("#context-estimate").textContent = item
    ? `${report.model}: about ${formatMiB(item.ram_mib)} of system memory${gpu ? ` and ${formatMiB(item.vram_mib)} of graphics memory` : ""} (conversation memory ${formatMiB(item.kv_mib)}). Available now: ${formatMiB(report.available_ram_mib)} RAM${gpu ? `, ${formatMiB(report.available_vram_mib)} graphics memory` : ""}. Model maximum: ${report.model_max ? report.model_max.toLocaleString() : "unknown"} tokens.`
    : "";
  const risky = value !== "auto" && item && item.level === "exceeds";
  qs("#context-warning").classList.toggle("hidden", !risky);
  qs("#context-override").checked = false;
  if (risky) qs("#context-warning-text").textContent = `${(size / 1024)}K tokens is estimated to need more memory than this computer has available. It may fail to start or make Windows slow.`;
}

async function applyContext() {
  const button = qs("#apply-context");
  button.disabled = true;
  try {
    const value = qs("#context-size").value;
    const response = await api("/api/settings", { method: "POST", body: JSON.stringify({ context_size: value === "auto" ? "auto" : Number(value), allow_over_estimate: qs("#context-override").checked, restart_engine: true }) });
    const result = await response.json();
    showNotice("AI engine restart requested with the new context length.", "temporary");
    if (result.job_id) await watchJob(result.job_id);
    await loadStatus();
    await loadSettings();
  } catch (error) { showNotice(error.message); }
  finally { button.disabled = false; }
}

function updateAccelerationControls() {
  const mode = qs("#acceleration-mode").value;
  const device = qs("#vulkan-device");
  device.disabled = mode !== "manual_vulkan" || !device.options.length || device.options[0].value === "";
  qs("#acceleration-note").textContent = mode === "cpu" ? "CPU mode is portable and requires no graphics driver." : "GPU mode is optional and saved only for this computer. CacheNorth makes one attempt; if it fails, CPU mode starts automatically and GPU is paused here until you apply it again.";
}

async function applyAcceleration() {
  const button = qs("#apply-acceleration");
  button.disabled = true;
  try {
    const mode = qs("#acceleration-mode").value;
    const selectedDevice = qs("#vulkan-device").value;
    const response = await api("/api/settings", { method: "POST", body: JSON.stringify({ acceleration_mode: mode, vulkan_device: mode === "manual_vulkan" && selectedDevice !== "" ? Number(selectedDevice) : null, restart_engine: true }) });
    const result = await response.json();
    showNotice("AI engine restart requested. Progress appears below.", "temporary");
    if (result.job_id) await watchJob(result.job_id);
    await loadStatus();
    await loadSettings();
  } catch (error) { showNotice(error.message); }
  finally { button.disabled = false; }
}

async function shutdown() {
  if (state.shuttingDown || !confirm("Close CacheNorth and stop the local AI engine?")) return;
  state.shuttingDown = true;
  qsa("#shutdown-button, #settings-close").forEach((button) => { button.disabled = true; });
  showNotice("Closing CacheNorth and stopping managed processes…");
  try {
    await api("/api/shutdown", { method: "POST" });
    if (window.chrome?.webview) {
      window.chrome.webview.postMessage("cache-north-close");
      return;
    }
    document.body.innerHTML = '<main style="padding:48px"><h1>CacheNorth is closed</h1><p>You may close this browser tab. Close Kiwix, GPXSee, and opened files before using Windows Safely Remove Hardware.</p></main>';
  } catch (error) {
    state.shuttingDown = false;
    qsa("#shutdown-button, #settings-close").forEach((button) => { button.disabled = false; });
    showNotice(error.message);
  }
}

async function initialize() {
  readToken(); if (!state.token) { showNotice("This dashboard was opened without its local session token. Start it using Launch CacheNorth.exe."); qs("#startup-screen").classList.add("ready"); return; }
  qsa(".nav-item").forEach((button) => button.addEventListener("click", () => setSection(button.dataset.section)));
  qsa(".mode-button").forEach((button) => button.addEventListener("click", () => setMode(button.dataset.mode)));
  const chatForm = qs("#chat-form"); const messageInput = qs("#message-input");
  chatForm.addEventListener("submit", sendChat);
  messageInput.addEventListener("keydown", (event) => {
    if (!shouldSendOnKeydown(event)) return;
    event.preventDefault();
    chatForm.requestSubmit();
  });
  qs("#stop-generation").addEventListener("click", stopGeneration); qs("#new-chat").addEventListener("click", newChat); qs("#conversation-list").addEventListener("change", (event) => loadConversation(event.target.value));
  qs("#add-document").addEventListener("click", () => qs("#document-picker").click()); qs("#document-picker").addEventListener("change", (event) => addDocuments([...event.target.files])); qs("#document-filter").addEventListener("input", renderDocuments); qs("#refresh-documents").addEventListener("click", refreshDocuments); qs("#rebuild-index").addEventListener("click", rebuildIndex);
  qs("#open-kiwix").addEventListener("click", () => openKiwix()); qs("#refresh-library").addEventListener("click", loadLibrary); qs("#library-filter").addEventListener("input", renderLibrary); qs("#open-maps").addEventListener("click", () => openMaps()); qs("#refresh-maps").addEventListener("click", loadMaps); qs("#refresh-guides").addEventListener("click", loadGuides); qs("#refresh-models").addEventListener("click", loadModels); qs("#restore-model").addEventListener("click", restoreModel); qs("#refresh-all").addEventListener("click", refreshAll); qsa(".open-folder").forEach((button) => button.addEventListener("click", () => openFolder(button.dataset.folder))); qs("#refresh-status").addEventListener("click", loadStatus); qs("#acceleration-mode").addEventListener("change", updateAccelerationControls); qs("#apply-acceleration").addEventListener("click", applyAcceleration); qs("#context-size").addEventListener("change", updateContextControls); qs("#apply-context").addEventListener("click", applyContext); qs("#clear-history").addEventListener("click", clearHistory); qs("#shutdown-button").addEventListener("click", shutdown); qs("#settings-close").addEventListener("click", shutdown);
  qs("#open-quick-start").addEventListener("click", () => openHelp("quick-start")); qs("#open-troubleshooting").addEventListener("click", () => openHelp("troubleshooting")); qs("#open-help-folder").addEventListener("click", () => openHelp("folder"));
  try { await Promise.all([loadDocuments(), loadLibrary(), loadMaps(), loadGuides(), loadModels(), loadStatus(), loadSettings(), loadChats()]); } catch (error) { showNotice(error.message); }
  const requestedParameters = new URLSearchParams(location.search);
  const requestedSection = requestedParameters.get("section");
  if (["chat", "library", "documents", "maps", "guides", "settings", "status"].includes(requestedSection)) setSection(requestedSection);
  const requestedConversation = requestedParameters.get("conversation");
  if (requestedConversation) await loadConversation(requestedConversation).catch(() => {});
  qs("#startup-screen").classList.add("ready");
  setInterval(loadStatus, 4000);
}

if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded", initialize);
if (typeof module !== "undefined") module.exports = { shouldSendOnKeydown };
