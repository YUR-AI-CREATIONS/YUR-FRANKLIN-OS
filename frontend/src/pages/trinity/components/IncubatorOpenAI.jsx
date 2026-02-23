import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — OPENAI INCUBATOR
//  Floating crystalline processing chamber
// ============================================================

export default function IncubatorOpenAI({ jobStatus }) {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (ref.current) {
      // Slow hover
      ref.current.position.y = Math.sin(t * 0.8) * 0.3 + 4;

      // Slow rotation
      ref.current.rotation.y = t * 0.25;

      // Status glow boost
      const active = jobStatus === "processing" ? 1.0 : 0.4;
      ref.current.children[0].material.emissiveIntensity = active;
    }
  });

  return (
    <group ref={ref} position={[-8, 4, 0]}>
      {/* Core chamber */}
      <mesh>
        <dodecahedronGeometry args={[1.8, 0]} />
        <meshStandardMaterial
          color={"#1DA9FF"}
          emissive={"#1DA9FF"}
          emissiveIntensity={0.5}
          metalness={0.8}
          roughness={0.2}
          transparent
          opacity={0.85}
        />
      </mesh>

      {/* Internal Light */}
      <pointLight intensity={3} distance={12} color={"#1DA9FF"} />
    </group>
  );
}
