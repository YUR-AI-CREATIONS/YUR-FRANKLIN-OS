import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_TIC_API ?? "http://localhost:8080";

export default function MicrocontainerList() {
  const [list, setList] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(`${API_BASE}/system/microcontainers`)
      .then((res) => setList(res.data))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <p className="text-red-700 font-semibold">Microcontainers unavailable: {error}</p>
      </div>
    );
  }

  if (!list) {
    return <div className="p-4 bg-white shadow rounded">Loading microcontainers...</div>;
  }

  return (
    <div className="p-5 bg-white shadow rounded">
      <h2 className="font-bold text-xl mb-3">Available Microcontainers</h2>
      <ul className="list-disc pl-5 space-y-1">
        {list.microcontainers.map((mc) => (
          <li key={mc}>{mc}</li>
        ))}
      </ul>
    </div>
  );
}
