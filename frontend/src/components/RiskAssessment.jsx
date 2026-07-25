import { useSelector } from "react-redux";

function sevClass(severity) {
  const s = (severity || "").toLowerCase();
  if (s === "critical") return "sev sev--critical";
  if (s === "major") return "sev sev--major";
  if (s === "minor") return "sev sev--minor";
  return "sev";
}

export default function RiskAssessment() {
  const risk = useSelector((s) => s.risk.data);
  const summary = useSelector((s) => s.summary.text);
  const hasRisk = risk.severity || risk.next_action || risk.rationale;

  return (
    <section className="card risk-card">
      <div className="card-head">
        <h2>✨ AI Co-pilot Risk Assessment</h2>
        {risk.severity && <span className={sevClass(risk.severity)}>{risk.severity}</span>}
      </div>

      {!hasRisk && (
        <p className="muted">
          The AI will reason about severity, risk level and next actions once a
          complaint is logged.
        </p>
      )}

      {hasRisk && (
        <div className="risk-body">
          {summary && (
            <div className="risk-block">
              <span className="risk-label">Complaint Summary</span>
              <p>{summary}</p>
            </div>
          )}
          <div className="risk-row">
            <span className="risk-label">Risk Level</span>
            <span className="risk-val">{risk.risk_level || "—"}</span>
          </div>
          <div className="risk-block">
            <span className="risk-label">Recommended Next Action</span>
            <p className="risk-action">{risk.next_action || "—"}</p>
          </div>
          {risk.rationale && (
            <div className="risk-block">
              <span className="risk-label">Rationale</span>
              <p>{risk.rationale}</p>
            </div>
          )}
          {risk.risk_factors?.length > 0 && (
            <div className="risk-block">
              <span className="risk-label">Risk Factors</span>
              <div className="chips">
                {risk.risk_factors.map((f, i) => (
                  <span className="chip" key={i}>{f}</span>
                ))}
              </div>
            </div>
          )}
          {risk.potential_root_cause && (
            <div className="risk-block">
              <span className="risk-label">Potential Root Cause</span>
              <p>{risk.potential_root_cause}</p>
            </div>
          )}
          {risk.capa_recommendation && (
            <div className="risk-block">
              <span className="risk-label">CAPA Recommendation</span>
              <p>{risk.capa_recommendation}</p>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
