import { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_TIC_API ?? "http://localhost:8080";

export default function JobSubmit({ onSubmitted }) {
  const [jobType, setJobType] = useState("website_autogen");
  const [prompt, setPrompt] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const form = new FormData();
      form.append("job_type", jobType);
      form.append(
        "payload",
        JSON.stringify({
          prompt: prompt || "Example prompt",
        })
      );
      if (file) {
        form.append("file", file);
      }

      const response = await axios.post(`${API_BASE}/jobs/submit`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(`Job ${response.data.job_id} queued`);
      onSubmitted?.(response.data.job_id);
      setPrompt("");
      setFile(null);
    } catch (err) {
      setMessage(`Submission failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="p-5 bg-white shadow rounded space-y-4" onSubmit={submit}>
      <h2 className="font-bold text-xl">Submit a Job</h2>

      <label className="block text-sm font-semibold">Job Type</label>
      <select
        value={jobType}
        onChange={(e) => setJobType(e.target.value)}
        className="border p-2 rounded w-full"
      >
        <option value="website_autogen">Website Autogen</option>
        <option value="render_image">Render Image</option>
        <option value="render_video">Render Video</option>
        <option value="pdf_to_sheet">PDF → Spreadsheet</option>
      </select>

      <label className="block text-sm font-semibold">Prompt / Payload</label>
      <input
        className="border p-2 rounded w-full"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your desired output"
      />

      <label className="block text-sm font-semibold">Optional File Upload</label>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="border p-2 rounded w-full"
      />

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? "Submitting..." : "Submit Job"}
      </button>

      {message && <p className="text-sm text-gray-600">{message}</p>}
    </form>
  );
}
