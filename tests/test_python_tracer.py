from algonim.python_tracer import trace


def test_trace_records_falsy_values(tmp_path):
    program = tmp_path / "program.py"
    program.write_text("i = 0\nflag = False\ni = 1\n")

    snapshots = [snapshot for _, snapshot in trace(program, {"i", "flag"})]

    assert [s.lineno for s in snapshots] == [1, 2, 3]
    # A line's snapshot shows state before that line runs
    assert snapshots[1].vars == {"i": 0}
    assert snapshots[2].vars == {"i": 0, "flag": False}


def test_snapshot_diff(tmp_path):
    program = tmp_path / "program.py"
    program.write_text("a = 1\nb = 2\na = 3\npass\n")

    snapshots = [snapshot for _, snapshot in trace(program, {"a", "b"})]
    new_vars, changed = snapshots[3].diff(snapshots[2])

    assert new_vars == set()
    assert changed["a"].from_ == 1
    assert changed["a"].to == 3
