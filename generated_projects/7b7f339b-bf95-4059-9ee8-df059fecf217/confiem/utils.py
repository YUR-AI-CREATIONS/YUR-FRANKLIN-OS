"""
Utility functions for confiem
"""

import os
import sys
from typing import Optional


def is_interactive() -> bool:
    """Check if running in interactive mode"""
    return sys.stdin.isatty() and sys.stdout.isatty()


def get_terminal_width() -> int:
    """Get terminal width, default to 80 if unavailable"""
    try:
        return os.get_terminal_size().columns
    except (OSError, AttributeError):
        return 80


def format_message(message: str, width: Optional[int] = None) -> str:
    """Format message to fit terminal width"""
    if width is None:
        width = get_terminal_width()
    
    if len(message) <= width:
        return message
    
    # Simple word wrapping
    words = message.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def clear_line():
    """Clear the current terminal line"""
    if is_interactive():
        print('\r' + ' ' * get_terminal_width() + '\r', end='')