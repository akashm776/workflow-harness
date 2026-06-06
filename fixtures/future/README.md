# Future / Example Fixtures

`fixtures/future/` contains **example/future-only** artifacts.

These artifacts:

- are **not** active governance inputs,
- are **not** control-plane inputs,
- are **not** consumed by compile or runtime behavior,
- exist only to demonstrate future artifact shapes and to be exercised by
  standalone validators (for example
  `compiler/side_effect_catalog_schema_validator.py`).

Nothing here grants authority or enables any capability. The compiler remains the
sole authority boundary, and V1 remains safe no-op only.
