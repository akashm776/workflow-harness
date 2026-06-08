# Future / Example Fixtures

`fixtures/future/` contains **example/future-only** artifacts.

These artifacts:

- are **not** active governance inputs,
- are **not** control-plane inputs,
- are **not** consumed by compile or runtime behavior,
- exist only to demonstrate future artifact shapes and to be exercised by
  standalone validators (for example
  `compiler/side_effect_catalog_schema_validator.py`).

Current future-only fixture sets include:

- `side-effect-catalog/SideEffectCatalog.json` for standalone schema-shape
  validation examples.
- `innovation-context/` for local fake program/repo/wiki/issue/rubric summaries.
  V1 does **not** load, execute, connect, or call MCP/tools/connectors from
  these fixtures.

Nothing here grants authority or enables any capability. The compiler remains the
sole authority boundary, and V1 remains safe no-op only.
