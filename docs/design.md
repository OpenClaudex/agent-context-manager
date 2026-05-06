# Design

`ctx` has three operations:

```text
/ctx-recall  -> background global recall job
/ctx-compact -> background current-session compact job
/ctx-jobs    -> review/apply/discard control plane
```

The design principle is:

```text
Recall globally. Compact locally. Apply deliberately.
```

## Recall

`/ctx-recall` searches across local CodeBuddy, Claude Code, and Codex logs. It creates a job immediately, runs retrieval and summarization in a background process, then stores the result in a local file-based job store.

## Compact

`/ctx-compact` only compacts the current session. It should not compact all history. Compact is a local operation on the active working context.

## Jobs

`/ctx-jobs` is the safety layer. It separates candidate context from applied context. This prevents noisy recall or poor summaries from automatically polluting the current session.
