import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — QUANTUM ICOSAHEDRON CAPSULE
//  The 20-sided job carrier that moves through tubes and reactors.
// ============================================================

export default function QuantumIcosahedron({ jobStatus, progress }) {
  const meshRef = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (meshRef.current) {
      // Base rotation
      meshRef.current.rotation.x = t * 0.4;
      meshRef.current.rotation.y = t * 0.6;

      // Progress-driven spin acceleration
      meshRef.current.rotation.z = (progress || 0) * 0.05;

      // Breathing scale (with progress intensification)
      const base = 1 + Math.sin(t * 3) * 0.05;
      const prog = 1 + (progress || 0) * 0.0025;
      meshRef.current.scale.setScalar(base * prog);

      // Emissive intensity increases with progress
      meshRef.current.material.emissiveIntensity = 0.8 + (progress || 0) * 0.03;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, 5]}>
      <icosahedronGeometry args={[1.5, 0]} />

      <meshStandardMaterial
        color={"#7F1DFF"}
        emissive={"#48FFDC"}
        emissiveIntensity={0.9}
        roughness={0.15}
        metalness={0.85}
      />

      {/* Internal light core */}
      <pointLight
        intensity={4 + (progress || 0) * 0.05}
        distance={20}
        color={"#48FFDC"}
      />
    </mesh>
  );
}
