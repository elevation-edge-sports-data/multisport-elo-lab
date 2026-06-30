import subprocess

models = ["BASE", "MOV", "HFA"]

for m in models:
    print(f"Running model: {m}")

    subprocess.run([
        "python",
        "src/run_backtest.py"
    ], env={**dict(__import__("os").environ), "MODEL": m})