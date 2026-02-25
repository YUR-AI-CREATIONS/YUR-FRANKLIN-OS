#!/usr/bin/env python3
"""
Advanced IDE with AI Orchestration and Security Framework
"""

import asyncio
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.security.quantum_gate import QuantumSecurityGate
from core.orchestration.trinity_manager import TrinityOrchestrator
from core.ide.main_window import IDEMainWindow
from core.ai.deterministic_agent import DeterministicCodingAgent
from core.container.micro_quarantine import MicroQuarantineManager
from utils.logging_config import setup_logging

class AdvancedIDEApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.logger = setup_logging()
        self.security_gate = QuantumSecurityGate()
        self.trinity_orchestrator = TrinityOrchestrator()
        self.quarantine_manager = MicroQuarantineManager()
        self.coding_agent = DeterministicCodingAgent()
        
    async def initialize_security_framework(self):
        """Initialize 8-gate security protocol"""
        self.logger.info("Initializing quantum security framework...")
        
        gates = [
            'quantum_gate', 'polygram_gate', 'python_rest_gate',
            'qpymc_gate', 'shard_algo_gate', 'blake3_gate',
            'immutable_gate', 'governance_gate'
        ]
        
        for gate in gates:
            result = await self.security_gate.verify_gate(gate)
            if not result:
                raise SecurityError(f"Security gate {gate} failed verification")
        
        self.logger.info("All 8 security gates passed verification")
    
    async def start_ide(self):
        """Start the IDE application"""
        try:
            await self.initialize_security_framework()
            
            # Initialize Trinity orchestration
            await self.trinity_orchestrator.initialize()
            
            # Start micro quarantine containers
            await self.quarantine_manager.initialize_containers()
            
            # Initialize deterministic coding agent
            await self.coding_agent.initialize()
            
            # Create main IDE window
            self.main_window = IDEMainWindow(
                trinity_orchestrator=self.trinity_orchestrator,
                coding_agent=self.coding_agent,
                quarantine_manager=self.quarantine_manager
            )
            
            self.main_window.show()
            self.logger.info("Advanced IDE started successfully")
            
            return self.app.exec_()
            
        except Exception as e:
            self.logger.error(f"Failed to start IDE: {e}")
            return 1

def main():
    """Main entry point"""
    ide_app = AdvancedIDEApplication()
    
    # Run async initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        exit_code = loop.run_until_complete(ide_app.start_ide())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    finally:
        loop.close()

if __name__ == "__main__":
    main()