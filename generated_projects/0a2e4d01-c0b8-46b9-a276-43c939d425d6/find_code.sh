#!/bin/bash
# Quick script to find code files using common patterns

echo "🔍 Where is the code? - Quick Code Finder"
echo "========================================"

# Set search directory (default to current directory)
SEARCH_DIR="${1:-.}"

echo "Searching in: $SEARCH_DIR"
echo

# Find Python files
echo "🐍 Python files:"
find "$SEARCH_DIR" -name "*.py" -type f 2>/dev/null | head -10
echo

# Find JavaScript/TypeScript files
echo "🟨 JavaScript/TypeScript files:"
find "$SEARCH_DIR" \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \) -type f 2>/dev/null | head -10
echo

# Find configuration files
echo "⚙️  Configuration files:"
find "$SEARCH_DIR" \( -name "package.json" -o -name "requirements.txt" -o -name "Dockerfile" -o -name "docker-compose.yml" \) -type f 2>/dev/null
echo

# Find common project directories
echo "📁 Project directories:"
find "$SEARCH_DIR" -type d \( -name "src" -o -name "lib" -o -name "app" -o -name "components" \) 2>/dev/null | head -10

echo
echo "💡 For more detailed analysis, run: python main.py $SEARCH_DIR"