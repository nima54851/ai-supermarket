# Supabase Backend Automation

> Supabase — PostgreSQL + Auth + Realtime + Storage + Edge Functions — AI 驱动的后端自动化

## 核心功能

- **Auth 自动化** — Magic Link / OAuth / MFA / SSO 注册登录
- **Realtime 订阅** — 数据库变更实时推送到前端
- **Storage 管理** — 文件上传、CDN、分发
- **Edge Functions** — Deno/TypeScript 边缘计算
- **RLS 策略** — 行级安全策略自动化生成
- **数据库管理** — 迁移、备份、监控

## 目录结构

```
supabase-automation/
├── SKILL.md
└── workflows/
    ├── n8n-supabase-auth-workflow.json     ← Auth + OAuth flow
    ├── n8n-realtime-sync-workflow.json     ← Realtime 订阅 pipeline
    ├── n8n-storage-upload-workflow.json    ← 文件处理 + Storage 上传
    └── supabase-edge-template.ts           ← Edge Function 模板
```

## 快速开始

### 1. Supabase 项目初始化

```bash
# 安装 Supabase CLI
npm install -g supabase

# 初始化项目
supabase init
supabase login

# 启动本地开发环境
supabase start
```

### 2. Auth 自动化（n8n）

导入 `workflows/n8n-supabase-auth-workflow.json`：

- 注册 → Magic Link 发送
- OAuth（Google/GitHub）→ 用户数据入库 → JWT 签发
- Token 刷新 → 自动续期
- MFA 启用 → TOTP 绑定

### 3. Realtime 订阅

```javascript
// 前端订阅数据库变更
const channel = supabase
  .channel('db-changes')
  .on(
    'postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'tasks',
      filter: 'user_id=eq.${userId}'
    },
    (payload) => {
      console.log('Change received!', payload);
    }
  )
  .subscribe();
```

### 4. Storage 自动化上传

```bash
curl -X POST https://your-n8n.com/webhook/supabase-upload \
  -F "file=@report.pdf" \
  -F "bucket=reports" \
  -F "user_id=user_123" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}"
```

### 5. Edge Function 示例

```typescript
// supabase/functions/ai-process/index.ts
import { serve } from "https://deno.land/std@0.177.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
  const { text, user_id } = await req.json()
  
  // 调用 AI 处理
  const aiResult = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}` },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{ role: 'user', content: `分析: ${text}` }]
    })
  })
  
  const { choices } = await aiResult.json()
  const analysis = choices[0].message.content
  
  // 存入数据库
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )
  
  await supabase.from('analyses').insert({
    user_id,
    original_text: text,
    ai_result: analysis
  })
  
  return new Response(JSON.stringify({ analysis }), {
    headers: { 'Content-Type': 'application/json' }
  })
})
```

## RLS 策略自动化

```sql
-- 自动化生成 RLS 策略（AI 辅助）
-- 用户只能看自己的数据
CREATE POLICY "Users can view own records" ON tasks
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 团队成员可以共享
CREATE POLICY "Team members can view shared tasks" ON tasks
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.user_id = auth.uid()
      AND team_members.team_id = tasks.team_id
    )
  );
```

## 相关 Skills

- `database-automation/` — 通用数据库管理
- `auth-automation/` — 通用身份认证
- `api-development/` — REST/GraphQL API 开发
- `database-migration-automation/` — 数据库迁移

---

*Version 1.0 | 2026-07-20*
