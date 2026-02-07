import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress ResizeObserver errors (React Flow known issue)
const origError = console.error;
console.error = (...args) => {
  if (args[0]?.includes?.('ResizeObserver') || String(args[0])?.includes?.('ResizeObserver')) return;
  origError.apply(console, args);
};

window.addEventListener('error', (e) => {
  if (e.message?.includes?.('ResizeObserver')) {
    e.stopImmediatePropagation();
    e.preventDefault();
    return true;
  }
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
