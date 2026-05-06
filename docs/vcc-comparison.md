# ctx and VCC

`ctx` is not a replacement for VCC.

VCC compiles raw conversation logs into views that agents can read and search. `ctx` uses that insight and adds an async review loop around context operations.

| Dimension | VCC | ctx |
|---|---|---|
| Main job | Compile and search conversation logs | Manage context operations as reviewable jobs |
| Primary commands | `/recall`, `/searchchat`, `/readchat` | `/ctx-recall`, `/ctx-compact`, `/ctx-jobs` |
| Scope | Historical logs | Historical recall plus current-session compact |
| Result | Transcript view or search view | Candidate context suggestion |
| Control | Direct lookup | Apply or discard after review |

Summary:

```text
VCC recovers context.
ctx manages whether recalled or compacted context should enter the current session.
```
