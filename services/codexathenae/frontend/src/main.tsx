import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ padding: 16 }}>
      <h1>CodexAthenae</h1>
      <p>Template mínimo. Siga os prompts em <code>prompts/frontend</code>.</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
