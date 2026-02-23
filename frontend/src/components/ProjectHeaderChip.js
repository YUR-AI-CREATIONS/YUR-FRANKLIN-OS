import React from 'react';
import { useProject } from '../context/ProjectContext';

const ProjectHeaderChip = () => {
  const { project } = useProject();
  if (!project) return null;
  return (
    <div className="px-3 py-1 rounded border border-white/20 bg-white/5 text-xs font-mono text-white/80">
      <span className="text-cyan-300 mr-2">◎ Project</span>
      <span className="mr-2">{project.name}</span>
      <span className="text-white/40">ID: {project.project_id}</span>
      <span className="ml-2 text-white/60">Stage: {project.stage || 'idle'}</span>
    </div>
  );
};

export default ProjectHeaderChip;
