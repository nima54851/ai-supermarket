#!/bin/bash
set -e

echo "🧪 Starting local dev server (with Workers AI emulation)..."
echo "📍 Visit http://localhost:8787/v1/chat"
echo "Press Ctrl+C to stop."

wrangler dev --local --port 8787
