import { useEffect, useState } from "react";
import { api } from "../api";

function sevClass(severity) {
  const s = (severity || "").toLowerCase();
  if (s === "critical") return "sev sev--critical";
  if (s === "major") return "sev sev--major";
  if (s === "minor") return "sev sev--minor";
  return "sev";
}

function DetailField({ label, value, full, area }) {
  return (
    <div className={`field ${full ? "field--full" : ""}`}>
      <label>{label}</label>
      <div className={`field-value filled ${area ? "field-value--area" : ""}`}>
        {value || <span className="placeholder">—</span>}
      </div>
    </div>
  );
}

function ComplaintDetail({ complaint, onClose }) {
  const c = complaint;
  const risk = c.risk_assessment || {};
  const hasRisk = risk.severity || risk.next_action || risk.rationale;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <h2>Complaint #{c.id}</h2>
            <p className="subtitle">
              Logged {c.created_at ? new Date(c.created_at).toLocaleString() : "—"}
            </p>
          </div>
          <button className="btn btn--ghost" onClick={onClose}>✕ Close</button>
        </div>

        {c.summary && (
          <div className="risk-block" style={{ marginTop: 14 }}>
            <span className="risk-label">AI Complaint Summary</span>
            <p>{c.summary}</p>
          </div>
        )}

        <fieldset>
          <legend>1 · Origin &amp; Customer Details</legend>
          <div className="grid-2">
            <DetailField label="Complaint Source" value={c.complaint_source} />
            <DetailField label="Customer Name" value={c.customer_name} />
          </div>
        </fieldset>

        <fieldset>
          <legend>2 · Product &amp; Batch Identification</legend>
          <div className="grid-2">
            <DetailField label="Product Name" value={c.product_name} />
            <DetailField label="Product Strength/Grade" value={c.product_strength_grade} />
            <DetailField label="Batch/Lot Number" value={c.batch_lot_number} />
            <DetailField label="Manufacturing Date" value={c.manufacturing_date} />
            <DetailField label="Expiry Date" value={c.expiry_date} />
            <DetailField label="Quantity Affected" value={c.quantity_affected} />
          </div>
        </fieldset>

        <fieldset>
          <legend>3 · Complaint Details</legend>
          <div className="grid-2">
            <DetailField label="Complaint Type" value={c.complaint_type} />
            <DetailField label="Complaint Date" value={c.complaint_date} />
          </div>
          <DetailField label="Detailed Complaint Description" value={c.detailed_description} full area />
        </fieldset>

        <fieldset>
          <legend>4 · Initial Assessment &amp; Priority</legend>
          <div className="grid-2">
            <DetailField label="Initial Severity" value={c.initial_severity} />
            <DetailField label="Priority" value={c.priority} />
          </div>
        </fieldset>

        <fieldset>
          <legend>✨ AI Co-pilot Risk Assessment</legend>
          {!hasRisk && <p className="muted">No risk assessment recorded.</p>}
          {hasRisk && (
            <div className="risk-body">
              <div className="risk-row">
                {risk.severity && <span className={sevClass(risk.severity)}>{risk.severity}</span>}
                <span className="risk-val">{risk.risk_level ? `Risk Level: ${risk.risk_level}` : ""}</span>
              </div>
              {risk.next_action && (
                <div className="risk-block">
                  <span className="risk-label">Recommended Next Action</span>
                  <p className="risk-action">{risk.next_action}</p>
                </div>
              )}
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
                    {risk.risk_factors.map((f, i) => <span className="chip" key={i}>{f}</span>)}
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
        </fieldset>
      </div>
    </div>
  );
}

export default function ComplaintHistory() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setComplaints(await api.listComplaints());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <section className="card history-card">
      <div className="card-head">
        <div>
          <h2>📋 Complaint History</h2>
          <p className="subtitle">All saved complaints, most recent first — click a row to view full details</p>
        </div>
        <button className="btn btn--ghost" onClick={load}>⟳ Refresh</button>
      </div>

      {loading && <p className="muted">Loading…</p>}
      {error && <p className="muted">⚠ {error}</p>}
      {!loading && !error && complaints.length === 0 && (
        <p className="muted">
          No complaints saved yet. Log one from the New Complaint tab, then save it.
        </p>
      )}

      {!loading && complaints.length > 0 && (
        <div className="table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Logged</th>
                <th>Source</th>
                <th>Product</th>
                <th>Batch</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((c) => (
                <tr key={c.id} className="history-row" onClick={() => setSelected(c)}>
                  <td>#{c.id}</td>
                  <td>{c.created_at ? new Date(c.created_at).toLocaleString() : "—"}</td>
                  <td>{c.complaint_source || "—"}</td>
                  <td>{c.product_name || "—"}</td>
                  <td>{c.batch_lot_number || "—"}</td>
                  <td>{c.complaint_type || "—"}</td>
                  <td>
                    {c.risk_assessment?.severity ? (
                      <span className={sevClass(c.risk_assessment.severity)}>
                        {c.risk_assessment.severity}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>{c.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && <ComplaintDetail complaint={selected} onClose={() => setSelected(null)} />}
    </section>
  );
}
