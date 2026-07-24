import { createSlice } from "@reduxjs/toolkit";
import { sendMessage, uploadDocument } from "../agentThunks";

const initialState = {
  data: {
    severity: "",
    risk_level: "",
    next_action: "",
    rationale: "",
    risk_factors: [],
    potential_root_cause: "",
    capa_recommendation: "",
  },
};

const riskSlice = createSlice({
  name: "risk",
  initialState,
  reducers: {
    resetRisk: (state) => {
      state.data = initialState.data;
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(
      (a) => [sendMessage.fulfilled.type, uploadDocument.fulfilled.type].includes(a.type),
      (state, action) => {
        if (action.payload.risk && Object.keys(action.payload.risk).length) {
          state.data = { ...state.data, ...action.payload.risk };
        }
      }
    );
  },
});

export const { resetRisk } = riskSlice.actions;
export default riskSlice.reducer;
