#!/bin/bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate it
# Mac/Linux
source venv/bin/activate

# Windows
# .\venv\Scripts\activate.bat

# 3. Install your packages inside the venv
pip install livekit-agents livekit-plugins-assemblyai livekit-plugins-openai livekit-plugins-silero python-dotenv "pydantic-ai-slim[openai,mcp]"

# 4. Run your agent
python agent.py dev