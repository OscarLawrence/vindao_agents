# stdlib
import json
from os import getenv
from pathlib import Path

# third-party
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# local
from vindao_agents import Agent
from vindao_agents.loaders import load_agent_from_markdown

USER_DATA_DIR = getenv("USER_DATA_DIR", Path.cwd() / ".vindao_agents")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sessions")
async def get_all_sessions():
    sessions_path = Path(USER_DATA_DIR) / "sessions"
    sessions = {}
    print(sessions_path)
    for file in sessions_path.iterdir():
        print(file.suffix)
        if file.suffix == ".json":
            with open(file) as f:
                sessions[file.stem] = json.load(f)
    return sessions


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    session_path = Path(USER_DATA_DIR) / "sessions" / f"{session_id}.json"
    if not session_path.exists():
        return {"error": "Session not found"}
    with open(session_path) as f:
        session_data = json.load(f)
    return session_data


@app.get("/agents")
async def get_agents():
    agents_path = Path(USER_DATA_DIR) / "agents"
    agents = {}
    for file in agents_path.iterdir():
        if file.suffix == ".md":
            agents[file.stem] = load_agent_from_markdown(file)
    return {"agents": agents}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        agent = Agent.from_json(data)
        for chunk, chunk_type in agent.invoke():
            if chunk_type == "content":
                await websocket.send_json({"type": "content", "data": chunk})
            elif chunk_type == "tool":
                await websocket.send_json({"type": "tool", "data": chunk.result})
