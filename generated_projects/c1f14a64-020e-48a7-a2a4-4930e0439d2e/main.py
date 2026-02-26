#!/usr/bin/env python3
"""
Main entry point for the Neural Link Orchestration System
Integrates all components: Grok, Trinity, OLK7, and Yur Vault
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.trinity_orchestrator import TrinityOrchestrator
from src.grok_self_healing_agent import GrokSelfHealingAgent
from src.ouroboros_lattice_kernel import OuroborosLatticeKernel
from src.yur_vault_citadel import YurVaultCitadel
from src.multi_kernel_orchestrator import MultiKernelOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neural_link.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NeuralLinkSystem:
    """Main system orchestrator integrating all components"""
    
    def __init__(self):
        self.trinity = None
        self.grok_agent = None
        self.olk7_kernel = None
        self.vault = None
        self.orchestrator = None
        self.running = False
        
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("🚀 Initializing Neural Link System...")
            
            # Initialize Yur Vault Citadel
            self.vault = YurVaultCitadel()
            await self.vault.initialize()
            logger.info("✅ Yur Vault Citadel initialized")
            
            # Initialize Ouroboros Lattice Kernel
            self.olk7_kernel = OuroborosLatticeKernel()
            await self.olk7_kernel.initialize()
            logger.info("✅ OLK7 Kernel initialized")
            
            # Initialize Grok Self-Healing Agent
            self.grok_agent = GrokSelfHealingAgent()
            await self.grok_agent.initialize()
            logger.info("✅ Grok Agent initialized")
            
            # Initialize Trinity Orchestrator
            self.trinity = TrinityOrchestrator()
            await self.trinity.initialize()
            logger.info("✅ Trinity Orchestrator initialized")
            
            # Initialize Multi-Kernel Orchestrator
            self.orchestrator = MultiKernelOrchestrator()
            await self.orchestrator.add_kernel("grok", self.grok_agent)
            await self.orchestrator.add_kernel("olk7", self.olk7_kernel)
            await self.orchestrator.add_kernel("trinity", self.trinity)
            await self.orchestrator.add_kernel("vault", self.vault)
            logger.info("✅ Multi-Kernel Orchestrator initialized")
            
            self.running = True
            logger.info("🌟 Neural Link System fully initialized!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
            
    async def run(self):
        """Main system run loop"""
        if not self.running:
            await self.initialize()
            
        logger.info("🔄 Starting main system loop...")
        
        try:
            # Start all services
            tasks = [
                self.trinity.run(),
                self.grok_agent.run(),
                self.olk7_kernel.run(),
                self.vault.run(),
                self.orchestrator.run(),
                self._health_monitor()
            ]
            
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown signal received")
            await self.shutdown()
        except Exception as e:
            logger.error(f"❌ System error: {e}")
            await self.shutdown()
            raise
            
    async def _health_monitor(self):
        """Monitor system health and auto-heal"""
        while self.running:
            try:
                # Check component health
                health_status = {
                    'trinity': await self.trinity.health_check(),
                    'grok': await self.grok_agent.health_check(),
                    'olk7': await self.olk7_kernel.health_check(),
                    'vault': await self.vault.health_check(),
                }
                
                # Auto-heal if needed
                for component, healthy in health_status.items():
                    if not healthy:
                        logger.warning(f"⚠️  {component} unhealthy, attempting heal...")
                        await self.orchestrator.heal_kernel(component)
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
                
    async def shutdown(self):
        """Graceful system shutdown"""
        logger.info("🔄 Shutting down Neural Link System...")
        self.running = False
        
        if self.orchestrator:
            await self.orchestrator.shutdown()
        if self.trinity:
            await self.trinity.shutdown()
        if self.grok_agent:
            await self.grok_agent.shutdown()
        if self.olk7_kernel:
            await self.olk7_kernel.shutdown()
        if self.vault:
            await self.vault.shutdown()
            
        logger.info("✅ System shutdown complete")

async def main():
    """Main entry point"""
    try:
        system = NeuralLinkSystem()
        await system.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())