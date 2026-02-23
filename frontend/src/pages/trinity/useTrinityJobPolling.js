import { useEffect, useState } from "react";

// ============================================================
// TRINITY OS — JOB POLLING HOOK
// Connects to the backend FastAPI /jobs/{jobId} route
// and streams status + progress into the 3D universe.
// ============================================================

export default function useTrinityJobPolling(jobId) {
  const [jobStatus, setJobStatus] = useState("idle");
  const [jobProgress, setJobProgress] = useState(0);

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/jobs/${jobId}`);
        if (!res.ok) return;

        const data = await res.json();

        setJobStatus(data.status || "unknown");
        setJobProgress(data.progress || 0);
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 800);

    return () => clearInterval(interval);
  }, [jobId]);

  return { jobStatus, jobProgress };
}
