import { Children, cloneElement, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { smoothOrbitPosition } from "../three/polish/orbitSmoothing.js";

export default function OrbitRing({ radius = 3, speed = 0.2, color = "#00eaff", children }) {
  const group = useRef();
  const nodes = useMemo(() => Children.toArray(children), [children]);

  useFrame((_, delta) => {
    if (group.current) {
      group.current.rotation.y += speed * delta;
    }
  });

  return (
    <group ref={group}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[radius, 0.01, 16, 256]} />
        <meshBasicMaterial color={color} opacity={0.35} transparent />
      </mesh>
      {nodes.map((child, index) => {
        const angle = (index / nodes.length) * Math.PI * 2;
        const position = smoothOrbitPosition(angle, radius);
        return cloneElement(child, { position, key: child.key || index });
      })}
    </group>
  );
}
