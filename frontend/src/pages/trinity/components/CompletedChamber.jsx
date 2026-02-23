import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — COMPLETED CHAMBER
//  Glowing crystalline destination pod for finished results
// ============================================================

export default function CompletedChamber({ jobStatus, progress }) {
  const ref = useRef();
  const innerRef = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (ref.current) {
      // Soft float
      ref.current.position.y = Math.sin(t * 0.45) * 0.3 - 4.2;
      ref.current.rotation.y = t * 0.15;
    }

    if (innerRef.current) {
      // Inner orb glow intensifies as completion approaches
      const p = (progress || 0) / 100;

      innerRef.current.scale.setScalar(0.8 + p * 1.8);
      innerRef.current.material.emissiveIntensity = 0.4 + p * 2.4;
      innerRef.current.material.opacity = 0.4 + p * 0.55;
    }
  });

  return (
    <group ref={ref} position={[0, -4, 0]}>
      {/* Outer crystalline shell */}
      <mesh>
        <dodecahedronGeometry args={[2.6, 1]} />
        <meshStandardMaterial
          color={"#7F1DFF"}
          emissive={"#1DA9FF"}
          emissiveIntensity={0.3}
          metalness={0.75}
          roughness={0.25}
          transparent
          opacity={0.4}
        />
      </mesh>

      {/* Inner completion orb */}
      <mesh ref={innerRef}>
        <sphereGeometry args={[1.2, 32, 32]} />
        <meshStandardMaterial
          color={"#48FFDC"}
          emissive={"#48FFDC"}
          emissiveIntensity={1.2}
          transparent
          opacity={0.5}
        />
      </mesh>

      {/* Ambient glow */}
      <pointLight intensity={3} distance={14} color={"#48FFDC"} />
    </group>
  );
}
