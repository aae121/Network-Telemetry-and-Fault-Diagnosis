from datetime import datetime
from pathlib import Path
import subprocess

SNAPSHOT_DIR = Path("snapshots")
DESTINATION = "1.1.1.1"


def run_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return result.stdout.strip() or result.stderr.strip() or "(no output)"


def save_snapshot(reason):
    moment = datetime.now().astimezone()
    SNAPSHOT_DIR.mkdir(exist_ok=True)

    ping = run_command(["ping", "-c", "3", "-W", "2", DESTINATION])
    interfaces = run_command(["ip", "-br", "link"])
    routes = run_command(["ip", "route"])

    contents = (
        f"Captured at: {moment.isoformat(timespec='seconds')}\n"
        f"Reason: {reason}\n\n"
        f"Ping to {DESTINATION}:\n{ping}\n\n"
        f"Interfaces:\n{interfaces}\n\n"
        f"Routes:\n{routes}\n"
    )

    filename = f"snapshot-{moment:%Y%m%d-%H%M%S}.txt"
    snapshot_path = SNAPSHOT_DIR / filename
    snapshot_path.write_text(contents, encoding="utf-8")
    print(f"Saved diagnostic snapshot: {snapshot_path}")


if __name__ == "__main__":
    save_snapshot("manual test")