import { useDispatch, useSelector } from "react-redux";
import { api } from "../api";
import { resetForm } from "../features/complaint/complaintSlice";
import { resetRisk } from "../features/risk/riskSlice";
import { resetSummary } from "../features/summary/summarySlice";
import { resetSession } from "../features/chat/chatSlice";

function Field({ name, label, value, changed, missing, full, area }) {
  const filled = value && value.trim() !== "";
  const showMissing = !filled && missing;
  return (
    <div className={`field ${full ? "field--full" : ""}`}>
      <label>
        {label}
        {filled && <span className="ai-badge">AI</span>}
        {showMissing && <span className="missing-badge">Required</span>}
      </label>
      <div className={`field-value ${filled ? "filled" : ""} ${changed ? "changed" : ""} ${showMissing ? "missing" : ""} ${area ? "field-value--area" : ""}`}>
        {filled ? value : <span className="placeholder">Awaiting AI extraction…</span>}
      </div>
    </div>
  );
}

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { fields, changedFields, missingFields, duplicateOf } = useSelector((s) => s.complaint);
  const risk = useSelector((s) => s.risk.data);
  const summary = useSelector((s) => s.summary.text);
  const sessionId = useSelector((s) => s.chat.sessionId);

  const isChanged = (n) => changedFields.includes(n);
  const isMissing = (n) => missingFields.includes(n);

  // Saving finalizes the record, so the form is reloaded blank, the risk
  // panel clears, and the chat log is cleared, ready for the next complaint.
  const handleSave = async () => {
    const res = await api.saveComplaint(sessionId, fields, risk, summary);
    dispatch(resetForm());
    dispatch(resetRisk());
    dispatch(resetSummary());
    dispatch(resetSession(res.id));
  };

  const handleReset = () => {
    dispatch(resetForm());
    dispatch(resetRisk());
    dispatch(resetSummary());
    dispatch(resetSession());
  };

  return (
    <section className="card form-card">
      <div className="card-head">
        <div>
          <h2>Log Customer Complaint</h2>
          <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <span className="pill pill--pending">Pending Triage</span>
      </div>

      {duplicateOf && (
        <div className="banner banner--warn">
          ⚠ Possible duplicate — an earlier complaint (#{duplicateOf}) exists for this
          product &amp; batch. Investigate as a potential batch-level issue.
        </div>
      )}

      <fieldset>
        <legend>1 · Origin &amp; Customer Details</legend>
        <div className="grid-2">
          <Field name="complaint_source" label="Complaint Source" value={fields.complaint_source} changed={isChanged("complaint_source")} missing={isMissing("complaint_source")} />
          <Field name="customer_name" label="Customer Name" value={fields.customer_name} changed={isChanged("customer_name")} missing={isMissing("customer_name")} />
        </div>
      </fieldset>

      <fieldset>
        <legend>2 · Product &amp; Batch Identification</legend>
        <div className="grid-2">
          <Field name="product_name" label="Product Name" value={fields.product_name} changed={isChanged("product_name")} missing={isMissing("product_name")} />
          <Field name="product_strength_grade" label="Product Strength/Grade" value={fields.product_strength_grade} changed={isChanged("product_strength_grade")} missing={isMissing("product_strength_grade")} />
          <Field name="batch_lot_number" label="Batch/Lot Number" value={fields.batch_lot_number} changed={isChanged("batch_lot_number")} missing={isMissing("batch_lot_number")} />
          <Field name="manufacturing_date" label="Manufacturing Date" value={fields.manufacturing_date} changed={isChanged("manufacturing_date")} missing={isMissing("manufacturing_date")} />
          <Field name="expiry_date" label="Expiry Date" value={fields.expiry_date} changed={isChanged("expiry_date")} missing={isMissing("expiry_date")} />
          <Field name="quantity_affected" label="Quantity Affected" value={fields.quantity_affected} changed={isChanged("quantity_affected")} missing={isMissing("quantity_affected")} />
        </div>
      </fieldset>

      <fieldset>
        <legend>3 · Complaint Details</legend>
        <div className="grid-2">
          <Field name="complaint_type" label="Complaint Type" value={fields.complaint_type} changed={isChanged("complaint_type")} missing={isMissing("complaint_type")} />
          <Field name="complaint_date" label="Complaint Date" value={fields.complaint_date} changed={isChanged("complaint_date")} missing={isMissing("complaint_date")} />
        </div>
        <Field name="detailed_description" label="Detailed Complaint Description" value={fields.detailed_description} changed={isChanged("detailed_description")} missing={isMissing("detailed_description")} full area />
      </fieldset>

      <fieldset>
        <legend>4 · Initial Assessment &amp; Priority</legend>
        <div className="grid-2">
          <Field name="initial_severity" label="Initial Severity" value={fields.initial_severity} changed={isChanged("initial_severity")} />
          <Field name="priority" label="Priority" value={fields.priority} changed={isChanged("priority")} />
        </div>
      </fieldset>

      <div className="form-actions">
        <button className="btn btn--ghost" onClick={handleReset}>↺ Reset Form</button>
        <button className="btn btn--primary" onClick={handleSave}>💾 Save Complaint</button>
      </div>
    </section>
  );
}
