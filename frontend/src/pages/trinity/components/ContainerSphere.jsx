import ContainerConstellation from "../three/ContainerConstellation.jsx";
import { useJobStore } from "../state/useJobStore";
import { useSphereStore } from "../state/useSphereStore";

export default function ContainerSphere() {
  const spheres = useJobStore((state) => state.spheres);
  const showConstellation = useSphereStore((state) => state.showConstellation);

  if (!showConstellation) {
    return (
      <div className="constellation-placeholder">
        <p>The sphere awaits injection.</p>
      </div>
    );
  }

  return (
    <div className="constellation-panel">
      <ContainerConstellation spheres={spheres} />
    </div>
  );
}
