"""
Utility functions for the demo application.
"""

import json
import datetime
from typing import Dict, List, Any

def save_data_to_json(data: Dict[str, Any], filename: str = "data.json") -> bool:
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def load_data_from_json(filename: str = "data.json") -> Dict[str, Any]:
    """Load data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return {}
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

def generate_sample_data() -> Dict[str, Any]:
    """Generate sample data for demonstration."""
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "sample_numbers": list(range(1, 11)),
        "sample_text": "This is generated sample data",
        "nested_data": {
            "version": "1.0",
            "features": ["file_io", "data_processing", "json_handling"]
        }
    }

def process_text_data(text: str) -> Dict[str, Any]:
    """Process text and return statistics."""
    words = text.split()
    return {
        "character_count": len(text),
        "word_count": len(words),
        "unique_words": len(set(word.lower().strip('.,!?') for word in words)),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
    }