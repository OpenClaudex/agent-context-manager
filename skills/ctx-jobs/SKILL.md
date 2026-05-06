---
name: ctx-jobs
description: "View and manage ctx async jobs. /ctx-jobs [--all]. Preview results, apply or discard completed jobs."
---

# ctx-jobs — 管理异步 context 任务

查看所有 ctx-recall 和 ctx-compact 的异步任务状态，预览结果，apply 或 discard。

## 用法

```
/ctx-jobs
/ctx-jobs --all
```

## 执行步骤

当用户调用 `/ctx-jobs` 时，按以下步骤执行：

### Step 1: 找到 ctx 目录

```bash
CTX_DIR="${CTX_HOME:-$(find ~ -maxdepth 5 -type d -name ctx 2>/dev/null | head -1)}"
```

### Step 2: 列出所有 jobs

```bash
cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.runner list
```

解析返回的 JSON。

### Step 3: 展示 job 表格

把 jobs 展示为可读的表格：

```
┌─────────┬──────────┬────────┬─────────┬───────────────────────────────┐
│ ID      │ Type     │ Status │ Age     │ Preview                       │
├─────────┼──────────┼────────┼─────────┼───────────────────────────────┤
│ abc123  │ recall   │ done   │ 2m ago  │ VCC architecture (3 hits)     │
│ def456  │ compact  │ done   │ 5m ago  │ [SESSION COMPACT] 主题：...    │
│ ghi789  │ recall   │ running│ 30s ago │ (running...)                  │
└─────────┴──────────┴────────┴─────────┴───────────────────────────────┘
```

### Step 4: 对 done 的 job 提供操作

对每个 `status=done` 的 job，用 AskUserQuestion 询问用户：

问题格式：
- header: "Job <id>"
- question: "Job <id> (<type>: '<query/instruction>') 已完成。如何处理？"
- 选项：
  - "Apply" — 注入结果到当前对话
  - "Show full" — 先看完整结果再决定
  - "Discard" — 丢弃

### Step 5: 执行用户选择

**如果用户选 "Show full"：**

```bash
cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.runner show <job-id>
```

展示完整 `result_full` 内容，然后再次问 apply 或 discard。

**如果用户选 "Apply"：**

```bash
cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.runner apply <job-id>
```

解析返回 JSON：
- 如果 `"status": "applied"` → 把 `result` 字段的内容直接输出（这就是注入到对话的上下文）
- 如果 `"status": "stale"` → 告诉用户：
  > ⚠️ 其他 session 的上下文已变化，Job <id> 可能过期。
  然后用 AskUserQuestion 问：
  - "Force apply" — 强制应用（忽略 stale）
  - "Discard" — 丢弃
  
  如果用户选 Force apply：
  ```bash
  cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.runner apply <job-id> --force
  ```

**如果用户选 "Discard"：**

```bash
cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.runner discard <job-id>
```

告诉用户：
> ✓ Job <id> 已丢弃。

### 其他状态的处理

- `running` → 告诉用户 "仍在执行中，稍后再查看"
- `failed` → 显示 error 信息
- `applied` / `discarded` → 已处理，仅展示不再提供操作
- `stale` → 建议用户重新执行
- `pending` → compact job 等待 Claude 生成摘要（异常状态）

### 注意事项

- 如果没有任何 job，告诉用户 "没有 ctx 任务。用 /ctx-recall 或 /ctx-compact 创建。"
- 默认只显示最近 10 个 job
- 按创建时间倒序排列（最新的在前）
