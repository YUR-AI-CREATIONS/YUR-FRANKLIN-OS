import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — GEMINI INCUBATOR
//  Prismatic teal/magenta energy chamber
// ============================================================

export default function IncubatorGemini({ jobStatus }) {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (ref.current) {
      // Gentle vertical hovering
      ref.current.position.y = Math.sin(t * 0.7 + 1.2) * 0.3 - 2;

      // Slow rotation
      ref.current.rotation.x = t * 0.18;
      ref.current.rotation.y = t * 0.22;

      // Status glow boost
      const active = jobStatus === "processing" ? 1.0 : 0.35;
      ref.current.children[0].material.emissiveIntensity = active;
    }
  });

  return (
    <group ref={ref} position={[8, -2, 0]}>
      {/* Core chamber */}
      <mesh>
        <octahedronGeometry args={[1.8, 0]} />
        <meshStandardMaterial
          color={"#48FFDC"}
          emissive={"#F72585"}
          emissiveIntensity={0.5}
          metalness={0.85}
          roughness={0.2}
          transparent
          opacity={0.85}
        />
      </mesh>

      {/* Prism Light */}
      <pointLight intensity={3} distance={12} color={"#48FFDC"} />
    </group>
  );
}
