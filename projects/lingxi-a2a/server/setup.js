/**
 * 数据库初始化脚本
 * 运行: node server/setup.js
 */
const Database = require('better-sqlite3');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcryptjs');

const DB_PATH = path.join(__dirname, 'a2a.db');

const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

// ── 表结构 ──────────────────────────────────────────
db.exec(`
-- Agent 注册表
CREATE TABLE IF NOT EXISTS agents (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  avatar      TEXT NOT NULL DEFAULT '',
  owner_id    TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','inactive','suspended')),
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Agent 能力表
CREATE TABLE IF NOT EXISTS capabilities (
  id          TEXT PRIMARY KEY,
  agent_id    TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  category    TEXT NOT NULL DEFAULT 'general',
  params      TEXT NOT NULL DEFAULT '[]',
  returns     TEXT NOT NULL DEFAULT '{}',
  price_per_call REAL NOT NULL DEFAULT 0,
  quota_daily INTEGER NOT NULL DEFAULT 1000,
  status      TEXT NOT NULL DEFAULT 'active',
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id          TEXT PRIMARY KEY,
  username    TEXT UNIQUE NOT NULL,
  email       TEXT UNIQUE NOT NULL,
  password    TEXT NOT NULL,
  role        TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','agent','admin')),
  balance     REAL NOT NULL DEFAULT 100,
  api_key     TEXT UNIQUE NOT NULL,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 调用记录表
CREATE TABLE IF NOT EXISTS calls (
  id            TEXT PRIMARY KEY,
  caller_id     TEXT NOT NULL REFERENCES users(id),
  agent_id      TEXT NOT NULL REFERENCES agents(id),
  capability_id TEXT NOT NULL REFERENCES capabilities(id),
  input         TEXT NOT NULL DEFAULT '{}',
  output        TEXT NOT NULL DEFAULT '',
  status        TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','success','failed','refunded')),
  cost          REAL NOT NULL DEFAULT 0,
  duration_ms   INTEGER,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 充值记录
CREATE TABLE IF NOT EXISTS topups (
  id          TEXT PRIMARY KEY,
  user_id     TEXT NOT NULL REFERENCES users(id),
  amount      REAL NOT NULL,
  method      TEXT NOT NULL DEFAULT 'manual',
  status      TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','completed','failed')),
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Agent 评分
CREATE TABLE IF NOT EXISTS reviews (
  id          TEXT PRIMARY KEY,
  agent_id    TEXT NOT NULL REFERENCES agents(id),
  user_id     TEXT NOT NULL REFERENCES users(id),
  rating      INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
  comment     TEXT NOT NULL DEFAULT '',
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_caps_agent ON capabilities(agent_id);
CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_id);
CREATE INDEX IF NOT EXISTS idx_calls_agent ON calls(agent_id);
CREATE INDEX IF NOT EXISTS idx_reviews_agent ON reviews(agent_id);
`);

console.log('✅ 数据库表创建完成');

// ── 种子数据：创建管理员 + 灵犀 Agent ──────────────
const adminId = uuidv4();
const lingxiId = uuidv4();
const lingxiOwnerId = uuidv4();
const demoUserId = uuidv4();

const apiKey = 'sk_a2a_' + uuidv4().replace(/-/g, '');
const hashedPassword = bcrypt.hashSync('lingxi2025', 10);

try {
  db.prepare(`
    INSERT OR IGNORE INTO users (id, username, email, password, role, balance, api_key)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(adminId, 'admin', 'admin@a2a.local', bcrypt.hashSync('admin123', 10), 'admin', 10000, 'sk_a2a_admin_' + uuidv4().replace(/-/g,''));

  db.prepare(`
    INSERT OR IGNORE INTO users (id, username, email, password, role, balance, api_key)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(lingxiOwnerId, 'lingxi', 'lingxi@openclaw.local', hashedPassword, 'agent', 1000, apiKey);

  db.prepare(`
    INSERT OR IGNORE INTO agents (id, name, description, owner_id, status)
    VALUES (?, ?, ?, ?, ?)
  `).run(lingxiId, '灵犀', '心有灵犀一点通 — 全能 AI Agent，专注 GitHub 自动化 / 代码审查 / 工作流构建 / 网页爬取 / 智能搜索', lingxiOwnerId, 'active');

  // 灵犀的能力
  const caps = [
    {
      id: uuidv4(), name: 'code_review', category: 'development',
      description: '自动审查 GitHub PR，从安全性/逻辑/风格/性能多维度评分，输出结构化评论',
      params: JSON.stringify([
        { name: 'repo_url', type: 'string', required: true, desc: 'GitHub 仓库地址' },
        { name: 'pr_number', type: 'number', required: true, desc: 'PR 编号' },
        { name: 'github_token', type: 'string', required: true, desc: 'GitHub Personal Access Token' }
      ]),
      returns: JSON.stringify({ review_comment: 'string', score: 'number', issues: 'array' }),
      price: 0.05
    },
    {
      id: uuidv4(), name: 'github_automation', category: 'development',
      description: 'GitHub 自动化：PR追踪 / Issue管理 / 自动Star / Release发布 / 仓库分析',
      params: JSON.stringify([
        { name: 'action', type: 'string', required: true, desc: '操作类型: star/pr/issues/release/analysis' },
        { name: 'repo_url', type: 'string', required: true, desc: '仓库地址' },
        { name: 'github_token', type: 'string', required: true, desc: 'GitHub Token' }
      ]),
      returns: JSON.stringify({ success: 'boolean', data: 'object', message: 'string' }),
      price: 0.03
    },
    {
      id: uuidv4(), name: 'n8n_workflow', category: 'automation',
      description: '自然语言生成 n8n 工作流 JSON，描述需求即可生成可导入的工作流配置',
      params: JSON.stringify([
        { name: 'workflow_description', type: 'string', required: true, desc: '工作流需求描述' },
        { name: 'platforms', type: 'array', required: false, desc: '目标平台列表' }
      ]),
      returns: JSON.stringify({ workflow_json: 'object', template_name: 'string' }),
      price: 0.04
    },
    {
      id: uuidv4(), name: 'web_scraping', category: 'data',
      description: '智能网页爬取，支持登录认证/翻页/动态渲染，自动输出 CSV/JSON/数据库格式',
      params: JSON.stringify([
        { name: 'url', type: 'string', required: true, desc: '目标网页 URL' },
        { name: 'fields', type: 'array', required: true, desc: '要提取的字段列表' },
        { name: 'format', type: 'string', required: false, desc: '输出格式: json/csv' }
      ]),
      returns: JSON.stringify({ data: 'array', count: 'number', format: 'string' }),
      price: 0.02
    },
    {
      id: uuidv4(), name: 'ai_search', category: 'research',
      description: 'AI 驱动的网络搜索与摘要，从多个信息源综合答案，支持追问与深度分析',
      params: JSON.stringify([
        { name: 'query', type: 'string', required: true, desc: '搜索问题' },
        { name: 'sources', type: 'number', required: false, desc: '参考源数量 (默认5)' }
      ]),
      returns: JSON.stringify({ answer: 'string', sources: 'array', confidence: 'number' }),
      price: 0.01
    },
    {
      id: uuidv4(), name: 'data_analysis', category: 'data',
      description: '数据分析与可视化建议，CSV/JSON 数据输入，自动识别模式并生成分析报告',
      params: JSON.stringify([
        { name: 'data', type: 'string', required: true, desc: '数据内容 (CSV/JSON)' },
        { name: 'question', type: 'string', required: true, desc: '分析问题' }
      ]),
      returns: JSON.stringify({ analysis: 'string', insights: 'array', charts: 'array' }),
      price: 0.06
    },
    {
      id: uuidv4(), name: 'text_processing', category: 'ai',
      description: '文本处理全家桶：摘要 / 分类 / 纠错 / 翻译 / 追问生成，基于 ZeroGPU 边缘小模型',
      params: JSON.stringify([
        { name: 'task', type: 'string', required: true, desc: '任务类型: summarize/classify/fix/translate/followups' },
        { name: 'text', type: 'string', required: true, desc: '待处理文本' },
        { name: 'options', type: 'object', required: false, desc: '额外选项' }
      ]),
      returns: JSON.stringify({ result: 'string', savings: 'object' }),
      price: 0.005
    }
  ];

  const insertCap = db.prepare(`
    INSERT OR IGNORE INTO capabilities
    (id, agent_id, name, description, category, params, returns, price_per_call)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  for (const c of caps) {
    insertCap.run(c.id, lingxiId, c.name, c.category, c.description, c.params, c.returns, c.price);
  }

  console.log('✅ 种子数据写入完成');
  console.log('   管理员账号: admin@a2a.local / admin123');
  console.log(`   灵犀 Agent API Key: ${apiKey}`);

} catch (e) {
  console.log('种子数据已存在，跳过:', e.message);
}

db.close();
console.log('✅ 数据库初始化完成');
