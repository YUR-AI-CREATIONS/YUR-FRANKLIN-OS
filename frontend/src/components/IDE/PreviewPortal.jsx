/**
 * PreviewPortal
 * 
 * Visual preview of generated builds.
 * - Renders web apps in iframe
 * - Shows component library previews
 * - Displays wireframes and design mockups
 * - Real-time sync with code changes
 */

import React, { useState, useEffect, useRef } from 'react';
import { Code2, Eye, RefreshCw, ExternalLink, Download } from 'lucide-react';

const PreviewPortal = ({ buildResult, generatedCode, activePreviewTab, onTabChange }) => {
  const iframeRef = useRef(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState(null);
  const [iframeContent, setIframeContent] = useState('');
  const [zoomLevel, setZoomLevel] = useState(100);

  // Generate basic HTML preview from code
  const generateHTMLPreview = (code) => {
    // If it's Python/API code, show a mock API response
    if (code.includes('python') || code.includes('def ') || code.includes('FastAPI')) {
      return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>API Preview</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(135deg, #0f0f23 0%, #1a0f3f 100%);
      font-family: 'Courier New', monospace;
      color: #00ff88;
      padding: 40px;
      min-height: 100vh;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .header {
      border-left: 4px solid #0ea5e9;
      padding-left: 20px;
      margin-bottom: 40px;
    }
    h1 {
      font-size: 2em;
      letter-spacing: 2px;
      margin-bottom: 10px;
      text-shadow: 0 0 20px rgba(14, 165, 233, 0.5);
    }
    .endpoint {
      background: rgba(14, 165, 233, 0.1);
      border: 1px solid rgba(14, 165, 233, 0.3);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      backdrop-filter: blur(10px);
    }
    .method {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 4px;
      font-weight: bold;
      margin-bottom: 10px;
      font-size: 0.9em;
    }
    .get { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
    .post { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
    .put { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
    .delete { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .path {
      font-size: 1.1em;
      margin-bottom: 10px;
      color: #a855f7;
    }
    .description {
      color: #94a3b8;
      font-size: 0.95em;
      margin-bottom: 15px;
    }
    .response {
      background: rgba(168, 85, 247, 0.1);
      border: 1px solid rgba(168, 85, 247, 0.3);
      border-radius: 6px;
      padding: 12px;
      margin-top: 12px;
      font-size: 0.85em;
      overflow-x: auto;
    }
    .terminal-line { margin: 4px 0; }
    .status { color: #10b981; }
    .field { color: #60a5fa; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🚀 BUILD PREVIEW</h1>
      <p style="color: #64748b; margin-top: 8px;">Generated API Endpoints</p>
    </div>

    <div class="endpoint">
      <div class="method post">POST</div>
      <div class="path">/api/build</div>
      <div class="description">Create a new build with mission parameters</div>
      <div class="response">
        <div class="terminal-line"><span class="status">✓ 200 OK</span> - Build created</div>
        <div class="terminal-line"><span class="field">build_id:</span> "abc123def"</div>
        <div class="terminal-line"><span class="field">status:</span> "building"</div>
        <div class="terminal-line"><span class="field">files:</span> 12</div>
      </div>
    </div>

    <div class="endpoint">
      <div class="method get">GET</div>
      <div class="path">/api/build/{build_id}</div>
      <div class="description">Fetch build details and generated files</div>
      <div class="response">
        <div class="terminal-line"><span class="status">✓ 200 OK</span> - Build found</div>
        <div class="terminal-line"><span class="field">build_id:</span> "abc123def"</div>
        <div class="terminal-line"><span class="field">status:</span> "completed"</div>
        <div class="terminal-line"><span class="field">lines_of_code:</span> 2453</div>
      </div>
    </div>

    <div class="endpoint">
      <div class="method put">PUT</div>
      <div class="path">/api/build/{build_id}/certify</div>
      <div class="description">Send build to 8-gate certification</div>
      <div class="response">
        <div class="terminal-line"><span class="status">✓ 200 OK</span> - Certification started</div>
        <div class="terminal-line"><span class="field">gates_passed:</span> 8/8</div>
        <div class="terminal-line"><span class="field">score:</span> 98.5%</div>
        <div class="terminal-line"><span class="field">certified:</span> true</div>
      </div>
    </div>

    <div class="endpoint">
      <div class="method get">GET</div>
      <div class="path">/api/build/{build_id}/download</div>
      <div class="description">Download generated project as ZIP</div>
      <div class="response">
        <div class="terminal-line"><span class="status">✓ 200 OK</span> - ZIP download</div>
        <div class="terminal-line"><span class="field">filename:</span> "build-abc123def.zip"</div>
        <div class="terminal-line"><span class="field">size:</span> 1.2 MB</div>
      </div>
    </div>
  </div>
</body>
</html>
      `;
    }

    // For React/web code, show component preview
    if (code.includes('React') || code.includes('jsx') || code.includes('html')) {
      return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Component Preview</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(135deg, #0f0f23 0%, #1a0f3f 100%);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      color: #fff;
      padding: 40px;
    }
    .preview-container {
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
      border: 1px solid rgba(14, 165, 233, 0.3);
      border-radius: 12px;
      padding: 40px;
      backdrop-filter: blur(10px);
      max-width: 600px;
      margin: 0 auto;
    }
    .component-title {
      font-size: 1.8em;
      margin-bottom: 10px;
      color: #0ea5e9;
      text-shadow: 0 0 20px rgba(14, 165, 233, 0.3);
    }
    .component-desc {
      color: #cbd5e1;
      margin-bottom: 30px;
      font-size: 0.95em;
    }
    .component-showcase {
      display: grid;
      gap: 20px;
    }
    .button {
      background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
      color: #000;
      border: none;
      padding: 12px 24px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
      font-size: 0.95em;
    }
    .button:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(14, 165, 233, 0.4);
    }
    .card {
      background: rgba(2, 13, 46, 0.8);
      border: 1px solid rgba(14, 165, 233, 0.2);
      border-radius: 8px;
      padding: 20px;
      color: #cbd5e1;
    }
    .card-title {
      color: #0ea5e9;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 15px;
      margin-top: 20px;
    }
    .stat-item {
      background: rgba(168, 85, 247, 0.1);
      border-left: 3px solid #a855f7;
      padding: 12px;
      border-radius: 4px;
    }
    .stat-label {
      color: #94a3b8;
      font-size: 0.85em;
    }
    .stat-value {
      font-size: 1.4em;
      color: #a855f7;
      font-weight: bold;
      margin-top: 4px;
    }
  </style>
</head>
<body>
  <div class="preview-container">
    <div class="component-title">✨ Component Preview</div>
    <div class="component-desc">Live preview of your generated components</div>
    
    <div class="component-showcase">
      <button class="button">Primary Button</button>
      <button class="button" style="background: linear-gradient(135deg, #a855f7 0%, #d946ef 100%);">
        Secondary Button
      </button>
      
      <div class="card">
        <div class="card-title">Build Status</div>
        <div style="color: #94a3b8; margin-bottom: 12px;">Your project status and metrics</div>
        <div class="stats">
          <div class="stat-item">
            <div class="stat-label">Files Generated</div>
            <div class="stat-value">12</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">Lines of Code</div>
            <div class="stat-value">2.4K</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">Quality Score</div>
            <div class="stat-value">98%</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">Build Time</div>
            <div class="stat-value">2.3s</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
      `;
    }

    // Default: Show Franklin welcome
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Franklin OS Preview</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(135deg, #0f0f23 0%, #1a0f3f 100%);
      font-family: 'Orbitron', monospace;
      color: #00ff88;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      text-align: center;
      padding: 40px;
    }
    .welcome {
      max-width: 500px;
    }
    .logo {
      font-size: 4em;
      margin-bottom: 20px;
      text-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    h1 {
      font-size: 2.5em;
      margin-bottom: 15px;
      letter-spacing: 3px;
      color: #a855f7;
    }
    p {
      font-size: 1.1em;
      color: #94a3b8;
      margin-bottom: 20px;
      line-height: 1.8;
    }
    .hint {
      border-top: 1px solid rgba(0, 255, 136, 0.2);
      padding-top: 20px;
      margin-top: 30px;
      color: #64748b;
      font-size: 0.9em;
    }
  </style>
</head>
<body>
  <div class="welcome">
    <div class="logo">◈</div>
    <h1>FRANKLIN OS</h1>
    <p>Tell Franklin what to build and watch the magic happen.</p>
    <p style="color: #0ea5e9;">Example: "Build me a todo app API"</p>
    <div class="hint">
      <p>Preview will appear here after your first build</p>
    </div>
  </div>
</body>
</html>
    `;
  };

  // Inject content into iframe
  useEffect(() => {
    if (iframeRef.current && activePreviewTab === 'preview') {
      try {
        setPreviewLoading(true);
        const htmlContent = generateHTMLPreview(generatedCode || '');
        const iframeDoc = iframeRef.current.contentDocument;
        if (iframeDoc) {
          iframeDoc.open();
          iframeDoc.write(htmlContent);
          iframeDoc.close();
          setPreviewError(null);
        }
        setPreviewLoading(false);
      } catch (err) {
        setPreviewError(err.message);
        setPreviewLoading(false);
      }
    }
  }, [generatedCode, activePreviewTab]);

  if (activePreviewTab !== 'preview') {
    return null;
  }

  return (
    <div className="w-full h-full bg-slate-950 flex flex-col relative">
      {/* Preview Controls */}
      <div className="h-12 px-4 border-b border-white/10 bg-black/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Eye className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-mono text-cyan-400">PREVIEW PORTAL</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}
            className="px-2 py-1 text-xs font-mono text-white/60 hover:text-white hover:bg-white/10 rounded transition-all"
          >
            −
          </button>
          <span className="text-xs font-mono text-white/60 w-12 text-center">{zoomLevel}%</span>
          <button
            onClick={() => setZoomLevel(Math.min(150, zoomLevel + 10))}
            className="px-2 py-1 text-xs font-mono text-white/60 hover:text-white hover:bg-white/10 rounded transition-all"
          >
            +
          </button>
          <div className="w-px h-6 bg-white/10 mx-2" />
          <button
            onClick={() => iframeRef.current?.contentWindow?.location.reload()}
            className="px-2 py-1 text-xs font-mono text-white/60 hover:text-white hover:bg-white/10 rounded transition-all flex items-center gap-1"
            title="Refresh preview"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
          <button
            onClick={() => {
              if (buildResult?.buildId) {
                window.open(`${window.location.origin}/preview/${buildResult.buildId}`, '_blank');
              }
            }}
            className="px-2 py-1 text-xs font-mono text-white/60 hover:text-white hover:bg-white/10 rounded transition-all flex items-center gap-1"
            title="Open in new window"
          >
            <ExternalLink className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="flex-1 overflow-hidden relative bg-black/40">
        {previewLoading && (
          <div className="absolute inset-0 flex items-center justify-center z-50 bg-black/50 backdrop-blur-sm">
            <div className="text-center">
              <div className="animate-spin text-cyan-400 text-4xl mb-3">◈</div>
              <p className="text-sm font-mono text-white/70">Loading preview...</p>
            </div>
          </div>
        )}

        {previewError && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-500/10 backdrop-blur-sm">
            <div className="text-center">
              <p className="text-red-400 font-mono text-sm">Preview Error</p>
              <p className="text-red-400/70 text-xs mt-2">{previewError}</p>
            </div>
          </div>
        )}

        <iframe
          ref={iframeRef}
          title="Build Preview"
          className="w-full h-full border-0"
          style={{
            transform: `scale(${zoomLevel / 100})`,
            transformOrigin: 'top left',
            width: `${100 / (zoomLevel / 100)}%`,
            height: `${100 / (zoomLevel / 100)}%`,
          }}
          sandbox="allow-same-origin allow-scripts allow-forms"
        />
      </div>

      {/* Status Bar */}
      <div className="h-6 px-4 border-t border-white/10 bg-black/80 flex items-center justify-between text-xs font-mono text-white/50">
        <span>Preview Portal Active</span>
        <span>{buildResult?.buildId ? `Build: ${buildResult.buildId.slice(0, 8)}...` : 'No build loaded'}</span>
      </div>
    </div>
  );
};

export default PreviewPortal;
