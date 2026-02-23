import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'franklin_project';

const createDefaultProject = () => ({
  project_id: `proj-${Date.now()}`,
  name: 'Franklin Project',
  stage: 'idle',
  contract: null,
  agent_id: null,
  agent_name: null,
  agent_badge: null
});

const ProjectContext = createContext({
  project: null,
  updateProject: () => {},
  ensureProject: () => {}
});

export const ProjectProvider = ({ children }) => {
  const [project, setProject] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) return JSON.parse(stored);
    } catch (_e) {
      // ignore parse errors
    }
    return createDefaultProject();
  });

  const updateProject = useCallback((patch) => {
    setProject((prev) => ({ ...(prev || createDefaultProject()), ...(patch || {}) }));
  }, []);

  const ensureProject = useCallback(() => {
    setProject((prev) => prev || createDefaultProject());
  }, []);

  useEffect(() => {
    if (!project) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(project));
    } catch (_e) {
      // ignore storage write errors
    }
  }, [project]);

  return (
    <ProjectContext.Provider value={{ project, updateProject, ensureProject }}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = () => useContext(ProjectContext);
