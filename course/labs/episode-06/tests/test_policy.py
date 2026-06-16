from loopath.actions import ReadFileAction, RunCommandAction
from loopath.policy import Policy, check_command


def test_blocks_env():
    assert not check_command("env").allowed


def test_blocks_rm_rf():
    assert not check_command("rm -rf /").allowed


def test_allows_pytest():
    assert check_command("pytest").allowed


def test_policy_allows_non_command_action():
    decision = Policy().check(ReadFileAction(type="read_file", path="app.py"))
    assert decision.allowed


def test_policy_blocks_dangerous_command_action():
    decision = Policy().check(RunCommandAction(type="run_command", command="env"))
    assert not decision.allowed
