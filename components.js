export function renderMetrics(panel, metrics) {
  if (!metrics) {
    panel.innerHTML = "";
    return;
  }

  const items = [
    ["Readability", metrics.readability],
    ["Maintainability", metrics.maintainability],
    ["Complexity", metrics.complexity],
    ["Security", metrics.security],
    ["Humanization", metrics.humanization],
    ["Overall", metrics.overall],
  ];

  panel.innerHTML = items
    .map(
      ([label, value]) => `
        <article class="metric-card">
          <div class="metric-head">
            <h3>${label}</h3>
            <strong>${value}</strong>
          </div>
          <div class="metric-bar">
            <span style="width:${value}%"></span>
          </div>
        </article>
      `
    )
    .join("");
}

export function renderInsights(panel, insights) {
  if (!insights?.length) {
    panel.innerHTML = '<p class="empty-state">Run an action to generate a walkthrough.</p>';
    return;
  }

  panel.innerHTML = insights
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

export function renderSecurity(panel, security) {
  if (!security) {
    panel.innerHTML = '<p class="empty-state">Security findings will appear here.</p>';
    return;
  }

  const findings = security.findings?.length
    ? security.findings
        .map(
          (finding) => `
            <div class="finding-card risk-${finding.risk.toLowerCase()}">
              <h3>${finding.title}</h3>
              <p>${finding.explanation}</p>
              <strong>${finding.risk} risk</strong>
              <span>${finding.recommended_fix}</span>
            </div>
          `
        )
        .join("")
    : '<p class="empty-state">No security issues detected by the current heuristic scan.</p>';

  panel.innerHTML = `
    <div class="risk-banner">Overall Risk Level: ${security.risk_level}</div>
    ${findings}
  `;
}

export function renderDeadCode(panel, items) {
  if (!items?.length) {
    panel.innerHTML = "<p class=\"empty-state\">No dead code detected.</p>";
    return;
  }

  panel.innerHTML = items.map((item) => `<div class="dead-item">${item}</div>`).join("");
}

export function renderCareer(panel, payload) {
  if (!payload) {
    panel.innerHTML = '<p class="empty-state">Career assistant output will appear here.</p>';
    return;
  }

  panel.innerHTML = `
    <section class="career-block">
      <h3>Project Summary</h3>
      <p>${payload.project_summary}</p>
    </section>
    <section class="career-block">
      <h3>Resume Bullet Points</h3>
      ${payload.resume_bullet_points.map((item) => `<p>${item}</p>`).join("")}
    </section>
    <section class="career-block">
      <h3>Technical Highlights</h3>
      ${payload.technical_highlights.map((item) => `<p>${item}</p>`).join("")}
    </section>
    <section class="career-block">
      <h3>Interview Questions</h3>
      ${payload.interview_questions.map((item) => `<p>${item}</p>`).join("")}
    </section>
    <section class="career-block">
      <h3>Interview Answers</h3>
      ${payload.interview_answers.map((item) => `<p>${item}</p>`).join("")}
    </section>
    <section class="career-block">
      <h3>Complexity Explanation</h3>
      <p>${payload.complexity_explanation}</p>
    </section>
  `;
}

export function renderConversion(panel, payload) {
  if (!payload) {
    panel.textContent = "";
    return;
  }

  panel.textContent = payload.converted_code || "";
}
