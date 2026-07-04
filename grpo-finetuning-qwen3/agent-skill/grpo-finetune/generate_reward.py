"""Reward validator. Proves reward.py satisfies the contract before any GPU spend.

Contract: reward.py must define score(completion, row=None) -> float in [0, 1].
Usage: python scripts/generate_reward.py --validate reward.py
"""

import argparse
import importlib.util
import sys
from pathlib import Path


def load_reward(path):
    spec = importlib.util.spec_from_file_location("reward_module", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_reward(path) -> int:
    path = Path(path)
    if not path.exists():
        print(f"FAIL  not found: {path}")
        return 1
    try:
        mod = load_reward(path)
    except Exception as e:
        print(f"FAIL  import error: {e}")
        return 1
    if not hasattr(mod, "score") or not callable(mod.score):
        print("FAIL  must define score(completion, row=None) -> float")
        return 1
    for probe in ["", "{}", "garbage", '{"a": 1}']:
        try:
            v = mod.score(probe, None)
        except Exception as e:
            print(f"FAIL  score() crashed on {probe!r}: {e}")
            return 1
        if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
            print(f"FAIL  score() returned {v!r} on {probe!r}, expected float in [0,1]")
            return 1
    failures = 0
    for i, (completion, row, expected) in enumerate(getattr(mod, "SELF_TESTS", [])):
        got = mod.score(completion, row)
        ok = abs(float(got) - float(expected)) < 1e-6
        print(f"  [{'ok  ' if ok else 'FAIL'}] test {i}: got {got}  expected {expected}")
        if not ok:
            failures += 1
    if failures:
        print(f"FAIL  {failures} self-test(s) failed")
        return 1
    tests = len(getattr(mod, "SELF_TESTS", []))
    print("PASS" + (f"  {tests} self-tests green" if tests else "  (add SELF_TESTS to pin the task)"))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", metavar="PATH", required=True)
    sys.exit(validate_reward(ap.parse_args().validate))
