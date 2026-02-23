import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useJobStore } from "../state/useJobStore.js";
import { getApiBaseUrl } from "../config/env.js";

const UPLOAD_LIMIT_MB = Number(import.meta.env.VITE_UPLOAD_MAX_MB) || 512;
const REQUIRE_AUTH = String(import.meta.env.VITE_REQUIRE_AUTH || "false").toLowerCase() === "true";

export default function UploadPortal() {
  const navigate = useNavigate();
  const setJobId = useJobStore((state) => state.setJobId);
  const updateStatus = useJobStore((state) => state.updateStatus);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > UPLOAD_LIMIT_MB * 1024 * 1024) {
      setError(`File exceeds ${UPLOAD_LIMIT_MB}MB limit.`);
      return;
    }

    const api = getApiBaseUrl();
    if (!api) {
      setError("API base URL not available. Configure VITE_API_URL or run behind the gateway.");
      return;
    }

    const headers = {};
    if (REQUIRE_AUTH) {
      const token = window.localStorage?.getItem("trinity_token");
      if (!token) {
        setError("Authentication required before uploading.");
        return;
      }
      headers.Authorization = `Bearer ${token}`;
    }

    const form = new FormData();
    form.append("file", file);

    try {
      setUploading(true);
      updateStatus("uploading");
      const response = await fetch(`${api}/jobs/large-upload`, {
        method: "POST",
        body: form,
        headers,
      });

      const bodyText = await response.text();
      if (!response.ok) {
        throw new Error(`Upload failed (${response.status}): ${bodyText}`);
      }

      const payload = bodyText ? JSON.parse(bodyText) : {};
      const jobId = payload.job_id || payload.id;
      if (!jobId) {
        throw new Error("API did not return job_id");
      }
      setJobId(jobId);
      updateStatus("processing");
      navigate(`/job/${jobId}`);
    } catch (err) {
      console.error(err);
      setError(err.message || "Upload failed. Check API response logs.");
      updateStatus("error");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="holo-panel panel-pulse w-[420px] text-white">
      <p className="text-xl mb-4">Drop your project to begin ascension</p>
      <label className="block cursor-pointer">
        <span className="block mb-2 text-sm uppercase tracking-widest opacity-70">Upload</span>
        <input
          type="file"
          onChange={handleUpload}
          className="w-full p-3 bg-black/40 border border-white/20 rounded focus:outline-none"
          disabled={uploading}
        />
      </label>
      {uploading && <p className="mt-4 text-cyan-300">Injecting into the Ascension Sphere…</p>}
      {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}
    </div>
  );
}
