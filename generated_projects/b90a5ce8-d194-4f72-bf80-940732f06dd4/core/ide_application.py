"""
Main IDE Application with Multi-Modal Interface
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QSplitter, QTabWidget, QTextEdit, QTreeView,
    QStatusBar, QMenuBar, QToolBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from .ui.liquid_wireframe import LiquidWireframe
from .ui.galactic_background import GalacticBackground
from .ui.drag_drop_handler import DragDropHandler
from .editors.code_editor import CodeEditor
from .editors.image_editor import ImageEditor
from .editors.video_editor import VideoEditor
from .terminals.multi_terminal import MultiTerminal
from .coding_agent.deterministic_agent import DeterministicCodingAgent
from .file_manager import FileManager
from .cloud_connectors import CloudConnectorManager

class IDEApplication(QMainWindow):
    def __init__(self, security_manager, orchestration_manager):
        super().__init__()
        self.security_manager = security_manager
        self.orchestration_manager = orchestration_manager
        self.app = QApplication.instance() or QApplication([])
        
        self.init_ui()
        self.init_components()
        
    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("Advanced Multi-Modal IDE")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Set dark theme with galactic styling
        self.setup_galactic_theme()
        
        # Create central widget with liquid wireframe
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Initialize galactic background
        self.galactic_bg = GalacticBackground()
        
        # Create liquid wireframe layout
        self.liquid_wireframe = LiquidWireframe()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.liquid_wireframe)
        
        # Setup drag and drop
        self.drag_drop_handler = DragDropHandler(max_size_mb=500)
        self.setAcceptDrops(True)
        
    def init_components(self):
        """Initialize all IDE components"""
        # File manager
        self.file_manager = FileManager()
        
        # Code editor with multi-language support
        self.code_editor = CodeEditor()
        
        # Image editor
        self.image_editor = ImageEditor()
        
        # Video editor
        self.video_editor = VideoEditor()
        
        # Multi-terminal
        self.multi_terminal = MultiTerminal()
        
        # Coding agent
        self.coding_agent = DeterministicCodingAgent()
        
        # Cloud connectors
        self.cloud_connectors = CloudConnectorManager()
        
        # Add components to wireframe
        self.liquid_wireframe.add_panel("file_manager", self.file_manager)
        self.liquid_wireframe.add_panel("code_editor", self.code_editor)
        self.liquid_wireframe.add_panel("image_editor", self.image_editor)
        self.liquid_wireframe.add_panel("video_editor", self.video_editor)
        self.liquid_wireframe.add_panel("terminals", self.multi_terminal)
        
    def setup_galactic_theme(self):
        """Setup the galactic dark theme"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 35))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 200, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 45))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 55))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 65))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(200, 200, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        self.app.setPalette(palette)
        
    async def run(self):
        """Run the IDE application"""
        self.show()
        
        # Start background services
        await self.orchestration_manager.start_services()
        await self.coding_agent.initialize()
        
        # Start event loop
        self.app.exec()

    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        self.drag_drop_handler.handle_drag_enter(event)
        
    def dropEvent(self, event):
        """Handle drop events"""
        files = self.drag_drop_handler.handle_drop(event)
        for file_path in files:
            self.open_file(file_path)
    
    def open_file(self, file_path: str):
        """Open file in appropriate editor"""
        path = Path(file_path)
        
        if path.suffix.lower() in ['.py', '.js', '.cpp', '.java', '.go', '.rs']:
            self.code_editor.open_file(file_path)
        elif path.suffix.lower() in ['.jpg', '.png', '.gif', '.bmp']:
            self.image_editor.open_file(file_path)
        elif path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
            self.video_editor.open_file(file_path)