# Future Innovation Context Fixtures

`fixtures/future/innovation-context/` contains local fake data only.

These artifacts are future-only example inputs for deterministic innovation-agent
context shape work:

- `ProgramContext.json`
- `RepoContextSummary.json`
- `ConfluenceContextSummary.json`
- `IssueTrackerContextSummary.json`
- `Rubric.json`

They are inert data only:

- V1 does **not** load these fixtures.
- V1 does **not** execute anything from these fixtures.
- V1 does **not** connect to tools, connectors, or MCP from these fixtures.
- They are **not** control-plane inputs.
- They grant no authority and enable no capability.

They are committed local fake summaries only:

- no real program data
- no external reads
- no credentials
- no approval behavior

These files exist only to support future docs/tests/design work around local
context artifacts. Compiler, runtime, CLI, planner, and example behavior remain
unchanged.
