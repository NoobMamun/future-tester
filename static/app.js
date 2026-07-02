/* Future Abdullah (2050) — Frontend (API client) */

const API_BASE = window.location.origin;
const SESSION_KEY = "future_abdullah_session_id";

const TOPIC_LABELS = {
  salary: "How much do I earn in 2050?",
  career: "Government or private — what happened?",
  sideproject: "Which project changed my life?",
  savings: "Did I build my dream house?",
  marriage: "How did married life go?",
  achievement: "What am I most proud of?",
};

let sessionId = localStorage.getItem(SESSION_KEY);
let voiceEnabled = false;
let isTyping = false;

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const voiceBtn = document.getElementById("voiceBtn");
const regretCount = document.getElementById("regretCount");
const bestCount = document.getElementById("bestCount");
const clockEl = document.getElementById("clock");
const connectionStatus = document.getElementById("connectionStatus");
const engineBadge = document.getElementById("engineBadge");
const sessionShort = document.getElementById("sessionShort");

async function init() {
  updateClock();
  setInterval(updateClock, 1000);

  chatForm.addEventListener("submit", handleSubmit);
  voiceBtn.addEventListener("click", toggleVoice);

  document.querySelectorAll(".quick-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const topic = btn.dataset.topic;
      const label = TOPIC_LABELS[topic];
      if (label) sendMessage(label, topic);
    });
  });

  try {
    await loadTimeline();
    await loadWelcome();
    setOnline(true);
    chatInput.disabled = false;
    sendBtn.disabled = false;
  } catch (err) {
    setOnline(false);
    addFutureMessage(
      "Arrey bhai — backend link failed! Start the Python server first:\n\npy -m pip install -r requirements.txt\npy -m uvicorn server.main:app --reload\n\nOr double-click run.bat\n\nThen open http://localhost:8000"
    );
  }
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }

  return res.json();
}

async function loadTimeline() {
  const items = await api("/api/timeline");
  const timeline = document.getElementById("timeline");
  timeline.innerHTML = items
    .map(
      (item) => `
      <div class="timeline-item">
        <span class="timeline-item__year">${escapeHtml(item.year)}</span>
        <span class="timeline-item__text">${escapeHtml(item.text)}</span>
      </div>
    `
    )
    .join("");
}

async function loadWelcome() {
  const params = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : "";
  const data = await api(`/api/welcome${params}`);

  sessionId = data.session_id;
  localStorage.setItem(SESSION_KEY, sessionId);
  updateSessionDisplay();
  updateStats(data.stats, true);

  setTimeout(() => addFutureMessage(data.message), 400);
}

function updateSessionDisplay() {
  if (sessionId) {
    sessionShort.textContent = sessionId.slice(0, 8) + "…";
  }
}

function setOnline(online) {
  connectionStatus.textContent = online ? "● FUTURE LINK ACTIVE" : "● OFFLINE";
  connectionStatus.classList.toggle("status-pill--online", online);
  if (!online) {
    connectionStatus.style.color = "#ff6b6b";
    connectionStatus.style.borderColor = "rgba(255,107,107,0.3)";
  }
}

function setEngine(engine) {
  engineBadge.textContent = `engine: ${engine}`;
  engineBadge.classList.toggle("status-pill--engine-ai", engine === "openai");
}

function updateClock() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const mins = String(now.getMinutes()).padStart(2, "0");
  clockEl.textContent = `2050-${month}-${day} ${hours}:${mins}`;
}

function updateStats(stats, animate = false) {
  if (!stats) return;

  if (animate) {
    animateCounter(regretCount, stats.regret_count, 1800);
    animateCounter(bestCount, stats.best_decision_count, 2200);
  } else {
    regretCount.textContent = stats.regret_count;
    bestCount.textContent = stats.best_decision_count;
  }
}

function animateCounter(el, target, duration) {
  const start = parseInt(el.textContent, 10) || 0;
  const startTime = performance.now();

  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(start + (target - start) * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
}

function handleSubmit(e) {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text || isTyping) return;
  chatInput.value = "";
  sendMessage(text);
}

async function sendMessage(userText, topic = null) {
  addUserMessage(userText);
  isTyping = true;
  chatInput.disabled = true;
  sendBtn.disabled = true;
  showTypingIndicator();

  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message: userText,
        session_id: sessionId,
        topic,
      }),
    });

    removeTypingIndicator();

    sessionId = data.session_id;
    localStorage.setItem(SESSION_KEY, sessionId);
    updateSessionDisplay();
    updateStats(data.stats);
    setEngine(data.engine);
    addFutureMessage(data.reply);
  } catch (err) {
    removeTypingIndicator();
    addFutureMessage(`Backend glitch, bhai — ${err.message}. Check if the server is running.`);
  } finally {
    isTyping = false;
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

function addUserMessage(text) {
  const el = document.createElement("div");
  el.className = "message message--user";
  el.innerHTML = `
    <div class="message__header">Young Abdullah · 2026</div>
    <div class="message__bubble">${escapeHtml(text)}</div>
  `;
  chatMessages.appendChild(el);
  scrollToBottom();
}

function addFutureMessage(text) {
  const el = document.createElement("div");
  el.className = "message message--future";
  el.innerHTML = `
    <div class="message__header">Future Abdullah · 2050</div>
    <div class="message__bubble">${formatMessage(text)}</div>
  `;
  chatMessages.appendChild(el);
  scrollToBottom();
  if (voiceEnabled) speak(text);
}

function showTypingIndicator() {
  const el = document.createElement("div");
  el.className = "message message--future message--typing";
  el.id = "typingIndicator";
  el.innerHTML = `
    <div class="message__header">Future Abdullah · 2050</div>
    <div class="message__bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  chatMessages.appendChild(el);
  scrollToBottom();
}

function removeTypingIndicator() {
  document.getElementById("typingIndicator")?.remove();
}

function formatMessage(text) {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function toggleVoice() {
  voiceEnabled = !voiceEnabled;
  voiceBtn.classList.toggle("voice-btn--active", voiceEnabled);
  voiceBtn.querySelector(".voice-icon").textContent = voiceEnabled ? "🔊" : "🔇";

  if (voiceEnabled && "speechSynthesis" in window) {
    speak("Voice replies enabled. Future Abdullah is now annoyingly loud.");
  }
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.replace(/\n/g, " "));
  utterance.rate = 0.95;
  utterance.pitch = 0.9;

  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(
    (v) => v.lang.startsWith("en") && (v.name.includes("Male") || v.name.includes("Google"))
  );
  if (preferred) utterance.voice = preferred;

  window.speechSynthesis.speak(utterance);
}

if ("speechSynthesis" in window) {
  window.speechSynthesis.onvoiceschanged = () => {};
}

init();
