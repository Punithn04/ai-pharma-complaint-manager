import { useState } from "react";
import ComplaintForm from "./components/ComplaintForm";
import RiskAssessment from "./components/RiskAssessment";
import ChatAssistant from "./components/ChatAssistant";
import ComplaintHistory from "./components/ComplaintHistory";

export default function App() {
  const [tab, setTab] = useState("new"); // "new" | "history"

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo">A</span>
          <div>
            <strong>AIVOA</strong>
            <span className="brand-sub">Customer Complaint Management · Pharma QMS</span>
          </div>
        </div>
        <span className="env-tag">API &amp; FDF</span>
      </header>

      <nav className="tabbar">
        <button
          className={`tab ${tab === "new" ? "tab--active" : ""}`}
          onClick={() => setTab("new")}
        >
          New Complaint
        </button>
        <button
          className={`tab ${tab === "history" ? "tab--active" : ""}`}
          onClick={() => setTab("history")}
        >
          📋 Complaint History
        </button>
      </nav>

      {tab === "new" ? (
        <main className="layout">
          <div className="col col--left">
            <ComplaintForm />
            <RiskAssessment />
          </div>
          <div className="col col--right">
            <ChatAssistant />
          </div>
        </main>
      ) : (
        <main className="layout layout--single">
          <ComplaintHistory />
        </main>
      )}
    </div>
  );
}
