import { useJobStore } from "../state/useJobStore.js";

export default function DeliverableHologram() {
  const outputs = useJobStore((state) => state.outputs);

  return (
    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-2xl p-6 bg-white/5 border border-white/20 backdrop-blur-xl rounded-2xl shadow-xl text-white">
      <h2 className="text-3xl font-bold mb-4 tracking-wide text-cyan-300">Your Deliverables</h2>
      {outputs.length === 0 && <p className="opacity-60">Awaiting exports…</p>}
      <div className="grid grid-cols-1 gap-3">
        {outputs.map((output) => (
          <a
            key={output.name}
            href={output.url}
            download
            className="p-3 rounded-xl bg-black/40 border border-cyan-400/30 hover:bg-cyan-500/20 transition-all"
          >
            {output.name}
          </a>
        ))}
      </div>
    </div>
  );
}
