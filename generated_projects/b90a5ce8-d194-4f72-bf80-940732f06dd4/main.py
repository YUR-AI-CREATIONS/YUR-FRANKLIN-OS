#!/usr/bin/env python3
"""
Advanced IDE with OLK-7 Integration and Multi-Modal Capabilities
"""

import asyncio
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from core.ide_application import IDEApplication
from core.security_manager import SecurityManager
from core.orchestration_manager import OrchestrationManager

async def main():
    """Main application entry point"""
    try:
        # Initialize security protocols
        security_manager = SecurityManager()
        await security_manager.initialize_eight_gate_protocol()
        
        # Initialize orchestration
        orchestration_manager = OrchestrationManager()
        await orchestration_manager.initialize()
        
        # Start IDE application
        ide = IDEApplication(security_manager, orchestration_manager)
        await ide.run()
        
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())