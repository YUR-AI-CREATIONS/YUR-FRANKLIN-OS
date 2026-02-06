import React, { useState, useCallback, useRef, useEffect } from 'react';
import './App.css';
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

// Panel Components
import Header from './components/panels/Header';
import InputPanel from './components/panels/InputPanel';
import ClarificationPanel from './components/panels/ClarificationPanel';
import NodeInspector from './components/panels/NodeInspector';
import SpecificationPanel from './components/panels/SpecificationPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const nodeTypes = {
  input: InputNode,
  ambiguity: AmbiguityNode,
  resolution: ResolutionNode,
  spec: SpecNode,
  processing: ProcessingNode,
};

const initialNodes = [];
const initialEdges = [];

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [answers, setAnswers] = useState({});
  const [specification, setSpecification] = useState(null);
  const [error, setError] = useState(null);
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
    nodeIdCounter.current = 0;
  };

  const analyzePrompt = async (prompt) => {
    setIsLoading(true);
    setError(null);
    clearCanvas();

    try {
      // Add input node
      const inputNodeId = generateNodeId();
      const inputNode = {
        id: inputNodeId,
        type: 'input',
        position: { x: 100, y: 250 },
        data: { label: 'User Input', content: prompt },
      };

      // Add processing node
      const processingNodeId = generateNodeId();
      const processingNode = {
        id: processingNodeId,
        type: 'processing',
        position: { x: 350, y: 250 },
        data: { label: 'Socratic Engine', status: 'analyzing' },
      };

      setNodes([inputNode, processingNode]);
      setEdges([{
        id: `e_${inputNodeId}_${processingNodeId}`,
        source: inputNodeId,
        target: processingNodeId,
        animated: true,
        style: { stroke: '#6366F1' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#6366F1' }
      }]);

      // Call API
      const response = await axios.post(`${API}/analyze`, { prompt });
      const { session_id, analysis, confidence_score, can_proceed } = response.data;

      setSession({
        session_id,
        original_prompt: prompt,
        analysis,
        confidence_score,
        can_proceed
      });

      // Update processing node
      setNodes((nds) => nds.map((n) => 
        n.id === processingNodeId 
          ? { ...n, data: { ...n.data, status: 'complete', confidence: confidence_score } }
          : n
      ));

      // Add ambiguity nodes
      const ambiguities = analysis.ambiguities || [];
      const newNodes = [];
      const newEdges = [];

      ambiguities.forEach((amb, index) => {
        const ambNodeId = generateNodeId();
        const yOffset = 150 + (index * 120);
        
        newNodes.push({
          id: ambNodeId,
          type: 'ambiguity',
          position: { x: 600, y: yOffset },
          data: {
            ...amb,
            label: amb.id,
            category: amb.category,
            question: amb.question,
            options: amb.options,
            priority: amb.priority,
          },
        });

        newEdges.push({
          id: `e_${processingNodeId}_${ambNodeId}`,
          source: processingNodeId,
          target: ambNodeId,
          animated: true,
          style: { stroke: '#F59E0B' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#F59E0B' }
        });
      });

      setNodes((nds) => [...nds, ...newNodes]);
      setEdges((eds) => [...eds, ...newEdges]);

    } catch (err) {
      console.error('Analysis error:', err);
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

      const { resolution, resolved_parameters, confidence_score, can_proceed } = response.data;

      // Add resolution nodes for answered questions
      const newNodes = [];
      const newEdges = [];

      Object.entries(answers).forEach(([ambId, answerData], index) => {
        const resNodeId = generateNodeId();
        
        // Find the ambiguity node position
        const ambNode = nodes.find(n => n.data?.id === ambId || n.data?.label === ambId);
        const xPos = ambNode ? ambNode.position.x + 250 : 850;
        const yPos = ambNode ? ambNode.position.y : 150 + (index * 120);

        newNodes.push({
          id: resNodeId,
          type: 'resolution',
          position: { x: xPos, y: yPos },
          data: {
            label: `Resolved: ${ambId}`,
            ambiguity_id: ambId,
            answer: answerData.answer || answerData.selected_option,
          },
        });

        // Find source node
        const sourceNode = nodes.find(n => n.data?.id === ambId || n.data?.label === ambId);
        if (sourceNode) {
          newEdges.push({
            id: `e_${sourceNode.id}_${resNodeId}`,
            source: sourceNode.id,
            target: resNodeId,
            animated: true,
            style: { stroke: '#10B981' },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#10B981' }
          });
        }
      });

      setNodes((nds) => [...nds, ...newNodes]);
      setEdges((eds) => [...eds, ...newEdges]);

      // Update session
      setSession((prev) => ({
        ...prev,
        analysis: {
          ...prev.analysis,
          ambiguities: [
            ...(resolution.remaining_ambiguities || []),
            ...(resolution.new_ambiguities || [])
          ]
        },
        resolved_parameters: resolved_parameters,
        confidence_score,
        can_proceed
      }));

      setAnswers({});

      // If can proceed, add spec generation node
      if (can_proceed) {
        const specNodeId = generateNodeId();
        const lastResNode = newNodes[newNodes.length - 1];
        
        setNodes((nds) => [...nds, {
          id: specNodeId,
          type: 'processing',
          position: { x: (lastResNode?.position?.x || 850) + 250, y: 250 },
          data: { label: 'Specification Ready', status: 'ready', confidence: confidence_score }
        }]);
      }

    } catch (err) {
      console.error('Resolution error:', err);
      setError(err.response?.data?.detail || 'Failed to resolve ambiguities');
    } finally {
      setIsLoading(false);
    }
  };

  const generateSpecification = async () => {
    if (!session || !session.can_proceed) return;
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API}/generate-spec`, {
        session_id: session.session_id
      });

      setSpecification(response.data);

      // Add spec node to canvas
      const specNodeId = generateNodeId();
      const lastNode = nodes[nodes.length - 1];
      
      setNodes((nds) => [...nds, {
        id: specNodeId,
        type: 'spec',
        position: { x: (lastNode?.position?.x || 850) + 200, y: 250 },
        data: { 
          label: 'Formal Specification',
          spec: response.data.specification
        }
      }]);

      // Connect to previous node
      if (lastNode) {
        setEdges((eds) => [...eds, {
          id: `e_${lastNode.id}_${specNodeId}`,
          source: lastNode.id,
          target: specNodeId,
          animated: true,
          style: { stroke: '#10B981' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#10B981' }
        }]);
      }

    } catch (err) {
      console.error('Spec generation error:', err);
      setError(err.response?.data?.detail || 'Failed to generate specification');
    } finally {
      setIsLoading(false);
    }
  };

  const currentAmbiguities = session?.analysis?.ambiguities || [];
  const hasUnresolvedAmbiguities = currentAmbiguities.length > 0;

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
              return '#3F3F46';
            }}
            maskColor="rgba(5, 5, 5, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* Header */}
      <Header 
        session={session}
        onClear={clearCanvas}
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

      {/* Generate Spec Button */}
      {session && session.can_proceed && !specification && (
        <div className="floating-panel" style={{ top: '80px', right: '24px' }}>
          <div className="glass-panel p-4 rounded-lg">
            <div className="text-center">
              <div className="text-emerald-400 font-mono text-sm mb-2">SPECIFICATION READY</div>
              <div className="text-2xl font-bold text-emerald-400 mb-3">
                {session.confidence_score?.toFixed(1)}%
              </div>
              <button
                data-testid="generate-spec-btn"
                onClick={generateSpecification}
                disabled={isLoading}
                className="w-full px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Generating...' : 'Generate Specification'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Specification Panel */}
      {specification && (
        <SpecificationPanel
          specification={specification}
          onClose={() => setSpecification(null)}
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
          className="fixed bottom-24 left-1/2 -translate-x-1/2 glass-panel px-4 py-3 rounded-lg border-l-4 border-red-500 animate-slide-in"
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
    </div>
  );
}

export default App;
