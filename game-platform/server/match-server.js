/**
 * game-platform 配对服务器
 * WebSocket 游戏对战匹配服务
 * 
 * 启动: node match-server.js
 * 端口可通过 PORT 环境变量配置 (默认 8080)
 */

const { WebSocketServer, WebSocket } = require('ws');
const http = require('http');

const PORT = process.env.PORT || 8080;

// ─────────────────────────────────────────────
// 房间管理
// ─────────────────────────────────────────────

const rooms = new Map(); // roomCode → Room

const ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // 排除易混淆字符 I,O,0,1

function generateRoomCode() {
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += ALPHABET[Math.floor(Math.random() * ALPHABET.length)];
  }
  return code;
}

function createRoom(code) {
  return {
    code,
    players: [],         // [{ ws, playerId, nickname }]
    started: false,
    createdAt: Date.now(),
  };
}

function findAvailableSlot(room) {
  if (room.players.length >= 2) return null;
  return room.players.length; // 0 = slot1, 1 = slot2
}

// ─────────────────────────────────────────────
// WebSocket 辅助
// ─────────────────────────────────────────────

function send(ws, obj) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(obj));
  }
}

function broadcast(room, obj, excludeWs = null) {
  room.players.forEach(p => {
    if (p.ws !== excludeWs) send(p.ws, obj);
  });
}

function sendTo(ws, type, data = {}) {
  send(ws, { type, ...data });
}

// ─────────────────────────────────────────────
// 连接处理
// ─────────────────────────────────────────────

// 每个 ws 保存元数据
const wsMeta = new WeakMap();

function onConnection(ws, req) {
  // 分配临时ID（连接后收到 join 消息才确定真实 playerId）
  const connId = `conn_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  wsMeta.set(ws, { connId, roomCode: null, playerId: null });

  console.log(`[+] 连接: ${connId}`);

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      sendTo(ws, 'error', { message: '无效的 JSON 格式' });
      return;
    }
    handleMessage(ws, msg);
  });

  ws.on('close', () => onDisconnect(ws));
  ws.on('error', (err) => {
    console.error(`[!] ws error ${connId}:`, err.message);
    onDisconnect(ws);
  });

  ws.on('pong', () => {
    const meta = wsMeta.get(ws);
    if (meta) meta.lastPong = Date.now();
  });
}

function onDisconnect(ws) {
  const meta = wsMeta.get(ws);
  if (!meta) return;

  const { connId, roomCode, playerId } = meta;
  console.log(`[-] 断开: ${connId} (room=${roomCode}, player=${playerId})`);

  if (roomCode && playerId) {
    const room = rooms.get(roomCode);
    if (room) {
      // 通知对方
      broadcast(room, { type: 'opponent_disconnect' }, ws);
      // 移除玩家
      room.players = room.players.filter(p => p.ws !== ws);

      if (room.players.length === 0) {
        // 无玩家了，销毁房间
        rooms.delete(roomCode);
        console.log(`[×] 房间 ${roomCode} 已销毁`);
      } else if (room.started) {
        // 游戏已开始但有人退出 → 通知仍在房间的人
        broadcast(room, { type: 'opponent_disconnect' });
      }
    }
  }

  wsMeta.delete(ws);
}

// ─────────────────────────────────────────────
// 消息路由
// ─────────────────────────────────────────────

function handleMessage(ws, msg) {
  const meta = wsMeta.get(ws);
  if (!meta) return;

  switch (msg.type) {
    case 'join':
      handleJoin(ws, msg);
      break;
    case 'move':
    case 'shoot':
    case 'sync':
      handleGameAction(ws, msg);
      break;
    case 'pong':
      // 客户端响应 ping
      break;
    default:
      sendTo(ws, 'error', { message: `未知消息类型: ${msg.type}` });
  }
}

// ─────────────────────────────────────────────
// join 处理
// ─────────────────────────────────────────────

function handleJoin(ws, msg) {
  const { roomCode, playerId, nickname } = msg;

  if (!roomCode || typeof roomCode !== 'string') {
    return sendTo(ws, 'error', { message: '缺少 roomCode' });
  }
  if (!playerId || typeof playerId !== 'string') {
    return sendTo(ws, 'error', { message: '缺少 playerId' });
  }

  const code = roomCode.toUpperCase().trim();

  let room = rooms.get(code);

  // 房间不存在 → 创建并加入（第一个玩家）
  if (!room) {
    room = createRoom(code);
    rooms.set(code, room);
    console.log(`[+] 创建房间: ${code}`);
  }

  // 房间已满
  if (room.players.length >= 2) {
    return sendTo(ws, 'error', { message: '房间已满' });
  }

  // 防止同一玩家重复加入
  if (room.players.some(p => p.playerId === playerId)) {
    return sendTo(ws, 'error', { message: '该 playerId 已在房间中' });
  }

  const slot = room.players.length; // 0 或 1
  const playerEntry = { ws, playerId, nickname: nickname || playerId };
  room.players.push(playerEntry);

  // 更新元数据
  const meta = wsMeta.get(ws);
  meta.roomCode = code;
  meta.playerId = playerId;

  console.log(`[>] 玩家 ${playerId} (${nickname || playerId}) 加入房间 ${code} [slot ${slot}]`);

  if (room.players.length === 2) {
    // 两人齐了，通知双方
    room.started = true;
    const playerList = room.players.map(p => ({
      playerId: p.playerId,
      nickname: p.nickname,
      slot: room.players.indexOf(p),
    }));

    room.players.forEach(p => {
      sendTo(p.ws, 'start', { players: playerList });
    });
    console.log(`[!] 房间 ${code} 游戏开始！`);
  } else {
    // 只有一人，等待
    sendTo(ws, 'joined', {
      playerId,
      players: room.players.map(p => ({
        playerId: p.playerId,
        nickname: p.nickname,
        slot: room.players.indexOf(p),
      })),
    });
  }
}

// ─────────────────────────────────────────────
// 游戏动作转发
// ─────────────────────────────────────────────

function handleGameAction(ws, msg) {
  const meta = wsMeta.get(ws);
  if (!meta || !meta.roomCode) {
    return sendTo(ws, 'error', { message: '未加入房间' });
  }

  const room = rooms.get(meta.roomCode);
  if (!room) {
    return sendTo(ws, 'error', { message: '房间不存在' });
  }
  if (!room.started) {
    return sendTo(ws, 'error', { message: '等待对手中，暂不可操作' });
  }

  const msgMap = {
    move:     'opponent_move',
    shoot:    'opponent_shoot',
    sync:     'opponent_sync',
  };

  const outType = msgMap[msg.type];
  if (!outType) return;

  // 转发给房间内其他玩家（附加发送者 playerId）
  broadcast(room, { type: outType, ...msg, fromPlayerId: meta.playerId }, ws);
}

// ─────────────────────────────────────────────
// 心跳保活
// ─────────────────────────────────────────────

const PING_INTERVAL  = 15000; // 服务端每 15s ping
const PONG_TIMEOUT    = 60000; // 60s 无 pong 判为断开

function startHeartbeat() {
  setInterval(() => {
    const now = Date.now();
    wss.clients.forEach(ws => {
      const meta = wsMeta.get(ws);
      if (!meta) return;

      // 跳过未加入房间的连接
      if (!meta.roomCode) return;

      // 检查 pong 超时
      if (meta.lastPong && now - meta.lastPong > PONG_TIMEOUT) {
        console.warn(`[!] 心跳超时，强制断开 ${meta.connId}`);
        ws.terminate();
        return;
      }

      if (ws.readyState === WebSocket.OPEN) {
        ws.ping();
      }
    });
  }, PING_INTERVAL);
}

// ─────────────────────────────────────────────
// HTTP 服务器（健康检查 + 生成配对码）
// ─────────────────────────────────────────────

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'ok', rooms: rooms.size, clients: wss.clients.size }));
    return;
  }

  if (url.pathname === '/new-room') {
    // 生成新房间码（自动加入空房间）
    let code;
    do {
      code = generateRoomCode();
    } while (rooms.has(code));
    res.writeHead(200);
    res.end(JSON.stringify({ roomCode: code }));
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'not found' }));
});

// ─────────────────────────────────────────────
// 启动
// ─────────────────────────────────────────────

const wss = new WebSocketServer({ server });

wss.on('connection', onConnection);

server.listen(PORT, () => {
  console.log(`🎮 配对服务器已启动`);
  console.log(`   WebSocket: ws://localhost:${PORT}`);
  console.log(`   健康检查:  http://localhost:${PORT}/health`);
  console.log(`   生成房间码: http://localhost:${PORT}/new-room`);
});

startHeartbeat();

// ─────────────────────────────────────────────
// 优雅退出
// ─────────────────────────────────────────────

process.on('SIGTERM', () => {
  console.log('\n[×] 收到 SIGTERM，关闭服务器...');
  wss.clients.forEach(ws => ws.terminate());
  server.close(() => {
    console.log('[×] 服务器已关闭');
    process.exit(0);
  });
});
