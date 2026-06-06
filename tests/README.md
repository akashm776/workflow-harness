# Tests

M1 test scope is intentionally narrow:

- canonical JSON hashing
- dependency digest determinism
- revision id determinism
- fixture contract shape

Compiler behavior, policy evaluation, and runtime side effects are deferred to later milestones.

Run tests consistently from the repo root with:

```powershell
& 'C:\Users\u230212\AppData\Local\Programs\Python\Python312\python.exe' -m unittest discover -s tests -v
```
