"""Headless end-to-end test of the full runtime (no Gradio UI)."""

import json
import os
import sys

from runtime.pipeline import run_demo

os.environ.setdefault("DF_CACHE", "hf-cache")

out = run_demo("squirrel",
               sphere_pos=[0.103, 0.822, 2.883],
               sphere_vel=[-2.34, -18.71, -65.61],
               seed=42, gravity=-5.0, seconds_after=2.0)

if "error" in out:
    print("FAIL:", out["error"])
    sys.exit(1)

print(json.dumps(out["info"], indent=2))
print("video:", out["video"], os.path.getsize(out["video"]), "bytes")
print("glb:", out["glb"], os.path.getsize(out["glb"]), "bytes")
assert out["info"]["n_fragments"] >= 2, "expected multiple fragments"
assert os.path.getsize(out["video"]) > 50_000, "video too small"

# also make sure the Gradio app imports cleanly
import app  # noqa: E402,F401
print("app import OK")
print("E2E PASS")
