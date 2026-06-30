/**
 * 灵犀 A2A 平台 — 主服务器 (JSON 数据库版)
 */
const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const jwt = require('jsonwebtoken');

const { db, genId, now, hashPassword, initDB } = require('./db');

const app = express();
const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'lingxi-a2a-secret-2026';
const JWT_EXP = '30d';

// ── 中间件 ─────────────────────────────────────────
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors({ origin: '*', methods: ['GET', 'POST', 'DELETE', 'PUT'] }));
app.use(express.json({ limit: '2mb' }));

const apiLimiter = rateLimit({ windowMs: 60 * 1000, max: 300, message: { error: '请求过于频繁' } });
app.use('/api/', apiLimiter);

// ── 初始化数据库 ────────────────────────────────────
initDB();

// ── 辅助 ───────────────────────────────────────────
const unauthorized = (res) => res.status(401).json({ error: '未授权' });
const forbidden = (res) => res.status(403).json({ error: '权限不足' });
const notFound = (res) => res.status(404).json({ error: '资源不存在' });
const badRequest = (res, msg) => res.status(400).json({ error: msg });

function authApiKey(req, res, next) {
  const key = req.headers['x-api-key'] || req.query.api_key;
  if (!key) return unauthorized(res);
  const user = db.getUserByApiKey(key);
  if (!user) return unauthorized(res);
  req.user = user; next();
}

function authBearer(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) return unauthorized(res);
  try {
    req.user = jwt.verify(auth.slice(7), JWT_SECRET);
    next();
  } catch { unauthorized(res); }
}

function adminOnly(req, res, next) {
  if (!req.user || req.user.role !== 'admin') return forbidden(res);
  next();
}

// ── 公开 API ───────────────────────────────────────

// 平台统计
app.get('/api/stats', (req, res) => {
  const s = db.getStats();
  res.json(s);
});

// 能力市场列表
app.get('/api/marketplace', (req, res) => {
  const { category, search, sort, page = 1, limit = 12 } = req.query;
  const caps = db.getCapabilities({ status: 'active' });
  const agents = db.getAgents({ status: 'active' });
  const reviews = {};

  let items = caps
    .filter(c => {
      if (category && category !== 'all' && c.category !== category) return false;
      if (search) {
        const s = search.toLowerCase();
        const agent = agents.find(a => a.id === c.agent_id);
        if (!c.name?.toLowerCase().includes(s) && !c.description?.toLowerCase().includes(s) && !agent?.name?.toLowerCase().includes(s)) return false;
      }
      return true;
    })
    .map(c => {
      const agent = agents.find(a => a.id === c.agent_id) || {};
      const capReviews = db.getReviews(c.id);
      const capCalls = db.getAllCalls().items.filter(x => x.capability_id === c.id);
      const avgRating = capReviews.length ? capReviews.reduce((s,r) => s+r.rating, 0) / capReviews.length : 0;
      return {
        ...c,
        agent_name: agent.name || '未知',
        agent_avatar: agent.avatar || '',
        agent_desc: agent.description || '',
        avg_rating: avgRating,
        review_count: capReviews.length,
        call_count: capCalls.filter(c=>c.status==='success').length
      };
    });

  if (sort === 'price_desc') items.sort((a,b) => b.price_per_call - a.price_per_call);
  else if (sort === 'popular') items.sort((a,b) => b.call_count - a.call_count);
  else items.sort((a,b) => a.price_per_call - b.price_per_call);

  const total = items.length;
  const offset = (page - 1) * limit;
  res.json({ items: items.slice(offset, offset + Number(limit)), total, page: Number(page), pages: Math.ceil(total / limit) });
});

// Agent 详情
app.get('/api/agents/:id', (req, res) => {
  const agent = db.getAgent(req.params.id);
  if (!agent || agent.status !== 'active') return notFound(res);
  const caps = db.getCapabilities({ agent_id: agent.id, status: 'active' });
  const reviews = db.getReviews(agent.id).map(r => {
    const user = db.getUserById(r.user_id);
    return { ...r, username: user?.username || '匿名' };
  });
  res.json({ agent, capabilities: caps, reviews });
});

// 能力详情
app.get('/api/capabilities/:id', (req, res) => {
  const cap = db.getCapability(req.params.id);
  if (!cap || cap.status !== 'active') return notFound(res);
  const agent = db.getAgent(cap.agent_id) || {};
  res.json({ ...cap, agent_name: agent.name || '', agent_avatar: agent.avatar || '', agent_status: agent.status || '' });
});

// ── 认证 ───────────────────────────────────────────

app.post('/api/auth/register', (req, res) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password) return badRequest(res, '缺少必填字段');
  if (password.length < 6) return badRequest(res, '密码至少6位');
  if (db.findUser({ email })) return badRequest(res, '邮箱已存在');
  if (db.findUser({ username })) return badRequest(res, '用户名已存在');

  const id = genId();
  const apiKey = 'sk_a2a_' + genId().replace(/-/g,'');
  const user = { id, username, email, password: hashPassword(password), role: 'user', balance: 100, api_key: apiKey, created_at: now() };
  db.createUser(user);

  const token = jwt.sign({ id, username, email, role: 'user', balance: 100 }, JWT_SECRET, { expiresIn: JWT_EXP });
  res.json({ token, api_key: apiKey, balance: 100 });
});

app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = db.findUser({ email });
  if (!user || user.password !== hashPassword(password)) return badRequest(res, '邮箱或密码错误');
  const token = jwt.sign({ id: user.id, username: user.username, email: user.email, role: user.role, balance: user.balance }, JWT_SECRET, { expiresIn: JWT_EXP });
  res.json({ token, api_key: user.api_key, balance: user.balance });
});

// ── 用户 API ───────────────────────────────────────

app.get('/api/user/balance', authBearer, (req, res) => {
  const user = db.getUserById(req.user.id);
  res.json({ balance: user?.balance ?? 0 });
});

app.get('/api/user/calls', authBearer, (req, res) => {
  const { page = 1, limit = 20 } = req.query;
  const result = db.getCalls({ caller_id: req.user.id }, { page: Number(page), limit: Number(limit) });
  res.json(result);
});

app.post('/api/user/topup', authBearer, (req, res) => {
  const { amount = 100 } = req.body;
  if (amount <= 0) return badRequest(res, '金额必须大于0');
  const topupId = genId();
  db.createTopup({ id: topupId, user_id: req.user.id, amount: Number(amount), method: 'manual', status: 'completed', created_at: now() });
  db.updateUser(req.user.id, { balance: (db.getUserById(req.user.id)?.balance || 0) + Number(amount) });
  const user = db.getUserById(req.user.id);
  res.json({ success: true, amount: Number(amount), balance: user.balance, topup_id: topupId });
});

// ── A2A 核心：调用能力 ─────────────────────────────
app.post('/api/a2a/call', authBearer, async (req, res) => {
  const { capability_id, params = {} } = req.body;
  if (!capability_id) return badRequest(res, '缺少 capability_id');

  const cap = db.getCapability(capability_id);
  if (!cap || cap.status !== 'active') return notFound(res);
  const agent = db.getAgent(cap.agent_id) || {};
  if (agent.status !== 'active') return notFound(res);

  const caller = db.getUserById(req.user.id);
  if ((caller?.balance || 0) < cap.price_per_call) {
    return res.status(402).json({ error: '余额不足，请先充值', balance: caller?.balance || 0, required: cap.price_per_call });
  }

  const callId = genId();
  const startTime = Date.now();

  // 扣款
  db.updateUser(req.user.id, { balance: (caller.balance || 0) - cap.price_per_call });

  db.createCall({
    id: callId, caller_id: req.user.id, agent_id: cap.agent_id,
    capability_id: cap.id, input: JSON.stringify(params), output: '',
    status: 'pending', cost: cap.price_per_call, duration_ms: 0, created_at: now()
  });

  // 执行（通过 OpenClaw MCP 路由）
  let output = {};
  try {
    output = await routeToAgent(cap, params, req.user);
  } catch (e) {
    output = { error: e.message || '执行失败' };
  }

  const duration = Date.now() - startTime;
  const success = !output.error;
  db.updateCall(callId, { output: JSON.stringify(output), status: success ? 'success' : 'failed', duration_ms: duration });

  if (!success) {
    // 失败退款
    const caller2 = db.getUserById(req.user.id);
    db.updateUser(req.user.id, { balance: (caller2.balance || 0) + cap.price_per_call });
  } else {
    // Agent 所有者入账（平台抽20%）
    const agentOwner = db.getUserById(agent.owner_id);
    if (agentOwner) {
      db.updateUser(agent.owner_id, { balance: (agentOwner.balance || 0) + cap.price_per_call * 0.8 });
    }
  }

  const callerFinal = db.getUserById(req.user.id);
  res.json({
    call_id: callId, capability: cap.name,
    cost: success ? cap.price_per_call : 0,
    duration_ms: duration, result: output,
    remaining_balance: callerFinal?.balance || 0
  });
});

/**
 * 路由到实际 Agent 执行
 * 预留 OpenClaw MCP 调用接口
 */
async function routeToAgent(capability, params, caller) {
  const { name } = capability;

  // ── 灵犀真实执行 ────────────────────────────────
  // 这里通过子进程调用 OpenClaw CLI 或直接路由
  // 暂时返回模拟结果，后续接入 OpenClaw MCP
  const results = {
    'code_review': () => ({
      review_comment: `🔍 **AI 代码审查报告**\n\n**安全性**: ✅ 通过\n**逻辑**: ⚠️ 建议检查边界条件\n**风格**: ✅ 符合最佳实践\n**性能**: ✅ 无明显问题\n\n**综合评分**: ${(8 + Math.random()*2).toFixed(1)}/10`,
      score: Number((8 + Math.random()*2).toFixed(1)),
      issues: [{ line: Math.floor(Math.random()*100)+1, severity: 'warning', message: '建议添加参数校验' }],
      reviewed_by: '灵犀', model: 'claude-opus-4'
    }),

    'github_automation': () => ({
      success: true, action: params.action, repo: params.repo_url,
      message: `✅ 已完成 ${params.action} 操作`,
      timestamp: new Date().toISOString()
    }),

    'n8n_workflow': () => ({
      workflow_json: {
        name: 'AI 生成工作流',
        nodes: [
          { name: 'Webhook', type: 'n8n-nodes-base.webhook', position: [250, 300] },
          { name: 'AI Agent', type: 'n8n-nodes-base.agent', position: [500, 300] },
          { name: 'Response', type: 'n8n-nodes-base.response', position: [750, 300] }
        ],
        connections: {}
      },
      template_name: (params.workflow_description || '自定义').slice(0, 20)
    }),

    'web_scraping': () => ({
      data: [
        Object.fromEntries((params.fields || ['title','url']).map((f,i) => [f, `数据${i+1}`])),
        Object.fromEntries((params.fields || ['title','url']).map((f,i) => [f, params.url || 'https://example.com']))
      ],
      count: 2, format: params.format || 'json',
      message: `✅ 从 ${params.url} 提取成功`
    }),

    'ai_search': () => ({
      answer: `根据搜索结果，灵犀 AI Agent 可以帮助您完成多种任务。核心结论：通过自动化工作流和 AI 能力调用，可显著提升效率。`,
      sources: [
        { title: 'GitHub Trending', url: 'https://github.com/trending', relevance: 0.95 },
        { title: 'Hacker News', url: 'https://news.ycombinator.com', relevance: 0.88 }
      ],
      confidence: 0.87
    }),

    'data_analysis': () => ({
      analysis: '数据分析完成，数据集包含多种维度，发现若干有价值的数据模式。',
      insights: [
        { metric: '数据总量', value: `${(Math.random()*10000+500).toFixed(0)} 条` },
        { metric: '平均增长率', value: `${(Math.random()*30+5).toFixed(1)}%` },
        { metric: '峰值分布', value: `${Math.floor(Math.random()*10+1)}:00 - ${Math.floor(Math.random()*10+12)}:00` }
      ],
      charts: ['折线图', '柱状图', '饼图']
    }),

    'text_processing': () => {
      if (params.task === 'summarize') return { result: '文本摘要：核心观点是...（内容已压缩）', word_count: Math.floor(Math.random()*500+100) };
      if (params.task === 'classify') return { result: '分类结果：技术类 / 开发相关', confidence: 0.92 };
      if (params.task === 'followups') return { result: '追问建议：1. 这个方法有什么局限？2. 能否扩展到其他场景？3. 有哪些替代方案？', questions: 3 };
      return { result: '处理完成' };
    }
  };

  const handler = results[name];
  if (!handler) return { error: `不支持的能力: ${name}` };

  // 模拟处理时间
  await new Promise(r => setTimeout(r, Math.random() * 800 + 200));
  return handler();
}

// ── 发布 Agent ─────────────────────────────────────
app.post('/api/agents', authBearer, (req, res) => {
  const { name, description, capabilities = [] } = req.body;
  if (!name) return badRequest(res, '缺少 Agent 名称');

  const agentId = genId();
  db.createAgent({ id: agentId, name, description: description || '', avatar: '', owner_id: req.user.id, status: 'active', created_at: now(), updated_at: now() });
  capabilities.forEach(c => {
    db.createCapability({ id: genId(), agent_id: agentId, name: c.name, description: c.description || '', category: c.category || 'general', params: c.params || [], returns: {}, status: 'active', price_per_call: c.price_per_call || 0.01, created_at: now() });
  });
  res.json({ agent_id: agentId, message: 'Agent 发布成功' });
});

// ── 评分 ───────────────────────────────────────────
app.post('/api/reviews', authBearer, (req, res) => {
  const { agent_id, rating, comment } = req.body;
  if (!agent_id || !rating) return badRequest(res, '缺少必填字段');
  if (rating < 1 || rating > 5) return badRequest(res, '评分1-5');
  db.createReview({ id: genId(), agent_id, user_id: req.user.id, rating, comment: comment || '', created_at: now() });
  res.json({ success: true });
});

// ── 管理员 API ─────────────────────────────────────
app.get('/api/admin/users', authBearer, adminOnly, (req, res) => {
  const users = db.getAllUsers().map(u => ({ ...u, password: undefined }));
  res.json({ items: users, total: users.length });
});

app.get('/api/admin/calls', authBearer, adminOnly, (req, res) => {
  const { page = 1, limit = 50 } = req.query;
  const result = db.getAllCalls({ page: Number(page), limit: Number(limit) });
  res.json(result);
});

app.get('/api/agents', (req, res) => {
  const agents = db.getAgents({ status: 'active' });
  res.json({ items: agents });
});

app.put('/api/admin/capabilities/:id', authBearer, adminOnly, (req, res) => {
  const { price_per_call } = req.body;
  db.updateCapability(req.params.id, { price_per_call: Number(price_per_call) });
  res.json({ success: true });
});

app.put('/api/admin/agents/:id', authBearer, adminOnly, (req, res) => {
  const { status } = req.body;
  if (!['active','inactive','suspended'].includes(status)) return badRequest(res, '无效状态');
  db.updateAgent(req.params.id, { status, updated_at: now() });
  res.json({ success: true });
});

// ── 健康检查 ───────────────────────────────────────
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', uptime: Math.floor(process.uptime()), timestamp: now() });
});

// ── 静态文件 ───────────────────────────────────────
app.use(express.static(path.join(__dirname, '../frontend'), { index: 'index.html' }));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

// ── 启动 ───────────────────────────────────────────
app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n╔══════════════════════════════════════════╗`);
  console.log(`║   灵犀 A2A 能力市场  v1.0.0              ║`);
  console.log(`╠══════════════════════════════════════════╣`);
  console.log(`║  🌐 前台:  http://localhost:${PORT}          ║`);
  console.log(`║  📊 API:   http://localhost:${PORT}/api     ║`);
  console.log(`╚══════════════════════════════════════════╝`);
  console.log(`  管理员: admin@a2a.local / admin123`);
  console.log(`  数据库: ${path.join(__dirname, '../data/a2a.json')}\n`);
});

module.exports = app;
