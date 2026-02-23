"""
Neo3 Test Suite
Validates core functionality of the AI cognitive evolvement system
"""

import unittest
import asyncio
from neo3_core import (
    Neo3System, CognitiveModule, NeuralCognitiveModule, 
    ReasoningModule, MemoryModule, OrchestrationEngine,
    EvolutionStrategy
)
from orchestration import (
    MultiAgentOrchestrator, AnalyzerAgent, StrategistAgent,
    ExecutorAgent, Task, DecisionPriority
)
from evolution import (
    GeneticEvolutionEngine, AdaptiveController, SelfImprovementEngine,
    Genome, AdaptationStrategy
)


class TestNeo3Core(unittest.TestCase):
    """Test cases for Neo3 core cognitive system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.neo3 = Neo3System()
        self.neo3.initialize()
    
    def test_system_initialization(self):
        """Test that system initializes correctly"""
        self.assertTrue(self.neo3.initialized)
        self.assertEqual(len(self.neo3.orchestrator.modules), 3)
    
    def test_cognitive_processing(self):
        """Test cognitive module processing"""
        result = self.neo3.process([1, 2, 3, 4, 5])
        self.assertIn("neural_core", result)
        self.assertIn("memory_system", result)
        self.assertIn("reasoning_engine", result)
    
    def test_system_evolution(self):
        """Test system evolution"""
        initial_state = self.neo3.orchestrator.global_state["total_evolutions"]
        self.neo3.evolve(iterations=5)
        final_state = self.neo3.orchestrator.global_state["total_evolutions"]
        self.assertEqual(final_state - initial_state, 5)
    
    def test_system_training(self):
        """Test system training with data"""
        training_data = [
            {"input": [1, 2, 3], "feedback": {"accuracy": 0.8}},
            {"input": [4, 5, 6], "feedback": {"accuracy": 0.9}},
        ]
        result = self.neo3.train(training_data)
        self.assertEqual(result["trained_samples"], 2)
    
    def test_neural_module(self):
        """Test neural cognitive module"""
        module = NeuralCognitiveModule("test_neural", input_dim=5, hidden_dim=32)
        result = module.process([1, 2, 3])
        self.assertIsNotNone(result)
        
        module.learn({"accuracy": 0.9})
        self.assertGreater(module.state.knowledge_level, 0.5)
    
    def test_reasoning_module(self):
        """Test reasoning module"""
        module = ReasoningModule("test_reasoning")
        result = module.process({"test": "data"})
        self.assertIsInstance(result, dict)
        
        module.learn({"new_rule": {"type": "test"}})
        self.assertEqual(len(module.rules), 1)
    
    def test_memory_module(self):
        """Test memory module"""
        module = MemoryModule("test_memory", capacity=100)
        
        # Test storage
        result = module.process("test_data")
        self.assertEqual(result["status"], "stored")
        
        # Test retrieval
        module.long_term_memory["test_key"] = "test_value"
        result = module.process({"query": "test_key"})
        self.assertEqual(result, "test_value")
    
    def test_orchestration_engine(self):
        """Test orchestration engine"""
        engine = OrchestrationEngine()
        module = NeuralCognitiveModule("test_module")
        engine.register_module(module)
        
        result = engine.orchestrate([1, 2, 3])
        self.assertIn("test_module", result)


class TestMultiAgentOrchestration(unittest.TestCase):
    """Test cases for multi-agent orchestration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.register_agent(AnalyzerAgent("test_analyzer"))
        self.orchestrator.register_agent(StrategistAgent("test_strategist"))
        self.orchestrator.register_agent(ExecutorAgent("test_executor"))
    
    def test_agent_registration(self):
        """Test agent registration"""
        self.assertEqual(len(self.orchestrator.agents), 3)
    
    def test_task_submission(self):
        """Test task submission"""
        task = Task("task_001", "analysis", {"data": "test"}, DecisionPriority.HIGH)
        self.orchestrator.submit_task(task)
        self.assertEqual(len(self.orchestrator.task_queue), 1)
    
    def test_task_processing(self):
        """Test task processing"""
        async def run_test():
            task = Task("task_002", "analysis", {"data": "test"}, DecisionPriority.MEDIUM)
            self.orchestrator.submit_task(task)
            result = await self.orchestrator.process_tasks()
            return result
        
        result = asyncio.run(run_test())
        self.assertEqual(result["processed_tasks"], 1)
    
    def test_agent_performance(self):
        """Test agent performance tracking"""
        agent = AnalyzerAgent("perf_test")
        initial_expertise = agent.expertise_level
        
        async def run_test():
            task = Task("task_003", "analysis", {"data": "test"}, DecisionPriority.HIGH)
            await agent.execute_task(task)
        
        asyncio.run(run_test())
        self.assertGreaterEqual(agent.expertise_level, initial_expertise)
    
    def test_orchestrator_status(self):
        """Test orchestrator status retrieval"""
        status = self.orchestrator.get_orchestrator_status()
        self.assertIn("registered_agents", status)
        self.assertIn("metrics", status)
        self.assertEqual(status["registered_agents"], 3)


class TestEvolutionEngine(unittest.TestCase):
    """Test cases for evolution and self-improvement"""
    
    def test_genome_creation(self):
        """Test genome creation and manipulation"""
        genome = Genome(genes=[0.1, 0.2, 0.3, 0.4, 0.5])
        self.assertEqual(len(genome.genes), 5)
        self.assertEqual(genome.generation, 0)
    
    def test_genome_mutation(self):
        """Test genome mutation"""
        genome = Genome(genes=[0.5] * 10)
        mutated = genome.mutate(mutation_rate=1.0)  # 100% mutation rate
        self.assertEqual(mutated.generation, 1)
        self.assertNotEqual(genome.genes, mutated.genes)
    
    def test_genome_crossover(self):
        """Test genome crossover"""
        parent1 = Genome(genes=[0.1] * 10)
        parent2 = Genome(genes=[0.9] * 10)
        child1, child2 = Genome.crossover(parent1, parent2)
        
        self.assertEqual(len(child1.genes), 10)
        self.assertEqual(len(child2.genes), 10)
    
    def test_genetic_evolution(self):
        """Test genetic evolution engine"""
        engine = GeneticEvolutionEngine(population_size=20, gene_length=10)
        engine.initialize_population()
        self.assertEqual(len(engine.population), 20)
        
        # Simple fitness function
        def fitness(genes):
            return sum(g ** 2 for g in genes)
        
        engine.evaluate_population(fitness)
        self.assertGreater(engine.metrics.best_fitness, 0)
        
        initial_gen = engine.metrics.generation
        engine.evolve_generation()
        self.assertEqual(engine.metrics.generation, initial_gen + 1)
    
    def test_adaptive_controller(self):
        """Test adaptive controller"""
        controller = AdaptiveController(AdaptationStrategy.HYBRID)
        
        # Test parameter retrieval
        learning_rate = controller.get_parameter("learning_rate")
        self.assertGreater(learning_rate, 0)
        
        # Test adaptation
        initial_lr = controller.parameters["learning_rate"]
        controller.adapt(0.9)  # High performance
        controller.adapt(0.8)
        controller.adapt(0.85)
        controller.adapt(0.9)
        controller.adapt(0.95)  # Improving trend
        
        # Parameters should have adapted
        self.assertGreater(controller.adaptation_count, 0)
    
    def test_self_improvement_engine(self):
        """Test self-improvement engine"""
        engine = SelfImprovementEngine()
        engine.initialize()
        
        result = engine.improve(iterations=5)
        self.assertEqual(result["iterations_completed"], 5)
        self.assertGreater(engine.improvement_cycles, 0)
        
        status = engine.get_status()
        self.assertIn("improvement_cycles", status)
        self.assertIn("genetic_evolution", status)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_cognitive_processing(self):
        """Test complete cognitive processing pipeline"""
        neo3 = Neo3System()
        neo3.initialize()
        
        # Process various data types
        result1 = neo3.process([1, 2, 3])
        result2 = neo3.process({"query": "test"})
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
    
    def test_evolution_with_training(self):
        """Test evolution combined with training"""
        neo3 = Neo3System()
        neo3.initialize()
        
        training_data = [
            {"input": [1, 2], "feedback": {"accuracy": 0.8}},
            {"input": [3, 4], "feedback": {"accuracy": 0.9}},
        ]
        
        neo3.train(training_data)
        neo3.evolve(iterations=3)
        
        status = neo3.get_status()
        self.assertGreater(status["global_state"]["total_evolutions"], 0)


def run_tests():
    """Run all tests and display results"""
    print("\n" + "="*70)
    print("Neo3 Test Suite")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNeo3Core))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiAgentOrchestration))
    suite.addTests(loader.loadTestsFromTestCase(TestEvolutionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
