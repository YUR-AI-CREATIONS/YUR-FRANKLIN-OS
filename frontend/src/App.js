import React, { useState, useCallback, useRef, useMemo } from 'react';
import './App.css';
import LandingPage from './components/LandingPage';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

// Custom Node Components
import InputNode from './components/nodes/InputNode';
import AmbiguityNode from './components/nodes/AmbiguityNode';
import ResolutionNode from './components/nodes/ResolutionNode';
import SpecNode from './components/nodes/SpecNode';
import ProcessingNode from './components/nodes/ProcessingNode';
import StageNode from './components/nodes/StageNode';

// Panel Components
import Header from './components/panels/Header';
import InputPanel from './components/panels/InputPanel';
import ClarificationPanel from './components/panels/ClarificationPanel';
import NodeInspector from './components/panels/NodeInspector';
import SpecificationPanel from './components/panels/SpecificationPanel';
import PipelinePanel from './components/panels/PipelinePanel';
import QualityGatePanel from './components/panels/QualityGatePanel';
import BuildPanel from './components/panels/BuildPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const nodeTypes = {
  input: InputNode,
  ambiguity: AmbiguityNode,
  resolution: ResolutionNode,
  spec: SpecNode,
  processing: ProcessingNode,
  stage: StageNode,
};

const PIPELINE_STAGES = [
  'inception', 'specification', 'architecture', 
  'construction', 'validation', 'evolution', 
  'deployment', 'governance'
];

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [answers, setAnswers] = useState({});
  const [specification, setSpecification] = useState(null);
  const [error, setError] = useState(null);
  
  // Genesis Pipeline state
  const [genesisProject, setGenesisProject] = useState(null);
  const [currentStage, setCurrentStage] = useState('inception');
  const [qualityAssessment, setQualityAssessment] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [showPipeline, setShowPipeline] = useState(false);
  const [showQualityGate, setShowQualityGate] = useState(false);
  const [llmStatus, setLLMStatus] = useState(null);
  
  const nodeIdCounter = useRef(0);

  const generateNodeId = () => {
    nodeIdCounter.current += 1;
    return `node_${nodeIdCounter.current}`;
  };

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({
      ...params,
      animated: true,
      style: { stroke: '#6366F1' },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#6366F1' }
    }, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const clearCanvas = () => {
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
    setSession(null);
    setAnswers({});
    setSpecification(null);
    setError(null);
    setGenesisProject(null);
    setQualityAssessment(null);
    setRoadmap(null);
    nodeIdCounter.current = 0;
  };

  // Initialize Genesis Project
  const initializeGenesisProject = async (name) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API}/genesis/project/init`, {
        name: name,
        description: `Genesis Project: ${name}`
      });
      
      setGenesisProject(response.data);
      setShowPipeline(true);
      
      // Create pipeline visualization nodes
      const stageNodes = PIPELINE_STAGES.map((stage, index) => ({
        id: `stage_${stage}`,
        type: 'stage',
        position: { x: 100 + (index * 180), y: 100 },
        data: {
          label: stage.charAt(0).toUpperCase() + stage.slice(1),
          stage: stage,
          status: index === 0 ? 'active' : 'pending',
          score: 0
        }
      }));
      
      const stageEdges = PIPELINE_STAGES.slice(0, -1).map((stage, index) => ({
        id: `edge_${stage}_${PIPELINE_STAGES[index + 1]}`,
        source: `stage_${stage}`,
        target: `stage_${PIPELINE_STAGES[index + 1]}`,
        animated: index === 0,
        style: { stroke: index === 0 ? '#6366F1' : '#3F3F46' },
        markerEnd: { type: MarkerType.ArrowClosed, color: index === 0 ? '#6366F1' : '#3F3F46' }
      }));
      
      setNodes(stageNodes);
      setEdges(stageEdges);
      
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initialize project');
    } finally {
      setIsLoading(false);
    }
  };

  // Run Quality Assessment
  const runQualityAssessment = async (artifact, stage) => {
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API}/genesis/quality/assess`, {
        artifact: artifact,
        stage: stage
      });
      
      setQualityAssessment(response.data);
      setShowQualityGate(true);
      
      // Update stage node with score
      setNodes((nds) => nds.map((n) => 
        n.id === `stage_${stage}` 
          ? { ...n, data: { ...n.data, score: response.data.aggregate_score, status: response.data.passed ? 'passed' : 'active' } }
          : n
      ));
      
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Quality assessment failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Execute Ouroboros Loop
  const executeOuroboros = async (artifact, stage) => {
    if (!genesisProject) {
      setError('Initialize a Genesis project first');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API}/genesis/ouroboros/execute`, {
        project_id: genesisProject.orchestrator_id,
        artifact: artifact,
        stage: stage
      });
      
      const result = response.data;
      
      // Update stage node
      setNodes((nds) => nds.map((n) => {
        if (n.id === `stage_${stage}`) {
          return {
            ...n,
            data: {
              ...n.data,
              score: result.final_score,
              status: result.status === 'CONVERGED' ? 'passed' : 
                      result.status === 'DRIFT_ALERT' ? 'drift' : 'active',
              iterations: result.iterations
            }
          };
        }
        return n;
      }));
      
      // If converged, activate next stage
      if (result.status === 'CONVERGED') {
        const currentIndex = PIPELINE_STAGES.indexOf(stage);
        if (currentIndex < PIPELINE_STAGES.length - 1) {
          const nextStage = PIPELINE_STAGES[currentIndex + 1];
          setCurrentStage(nextStage);
          
          setNodes((nds) => nds.map((n) => 
            n.id === `stage_${nextStage}` 
              ? { ...n, data: { ...n.data, status: 'active' } }
              : n
          ));
          
          setEdges((eds) => eds.map((e) => 
            e.target === `stage_${nextStage}`
              ? { ...e, animated: true, style: { stroke: '#6366F1' } }
              : e
          ));
        }
      }
      
      setQualityAssessment(result.assessment);
      setShowQualityGate(true);
      
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || 'Ouroboros execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Analyze prompt (Socratic Engine)
  const analyzePrompt = async (prompt) => {
    setIsLoading(true);
    setError(null);

    try {
      // Initialize project if not exists
      if (!genesisProject) {
        await initializeGenesisProject(prompt.substring(0, 30));
      }
      
      const response = await axios.post(`${API}/analyze`, { prompt });
      const { session_id, analysis, confidence_score, can_proceed } = response.data;

      setSession({
        session_id,
        original_prompt: prompt,
        analysis,
        confidence_score,
        can_proceed
      });

      // Add input node to canvas
      const inputNodeId = generateNodeId();
      const newNode = {
        id: inputNodeId,
        type: 'input',
        position: { x: 100, y: 300 },
        data: { label: 'User Input', content: prompt },
      };
      
      setNodes((nds) => [...nds, newNode]);

      // Add ambiguity nodes
      const ambiguities = analysis.ambiguities || [];
      const ambNodes = ambiguities.map((amb, index) => ({
        id: generateNodeId(),
        type: 'ambiguity',
        position: { x: 350, y: 200 + (index * 100) },
        data: { ...amb, label: amb.id },
      }));
      
      const ambEdges = ambNodes.map((n) => ({
        id: `e_${inputNodeId}_${n.id}`,
        source: inputNodeId,
        target: n.id,
        animated: true,
        style: { stroke: '#F59E0B' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#F59E0B' }
      }));
      
      setNodes((nds) => [...nds, ...ambNodes]);
      setEdges((eds) => [...eds, ...ambEdges]);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze prompt');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (ambiguityId, answer, selectedOption) => {
    setAnswers((prev) => ({
      ...prev,
      [ambiguityId]: { answer, selected_option: selectedOption }
    }));
  };

  const submitAnswers = async () => {
    if (!session) return;
    setIsLoading(true);
    setError(null);

    try {
      const formattedAnswers = Object.entries(answers).map(([id, data]) => ({
        ambiguity_id: id,
        answer: data.answer || data.selected_option || '',
        selected_option: data.selected_option || null
      }));

      const response = await axios.post(`${API}/resolve`, {
        session_id: session.session_id,
        answers: formattedAnswers
      });

      const { analysis, confidence_score, can_proceed } = response.data;

      setSession((prev) => ({
        ...prev,
        analysis,
        confidence_score,
        can_proceed
      }));

      setAnswers({});

      // If ready, run quality assessment
      if (can_proceed && genesisProject) {
        await runQualityAssessment(
          { ...analysis, prompt: session.original_prompt },
          currentStage
        );
      }

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resolve ambiguities');
    } finally {
      setIsLoading(false);
    }
  };

  const currentAmbiguities = session?.analysis?.ambiguities || [];
  const hasUnresolvedAmbiguities = currentAmbiguities.length > 0;

  // Show landing page first
  if (showLanding) {
    return <LandingPage onEnterApp={() => setShowLanding(false)} />;
  }

  return (
    <div className="sgp-app" data-testid="sgp-app">
      {/* React Flow Canvas */}
      <div className="canvas-container grid-pattern">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Background color="#27272A" gap={24} size={1} />
          <Controls />
          <MiniMap 
            nodeColor={(n) => {
              if (n.type === 'ambiguity') return '#F59E0B';
              if (n.type === 'resolution') return '#10B981';
              if (n.type === 'spec') return '#6366F1';
              if (n.type === 'stage') {
                if (n.data?.status === 'passed') return '#10B981';
                if (n.data?.status === 'active') return '#6366F1';
                if (n.data?.status === 'drift') return '#EF4444';
                return '#3F3F46';
              }
              return '#3F3F46';
            }}
            maskColor="rgba(5, 5, 5, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* Header */}
      <Header 
        session={session}
        genesisProject={genesisProject}
        currentStage={currentStage}
        onClear={clearCanvas}
        onTogglePipeline={() => setShowPipeline(!showPipeline)}
        onLLMStatusChange={setLLMStatus}
      />

      {/* Input Panel */}
      <InputPanel
        onSubmit={analyzePrompt}
        isLoading={isLoading}
        disabled={isLoading}
      />

      {/* Clarification Panel */}
      {session && hasUnresolvedAmbiguities && (
        <ClarificationPanel
          ambiguities={currentAmbiguities}
          answers={answers}
          onAnswerChange={handleAnswerChange}
          onSubmit={submitAnswers}
          isLoading={isLoading}
          confidenceScore={session.confidence_score}
        />
      )}

      {/* Quality Gate Panel */}
      {showQualityGate && qualityAssessment && (
        <QualityGatePanel
          assessment={qualityAssessment}
          stage={currentStage}
          onClose={() => setShowQualityGate(false)}
          onRunOuroboros={() => executeOuroboros(
            { ...session?.analysis, prompt: session?.original_prompt },
            currentStage
          )}
          isLoading={isLoading}
        />
      )}

      {/* Pipeline Panel */}
      {showPipeline && genesisProject && (
        <PipelinePanel
          project={genesisProject}
          currentStage={currentStage}
          stages={PIPELINE_STAGES}
          onClose={() => setShowPipeline(false)}
        />
      )}

      {/* Node Inspector */}
      {selectedNode && (
        <NodeInspector
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}

      {/* Error Toast */}
      {error && (
        <div 
          className="fixed bottom-24 left-1/2 -translate-x-1/2 glass-panel px-4 py-3 rounded-lg border-l-4 border-red-500 animate-slide-in z-50"
          data-testid="error-toast"
        >
          <div className="flex items-center gap-3">
            <span className="text-red-400 font-mono text-sm">ERROR:</span>
            <span className="text-sm text-zinc-300">{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-2 text-zinc-500 hover:text-zinc-300"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Build Panel - Floating button and modal */}
      <BuildPanel 
        session={session}
        specification={session?.analysis}
        onBuildComplete={(result) => {
          console.log('Build complete:', result);
        }}
      />
    </div>
  );
}

export default App;
