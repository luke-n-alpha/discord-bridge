import argparse
import shutil
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build(output_dir: Path, spec: str | None) -> Path:
    env = {
        "PYTHONPATH": str(PROJECT_ROOT),
        # Ensure user-local bin (pyinstaller) is on PATH
        "PATH": f"{os.path.expanduser('~/.local/bin')}:{os.environ.get('PATH','')}",
        **dict(**{}),
    }
    cmd = [os.fspath(Path(Path(os.sys.executable).parent) / "pyinstaller")]
    if not Path(cmd[0]).exists():
        # fallback to module invocation
        cmd = [os.sys.executable, "-m", "PyInstaller"]
    cmd.extend(["--onefile", "--name", "bridge-cli"])
    if spec:
        cmd.extend(["--specpath", str(Path(spec).parent)])
    script = PROJECT_ROOT / "bridge" / "cli.py"
    cmd.append(str(script))

    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT, env={**env})
    dist_dir = PROJECT_ROOT / "dist"
    if not dist_dir.exists():
        raise FileNotFoundError(f"dist directory missing after PyInstaller run")
    target = dist_dir / "bridge-cli"
    if not target.exists():
        # Windows adds .exe
        target = target.with_suffix(".exe")
    final = output_dir / target.name
    shutil.copy2(target, final)
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description="Build bridge-cli with PyInstaller")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("build/bin"),
        help="Directory to place the built binary",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="Optional spec file to reuse PyInstaller settings",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    built = build(args.output_dir, spec=args.spec)
    print(f"Built bridge-cli binary at {built}")


if __name__ == "__main__":
    main()
