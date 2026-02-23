import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — FRANKLIN REACTOR CORE
//  Pulsing energy star with rotating ion rings and job-driven
//  luminosity.
// ============================================================

export default function Reactor({ jobStatus, progress }) {
  const coreRef = useRef();
  const ring1Ref = useRef();
  const ring2Ref = useRef();
  const ring3Ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // CORES
    if (coreRef.current) {
      coreRef.current.scale.setScalar(
        1.5 + Math.sin(t * 3) * 0.08 + (progress || 0) * 0.003
      );
      coreRef.current.material.emissiveIntensity =
        1.2 + (progress || 0) * 0.02;
    }

    // RINGS
    if (ring1Ref.current) {
      ring1Ref.current.rotation.z = t * 0.3;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.x = t * 0.2;
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.y = -t * 0.25;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* CORE */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[1.2, 2]} />
        <meshStandardMaterial
          color={"#48FFDC"}
          emissive={"#1DA9FF"}
          emissiveIntensity={1.5}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* RING 1 */}
      <mesh ref={ring1Ref}>
        <torusGeometry args={[3, 0.08, 16, 200]} />
        <meshStandardMaterial
          color={"#7F1DFF"}
          emissive={"#7F1DFF"}
          emissiveIntensity={0.8}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* RING 2 */}
      <mesh ref={ring2Ref} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[4, 0.06, 16, 200]} />
        <meshStandardMaterial
          color={"#48FFDC"}
          emissive={"#48FFDC"}
          emissiveIntensity={0.7}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* RING 3 */}
      <mesh ref={ring3Ref} rotation={[0, Math.PI / 2, 0]}>
        <torusGeometry args={[5.1, 0.05, 16, 200]} />
        <meshStandardMaterial
          color={"#1DA9FF"}
          emissive={"#1DA9FF"}
          emissiveIntensity={0.6}
          transparent
          opacity={0.5}
        />
      </mesh>

      {/* AURORA SOFT GLOW */}
      <pointLight
        position={[0, 0, 0]}
        intensity={3 + (progress || 0) * 0.03}
        distance={50}
        color={"#48FFDC"}
      />
    </group>
  );
}
