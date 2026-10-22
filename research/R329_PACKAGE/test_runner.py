#!/usr/bin/env python3
"""R329 pure weight-function synthetic tests; no market PnL."""
import importlib.util, pathlib
p=pathlib.Path(__file__).with_name("runner.py")
s=importlib.util.spec_from_file_location("r329_runner", p)
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for msg in m.self_tests(): print(msg)
print("market data/PnL: NOT TOUCHED by tests")
