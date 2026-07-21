# SKILL.md — Database Migration Automation

## 概述
AI 驱动的数据库迁移自动化：自动生成迁移脚本、检测数据一致性、执行零停机部署、回滚管理。支持 PostgreSQL、MySQL、MongoDB。

## 核心能力
- **Schema 变更分析**：对比新旧 Schema，生成 ALTER/Migration 脚本
- **AI SQL 生成**：自然语言描述 → 安全 SQL 迁移脚本
- **数据校验**：迁移前后数据一致性校验，完整性检查
- **灰度发布**：blue-green 部署，先写新表再切换
- **自动回滚**：检测异常时自动回滚至上一稳定版本
- **迁移日志**：完整审计追踪，生成迁移报告

## 典型场景
- 数据库版本升级（MySQL 5.7 → 8.0）
- 微服务拆分/合并时的数据迁移
- 大表加索引（Online DDL）
- 冷热数据分离

## 工具依赖
- PostgreSQL: `pg_dump`, `pg_restore`, `psql`
- MySQL: `mysqldump`, `mysql`
- MongoDB: `mongodump`, `mongorestore`
- AI LLM（生成迁移脚本）

## n8n 集成
→ `integrations/database-migration-automation/n8n-migration-workflow.json`

## 安全规范
- ⚠️ 生产环境必须使用 `--dry-run` 模式验证
- ⚠️ 大表迁移前必须备份
- ⚠️ 执行前在测试环境验证

## 示例命令
```bash
# PostgreSQL: 生成迁移脚本
pg_dump --schema-only mydb > schema.sql
diff schema_old.sql schema_new.sql > migration.diff

# MySQL: 在线加索引
ALTER TABLE orders ADD INDEX idx_user_id (user_id), ALGORITHM=INPLACE, LOCK=NONE;

# 回滚
psql -h localhost -U admin mydb < rollback_v2.sql
```
