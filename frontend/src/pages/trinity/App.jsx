import { Canvas } from "@react-three/fiber";
import { Suspense, useRef, useState } from "react";
import { OrbitControls } from "@react-three/drei";

import GalaxyBackground from "./components/GalaxyBackground";
import Reactor from "./components/Reactor";
import IncubatorOpenAI from "./components/IncubatorOpenAI";
import IncubatorGemini from "./components/IncubatorGemini";
import IncubatorAnthropic from "./components/IncubatorAnthropic";
import CompletedChamber from "./components/CompletedChamber";
import QuantumIcosahedron from "./components/QuantumIcosahedron";
import Tubes from "./components/Tubes";
import CapsuleTravelEngine from "./components/CapsuleTravelEngine";

import useTrinityJobPolling from "./hooks/useTrinityJobPolling";

import "./index.css";

// ============================================================
// TRINITY OS — FULL COSMIC ORCHESTRATION SCENE
// Franklin OS → Microfragmentation → Continuous Flow Tubes
// ============================================================

export default function App() {
  const [jobId, setJobId] = useState(null);

  // Pull live status + progress
  const { jobStatus, jobProgress } = useTrinityJobPolling(jobId);

  // Franklin OS is always the FIRST incubator
  const franklinStatus = jobStatus;

  return (
    <>
      {/* ---------------------------------------------------------
          HUD OVERLAY
      ---------------------------------------------------------- */}
      <div className="absolute top-4 left-4 text-xl font-bold holo-text">
        TRINITY INTELLIGENCE CLOUD — ETHEREAL GALAXY MODE
      </div>

      <div className="absolute top-16 left-4 float-panel">
        <div>Franklin OS Status: {franklinStatus || "Idle"}</div>
        <div>Job ID: {jobId || "—"}</div>
        <div>Progress: {jobProgress || 0}%</div>

        {/* Quick job starter for testing */}
        <button
          className="mt-4 px-4 py-2 rounded bg-galaxy-purple text-white"
          onClick={() => setJobId("local-dev-job")}
        >
          Start Simulated Job
        </button>
      </div>

      {/* ---------------------------------------------------------
         3D UNIVERSE
      ---------------------------------------------------------- */}
      <Canvas
        camera={{ position: [0, 0, 22], fov: 55 }}
        gl={{ antialias: true }}
        shadows
      >
        <Suspense fallback={null}>
          {/* Galaxy Nebula Background */}
          <GalaxyBackground />

          {/* Franklin OS Reactor Core */}
          <Reactor jobStatus={franklinStatus} progress={jobProgress} />

          {/* Crystal Splines / Tube Highways */}
          <Tubes />

          {/* ------------------------------------------------------
              QUANTUM CAPSULE SYSTEM
              - Always in motion
              - Continuous flow
              - Franklin → Incubators → Completion
          ------------------------------------------------------- */}
          <CapsuleTravelEngine progress={jobProgress}>
            <QuantumIcosahedron
              jobStatus={franklinStatus}
              progress={jobProgress}
            />
          </CapsuleTravelEngine>

          {/* ------------------------------------------------------
              AI INCUBATORS (DESTINATIONS)
              - Franklin splits microfragments
              - Tubes route them instantly
          ------------------------------------------------------- */}
          <IncubatorOpenAI jobStatus={jobStatus} />
          <IncubatorGemini jobStatus={jobStatus} />
          <IncubatorAnthropic jobStatus={jobStatus} />

          {/* Final collection chamber */}
          <CompletedChamber jobStatus={jobStatus} progress={jobProgress} />

          {/* Developer camera (can disable later) */}
          <OrbitControls />
        </Suspense>
      </Canvas>
    </>
  );
}
