#!/usr/bin/env python3
"""
Code Location Finder - A utility to help locate code files and projects
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set
import json
import fnmatch

class CodeFinder:
    def __init__(self):
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.less', '.vue', '.svelte', '.r',
            '.m', '.mm', '.pl', '.sh', '.bash', '.zsh', '.ps1', '.sql'
        }
        
        self.ignore_dirs = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules', 
            '.pytest_cache', '.coverage', 'build', 'dist', 'target',
            '.idea', '.vscode', '.vs', 'bin', 'obj', 'logs', 'tmp'
        }
        
        self.project_files = {
            'requirements.txt', 'setup.py', 'pyproject.toml',
            'package.json', 'package-lock.json', 'yarn.lock',
            'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
            'Makefile', 'CMakeLists.txt', 'Dockerfile'
        }

    def find_code_files(self, root_path: str, max_depth: int = 10) -> Dict[str, List[str]]:
        """Find all code files in the given directory"""
        results = {
            'projects': [],
            'code_files': [],
            'statistics': {}
        }
        
        root_path = Path(root_path).resolve()
        
        if not root_path.exists():
            print(f"Error: Path '{root_path}' does not exist")
            return results
            
        # Track file extensions and counts
        ext_counts = {}
        total_files = 0
        
        for current_path in self._walk_directory(root_path, max_depth):
            if current_path.is_file():
                # Check if it's a project file
                if current_path.name in self.project_files:
                    results['projects'].append({
                        'type': self._identify_project_type(current_path.name),
                        'path': str(current_path),
                        'directory': str(current_path.parent)
                    })
                
                # Check if it's a code file
                if current_path.suffix.lower() in self.code_extensions:
                    results['code_files'].append(str(current_path))
                    
                    # Update statistics
                    ext = current_path.suffix.lower()
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1
                    total_files += 1
        
        results['statistics'] = {
            'total_code_files': total_files,
            'extensions': ext_counts,
            'total_projects': len(results['projects'])
        }
        
        return results

    def _walk_directory(self, root_path: Path, max_depth: int):
        """Walk directory with depth limit and ignore common non-code directories"""
        def _walk_recursive(path: Path, current_depth: int):
            if current_depth > max_depth:
                return
                
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        if item.name not in self.ignore_dirs and not item.name.startswith('.'):
                            yield from _walk_recursive(item, current_depth + 1)
                    else:
                        yield item
            except PermissionError:
                print(f"Permission denied: {path}")
            except OSError as e:
                print(f"Error accessing {path}: {e}")
        
        yield from _walk_recursive(root_path, 0)

    def _identify_project_type(self, filename: str) -> str:
        """Identify project type based on project files"""
        project_types = {
            'requirements.txt': 'Python',
            'setup.py': 'Python',
            'pyproject.toml': 'Python',
            'package.json': 'Node.js/JavaScript',
            'package-lock.json': 'Node.js/JavaScript',
            'yarn.lock': 'Node.js/JavaScript',
            'Cargo.toml': 'Rust',
            'go.mod': 'Go',
            'pom.xml': 'Java/Maven',
            'build.gradle': 'Java/Gradle',
            'Makefile': 'C/C++/Make',
            'CMakeLists.txt': 'C/C++/CMake',
            'Dockerfile': 'Docker'
        }
        return project_types.get(filename, 'Unknown')

    def search_by_pattern(self, root_path: str, pattern: str) -> List[str]:
        """Search for files matching a specific pattern"""
        results = []
        root_path = Path(root_path).resolve()
        
        for current_path in self._walk_directory(root_path, 10):
            if current_path.is_file():
                if fnmatch.fnmatch(current_path.name.lower(), pattern.lower()):
                    results.append(str(current_path))
        
        return results

    def find_by_extension(self, root_path: str, extension: str) -> List[str]:
        """Find all files with a specific extension"""
        if not extension.startswith('.'):
            extension = '.' + extension
            
        results = []
        root_path = Path(root_path).resolve()
        
        for current_path in self._walk_directory(root_path, 10):
            if current_path.is_file() and current_path.suffix.lower() == extension.lower():
                results.append(str(current_path))
        
        return results

def format_results(results: Dict, format_type: str = 'table'):
    """Format and display results"""
    if format_type == 'json':
        print(json.dumps(results, indent=2))
        return
    
    # Table format
    print("\n🔍 CODE LOCATION FINDER RESULTS")
    print("=" * 50)
    
    # Statistics
    stats = results['statistics']
    print(f"\n📊 STATISTICS:")
    print(f"  Total code files: {stats['total_code_files']}")
    print(f"  Total projects: {stats['total_projects']}")
    
    if stats['extensions']:
        print(f"\n📁 FILE EXTENSIONS:")
        for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count} files")
    
    # Projects
    if results['projects']:
        print(f"\n🚀 DETECTED PROJECTS:")
        for project in results['projects']:
            print(f"  {project['type']}: {project['directory']}")
    
    # Code files (limited to first 20 for readability)
    if results['code_files']:
        print(f"\n📄 CODE FILES (showing first 20):")
        for file_path in results['code_files'][:20]:
            print(f"  {file_path}")
        
        if len(results['code_files']) > 20:
            print(f"  ... and {len(results['code_files']) - 20} more files")

def main():
    parser = argparse.ArgumentParser(
        description="Find and locate code files in directories",
        epilog="Example: python main.py /path/to/search --pattern '*.py' --format json"
    )
    
    parser.add_argument(
        'path', 
        nargs='?', 
        default='.', 
        help='Path to search for code (default: current directory)'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        help='Search for files matching pattern (e.g., "*.py", "test*")'
    )
    
    parser.add_argument(
        '--extension', '-e',
        help='Search for files with specific extension (e.g., "py", "js")'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['table', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    
    parser.add_argument(
        '--depth', '-d',
        type=int,
        default=10,
        help='Maximum directory depth to search (default: 10)'
    )
    
    args = parser.parse_args()
    
    finder = CodeFinder()
    
    try:
        if args.pattern:
            # Pattern search
            files = finder.search_by_pattern(args.path, args.pattern)
            results = {
                'pattern_results': files,
                'statistics': {'total_matches': len(files)},
                'projects': [],
                'code_files': files
            }
        elif args.extension:
            # Extension search
            files = finder.find_by_extension(args.path, args.extension)
            results = {
                'extension_results': files,
                'statistics': {'total_matches': len(files)},
                'projects': [],
                'code_files': files
            }
        else:
            # Full search
            results = finder.find_code_files(args.path, args.depth)
        
        format_results(results, args.format)
        
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()