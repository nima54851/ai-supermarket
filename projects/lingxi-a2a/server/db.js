const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DB_PATH = path.join(__dirname, '../data/a2a.json');

function ensureDB() {
  const dir = path.dirname(DB_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(DB_PATH)) {
    const init = { users: {}, agents: {}, capabilities: {}, calls: {}, topups: {}, reviews: {}, _meta: { version: '1.0', created: new Date().toISOString() } };
    fs.writeFileSync(DB_PATH, JSON.stringify(init, null, 2));
  }
}

function readDB() {
  ensureDB();
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
}

function writeDB(data) {
  ensureDB();
  fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2));
}

function genId() { return crypto.randomUUID(); }
function now() { return new Date().toISOString(); }
function hashPassword(pw) { return crypto.createHash('sha256').update(pw).digest('hex'); }

// ── 初始化 ─────────────────────────────────────────
function initDB() {
  const db_data = readDB();
  let changed = false;

  if (!Object.values(db_data.users).find(u => u.role === 'admin')) {
    db_data.users[genId()] = {
      id: genId(), username: 'admin', email: 'admin@a2a.local',
      password: hashPassword('admin123'), role: 'admin', balance: 10000,
      api_key: 'sk_a2a_admin_' + genId().replace(/-/g,''), created_at: now()
    };
    changed = true;
    console.log('✅ 管理员: admin@a2a.local / admin123');
  }

  if (!Object.values(db_data.users).find(u => u.username === 'lingxi')) {
    const ownerId = genId();
    db_data.users[ownerId] = {
      id: ownerId, username: 'lingxi', email: 'lingxi@openclaw.local',
      password: hashPassword('lingxi2025'), role: 'agent', balance: 1000,
      api_key: 'sk_a2a_' + genId().replace(/-/g,''), created_at: now()
    };
    const lingxiId = genId();
    db_data.agents[lingxiId] = {
      id: lingxiId, name: '灵犀', description: '心有灵犀一点通 — 全能 AI Agent，专注 GitHub 自动化 / 代码审查 / 工作流构建 / 网页爬取 / 智能搜索',
      avatar: '', owner_id: ownerId, status: 'active', created_at: now(), updated_at: now()
    };

    const caps = [
      { name: 'code_review', category: 'development', price: 0.05,
        description: '自动审查 GitHub PR，从安全性/逻辑/风格/性能多维度评分，输出结构化评论',
        params: [
          { name: 'repo_url', type: 'string', required: true, desc: 'GitHub 仓库地址' },
          { name: 'pr_number', type: 'number', required: true, desc: 'PR 编号' },
          { name: 'github_token', type: 'string', required: true, desc: 'GitHub Personal Access Token' }
        ]},
      { name: 'github_automation', category: 'development', price: 0.03,
        description: 'GitHub 自动化：PR追踪 / Issue管理 / 自动Star / Release发布 / 仓库分析',
        params: [
          { name: 'action', type: 'string', required: true, desc: '操作类型: star/pr/issues/release/analysis' },
          { name: 'repo_url', type: 'string', required: true, desc: '仓库地址' },
          { name: 'github_token', type: 'string', required: true, desc: 'GitHub Token' }
        ]},
      { name: 'n8n_workflow', category: 'automation', price: 0.04,
        description: '自然语言生成 n8n 工作流 JSON，描述需求即可生成可导入的工作流配置',
        params: [
          { name: 'workflow_description', type: 'string', required: true, desc: '工作流需求描述' },
          { name: 'platforms', type: 'array', required: false, desc: '目标平台列表' }
        ]},
      { name: 'web_scraping', category: 'data', price: 0.02,
        description: '智能网页爬取，支持登录认证/翻页/动态渲染，自动输出 CSV/JSON 格式',
        params: [
          { name: 'url', type: 'string', required: true, desc: '目标网页 URL' },
          { name: 'fields', type: 'array', required: true, desc: '要提取的字段列表' },
          { name: 'format', type: 'string', required: false, desc: '输出格式: json/csv' }
        ]},
      { name: 'ai_search', category: 'research', price: 0.01,
        description: 'AI 驱动的网络搜索与摘要，从多个信息源综合答案，支持追问与深度分析',
        params: [
          { name: 'query', type: 'string', required: true, desc: '搜索问题' },
          { name: 'sources', type: 'number', required: false, desc: '参考源数量 (默认5)' }
        ]},
      { name: 'data_analysis', category: 'data', price: 0.06,
        description: '数据分析与可视化建议，CSV/JSON 数据输入，自动识别模式并生成分析报告',
        params: [
          { name: 'data', type: 'string', required: true, desc: '数据内容 (CSV/JSON)' },
          { name: 'question', type: 'string', required: true, desc: '分析问题' }
        ]},
      { name: 'text_processing', category: 'ai', price: 0.005,
        description: '文本处理全家桶：摘要 / 分类 / 纠错 / 翻译 / 追问生成，基于 ZeroGPU 边缘小模型',
        params: [
          { name: 'task', type: 'string', required: true, desc: '任务类型: summarize/classify/fix/translate/followups' },
          { name: 'text', type: 'string', required: true, desc: '待处理文本' },
          { name: 'options', type: 'object', required: false, desc: '额外选项' }
        ]}
    ];

    caps.forEach(c => {
      db_data.capabilities[genId()] = {
        id: genId(), agent_id: lingxiId, name: c.name, description: c.description,
        category: c.category, params: c.params, returns: {}, status: 'active',
        price_per_call: c.price, created_at: now()
      };
    });
    changed = true;
    console.log('✅ 灵犀 Agent + 7个能力已创建');
  }

  if (changed) writeDB(db_data);
  console.log('✅ 数据库就绪: ' + DB_PATH);
}

// ── DB 操作封装 ───────────────────────────────────
const db_ops = {
  findUser: (filter) => {
    const data = readDB();
    return Object.values(data.users).find(u => Object.entries(filter).every(([k,v]) => u[k] === v));
  },
  getUserById: (id) => readDB().users[id],
  getUserByApiKey: (key) => Object.values(readDB().users).find(u => u.api_key === key),
  createUser: (user) => { const d = readDB(); d.users[user.id] = user; writeDB(d); },
  updateUser: (id, fields) => { const d = readDB(); if(d.users[id]){Object.assign(d.users[id],fields);writeDB(d);} },

  getAgents: (filter = {}) => {
    const data = readDB();
    let list = Object.values(data.agents);
    if (filter.status) list = list.filter(a => a.status === filter.status);
    return list.map(a => ({ ...a, cap_count: Object.values(data.capabilities).filter(c => c.agent_id === a.id).length }));
  },
  getAgent: (id) => readDB().agents[id],
  createAgent: (agent) => { const d = readDB(); d.agents[agent.id] = agent; writeDB(d); },
  updateAgent: (id, fields) => { const d = readDB(); if(d.agents[id]){Object.assign(d.agents[id],fields);writeDB(d);} },

  getCapabilities: (filter = {}) => {
    const data = readDB();
    let list = Object.values(data.capabilities);
    if (filter.agent_id) list = list.filter(c => c.agent_id === filter.agent_id);
    if (filter.status) list = list.filter(c => c.status === filter.status);
    if (filter.id) { const r = list.find(c => c.id === filter.id); return r ? [r] : []; }
    return list;
  },
  getCapability: (id) => readDB().capabilities[id],
  updateCapability: (id, fields) => { const d = readDB(); if(d.capabilities[id]){Object.assign(d.capabilities[id],fields);writeDB(d);} },
  createCapability: (cap) => { const d = readDB(); d.capabilities[cap.id] = cap; writeDB(d); },

  createCall: (call) => { const d = readDB(); d.calls[call.id] = call; writeDB(d); },
  updateCall: (id, fields) => { const d = readDB(); if(d.calls[id]){Object.assign(d.calls[id],fields);writeDB(d);} },

  getCalls: (filter = {}, opts = {}) => {
    const data = readDB();
    let list = Object.values(data.calls);
    if (filter.caller_id) list = list.filter(c => c.caller_id === filter.caller_id);
    if (filter.agent_id) list = list.filter(c => c.agent_id === filter.agent_id);
    if (filter.status) list = list.filter(c => c.status === filter.status);
    list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    const off = ((opts.page||1)-1) * (opts.limit||50);
    return { items: list.slice(off, off+(opts.limit||50)), total: list.length };
  },

  getAllCalls: (opts = {}) => {
    const data = readDB();
    const caps = data.capabilities, agents = data.agents, users = data.users;
    let list = Object.values(data.calls).map(c => ({
      ...c,
      username: users[c.caller_id]?.username || '',
      cap_name: caps[c.capability_id]?.name || '',
      agent_name: agents[c.agent_id]?.name || ''
    }));
    list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    const off = ((opts.page||1)-1) * (opts.limit||50);
    return { items: list.slice(off, off+(opts.limit||50)), total: list.length };
  },

  getReviews: (agentId) => Object.values(readDB().reviews).filter(r => r.agent_id === agentId),
  createReview: (review) => { const d = readDB(); d.reviews[review.id] = review; writeDB(d); },

  createTopup: (topup) => { const d = readDB(); d.topups[topup.id] = topup; writeDB(d); },

  getStats: () => {
    const data = readDB();
    return {
      agents: Object.values(data.agents).filter(a => a.status === 'active').length,
      capabilities: Object.values(data.capabilities).filter(c => c.status === 'active').length,
      total_calls: Object.values(data.calls).filter(c => c.status === 'success').length,
      users: Object.values(data.users).filter(u => u.role === 'user').length
    };
  },

  getAllUsers: () => Object.values(readDB().users).map(u => { const x=Object.assign({},u); delete x.password; return x; })
};

module.exports = { db: db_ops, initDB, readDB, writeDB, genId, now, hashPassword };
