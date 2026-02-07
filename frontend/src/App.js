import React, { useState, useCallback, useRef, useMemo, useEffect } from 'react';
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
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import dagre from 'dagre';

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

// Helper to safely extract error message from API responses
const getErrorMessage = (err, fallback = 'An error occurred') => {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(d => d.msg || String(d)).join(', ');
  if (detail?.msg) return detail.msg;
  if (err?.message) return err.message;
  return fallback;
};

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

// Auto-layout using dagre
const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const nodeWidth = 150;
  const nodeHeight = 80;
  
  dagreGraph.setGraph({ rankdir: direction, nodesep: 80, ranksep: 100 });
  
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });
  
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });
  
  dagre.layout(dagreGraph);
  
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });
  
  return { nodes: layoutedNodes, edges };
};

function AppContent() {
  const { fitView } = useReactFlow();
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
  const layoutTimeout = useRef(null);

  const generateNodeId = () => {
    nodeIdCounter.current += 1;
    return `node_${nodeIdCounter.current}`;
  };

  // Auto-layout and fit view when nodes/edges change
  const applyAutoLayout = useCallback(() => {
    if (nodes.length < 2) return;
    
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(nodes, edges, 'LR');
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
    
    // Fit view after layout
    setTimeout(() => {
      fitView({ padding: 0.2, duration: 300 });
    }, 50);
  }, [nodes, edges, setNodes, setEdges, fitView]);

  // Debounced auto-layout trigger
  useEffect(() => {
    if (layoutTimeout.current) {
      clearTimeout(layoutTimeout.current);
    }
    layoutTimeout.current = setTimeout(() => {
      if (nodes.length > 1) {
        applyAutoLayout();
      }
    }, 500);
    
    return () => {
      if (layoutTimeout.current) {
        clearTimeout(layoutTimeout.current);
      }
    };
  }, [nodes.length]); // Only trigger on node count change

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

  // Add a workflow node visually
  const addWorkflowNode = useCallback((label, type, parentStageId, data = {}) => {
    const nodeId = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const stageIndex = PIPELINE_STAGES.indexOf(parentStageId);
    
    // Calculate position - spread out from the stage node
    const baseX = 100 + (stageIndex * 180);
    const baseY = 100;
    const offsetX = (Math.random() - 0.5) * 100;
    const offsetY = 180 + (Math.random() * 100);
    
    const newNode = {
      id: nodeId,
      type: type || 'processing',
      position: { x: baseX + offsetX, y: baseY + offsetY },
      data: { label, ...data }
    };
    
    const newEdge = {
      id: `edge_${nodeId}`,
      source: `stage_${parentStageId}`,
      target: nodeId,
      animated: true,
      style: { stroke: '#6366F1' }
    };
    
    setNodes(nds => [...nds, newNode]);
    setEdges(eds => [...eds, newEdge]);
    
    return nodeId;
  }, [setNodes, setEdges]);

  // Connect two workflow nodes
  const connectNodes = useCallback((sourceId, targetId, color = '#10B981') => {
    const newEdge = {
      id: `edge_${sourceId}_${targetId}`,
      source: sourceId,
      target: targetId,
      animated: true,
      style: { stroke: color }
    };
    setEdges(eds => [...eds, newEdge]);
  }, [setEdges]);

  // Handle running a stage from stage node
  const handleRunStage = useCallback(async (stageId) => {
    setIsLoading(true);
    setError(null);
    
    const stageIndex = PIPELINE_STAGES.indexOf(stageId);
    
    // Mark stage as active
    setCurrentStage(stageId);
    setNodes(nds => nds.map(n => {
      if (n.id === `stage_${stageId}`) {
        return { ...n, data: { ...n.data, status: 'active' } };
      }
      return n;
    }));

    try {
      switch (stageId) {
        case 'inception':
          if (!genesisProject) {
            addWorkflowNode('Project Init', 'processing', 'inception', { status: 'active' });
            await new Promise(r => setTimeout(r, 300));
            await initializeGenesisProject('New Project');
          }
          break;
          
        case 'specification':
          if (session?.analysis?.ambiguities?.length > 0) {
            // Add nodes for each ambiguity being resolved
            const specNode = addWorkflowNode('Resolving Specs', 'processing', 'specification');
            await new Promise(r => setTimeout(r, 300));
            
            const autoAnswers = session.analysis.ambiguities.map(amb => ({
              ambiguity_id: amb.id,
              answer: amb.options?.[0] || 'Default',
              selected_option: amb.options?.[0] || null
            }));
            
            // Show some decision nodes
            for (let i = 0; i < Math.min(3, autoAnswers.length); i++) {
              const decisionNode = addWorkflowNode(`Decision ${i + 1}`, 'resolution', 'specification');
              connectNodes(specNode, decisionNode);
              await new Promise(r => setTimeout(r, 200));
            }
            
            await axios.post(`${API}/resolve`, {
              session_id: session.session_id,
              answers: autoAnswers
            });
          }
          break;
          
        case 'architecture':
          // Show architecture components being designed
          const archNode = addWorkflowNode('System Design', 'processing', 'architecture');
          await new Promise(r => setTimeout(r, 500));
          
          const frontendNode = addWorkflowNode('Frontend', 'spec', 'architecture');
          connectNodes(archNode, frontendNode);
          await new Promise(r => setTimeout(r, 400));
          
          const backendNode = addWorkflowNode('Backend', 'spec', 'architecture');
          connectNodes(archNode, backendNode);
          await new Promise(r => setTimeout(r, 400));
          
          const dbNode = addWorkflowNode('Database', 'spec', 'architecture');
          connectNodes(archNode, dbNode);
          await new Promise(r => setTimeout(r, 400));
          
          // Connect components to each other (spider web effect)
          connectNodes(frontendNode, backendNode, '#8B5CF6');
          await new Promise(r => setTimeout(r, 200));
          connectNodes(backendNode, dbNode, '#8B5CF6');
          
          if (session?.analysis) {
            const qualityResponse = await axios.post(`${API}/genesis/quality/assess`, {
              artifact: session.analysis,
              stage: 'architecture'
            });
            setQualityAssessment(qualityResponse.data);
          }
          break;
          
        case 'construction':
          // Show files being generated
          const buildNode = addWorkflowNode('Build Engine', 'processing', 'construction');
          await new Promise(r => setTimeout(r, 500));
          
          const filesNodes = ['main.py', 'routes.py', 'schema.sql'];
          let prevNode = buildNode;
          for (const file of filesNodes) {
            const fileNode = addWorkflowNode(file, 'spec', 'construction');
            connectNodes(prevNode, fileNode, '#F59E0B');
            prevNode = fileNode;
            await new Promise(r => setTimeout(r, 300));
          }
          
          const projectId = `build-${Date.now()}`;
          const projectName = session?.original_prompt?.substring(0, 20).replace(/[^a-zA-Z0-9]/g, '') + 'App' || 'GeneratedApp';
          await axios.post(`${API}/build/generate`, {
            project_id: projectId,
            project_name: projectName,
            specification: {
              name: projectName,
              data_model: {
                entities: session?.analysis?.entities || []
              },
              api_contracts: session?.analysis?.api_contracts || []
            },
            tech_stack: {
              frontend_framework: 'nextjs',
              backend_framework: 'fastapi',
              database: 'postgresql'
            }
          });
          break;
          
        case 'validation':
          // Show validation checks
          const validNode = addWorkflowNode('Quality Gate', 'processing', 'validation');
          await new Promise(r => setTimeout(r, 300));
          
          const checks = ['Code Quality', 'Security', 'Performance', 'API Tests'];
          for (const check of checks) {
            const checkNode = addWorkflowNode(check, 'resolution', 'validation');
            connectNodes(validNode, checkNode, '#10B981');
            await new Promise(r => setTimeout(r, 200));
          }
          
          if (session?.analysis) {
            await axios.post(`${API}/genesis/quality/assess`, {
              artifact: session.analysis,
              stage: 'validation'
            });
          }
          break;
        
        case 'evolution':
          // Show evolution/optimization nodes
          const evolveNode = addWorkflowNode('Optimization', 'processing', 'evolution');
          await new Promise(r => setTimeout(r, 300));
          addWorkflowNode('Refactor', 'spec', 'evolution');
          addWorkflowNode('Enhance', 'spec', 'evolution');
          break;
          
        case 'deployment':
          // Show deployment targets
          const deployNode = addWorkflowNode('Deploy Engine', 'processing', 'deployment');
          await new Promise(r => setTimeout(r, 300));
          
          const targets = ['Render', 'Vercel', 'Docker'];
          for (const target of targets) {
            const targetNode = addWorkflowNode(target, 'spec', 'deployment');
            connectNodes(deployNode, targetNode, '#EF4444');
            await new Promise(r => setTimeout(r, 200));
          }
          break;
          
        case 'governance':
          // Show governance checks
          const govNode = addWorkflowNode('Compliance', 'processing', 'governance');
          await new Promise(r => setTimeout(r, 300));
          addWorkflowNode('Audit Log', 'spec', 'governance');
          addWorkflowNode('Approval', 'resolution', 'governance');
          break;
          
        default:
          break;
      }
      
      // Mark stage as completed, activate next stage
      setNodes(nds => nds.map(n => {
        if (n.id === `stage_${stageId}`) {
          return { ...n, data: { ...n.data, status: 'completed' } };
        }
        if (stageIndex < PIPELINE_STAGES.length - 1 && n.id === `stage_${PIPELINE_STAGES[stageIndex + 1]}`) {
          return { ...n, data: { ...n.data, status: 'active' } };
        }
        return n;
      }));
      
      setEdges(eds => eds.map(e => {
        if (e.source === `stage_${stageId}`) {
          return { ...e, animated: true, style: { ...e.style, stroke: '#10B981' } };
        }
        return e;
      }));
      
      if (stageIndex < PIPELINE_STAGES.length - 1) {
        setCurrentStage(PIPELINE_STAGES[stageIndex + 1]);
      }
      
    } catch (err) {
      let errorMsg = `Failed to run ${stageId}`;
      if (typeof err === 'string') {
        errorMsg = err;
      } else if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        errorMsg = typeof detail === 'string' ? detail : JSON.stringify(detail);
      } else if (err?.message) {
        errorMsg = err.message;
      }
      setError(errorMsg);
      setNodes(nds => nds.map(n => {
        if (n.id === `stage_${stageId}`) {
          return { ...n, data: { ...n.data, status: 'failed' } };
        }
        return n;
      }));
    } finally {
      setIsLoading(false);
    }
  }, [genesisProject, session, setNodes, setEdges]);

  // Update stage nodes with the run handler when they change
  useEffect(() => {
    setNodes(nds => nds.map(n => {
      if (n.type === 'stage') {
        return { ...n, data: { ...n.data, onRunStage: handleRunStage } };
      }
      return n;
    }));
  }, [handleRunStage, setNodes]);

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
      
      // Create pipeline visualization nodes - onRunStage will be added via useEffect
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
      setError(getErrorMessage(err, 'Failed to initialize project'));
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
      setError(getErrorMessage(err, 'Quality assessment failed'));
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
      setError(getErrorMessage(err, 'Ouroboros execution failed'));
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

      // Always advance to specification stage after analysis completes
      setCurrentStage('specification');
      // Update stage nodes
      setNodes((nds) => nds.map(n => {
        if (n.id === 'stage_inception') {
          return { ...n, data: { ...n.data, status: 'completed' } };
        }
        if (n.id === 'stage_specification') {
          return { ...n, data: { ...n.data, status: 'active' } };
        }
        return n;
      }));
      // Highlight the edge
      setEdges((eds) => eds.map(e => {
        if (e.target === 'stage_specification') {
          return { ...e, animated: true, style: { ...e.style, stroke: '#10B981' } };
        }
        return e;
      }));

    } catch (err) {
      setError(getErrorMessage(err, 'Failed to analyze prompt'));
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
      setError(getErrorMessage(err, 'Failed to resolve ambiguities'));
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate Full Build - autonomous mode
  const simulateFullBuild = async () => {
    if (!session) return;
    
    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Auto-select AI recommended answers (first option for each)
      const autoAnswers = {};
      const ambiguities = session.analysis?.ambiguities || [];
      ambiguities.forEach(amb => {
        if (amb.options && amb.options.length > 0) {
          autoAnswers[amb.id] = { answer: amb.options[0], selected_option: amb.options[0] };
        }
      });
      setAnswers(autoAnswers);

      // Step 2: Submit the answers
      const formattedAnswers = Object.entries(autoAnswers).map(([id, data]) => ({
        ambiguity_id: id,
        answer: data.answer,
        selected_option: data.selected_option
      }));

      const resolveResponse = await axios.post(`${API}/resolve`, {
        session_id: session.session_id,
        answers: formattedAnswers
      });

      const { analysis, confidence_score, can_proceed } = resolveResponse.data;
      setSession(prev => ({ ...prev, analysis, confidence_score, can_proceed }));

      // Step 3: Advance to architecture stage
      setCurrentStage('architecture');
      setNodes(nds => nds.map(n => {
        if (n.id === 'stage_specification') return { ...n, data: { ...n.data, status: 'completed' } };
        if (n.id === 'stage_architecture') return { ...n, data: { ...n.data, status: 'active' } };
        return n;
      }));

      // Step 4: Run quality assessment
      const qualityResponse = await axios.post(`${API}/genesis/quality/assess`, {
        artifact: { ...analysis, prompt: session.original_prompt },
        stage: 'architecture'
      });
      setQualityAssessment(qualityResponse.data);

      // Step 5: Advance to construction stage
      setCurrentStage('construction');
      setNodes(nds => nds.map(n => {
        if (n.id === 'stage_architecture') return { ...n, data: { ...n.data, status: 'completed' } };
        if (n.id === 'stage_construction') return { ...n, data: { ...n.data, status: 'active' } };
        return n;
      }));

      // Step 6: Generate the build
      const projectId = `sim-${Date.now()}`;
      const projectName = session.original_prompt.substring(0, 20).replace(/[^a-zA-Z0-9]/g, '') + 'App';
      
      const buildResponse = await axios.post(`${API}/build/enhanced`, {
        prompt: session.original_prompt,
        options: {
          include_auth: true,
          include_tests: true,
          include_crud: true
        }
      });

      // Step 7: Advance to validation stage
      setCurrentStage('validation');
      setNodes(nds => nds.map(n => {
        if (n.id === 'stage_construction') return { ...n, data: { ...n.data, status: 'completed' } };
        if (n.id === 'stage_validation') return { ...n, data: { ...n.data, status: 'active' } };
        return n;
      }));

      // Step 8: Complete - advance to deployment stage
      setTimeout(() => {
        setCurrentStage('deployment');
        setNodes(nds => nds.map(n => {
          if (n.id === 'stage_validation') return { ...n, data: { ...n.data, status: 'completed' } };
          if (n.id === 'stage_deployment') return { ...n, data: { ...n.data, status: 'active' } };
          return n;
        }));
      }, 1000);

      // Show success and open build panel
      alert(`✅ Simulation Complete!\n\nProject: ${projectName}\nFiles Generated: ${buildResponse.data?.artifacts?.length || 15}+\n\nClick "Build Project" to download your code.`);

    } catch (err) {
      setError(getErrorMessage(err, 'Simulation failed'));
    } finally {
      setIsLoading(false);
    }
  };

  // Quick Demo - one click to full simulation
  const quickSimulate = async (demoPrompt) => {
    setIsLoading(true);
    setError(null);

    try {
      // Initialize project
      if (!genesisProject) {
        await initializeGenesisProject(demoPrompt.substring(0, 30));
      }

      // Run analysis
      const response = await axios.post(`${API}/analyze`, { prompt: demoPrompt });
      const { session_id, analysis, confidence_score, can_proceed } = response.data;

      setSession({
        session_id,
        original_prompt: demoPrompt,
        analysis,
        confidence_score,
        can_proceed
      });

      // Advance to specification
      setCurrentStage('specification');
      setNodes(nds => nds.map(n => {
        if (n.id === 'stage_inception') return { ...n, data: { ...n.data, status: 'completed' } };
        if (n.id === 'stage_specification') return { ...n, data: { ...n.data, status: 'active' } };
        return n;
      }));

      // Auto-select answers
      const autoAnswers = {};
      const ambiguities = analysis?.ambiguities || [];
      ambiguities.forEach(amb => {
        if (amb.options && amb.options.length > 0) {
          autoAnswers[amb.id] = { answer: amb.options[0], selected_option: amb.options[0] };
        }
      });
      setAnswers(autoAnswers);

      // Submit answers
      const formattedAnswers = Object.entries(autoAnswers).map(([id, data]) => ({
        ambiguity_id: id,
        answer: data.answer,
        selected_option: data.selected_option
      }));

      await axios.post(`${API}/resolve`, {
        session_id: session_id,
        answers: formattedAnswers
      });

      // Progress through stages
      for (const stage of ['architecture', 'construction', 'validation']) {
        await new Promise(r => setTimeout(r, 500));
        setCurrentStage(stage);
        setNodes(nds => nds.map(n => {
          const prevStage = stage === 'architecture' ? 'specification' : stage === 'construction' ? 'architecture' : 'construction';
          if (n.id === `stage_${prevStage}`) return { ...n, data: { ...n.data, status: 'completed' } };
          if (n.id === `stage_${stage}`) return { ...n, data: { ...n.data, status: 'active' } };
          return n;
        }));
      }

      // Generate build
      await axios.post(`${API}/build/enhanced`, {
        prompt: demoPrompt,
        options: { include_auth: true, include_tests: true, include_crud: true }
      });

      // Complete
      setCurrentStage('deployment');
      setNodes(nds => nds.map(n => {
        if (n.id === 'stage_validation') return { ...n, data: { ...n.data, status: 'completed' } };
        if (n.id === 'stage_deployment') return { ...n, data: { ...n.data, status: 'active' } };
        return n;
      }));

      alert(`✅ Quick Demo Complete!\n\nPrompt: "${demoPrompt}"\n\nClick "Build Project" to customize and download your code.`);

    } catch (err) {
      setError(getErrorMessage(err, 'Quick demo failed'));
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
        onQuickSimulate={quickSimulate}
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
          onSimulate={simulateFullBuild}
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

// Wrap with ReactFlowProvider for useReactFlow hook
function App() {
  return (
    <ReactFlowProvider>
      <AppContent />
    </ReactFlowProvider>
  );
}

export default App;
