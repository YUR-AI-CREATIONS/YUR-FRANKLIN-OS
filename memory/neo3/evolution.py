"""
Neo3 Evolution and Adaptation Engine
Self-improvement mechanisms and performance optimization
"""

import random
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class EvolutionaryAlgorithm(Enum):
    """Types of evolutionary algorithms"""
    GENETIC = "genetic"
    PARTICLE_SWARM = "particle_swarm"
    DIFFERENTIAL_EVOLUTION = "differential_evolution"
    NEUROEVOLUTION = "neuroevolution"
    COEVOLUTION = "coevolution"


class AdaptationStrategy(Enum):
    """Strategies for system adaptation"""
    REACTIVE = "reactive"  # React to changes
    PROACTIVE = "proactive"  # Anticipate changes
    HYBRID = "hybrid"  # Combine both
    AUTONOMOUS = "autonomous"  # Fully self-directed


@dataclass
class Genome:
    """Represents a genetic configuration"""
    genes: List[float]
    fitness: float = 0.0
    generation: int = 0
    mutations: int = 0
    
    def mutate(self, mutation_rate: float = 0.1) -> 'Genome':
        """Create a mutated copy of this genome"""
        mutated_genes = []
        mutations = 0
        for gene in self.genes:
            if random.random() < mutation_rate:
                # Gaussian mutation
                mutated_gene = gene + random.gauss(0, 0.1)
                mutated_genes.append(max(-1.0, min(1.0, mutated_gene)))
                mutations += 1
            else:
                mutated_genes.append(gene)
        
        return Genome(
            genes=mutated_genes,
            generation=self.generation + 1,
            mutations=self.mutations + mutations
        )
    
    @staticmethod
    def crossover(parent1: 'Genome', parent2: 'Genome') -> Tuple['Genome', 'Genome']:
        """Create two offspring from two parents"""
        crossover_point = random.randint(1, len(parent1.genes) - 1)
        
        child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
        
        child1 = Genome(genes=child1_genes, generation=max(parent1.generation, parent2.generation) + 1)
        child2 = Genome(genes=child2_genes, generation=max(parent1.generation, parent2.generation) + 1)
        
        return child1, child2


@dataclass
class EvolutionMetrics:
    """Tracks evolution progress metrics"""
    generation: int = 0
    best_fitness: float = 0.0
    average_fitness: float = 0.0
    diversity: float = 0.0
    stagnation_count: int = 0
    total_evaluations: int = 0


class GeneticEvolutionEngine:
    """Genetic algorithm-based evolution engine"""
    
    def __init__(self, population_size: int = 50, gene_length: int = 20):
        self.population_size = population_size
        self.gene_length = gene_length
        self.population: List[Genome] = []
        self.metrics = EvolutionMetrics()
        self.elite_size = max(2, population_size // 10)
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        
    def initialize_population(self) -> None:
        """Initialize random population"""
        self.population = [
            Genome(genes=[random.uniform(-1, 1) for _ in range(self.gene_length)])
            for _ in range(self.population_size)
        ]
    
    def evaluate_population(self, fitness_function: callable) -> None:
        """Evaluate fitness of entire population"""
        for genome in self.population:
            genome.fitness = fitness_function(genome.genes)
            self.metrics.total_evaluations += 1
        
        # Update metrics
        fitnesses = [g.fitness for g in self.population]
        self.metrics.best_fitness = max(fitnesses)
        self.metrics.average_fitness = sum(fitnesses) / len(fitnesses)
        self.metrics.diversity = self._calculate_diversity()
    
    def evolve_generation(self) -> None:
        """Evolve population by one generation"""
        # Sort by fitness
        self.population.sort(key=lambda g: g.fitness, reverse=True)
        
        # Check for stagnation
        if abs(self.metrics.best_fitness - self.population[0].fitness) < 0.001:
            self.metrics.stagnation_count += 1
        else:
            self.metrics.stagnation_count = 0
        
        # Elitism: keep best individuals
        new_population = self.population[:self.elite_size]
        
        # Generate offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = Genome.crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutation
            child1 = child1.mutate(self.mutation_rate)
            child2 = child2.mutate(self.mutation_rate)
            
            new_population.extend([child1, child2])
        
        self.population = new_population[:self.population_size]
        self.metrics.generation += 1
        
        # Adaptive parameters
        self._adapt_parameters()
    
    def _tournament_selection(self, tournament_size: int = 3) -> Genome:
        """Select individual using tournament selection"""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda g: g.fitness)
    
    def _calculate_diversity(self) -> float:
        """Calculate genetic diversity in population"""
        if len(self.population) < 2:
            return 0.0
        
        total_distance = 0.0
        comparisons = 0
        
        for i in range(min(10, len(self.population))):
            for j in range(i + 1, min(10, len(self.population))):
                distance = sum((g1 - g2) ** 2 for g1, g2 in zip(
                    self.population[i].genes, self.population[j].genes
                ))
                total_distance += math.sqrt(distance)
                comparisons += 1
        
        return total_distance / comparisons if comparisons > 0 else 0.0
    
    def _adapt_parameters(self) -> None:
        """Adapt evolution parameters based on progress"""
        # Increase mutation rate if stagnating
        if self.metrics.stagnation_count > 5:
            self.mutation_rate = min(0.3, self.mutation_rate * 1.1)
        else:
            self.mutation_rate = max(0.05, self.mutation_rate * 0.95)
        
        # Adjust diversity
        if self.metrics.diversity < 0.5:
            self.mutation_rate *= 1.2
    
    def get_best_genome(self) -> Genome:
        """Get the best genome in current population"""
        return max(self.population, key=lambda g: g.fitness)
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Get comprehensive evolution report"""
        best = self.get_best_genome()
        return {
            "generation": self.metrics.generation,
            "best_fitness": round(self.metrics.best_fitness, 4),
            "average_fitness": round(self.metrics.average_fitness, 4),
            "diversity": round(self.metrics.diversity, 4),
            "total_evaluations": self.metrics.total_evaluations,
            "mutation_rate": round(self.mutation_rate, 4),
            "best_genome": {
                "fitness": round(best.fitness, 4),
                "generation": best.generation,
                "mutations": best.mutations
            }
        }


class AdaptiveController:
    """Controller for adaptive system behavior"""
    
    def __init__(self, strategy: AdaptationStrategy = AdaptationStrategy.HYBRID):
        self.strategy = strategy
        self.parameters: Dict[str, float] = {
            "learning_rate": 0.01,
            "exploration_rate": 0.1,
            "momentum": 0.9,
            "temperature": 1.0
        }
        self.performance_history: List[float] = []
        self.adaptation_count = 0
    
    def adapt(self, performance_metric: float) -> None:
        """Adapt parameters based on performance"""
        self.performance_history.append(performance_metric)
        
        if len(self.performance_history) < 5:
            return
        
        # Analyze recent performance trend
        recent = self.performance_history[-5:]
        trend = (recent[-1] - recent[0]) / len(recent)
        
        if self.strategy in [AdaptationStrategy.REACTIVE, AdaptationStrategy.HYBRID]:
            self._reactive_adaptation(trend)
        
        if self.strategy in [AdaptationStrategy.PROACTIVE, AdaptationStrategy.HYBRID]:
            self._proactive_adaptation(trend)
        
        if self.strategy == AdaptationStrategy.AUTONOMOUS:
            self._autonomous_adaptation()
        
        self.adaptation_count += 1
    
    def _reactive_adaptation(self, trend: float) -> None:
        """React to observed performance trends"""
        if trend < -0.01:  # Performance declining
            self.parameters["learning_rate"] *= 1.1
            self.parameters["exploration_rate"] *= 1.2
        elif trend > 0.01:  # Performance improving
            self.parameters["learning_rate"] *= 0.95
            self.parameters["exploration_rate"] *= 0.9
    
    def _proactive_adaptation(self, trend: float) -> None:
        """Proactively adjust to anticipated changes"""
        # Predict future performance
        if len(self.performance_history) >= 10:
            recent_volatility = self._calculate_volatility(self.performance_history[-10:])
            
            if recent_volatility > 0.1:
                # High volatility: increase stability
                self.parameters["momentum"] = min(0.99, self.parameters["momentum"] * 1.05)
                self.parameters["temperature"] *= 0.95
            else:
                # Low volatility: encourage exploration
                self.parameters["momentum"] = max(0.5, self.parameters["momentum"] * 0.95)
                self.parameters["temperature"] *= 1.05
    
    def _autonomous_adaptation(self) -> None:
        """Fully autonomous self-directed adaptation"""
        # Meta-learning: learn how to learn
        for param_name in self.parameters:
            # Small random perturbation
            perturbation = random.gauss(0, 0.01)
            self.parameters[param_name] = max(0.001, self.parameters[param_name] + perturbation)
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation)"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def get_parameter(self, name: str) -> float:
        """Get current value of a parameter"""
        return self.parameters.get(name, 0.0)
    
    def get_adaptation_status(self) -> Dict[str, Any]:
        """Get adaptation status report"""
        return {
            "strategy": self.strategy.value,
            "parameters": {k: round(v, 4) for k, v in self.parameters.items()},
            "adaptation_count": self.adaptation_count,
            "performance_trend": self._get_trend_description()
        }
    
    def _get_trend_description(self) -> str:
        """Describe current performance trend"""
        if len(self.performance_history) < 5:
            return "insufficient_data"
        
        recent = self.performance_history[-5:]
        trend = (recent[-1] - recent[0]) / len(recent)
        
        if trend > 0.02:
            return "improving"
        elif trend < -0.02:
            return "declining"
        else:
            return "stable"


class SelfImprovementEngine:
    """Engine for continuous self-improvement"""
    
    def __init__(self):
        self.genetic_engine = GeneticEvolutionEngine(population_size=30, gene_length=15)
        self.adaptive_controller = AdaptiveController(AdaptationStrategy.HYBRID)
        self.improvement_cycles = 0
        self.cumulative_improvement = 0.0
        self.baseline_performance = 0.0
    
    def initialize(self) -> None:
        """Initialize self-improvement systems"""
        self.genetic_engine.initialize_population()
        self.baseline_performance = 0.5  # Starting baseline
    
    def improve(self, iterations: int = 10) -> Dict[str, Any]:
        """Run self-improvement for specified iterations"""
        results = []
        
        for i in range(iterations):
            # Evolve genetic population
            self.genetic_engine.evaluate_population(self._fitness_function)
            self.genetic_engine.evolve_generation()
            
            # Get best performance
            best_genome = self.genetic_engine.get_best_genome()
            current_performance = best_genome.fitness
            
            # Adapt parameters
            self.adaptive_controller.adapt(current_performance)
            
            # Track improvement
            improvement = current_performance - self.baseline_performance
            self.cumulative_improvement += improvement
            
            self.improvement_cycles += 1
            
            results.append({
                "cycle": self.improvement_cycles,
                "performance": round(current_performance, 4),
                "improvement": round(improvement, 4),
                "cumulative": round(self.cumulative_improvement, 4)
            })
        
        return {
            "iterations_completed": iterations,
            "final_performance": round(current_performance, 4),
            "total_improvement": round(self.cumulative_improvement, 4),
            "improvement_rate": round(self.cumulative_improvement / self.improvement_cycles, 4),
            "results": results
        }
    
    def _fitness_function(self, genes: List[float]) -> float:
        """Fitness function for evolution (example implementation)"""
        # Complex fitness landscape with multiple objectives
        
        # Objective 1: Maximize sum of squared genes (exploration)
        exploration_score = sum(g ** 2 for g in genes) / len(genes)
        
        # Objective 2: Minimize variance (stability)
        mean = sum(genes) / len(genes)
        variance = sum((g - mean) ** 2 for g in genes) / len(genes)
        stability_score = 1.0 / (1.0 + variance)
        
        # Objective 3: Reward specific patterns (problem-solving)
        pattern_score = abs(sum(genes[i] * genes[i+1] for i in range(len(genes)-1)))
        
        # Combine objectives with adaptive weights
        weights = [
            self.adaptive_controller.get_parameter("learning_rate") * 10,
            self.adaptive_controller.get_parameter("momentum"),
            self.adaptive_controller.get_parameter("exploration_rate") * 5
        ]
        
        fitness = (exploration_score * weights[0] +
                  stability_score * weights[1] +
                  pattern_score * weights[2])
        
        return fitness / sum(weights)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of self-improvement"""
        return {
            "improvement_cycles": self.improvement_cycles,
            "cumulative_improvement": round(self.cumulative_improvement, 4),
            "improvement_rate": round(
                self.cumulative_improvement / self.improvement_cycles if self.improvement_cycles > 0 else 0.0, 
                4
            ),
            "genetic_evolution": self.genetic_engine.get_evolution_report(),
            "adaptive_control": self.adaptive_controller.get_adaptation_status()
        }


def demonstrate_evolution():
    """Demonstrate the evolution and self-improvement capabilities"""
    print("\n" + "="*70)
    print("Neo3 Evolution and Self-Improvement Engine")
    print("="*70)
    
    # Create self-improvement engine
    engine = SelfImprovementEngine()
    engine.initialize()
    
    print("\n✓ Self-Improvement Engine Initialized")
    print(f"  Population size: {engine.genetic_engine.population_size}")
    print(f"  Genome length: {engine.genetic_engine.gene_length}")
    print(f"  Adaptation strategy: {engine.adaptive_controller.strategy.value}")
    
    # Run improvement cycles
    print("\n--- Running Self-Improvement Cycles ---")
    result = engine.improve(iterations=20)
    
    print(f"\n✓ Completed {result['iterations_completed']} improvement cycles")
    print(f"  Final performance: {result['final_performance']:.4f}")
    print(f"  Total improvement: {result['total_improvement']:.4f}")
    print(f"  Improvement rate: {result['improvement_rate']:.4f}")
    
    # Show progress samples
    print("\n--- Improvement Progress (Sample) ---")
    samples = [result['results'][i] for i in [0, 4, 9, 14, 19] if i < len(result['results'])]
    for sample in samples:
        print(f"  Cycle {sample['cycle']:3d}: Performance={sample['performance']:.4f}, "
              f"Improvement={sample['improvement']:+.4f}")
    
    # Get detailed status
    print("\n--- System Status ---")
    status = engine.get_status()
    print(json.dumps(status, indent=2))
    
    print("\n" + "="*70)
    print("Evolution Demonstration Complete")
    print(f"System has achieved {status['cumulative_improvement']:.2f} cumulative improvement")
    print(f"through {status['improvement_cycles']} cycles of evolution")
    print("="*70)


if __name__ == "__main__":
    demonstrate_evolution()
