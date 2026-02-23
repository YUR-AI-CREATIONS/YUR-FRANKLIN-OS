import { useEffect } from "react";
import { useJobStore } from "../state/useJobStore";

export default function CompletionPanel() {
  const { jobId, outputs, setOutputs } = useJobStore((state) => ({
    jobId: state.jobId,
    outputs: state.outputs,
    setOutputs: state.setOutputs,
  }));

  useEffect(() => {
    const baseUrl = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
    if (!jobId || !baseUrl) return;

    const fetchOutputs = async () => {
      try {
        const response = await fetch(`${baseUrl}/jobs/${jobId}/outputs`);
        if (!response.ok) {
          throw new Error("Unable to list outputs");
        }
        const payload = await response.json();
        setOutputs(payload.outputs || []);
      } catch (error) {
        console.warn("Failed to fetch outputs", error);
      }
    };

    fetchOutputs();
  }, [jobId, setOutputs]);

  return (
    <div className="completion-panel">
      <p className="eyebrow">THE UNIFICATION EVENT</p>
      <h2>MasterPackage ready.</h2>
      <p>
        Every orbit collapses inward. Data fuses and the final crystalline sphere cracks open, revealing every deliverable.
      </p>
      <div className="completion-panel__grid">
        {outputs.length === 0 && <p>Awaiting final exports…</p>}
        {outputs.map((output) => (
          <a key={output.name} href={output.url} target="_blank" rel="noreferrer" className="deliverable-card">
            <span>{output.name}</span>
            <small>{output.size || "live"}</small>
          </a>
        ))}
      </div>
    </div>
  );
}
