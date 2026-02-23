import { useMemo } from "react";
import AscensionSphere from "../three/AscensionSphere.jsx";
import { useSphereStore } from "../state/useSphereStore";
import { useJobStore } from "../state/useJobStore";

export default function JobSphere() {
  const { injected, shatterMode, completionPulse } = useSphereStore((state) => ({
    injected: state.injected,
    shatterMode: state.shatterMode,
    completionPulse: state.completionPulse,
  }));
  const status = useJobStore((state) => state.status);

  const statusLabel = useMemo(() => {
    switch (status) {
      case "uploading":
        return "Injection bolt firing";
      case "processing":
        return shatterMode ? "Shatter mode engaged" : "Autoscaler uplifting";
      case "completed":
        return "Fusion complete";
      case "error":
        return "Anomoly detected";
      default:
        return "Idle";
    }
  }, [status, shatterMode]);

  return (
    <div className={`job-sphere ${completionPulse ? "pulse" : ""}`}>
      <div className={`job-sphere__glow ${injected ? "active" : ""}`} />
      <AscensionSphere reactive shatter={shatterMode} highlight={completionPulse} />
      <div className="job-sphere__status">
        <p>{statusLabel}</p>
        <span className="muted">Sphere telemetry live</span>
      </div>
    </div>
  );
}
