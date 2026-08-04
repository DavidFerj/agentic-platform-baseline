import json
import logging

from platform_api.core.logging import RequestIdFilter, configure_logging


def test_request_id_filter_adds_default_context() -> None:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "message", (), None)

    assert RequestIdFilter().filter(record) is True
    assert record.request_id == "unassigned"  # type: ignore[attr-defined]


def test_configure_logging_emits_json_and_reparents_uvicorn(capsys) -> None:
    child = logging.getLogger("uvicorn")
    child.handlers = [logging.NullHandler()]
    child.propagate = False

    configure_logging("INFO")
    logging.getLogger("platform.test").info("structured message")

    payload = json.loads(capsys.readouterr().err)
    assert payload["level"] == "INFO"
    assert payload["message"] == "structured message"
    assert payload["request_id"] == "unassigned"
    assert child.handlers == []
    assert child.propagate is True
