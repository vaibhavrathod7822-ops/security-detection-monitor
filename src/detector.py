import re
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "auth.log"
REPORT_DIR = BASE_DIR / "reports"
REPORT_FILE = REPORT_DIR / "security_report.json"

FAILED_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)"
)
SUCCESS_PATTERN = re.compile(
    r"Accepted password for (\S+) from (\d+\.\d+\.\d+\.\d+)"
)

def main():
    if not LOG_FILE.exists():
        raise SystemExit(f"Log file not found: {LOG_FILE}")

    REPORT_DIR.mkdir(exist_ok=True)
    failed_by_ip = Counter()
    alerts = []
    total_lines = 0

    for line in LOG_FILE.read_text(errors="replace").splitlines():
        total_lines += 1

        failed = FAILED_PATTERN.search(line)
        if failed:
            username, ip = failed.groups()
            failed_by_ip[ip] += 1
            continue

        success = SUCCESS_PATTERN.search(line)
        if success:
            username, ip = success.groups()
            alerts.append({
                "type": "successful_login",
                "severity": "INFO",
                "username": username,
                "source_ip": ip,
                "message": f"Successful login for {username} from {ip}"
            })

    for ip, count in failed_by_ip.items():
        if count >= 3:
            alerts.append({
                "type": "repeated_failed_logins",
                "severity": "HIGH",
                "source_ip": ip,
                "attempts": count,
                "message": f"{count} failed login attempts from {ip}"
            })
        else:
            alerts.append({
                "type": "failed_login_activity",
                "severity": "MEDIUM",
                "source_ip": ip,
                "attempts": count,
                "message": f"{count} failed login attempt(s) from {ip}"
            })

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "log_file": str(LOG_FILE.relative_to(BASE_DIR)),
        "total_log_lines": total_lines,
        "alerts_count": len(alerts),
        "alerts": alerts,
        "note": "Detection uses supplied sample logs; this is not live monitoring."
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2))
    print("=== SECURITY DETECTION & MONITORING ===")
    print(f"Log lines analyzed: {total_lines}")
    print(f"Alerts generated: {len(alerts)}")

    for alert in alerts:
        print(f"[{alert['severity']}] {alert['message']}")

    print(f"\nReport saved to: {REPORT_FILE}")

if __name__ == "__main__":
    main()
