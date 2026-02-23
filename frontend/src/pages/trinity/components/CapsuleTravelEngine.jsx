import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { CatmullRomCurve3, Vector3 } from "three";

// =====================================================================
// TRINITY OS — CAPSULE TRAVEL ENGINE
// Moves the Quantum Icosahedron along the crystalline tubes
// =====================================================================

export default function CapsuleTravelEngine({ progress, children }) {
  const capsuleRef = useRef();

  // ----------------------------
  // 1. Define tube path curves
  // ----------------------------
  const paths = useMemo(() => {
    return {
      openai: new CatmullRomCurve3([
        new Vector3(0, 0, 5),
        new Vector3(-3, 2, 2),
        new Vector3(-6, 3.5, 1),
        new Vector3(-8, 4, 0),
      ]),
      gemini: new CatmullRomCurve3([
        new Vector3(0, 0, 5),
        new Vector3(3, -1, 2),
        new Vector3(6, -2.5, 1),
        new Vector3(8, -2, 0),
      ]),
      anthropic: new CatmullRomCurve3([
        new Vector3(0, 0, 5),
        new Vector3(0, 1, 1),
        new Vector3(0, 1.5, -3),
        new Vector3(0, 2, -6),
      ]),
      complete: new CatmullRomCurve3([
        new Vector3(0, 0, 5),
        new Vector3(0, -1.5, 2),
        new Vector3(0, -3, 0),
        new Vector3(0, -4, 0),
      ]),
    };
  }, []);

  // ----------------------------------------------------------
  // 2. Animate capsule along chosen path based on progress
  // ----------------------------------------------------------
  useFrame(() => {
    if (!capsuleRef.current) return;

    const p = Math.min(Math.max(progress / 100, 0), 1);

    // CHOOSE ROUTE BASED ON PROGRESS
    let route = paths.openai;
    if (progress > 25 && progress <= 50) route = paths.gemini;
    if (progress > 50 && progress <= 75) route = paths.anthropic;
    if (progress > 75) route = paths.complete;

    const pos = route.getPointAt(p);
    const tangent = route.getTangentAt(p);

    capsuleRef.current.position.copy(pos);

    // Orient rotation along tube tangent
    const axis = new THREE.Vector3(0, 1, 0);
    const quaternion = new THREE.Quaternion();
    quaternion.setFromUnitVectors(axis, tangent.normalize());
    capsuleRef.current.quaternion.copy(quaternion);

    // Glow intensifies during movement
    capsuleRef.current.children.forEach((child) => {
      if (child.material) {
        child.material.emissiveIntensity = 0.8 + p * 2.2;
      }
    });
  });

  return <group ref={capsuleRef}>{children}</group>;
}
