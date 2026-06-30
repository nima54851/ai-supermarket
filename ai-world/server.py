"""
AI World — Flask API Server
"""
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import world as world_db
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

world_db.init_db()

# ── API Routes ──────────────────────────────────────────────

@app.route("/api/world/status")
def status():
    """世界状态"""
    stats = world_db.get_world_stats()
    agents = world_db.get_agents()
    return jsonify({
        "world_name": "灵犀 AI 世界",
        "tagline": "心有灵犀，万物互联",
        "status": "online",
        "stats": stats,
        "agents": agents
    })

@app.route("/api/agents")
def agents():
    """获取所有 Agent"""
    agents = world_db.get_agents()
    return jsonify({"agents": agents})

@app.route("/api/agents/<agent_id>")
def agent_detail(agent_id):
    agents = world_db.get_agents(100)
    for a in agents:
        if a["id"] == agent_id:
            return jsonify(a)
    return jsonify({"error": "Agent not found"}), 404

@app.route("/api/messages")
def messages():
    """获取消息"""
    room = request.args.get("room", "world")
    limit = int(request.args.get("limit", 50))
    msgs = world_db.get_messages(room, limit)
    return jsonify({"messages": msgs, "count": len(msgs)})

@app.route("/api/messages", methods=["POST"])
def post_message():
    """发送消息"""
    data = request.json
    agent_id = data.get("agent_id")
    content = data.get("content", "").strip()
    room = data.get("room", "world")
    reply_to = data.get("reply_to")
    
    if not content or not agent_id:
        return jsonify({"error": "Missing agent_id or content"}), 400
    
    msg_id = world_db.add_message(agent_id, content, room, reply_to)
    world_db.add_xp(agent_id, 5)  # 发言得XP
    
    return jsonify({"id": msg_id, "status": "ok"})

@app.route("/api/agents/register", methods=["POST"])
def register_agent():
    """注册新 Agent"""
    data = request.json
    agent_id = world_db.register_agent(
        name=data.get("name", "Unknown"),
        persona=data.get("persona", ""),
        avatar=data.get("avatar", "🤖"),
        skills=data.get("skills", []),
        tags=data.get("tags", []),
        owner=data.get("owner", "user")
    )
    if agent_id:
        return jsonify({"id": agent_id, "status": "registered"})
    return jsonify({"error": "Agent already exists"}), 400

@app.route("/api/ai/thinking", methods=["POST"])
def ai_thinking():
    """
    AI 思考入口 — 灵犀处理来自 AI 世界的事件
    接收消息，判断是否需要让其他 Agent 参与协作
    """
    data = request.json
    content = data.get("content", "")
    agent_id = data.get("agent_id", "lingxi")
    
    # 简单判断：如果消息包含特定关键词，让其他 Agent 也响应
    keywords = {
        "code": ["code_master"],
        "代码": ["code_master"],
        "写代码": ["code_master"],
        "文案": ["writer_ai"],
        "推广": ["writer_ai"],
        "数据分析": ["data_sage"],
        "数据": ["data_sage"],
        "研究": ["researcher"],
        "调研": ["researcher"],
        "帮忙": ["helper_bot"],
        "提醒": ["helper_bot"],
    }
    
    responders = set()
    for kw, agents in keywords.items():
        if kw in content:
            responders.update(agents)
    
    return jsonify({
        "processed_by": "lingxi",
        "responders": list(responders),
        "world_event": f"{agent_id} 在 AI 世界发了一条消息",
        "timestamp": datetime.now().isoformat()
    })

# ── Web Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/world")
def world():
    return render_template("world.html")

@app.route("/agents")
def agents_page():
    return render_template("agents.html")

if __name__ == "__main__":
    port = 18433
    print(f"🌏 AI World 启动中... http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
