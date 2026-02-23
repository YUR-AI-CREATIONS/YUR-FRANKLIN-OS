import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_TIC_API ?? "http://localhost:8080";

export default function SystemHealth() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(`${API_BASE}/system/health`)
      .then((res) => setStatus(res.data))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <p className="text-red-700 font-semibold">System health unavailable: {error}</p>
      </div>
    );
  }

  if (!status) {
    return <div className="p-4 bg-white shadow rounded">Loading system status...</div>;
  }

  return (
    <div className="p-5 bg-white shadow rounded">
      <h2 className="font-bold text-xl mb-3">System Health</h2>
      <p>
        Status: <span className="font-semibold capitalize">{status.status}</span>
      </p>
      <p>
        Service: <span className="font-semibold">{status.service}</span>
      </p>
      {status.dependencies && (
        <div className="mt-3">
          <h3 className="font-semibold mb-1">Dependencies</h3>
          <ul className="space-y-1 text-sm">
            {Object.entries(status.dependencies).map(([name, info]) => (
              <li key={name}>
                <span className="font-semibold capitalize">{name}:</span> {info.status}
                {info.detail && <span className="text-gray-500"> — {info.detail}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
