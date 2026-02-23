import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — ANTHROPIC INCUBATOR
//  Golden crystalline chamber with harmonic energy resonance
// ============================================================

export default function IncubatorAnthropic({ jobStatus }) {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (ref.current) {
      // Smooth harmonic hovering
      ref.current.position.y = Math.sin(t * 0.9 + 2.5) * 0.35 + 1;

      // Graceful slow rotation
      ref.current.rotation.x = t * 0.12;
      ref.current.rotation.z = t * 0.15;

      // Status glow boost
      const active = jobStatus === "processing" ? 1.0 : 0.3;
      ref.current.children[0].material.emissiveIntensity = active;
    }
  });

  return (
    <group ref={ref} position={[0, 2, -6]}>
      {/* Core chamber */}
      <mesh>
        <icosahedronGeometry args={[1.7, 0]} />
        <meshStandardMaterial
          color={"#FFD56E"}
          emissive={"#FFF3CC"}
          emissiveIntensity={0.45}
          metalness={0.9}
          roughness={0.15}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Warm internal light */}
      <pointLight intensity={3} distance={12} color={"#FFD56E"} />
    </group>
  );
}
