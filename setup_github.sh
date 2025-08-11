#!/bin/bash

# Setup script for publishing to GitHub

echo "🚀 Setting up ChatGPT to Markdown for GitHub..."

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ChatGPT to Markdown exporter

Features:
- Export ChatGPT conversations from share URLs
- Generate AI-powered insights and tags
- Multiple output formats (standard, Obsidian, blog)
- Configuration file support
- Bilingual documentation (EN/JA)"

# Add remote (you'll need to create the repo on GitHub first)
echo ""
echo "📦 Next steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "   - Name: chatgpt-to-markdown"
echo "   - Description: Export ChatGPT conversations as beautiful markdown files"
echo "   - Public repository"
echo ""
echo "2. Run these commands:"
echo "   git remote add origin https://github.com/snufkin0866/chatgpt-to-markdown.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Add topics on GitHub: chatgpt, markdown, export, obsidian, conversation, ai"