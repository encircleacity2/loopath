import pytest

from loopath.actions import ActionParseError, ReadFileAction, parse_action


def test_parse_read_file_action():
    action = parse_action('{"type":"read_file","path":"app.py"}')
    assert isinstance(action, ReadFileAction)
    assert action.path == "app.py"


def test_reject_invalid_json():
    with pytest.raises(ActionParseError):
        parse_action("read app.py")


def test_reject_unknown_action_type():
    with pytest.raises(ActionParseError):
        parse_action('{"type":"delete_everything","path":"."}')


def test_reject_missing_required_field():
    with pytest.raises(ActionParseError):
        parse_action('{"type":"read_file"}')
