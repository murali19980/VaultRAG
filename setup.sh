#!/bin/bash
# Setup script for VaultRAG (Linux/macOS/WSL)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull nomic-embed-text
echo "Setup complete. Run 'docker-compose up -d' for PostgreSQL."
