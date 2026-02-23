import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

export default function MicroSphere({ data, position = [0, 0, 0] }) {
  const meshRef = useRef();

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.6;
      meshRef.current.rotation.y += delta * 0.4;
      if (typeof data?.progress === "number") {
        const scale = 0.6 + data.progress * 0.4;
        meshRef.current.scale.set(scale, scale, scale);
      }
    }
  });

  const color = data?.status === "done" ? "#00ff87" : data?.status === "error" ? "#ff006e" : "#00cfff";

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.18, 32, 32]} />
      <meshStandardMaterial color={color} metalness={0.9} roughness={0.2} emissive={color} emissiveIntensity={0.3} />
    </mesh>
  );
}
