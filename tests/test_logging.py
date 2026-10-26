import json
from app.logging_utils import build_logger, log_event

def test_json_logging_is_written_to_isolated_file(tmp_path):
    log_path = tmp_path / "isolated" / "test.jsonl"
    logger = build_logger(log_path)
    log_event(logger, "unit_test_event", country="India", status_code=200)
    for handler in logger.handlers:
        handler.flush()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[-1])
    assert event["message"] == "unit_test_event"
    assert event["country"] == "India"
    assert event["status_code"] == 200
