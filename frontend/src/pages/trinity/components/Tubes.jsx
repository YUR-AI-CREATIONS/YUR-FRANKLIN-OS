import { useMemo } from "react";
import { TubeGeometry, Vector3, CatmullRomCurve3 } from "three";
import { extend, useFrame } from "@react-three/fiber";
import * as THREE from "three";

extend({ TubeGeometry });

// ====================================================================
// TRINITY OS — CRYSTALLINE ENERGY TUBES
// Curved spline pathways connecting the Reactor → Incubators → Chamber
// ====================================================================

export default function Tubes() {
  // ------------------------------------------------------------
  // 1. Define spline curves between reactor and incubators
  // ------------------------------------------------------------
  const paths = useMemo(() => {
    const p = [];

    // Reactor → OpenAI (left top)
    p.push(
      new CatmullRomCurve3([
        new Vector3(0, 0, 0),
        new Vector3(-3, 2, 2),
        new Vector3(-6, 3.5, 1),
        new Vector3(-8, 4, 0),
      ])
    );

    // Reactor → Gemini (right bottom)
    p.push(
      new CatmullRomCurve3([
        new Vector3(0, 0, 0),
        new Vector3(3, -1, 1),
        new Vector3(6, -2.5, 1),
        new Vector3(8, -2, 0),
      ])
    );

    // Reactor → Anthropic (rear center)
    p.push(
      new CatmullRomCurve3([
        new Vector3(0, 0, 0),
        new Vector3(0, 1, -1.5),
        new Vector3(0, 1.5, -3),
        new Vector3(0, 2, -6),
      ])
    );

    // Incubators → Completed Chamber (down center)
    p.push(
      new CatmullRomCurve3([
        new Vector3(0, 0, 0),
        new Vector3(0, -1.5, 0),
        new Vector3(0, -3, 0),
        new Vector3(0, -4, 0),
      ])
    );

    return p;
  }, []);

  // Tube material
  const material = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#48FFDC",
        emissive: "#1DA9FF",
        emissiveIntensity: 0.4,
        transparent: true,
        opacity: 0.25,
        roughness: 0.1,
        metalness: 0.9,
      }),
    []
  );

  // ------------------------------------------------------------
  // Energy Pulse Animation
  // ------------------------------------------------------------
  useFrame(({ clock, scene }) => {
    const t = clock.getElapsedTime();

    scene.traverse((child) => {
      if (child.userData?.isTube) {
        const pulse = (Math.sin(t * 4 + child.userData.phase) + 1) / 2;
        child.material.emissiveIntensity = 0.3 + pulse * 1.2;
        child.material.opacity = 0.15 + pulse * 0.15;
      }
    });
  });

  return (
    <group>
      {paths.map((curve, i) => {
        const geometry = new TubeGeometry(curve, 200, 0.2, 16, false);

        return (
          <mesh
            key={i}
            geometry={geometry}
            material={material}
            position={[0, 0, 0]}
            userData={{ isTube: true, phase: i * 1.3 }}
          />
        );
      })}
    </group>
  );
}
