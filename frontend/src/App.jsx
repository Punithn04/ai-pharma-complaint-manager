import ComplaintForm from "./components/ComplaintForm";
import RiskAssessment from "./components/RiskAssessment";
import ChatAssistant from "./components/ChatAssistant";

export default function App() {
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

      <main className="layout">
        <div className="col col--left">
          <ComplaintForm />
          <RiskAssessment />
        </div>
        <div className="col col--right">
          <ChatAssistant />
        </div>
      </main>
    </div>
  );
}
