import { useMemo } from "react";
import AscensionSphere from "../three/AscensionSphere.jsx";

export default function LandingHero() {
  const dataLabels = useMemo(
    () => ["OCR", "Rendering", "QTO", "Cost Indexing", "AI Analysis", "Merge Engine", "Sentinel Oversight"],
    []
  );

  return (
    <section className="landing-hero">
      <div className="landing-hero__canvas">
        <AscensionSphere />
        <div className="landing-hero__labels">
          {dataLabels.map((label) => (
            <span key={label}>{label}</span>
          ))}
        </div>
      </div>
      <div className="landing-hero__text">
        <p className="landing-hero__eyebrow">TRINITY INTELLIGENCE CLOUD</p>
        <h1>Upload Reality.<br />We&apos;ll build the truth.</h1>
        <p className="landing-hero__subtitle">
          A living AI organism that ingests construction documents, atomizes each page into microservices,
          and reassembles a perfect intelligence package in real time.
        </p>
        <div className="landing-hero__cta">
          <a href="#upload" className="cta-button">
            Initiate Injection Event
          </a>
          <p>Hover over the sphere to reveal the Trinity stack.</p>
        </div>
      </div>
    </section>
  );
}
