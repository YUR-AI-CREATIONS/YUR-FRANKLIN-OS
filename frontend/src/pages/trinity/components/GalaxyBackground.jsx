import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ============================================================
//  TRINITY OS — ETHEREAL GALAXY BACKDROP
//  A soft, volumetric, drifting nebula with starfield parallax
// ============================================================

export default function GalaxyBackground() {
  const groupRef = useRef();
  const starsRef = useRef();

  // Create star positions procedurally
  const starPositions = new Float32Array(5000).map((_, i) =>
    (Math.random() - 0.5) * 200
  );

  // Nebula color gradients
  const gradient1 = new THREE.Color("#1DA9FF");
  const gradient2 = new THREE.Color("#7F1DFF");
  const gradient3 = new THREE.Color("#48FFDC");
  const gradient4 = new THREE.Color("#F72585");

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // Parallax drift
    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.01;
    }

    // Star twinkle
    if (starsRef.current) {
      starsRef.current.material.opacity = 0.6 + Math.sin(t * 0.5) * 0.2;
    }
  });

  return (
    <group ref={groupRef} position={[0, 0, -40]}>
      {/* Soft Nebula Fog */}
      <mesh>
        <sphereGeometry args={[80, 32, 32]} />
        <meshBasicMaterial
          side={THREE.BackSide}
          transparent
          opacity={0.55}
          color={gradient1}
        />
      </mesh>

      {/* Layer 2 Nebula */}
      <mesh>
        <sphereGeometry args={[120, 32, 32]} />
        <meshBasicMaterial
          side={THREE.BackSide}
          transparent
          opacity={0.35}
          color={gradient2}
        />
      </mesh>

      {/* Layer 3 — Aurora tint */}
      <mesh>
        <sphereGeometry args={[160, 32, 32]} />
        <meshBasicMaterial
          side={THREE.BackSide}
          transparent
          opacity={0.25}
          color={gradient3}
        />
      </mesh>

      {/* Main starfield */}
      <points ref={starsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={starPositions.length / 3}
            array={starPositions}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.15}
          sizeAttenuation
          color="white"
          transparent
          opacity={0.7}
        />
      </points>
    </group>
  );
}
