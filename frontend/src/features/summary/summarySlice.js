import { createSlice } from "@reduxjs/toolkit";
import { sendMessage, uploadDocument } from "../agentThunks";

const initialState = { text: "" };

const summarySlice = createSlice({
  name: "summary",
  initialState,
  reducers: {
    resetSummary: (state) => {
      state.text = "";
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(
      (a) => [sendMessage.fulfilled.type, uploadDocument.fulfilled.type].includes(a.type),
      (state, action) => {
        if (action.payload.summary) state.text = action.payload.summary;
      }
    );
  },
});

export const { resetSummary } = summarySlice.actions;
export default summarySlice.reducer;
