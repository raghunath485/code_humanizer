const sourceCode = document.getElementById("sourceCode");
const humanizedCode = document.getElementById("humanizedCode");
const insightList = document.getElementById("insightList");
const summaryToggle = document.getElementById("summaryToggle");
const renameToggle = document.getElementById("renameToggle");
const spacingToggle = document.getElementById("spacingToggle");
const languageHint = document.getElementById("languageHint");
const humanizeButton = document.getElementById("humanizeButton");
const clearButton = document.getElementById("clearButton");
const loadExampleButton = document.getElementById("loadExample");
const copyButton = document.getElementById("copyButton");
const statusMessage = document.getElementById("statusMessage");
const resultMeta = document.getElementById("resultMeta");
const metricsPanel = document.getElementById("metricsPanel");
const uploadInput = document.getElementById("uploadInput");
const deadCodePanel = document.getElementById("deadCodePanel");

const exampleSnippet = `async function hndlUsrMsg(msg, llmSvc, sessCtx){
const sysPrompt = buildSysPrompt(sessCtx)
const convoHist = sessCtx.hist || []
const resp = await llmSvc.genResp({
msg,
sysPrompt,
convoHist
})
return {resp, nxtIntent: routeIntent(msg)}
}`;

function renderInsights(insights) {
  if (!insights.length) {
    insightList.innerHTML =
      '<p class="insight-empty">Add some code and run the tool to generate a walkthrough.</p>';
    return;
  }

  insightList.innerHTML = insights
    .map(
      (insight) => `
        <article class="insight-card">
          <h3>${insight.title}</h3>
          <p>${insight.body}</p>
        </article>
      `
    )
    .join("");
}

function renderMetrics(metrics) {
  if (!metrics) return;

  metricsPanel.innerHTML = `
    <div class="metric-card">
      <h3>Complexity</h3>
      <p>${metrics.level}</p>
      <span>Score: ${metrics.score}</span>
    </div>
  `;
}

function renderDeadCode(items) {
  if (!items.length) {
    deadCodePanel.innerHTML = "<p>No dead code detected.</p>";
    return;
  }

  deadCodePanel.innerHTML = items
    .map(item => `<div class="dead-item">${item}</div>`)
    .join("");
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.dataset.state = isError ? "error" : "idle";
}

function setResultMeta(language = "generic", chatbotSignals = []) {
  const readableLanguage = language === "generic" ? "language-neutral" : language;
  resultMeta.textContent = chatbotSignals.length
    ? `${readableLanguage} | developer-friendly profile | ${chatbotSignals.join(", ")}`
    : `${readableLanguage} | developer-friendly profile`;
}

async function runHumanizer() {
  const code = sourceCode.value.trim();

  if (!code) {
    humanizedCode.textContent = "// Humanized code will appear here.";
    renderInsights([]);
    setStatus("Paste some code to humanize.");
    return;
  }

  humanizeButton.disabled = true;
  setStatus("Humanizing your code...");

  try {
    const response = await fetch("/api/humanize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        options: {
          add_summary_comment: summaryToggle.checked,
          rename_identifiers: renameToggle.checked,
          normalize_spacing: spacingToggle.checked,
          language_hint: languageHint.value,
          target_profile: "developer_friendly",
          add_docstrings: true,
          explain_complexity: true,
          detect_dead_code: true,
        },
      }),
    });

    if (!response.ok) {
      throw new Error("The backend could not process this request.");
    }

    const payload = await response.json();
    humanizedCode.textContent = payload.code || "// Humanized code will appear here.";
    renderInsights(payload.insights || []);
    renderMetrics(payload.complexity);
    renderDeadCode(payload.dead_code || []);
    setResultMeta(payload.language, payload.chatbot_signals || []);
    setStatus(`Humanized successfully as ${payload.language || "generic"} developer-friendly code.`);
  } catch (error) {
    humanizedCode.textContent = "// Start the Python server and try again.";
    renderInsights([]);
    metricsPanel.innerHTML = "";
    renderDeadCode([]);
    setResultMeta();
    setStatus(error.message || "Unable to reach the backend.", true);
  } finally {
    humanizeButton.disabled = false;
  }
}

humanizeButton.addEventListener("click", runHumanizer);

clearButton.addEventListener("click", () => {
  sourceCode.value = "";
  humanizedCode.textContent = "// Humanized code will appear here.";
  renderInsights([]);
  metricsPanel.innerHTML = "";
  renderDeadCode([]);
  setResultMeta();
  setStatus("Cleared.");
});

loadExampleButton.addEventListener("click", () => {
  sourceCode.value = exampleSnippet;
  languageHint.value = "javascript";
  setStatus("Example loaded.");
});

copyButton.addEventListener("click", async () => {
  const output = humanizedCode.textContent;

  if (!output || output === "// Humanized code will appear here.") {
    return;
  }

  try {
    await navigator.clipboard.writeText(output);
    copyButton.textContent = "Copied";
  } catch (error) {
    copyButton.textContent = "Copy manually";
  }

  window.setTimeout(() => {
    copyButton.textContent = "Copy result";
  }, 1400);
});

uploadInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];

  if (!file) return;

  const text = await file.text();

  sourceCode.value = text;

  setStatus(`Loaded ${file.name}`);
});
