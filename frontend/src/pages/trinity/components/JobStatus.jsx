import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_TIC_API ?? "http://localhost:8080";

export default function JobStatus({ jobId }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!jobId) return undefined;
    const interval = setInterval(() => {
      axios
        .get(`${API_BASE}/jobs/${jobId}`, {
          params: { include_download_url: true },
        })
        .then((res) => setStatus(res.data))
        .catch((err) => setStatus({ error: err.message, job_id: jobId }));
    }, 1500);
    return () => clearInterval(interval);
  }, [jobId]);

  if (!status) {
    return <div className="p-4 bg-white shadow rounded">Checking status...</div>;
  }

  return (
    <div className="p-5 bg-white shadow rounded">
      <h2 className="font-bold text-xl mb-3">Job Status</h2>
      <p>
        <strong>ID:</strong> {status.job_id}
      </p>
      <p>
        <strong>Status:</strong> {status.status}
      </p>

      {status.download_url && (
        <a
          className="text-blue-600 underline mt-2 inline-block"
          href={status.download_url}
          target="_blank"
          rel="noreferrer"
        >
          Download Output
        </a>
      )}

      {status.error && (
        <p className="text-red-600 mt-2">
          <strong>Error:</strong> {status.error}
        </p>
      )}
    </div>
  );
}
