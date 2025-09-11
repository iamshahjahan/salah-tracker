#!/bin/bash

# Install Git hooks for Salah Tracker
# This script sets up pre-commit and pre-push hooks for code quality

echo "🔧 Installing Git Hooks for Salah Tracker..."
echo "=============================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from the root of the git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy hooks
echo "📋 Installing pre-commit hook..."
cp .git/hooks/pre-commit .git/hooks/pre-commit.backup 2>/dev/null || true
chmod +x .git/hooks/pre-commit

echo "📋 Installing pre-push hook..."
cp .git/hooks/pre-push .git/hooks/pre-push.backup 2>/dev/null || true
chmod +x .git/hooks/pre-push

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "📝 What these hooks do:"
echo "   • Pre-commit: Checks for large files, sensitive data, syntax errors"
echo "   • Pre-push: Runs comprehensive tests before pushing to remote"
echo ""
echo "💡 To bypass hooks (not recommended):"
echo "   • git commit --no-verify"
echo "   • git push --no-verify"
echo ""
echo "🧪 To test hooks manually:"
echo "   • .git/hooks/pre-commit"
echo "   • .git/hooks/pre-push"
echo ""
echo "🎉 Your repository is now protected with automated quality checks!"
