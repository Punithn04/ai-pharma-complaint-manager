import { useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendMessage, uploadDocument } from "../features/agentThunks";

export default function ChatAssistant() {
  const dispatch = useDispatch();
  const { messages, status } = useSelector((s) => s.chat);
  const [text, setText] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef(null);
  const loading = status === "loading";

  const submit = (e) => {
    e.preventDefault();
    const value = text.trim();
    if (!value || loading) return;
    dispatch(sendMessage(value));
    setText("");
  };

  const onFile = (file) => {
    if (file && !loading) dispatch(uploadDocument(file));
  };

  return (
    <section className="card assistant-card">
      <div className="card-head">
        <h2>✨ AI Complaint Intake Assistant</h2>
        <span className="pill pill--beta">BETA</span>
      </div>

      <div
        className={`dropzone ${dragging ? "dragging" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); onFile(e.dataTransfer.files[0]); }}
        onClick={() => fileRef.current?.click()}
      >
        <div className="drop-icon">⬆</div>
        <p>Drag &amp; drop complaint document here<br /><span className="link">or click to browse</span></p>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt,.eml,.docx,.md"
          hidden
          onChange={(e) => onFile(e.target.files[0])}
        />
      </div>
      <p className="hint">Supported: PDF, TXT, EML · Max 10 MB</p>

      <div className="chat-log">
        {messages.map((m, i) => (
          <div key={i} className={`msg msg--${m.role}`}>
            {m.role === "assistant" && <span className="msg-avatar">🤖</span>}
            <div className="msg-bubble">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="msg msg--assistant">
            <span className="msg-avatar">🤖</span>
            <div className="msg-bubble typing"><span></span><span></span><span></span></div>
          </div>
        )}
      </div>

      <form className="chat-input" onSubmit={submit}>
        <input
          type="text"
          placeholder="Describe the complaint or a correction…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="send-btn" disabled={loading || !text.trim()}>➤</button>
      </form>
      <p className="disclaimer">AI responses may contain errors. Please verify information.</p>
    </section>
  );
}
