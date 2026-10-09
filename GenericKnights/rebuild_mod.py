"""Rebuild the GenericKnights table package without stale NXD payloads."""

from pathlib import Path
import subprocess
import sys
import os

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "Mod" / "FFTIVC" / "data" / "enhanced" / "nxd"
TOOLS = Path(os.environ.get("FF16TOOLS_CLI", str(ROOT.parent / "FF16 Tools/win-x64/FF16Tools.CLI.exe")))


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "build_tables.py")], check=True)

    # The converter writes only the tables present in the SQLite source.  A
    # clean directory prevents legacy Ability and UiJobAbilityHelp snapshots
    # (inherited from GenericJobs by earlier builds) being shipped again.
    TARGET.mkdir(parents=True, exist_ok=True)
    for path in TARGET.glob("*.nxd"):
        path.unlink()

    subprocess.run(
        [str(TOOLS), "sqlite-to-nxd", "-i", str(ROOT / "GenericKnights.sqlite"),
         "-o", str(TARGET), "-g", "fft"],
        check=True,
    )


if __name__ == "__main__":
    main()
