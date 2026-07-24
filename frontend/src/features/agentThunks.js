import { createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../api";

// One thunk per user action. Both resolve to the same payload shape
// { reply, form, risk, changed_fields, intent, duplicate_of }, and multiple
// slices (chat / complaint / risk) react to it via extraReducers.

export const sendMessage = createAsyncThunk(
  "agent/sendMessage",
  async (message, { getState }) => {
    const { sessionId } = getState().chat;
    return api.chat(sessionId, message);
  }
);

export const uploadDocument = createAsyncThunk(
  "agent/uploadDocument",
  async (file, { getState }) => {
    const { sessionId } = getState().chat;
    return api.upload(sessionId, file);
  }
);
