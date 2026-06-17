import { api } from "./services.js";
import {
  renderCareer,
  renderConversion,
  renderDeadCode,
  renderInsights,
  renderMetrics,
  renderSecurity,
} from "./components.js";

const state = {
  activeTab: "humanizer",
  monacoReady: false,
  sourceEditor: null,
  humanizedEditor: null,
  convertedEditor: null,
};

const sourceFallback = document.getElementById("sourceCode");
const humanizedFallback = document.getElementById("humanizedCode");
const convertedFallback = document.getElementById("convertedCode");
const insightPanel = document.getElementById("insightList");
const metricsPanel = document.getElementById("metricsPanel");
const deadCodePanel = document.getElementById("deadCodePanel");
const securityPanel = document.getElementById("securityPanel");
const careerPanel = document.getElementById("careerPanel");
const uploadInput = document.getElementById("uploadInput");
const dropZone = document.getElementById("dropZone");
const statusMessage = document.getElementById("statusMessage");
const themeToggle = document.getElementById("themeToggle");
const languageHint = document.getElementById("languageHint");
const sourceLanguage = document.getElementById("sourceLanguage");
const targetLanguage = document.getElementById("targetLanguage");
const refactorMode = document.getElementById("refactorMode");
const conceptInputs = Array.from(document.querySelectorAll("[data-concept]"));
const downloadButton = document.getElementById("downloadConverted");

function getSelectedConcepts() {
  return conceptInputs.filter((input) => input.checked).map((input) => input.value);
}

function setStatus(message, tone = "idle") {
  statusMessage.textContent = message;
  statusMessage.dataset.state = tone;
}

function getSourceCode() {
  return state.sourceEditor ? state.sourceEditor.getValue() : sourceFallback.value;
}

function setSourceCode(value) {
  if (state.sourceEditor) {
    state.sourceEditor.setValue(value);
  }
  sourceFallback.value = value;
}

function setHumanizedCode(value) {
  if (state.humanizedEditor) {
    state.humanizedEditor.setValue(value);
  }
  humanizedFallback.textContent = value;
}

function setConvertedCode(value) {
  if (state.convertedEditor) {
    state.convertedEditor.setValue(value);
  }
  convertedFallback.textContent = value;
}

function currentTheme() {
  return document.body.dataset.theme || "dark";
}

function toggleTheme() {
  document.body.dataset.theme = currentTheme() === "dark" ? "light" : "dark";
  themeToggle.textContent = currentTheme() === "dark" ? "Light Mode" : "Dark Mode";
}

function switchTab(tab) {
  state.activeTab = tab;
  document.querySelectorAll("[data-tab-button]").forEach((button) => {
    button.dataset.active = String(button.dataset.tabButton === tab);
  });
  document.querySelectorAll("[data-tab-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.tabPanel !== tab;
  });
}

async function runHumanizer() {
  const code = getSourceCode().trim();
  if (!code) {
    setStatus("Paste or drop some code first.", "warning");
    return;
  }

  setStatus("Humanizing code with concept and quality analysis...");
  const payload = await api.humanize({
    code,
    language_hint: languageHint.value,
    concept_preferences: getSelectedConcepts(),
    refactor_mode: refactorMode.value,
    options: {
      add_summary_comment: true,
      rename_identifiers: true,
      normalize_spacing: true,
      add_docstrings: true,
      explain_complexity: true,
      detect_dead_code: true,
      target_profile: "developer_friendly",
    },
  });

  setHumanizedCode(payload.code || "");
  renderInsights(insightPanel, payload.insights || []);
  renderMetrics(metricsPanel, payload.quality);
  renderDeadCode(deadCodePanel, payload.dead_code || []);
  renderSecurity(securityPanel, payload.security);
  setStatus(`Humanized as ${payload.language} in ${payload.mode} mode.`);
}

async function runConverter() {
  const code = getSourceCode().trim();
  if (!code) {
    setStatus("Paste or drop some code first.", "warning");
    return;
  }

  setStatus("Converting code between languages...");
  const payload = await api.convert({
    code,
    source_language: sourceLanguage.value,
    target_language: targetLanguage.value,
    concept_preferences: getSelectedConcepts(),
    refactor_mode: refactorMode.value,
  });

  renderConversion(convertedFallback, payload);
  setConvertedCode(payload.converted_code || "");
  document.getElementById("conversionMeta").innerHTML = `
    <strong>Confidence:</strong> ${payload.confidence_score}%<br />
    <strong>Warnings:</strong> ${(payload.warnings || []).join(" | ")}
  `;
  setStatus(`Converted ${payload.source_language} to ${payload.target_language}.`);
}

async function runCareerAssistant() {
  const code = getSourceCode().trim();
  if (!code) {
    setStatus("Paste or drop some code first.", "warning");
    return;
  }

  setStatus("Building project summary, resume bullets, and interview prep...");
  const payload = await api.assistant({
    code,
    language_hint: languageHint.value,
    project_name: "Code Humanizer V2",
  });

  renderCareer(careerPanel, payload.career_pack);
  renderMetrics(metricsPanel, payload.analysis.quality);
  renderSecurity(securityPanel, payload.analysis.security);
  renderInsights(insightPanel, payload.analysis.insights || []);
  setStatus("Career assistant pack generated.");
}

function downloadConvertedCode() {
  const blob = new Blob([convertedFallback.textContent || ""], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `converted.${targetLanguage.value === "python" ? "py" : targetLanguage.value}`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function attachUploadHandlers() {
  uploadInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) {
      return;
    }

    setSourceCode(await file.text());
    setStatus(`Loaded ${file.name}.`);
  });

  ["dragenter", "dragover"].forEach((eventName) =>
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.dataset.drag = "true";
    })
  );

  ["dragleave", "drop"].forEach((eventName) =>
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.dataset.drag = "false";
    })
  );

  dropZone.addEventListener("drop", async (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (!file) {
      return;
    }
    setSourceCode(await file.text());
    setStatus(`Loaded ${file.name} from drag and drop.`);
  });
}

function setupMonaco() {
  if (!window.require) {
    return;
  }

  window.require.config({ paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs" } });
  window.require(["vs/editor/editor.main"], () => {
    state.monacoReady = true;
    state.sourceEditor = monaco.editor.create(document.getElementById("sourceEditor"), {
      value: sourceFallback.value,
      language: "python",
      automaticLayout: true,
      minimap: { enabled: false },
      theme: currentTheme() === "dark" ? "vs-dark" : "vs",
    });
    state.humanizedEditor = monaco.editor.create(document.getElementById("humanizedEditor"), {
      value: "",
      language: "python",
      readOnly: true,
      automaticLayout: true,
      minimap: { enabled: false },
      theme: currentTheme() === "dark" ? "vs-dark" : "vs",
    });
    state.convertedEditor = monaco.editor.create(document.getElementById("convertedEditor"), {
      value: "",
      language: "python",
      readOnly: true,
      automaticLayout: true,
      minimap: { enabled: false },
      theme: currentTheme() === "dark" ? "vs-dark" : "vs",
    });
  });
}

function bindEvents() {
  document.getElementById("humanizeButton").addEventListener("click", () => runHumanizer().catch((error) => setStatus(error.message, "error")));
  document.getElementById("convertButton").addEventListener("click", () => runConverter().catch((error) => setStatus(error.message, "error")));
  document.getElementById("assistantButton").addEventListener("click", () => runCareerAssistant().catch((error) => setStatus(error.message, "error")));
  document.getElementById("clearButton").addEventListener("click", () => {
    setSourceCode("");
    setHumanizedCode("");
    setConvertedCode("");
    renderInsights(insightPanel, []);
    renderMetrics(metricsPanel, null);
    renderDeadCode(deadCodePanel, []);
    renderSecurity(securityPanel, null);
    renderCareer(careerPanel, null);
    setStatus("Workspace cleared.");
  });
  document.getElementById("loadExample").addEventListener("click", () => {
    setSourceCode(`def hndl_usr_msg(msg, llm_svc, sess_ctx):\n    resp = llm_svc.gen_resp(msg=msg)\n    return resp`);
    languageHint.value = "python";
    sourceLanguage.value = "python";
    targetLanguage.value = "java";
    setStatus("Example loaded.");
  });
  document.querySelectorAll("[data-tab-button]").forEach((button) =>
    button.addEventListener("click", () => switchTab(button.dataset.tabButton))
  );
  document.getElementById("copyHumanized").addEventListener("click", () => navigator.clipboard.writeText(humanizedFallback.textContent || ""));
  document.getElementById("copyConverted").addEventListener("click", () => navigator.clipboard.writeText(convertedFallback.textContent || ""));
  downloadButton.addEventListener("click", downloadConvertedCode);
  themeToggle.addEventListener("click", toggleTheme);
}

bindEvents();
attachUploadHandlers();
switchTab("humanizer");
renderInsights(insightPanel, []);
renderDeadCode(deadCodePanel, []);
renderSecurity(securityPanel, null);
renderCareer(careerPanel, null);
setupMonaco();
