import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress ResizeObserver errors (React Flow known issue)
const resizeObserverError = window.onerror;
window.onerror = (message, ...args) => {
  if (message?.includes?.('ResizeObserver')) return true;
  return resizeObserverError?.(message, ...args);
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
