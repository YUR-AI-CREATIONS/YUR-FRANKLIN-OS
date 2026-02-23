import { useMemo } from "react";
import { useJobStore } from "../state/useJobStore.js";

export default function ProgressConsole() {
  const events = useJobStore((state) => state.events);
  const latest = useMemo(() => events.slice(-120).reverse(), [events]);

  return (
    <div className="h-full flex flex-col bg-black/60 border-l border-white/10">
      <div className="p-6 border-b border-white/10">
        <p className="text-xs tracking-[0.4em] uppercase text-cyan-300">Execution Trajectory</p>
        <h3 className="text-2xl mt-2">Real-time telemetry feed</h3>
      </div>
      <div className="flex-1 overflow-y-auto font-mono text-sm space-y-2 p-6 bg-black/40">
        {latest.length === 0 && <p className="opacity-60">Waiting for worker events…</p>}
        {latest.map((evt, index) => {
          const timestamp = Number(evt.timestamp);
          const displayTime = Number.isFinite(timestamp)
            ? new Date(timestamp * 1000).toLocaleTimeString()
            : new Date(evt.timestamp ?? Date.now()).toLocaleTimeString();
          return (
            <div key={`${evt.event}-${index}`} className="flex gap-2 border-b border-white/5 pb-2">
              <span className="text-cyan-300">[{displayTime}]</span>
              <span>{evt.event}</span>
              {evt.metadata?.page && <span>· Page {evt.metadata.page}</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
