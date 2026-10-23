const $ = (id) => document.getElementById(id);
let lastTicket = "";
let lastPrediction = null;
let categoryNames = [];
const examples = [
  "Our team cannot sign in after the latest update and password reset emails never arrive. This is blocking our work.",
  "I was charged twice for my subscription and need the duplicate payment reversed today.",
  "Could you add a CSV export option to the reports page?",
  "I see unknown administrator logins and suspect our account has been compromised.",
  "The service is unavailable across our region and customers cannot use the platform at all."
];
const titleCase = (s) => s.charAt(0).toUpperCase() + s.slice(1);
async function api(url, options = {}) {
  const response = await fetch(url, {headers: {"Content-Type":"application/json"}, ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}
function setMessage(id, message, error = false) {
  $(id).textContent = message;
  $(id).style.color = error ? "#b6482d" : "";
}
async function loadCategories() {
  const data = await api("/api/categories");
  categoryNames = data.categories;
  $("correctCategory").innerHTML = categoryNames.map(c => `<option value="${c}">${c}</option>`).join("");
}
async function loadMetrics() {
  const m = await api("/api/metrics");
  $("catMetric").textContent = `${Math.round(m.category_accuracy * 100)}%`;
  $("priMetric").textContent = `${Math.round(m.priority_accuracy * 100)}%`;
  $("f1Metric").textContent = m.priority_macro_f1.toFixed(2);
  $("examplesMetric").textContent = m.training_examples;
  $("metricNote").textContent = m.data_note;
}
async function classify() {
  const text = $("ticketText").value.trim();
  if (text.length < 8) {
    setMessage("feedbackMessage", "Enter at least 8 characters so the model has enough context.", true);
    $("ticketText").focus(); return;
  }
  $("classifyBtn").disabled = true;
  $("classifyBtn").innerHTML = "Classifying… <span>↻</span>";
  setMessage("feedbackMessage", "");
  try {
    const result = await api("/api/predict", {method:"POST", body:JSON.stringify({text})});
    lastTicket = text; lastPrediction = result;
    $("emptyState").hidden = true; $("resultContent").hidden = false;
    $("categoryValue").textContent = result.category;
    $("categoryConfidence").textContent = `${Math.round(result.category_confidence * 100)}%`;
    $("categoryMeter").style.width = `${Math.round(result.category_confidence * 100)}%`;
    $("priorityValue").textContent = titleCase(result.priority);
    $("priorityValue").className = `priority-value ${result.priority}`;
    $("priorityConfidence").textContent = `${Math.round(result.priority_confidence * 100)}%`;
    $("reviewBadge").textContent = result.needs_review ? "REVIEW SUGGESTED" : "MODEL OUTPUT";
    $("reviewBadge").className = result.needs_review ? "status-badge review" : "status-badge";
    $("reviewMessage").hidden = !result.needs_review;
    $("reviewMessage").textContent = result.review_reason || "";
    $("keywords").innerHTML = result.keywords.length ? result.keywords.map(k => `<span class="chip">${escapeHtml(k)}</span>`).join("") : '<span class="chip">No strong terms</span>';
    $("correctCategory").value = result.category;
    $("correctPriority").value = result.priority;
    $("feedbackMessage").textContent = "";
    $("resultPanel").scrollIntoView({behavior:"smooth", block:"nearest"});
  } catch (e) {
    setMessage("feedbackMessage", e.message, true);
  } finally {
    $("classifyBtn").disabled = false;
    $("classifyBtn").innerHTML = 'Classify ticket <span>→</span>';
  }
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
$("ticketText").addEventListener("input", () => {
  $("charCount").textContent = `${$("ticketText").value.length} / 5000 characters`;
});
$("exampleBtn").addEventListener("click", () => {
  const current = $("ticketText").value;
  let next = examples[Math.floor(Math.random() * examples.length)];
  if (next === current) next = examples[(examples.indexOf(next) + 1) % examples.length];
  $("ticketText").value = next;
  $("ticketText").dispatchEvent(new Event("input"));
});
$("classifyBtn").addEventListener("click", classify);
$("feedbackBtn").addEventListener("click", async () => {
  if (!lastPrediction || !lastTicket) return;
  $("feedbackBtn").disabled = true;
  try {
    const result = await api("/api/feedback", {method:"POST", body:JSON.stringify({
      text:lastTicket, predicted_category:lastPrediction.category, predicted_priority:lastPrediction.priority,
      correct_category:$("correctCategory").value, correct_priority:$("correctPriority").value, helpful:true
    })});
    setMessage("feedbackMessage", `Correction saved. ${result.feedback_count} feedback item(s) recorded locally.`);
  } catch(e) { setMessage("feedbackMessage", e.message, true); }
  finally { $("feedbackBtn").disabled = false; }
});
$("retrainBtn").addEventListener("click", async () => {
  $("retrainBtn").disabled = true; setMessage("retrainMessage", "Retraining models…");
  try {
    const result = await api("/api/retrain", {method:"POST", body:"{}"});
    setMessage("retrainMessage", result.message);
    await loadMetrics();
  } catch(e) { setMessage("retrainMessage", e.message, true); }
  finally { $("retrainBtn").disabled = false; }
});
Promise.all([loadCategories(), loadMetrics()]).catch(e => {
  $("metricNote").textContent = `API connection error: ${e.message}. Start the FastAPI server and refresh.`;
});
