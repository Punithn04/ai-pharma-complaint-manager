import { createSlice } from "@reduxjs/toolkit";
import { sendMessage, uploadDocument } from "../agentThunks";

const EMPTY = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength_grade: "",
  batch_lot_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: "",
  complaint_type: "",
  complaint_date: "",
  detailed_description: "",
  initial_severity: "",
  priority: "",
};

const initialState = {
  fields: { ...EMPTY },
  changedFields: [], // highlighted in the UI after the latest turn
  duplicateOf: null,
  saved: null, // saved complaint id
};

// The agent owns the form. Merge returned fields on top of what we have so a
// partial extraction/edit never blanks existing values (mirrors the backend
// delta-merge reducer).
function applyAgentResult(state, payload) {
  state.fields = { ...state.fields, ...payload.form };
  state.changedFields = payload.changed_fields || [];
  state.duplicateOf = payload.duplicate_of ?? null;
  state.saved = null;
}

const complaintSlice = createSlice({
  name: "complaint",
  initialState,
  reducers: {
    resetForm: (state) => {
      state.fields = { ...EMPTY };
      state.changedFields = [];
      state.duplicateOf = null;
      state.saved = null;
    },
    markSaved: (state, action) => {
      state.saved = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addMatcher(
        (a) => [sendMessage.fulfilled.type, uploadDocument.fulfilled.type].includes(a.type),
        (state, action) => applyAgentResult(state, action.payload)
      );
  },
});

export const { resetForm, markSaved } = complaintSlice.actions;
export default complaintSlice.reducer;
