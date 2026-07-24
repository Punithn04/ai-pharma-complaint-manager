import { configureStore } from "@reduxjs/toolkit";
import chatReducer from "./features/chat/chatSlice";
import complaintReducer from "./features/complaint/complaintSlice";
import riskReducer from "./features/risk/riskSlice";

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    complaint: complaintReducer,
    risk: riskReducer,
  },
});
