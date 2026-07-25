import { createSlice, nanoid } from "@reduxjs/toolkit";
import { sendMessage, uploadDocument } from "../agentThunks";

const initialState = {
  sessionId: nanoid(),
  messages: [
    {
      role: "assistant",
      content:
        "Upload a complaint document or describe the complaint, and I'll " +
        "extract the details and fill the form on the left for you.",
    },
  ],
  status: "idle", // idle | loading | error
  error: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    // Starts a brand-new chat session. When called with a saved complaint id
    // (after Save Complaint), it also clears the prior conversation log and
    // greets with a confirmation instead of the generic welcome message.
    resetSession: {
      prepare: (savedId) => ({ payload: savedId ?? null }),
      reducer: (state, action) => {
        state.sessionId = nanoid();
        state.messages = action.payload
          ? [{
              role: "assistant",
              content: `✅ Complaint #${action.payload} saved successfully. ` +
                "Starting a new complaint — describe it or upload a document to begin.",
            }]
          : initialState.messages;
        state.status = "idle";
        state.error = null;
      },
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.messages.push({ role: "user", content: action.meta.arg });
        state.status = "loading";
        state.error = null;
      })
      .addCase(uploadDocument.pending, (state, action) => {
        state.messages.push({
          role: "user",
          content: `📎 Uploaded: ${action.meta.arg.name}`,
        });
        state.status = "loading";
        state.error = null;
      })
      .addMatcher(
        (a) => [sendMessage.fulfilled.type, uploadDocument.fulfilled.type].includes(a.type),
        (state, action) => {
          state.status = "idle";
          state.messages.push({ role: "assistant", content: action.payload.reply });
        }
      )
      .addMatcher(
        (a) => [sendMessage.rejected.type, uploadDocument.rejected.type].includes(a.type),
        (state, action) => {
          state.status = "error";
          state.error = action.error.message;
          state.messages.push({
            role: "assistant",
            content: `⚠️ ${action.error.message}`,
          });
        }
      );
  },
});

export const { resetSession } = chatSlice.actions;
export default chatSlice.reducer;
