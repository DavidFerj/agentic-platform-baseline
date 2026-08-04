# Cloud Run functions

Functions are reserved for narrow HTTP or CloudEvent adapters such as validated webhooks,
event ingestion, and small idempotent notifications. No function is created until a
requirement identifies its trigger, contract, owner, IAM identity, timeout, retry policy,
idempotency key, and dead-letter behavior.

Each Python function is independently deployable and should normally contain:

```text
function-name/
  main.py
  pyproject.toml
  uv.lock
  src/function_name/
    config.py
    dto.py
    service.py
    clients.py
    errors.py
  tests/
```

`main.py` adapts the trigger, validates input, wires dependencies, invokes application
behavior, and maps the result. Business rules, database code, and provider-specific
details do not belong in the entry point.

Dependencies are local to the function deployment root. Shared code must be a small,
versioned package or included deliberately in the build; functions must not import
undeployed sibling source directories.
