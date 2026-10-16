import json
import subprocess
import sys
from pathlib import Path
import streamlit as st

BASE = Path(__file__).resolve().parent
REPORT = BASE / "reports" / "security_report.json"
DETECTOR = BASE / "src" / "detector.py"

st.set_page_config(page_title="Security Detection & Monitoring", page_icon="🛡️", layout="wide")
st.title("🛡️ Security Detection & Monitoring")
st.caption("Authentication log analysis • Severity-based alerts • JSON reports")

if st.button("🔄 Run Detection Scan", type="primary"):
    result = subprocess.run(
        [sys.executable, str(DETECTOR)],
        cwd=BASE, capture_output=True, text=True
    )
    if result.returncode == 0:
        st.success("Detection scan completed.")
        st.code(result.stdout or "Scan completed.")
    else:
        st.error("Scan failed. Check the error below.")
        st.code(result.stderr or result.stdout)

if REPORT.exists():
    try:
        report = json.loads(REPORT.read_text())
        alerts = report.get("alerts", [])
        total = report.get("total_log_lines", 0)
        high = sum(a.get("severity") == "HIGH" for a in alerts)
        medium = sum(a.get("severity") == "MEDIUM" for a in alerts)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Log Lines Analyzed", total)
        c2.metric("Total Alerts", len(alerts))
        c3.metric("High Severity", high)
        c4.metric("Medium Severity", medium)

        st.subheader("Detected Security Events")
        if alerts:
            st.dataframe(alerts, use_container_width=True, hide_index=True)
        else:
            st.info("No alerts found in the report.")

        st.subheader("JSON Security Report")
        st.json(report)
        st.download_button(
            "Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name="security_report.json",
            mime="application/json"
        )
        st.caption(report.get("note", ""))
    except (json.JSONDecodeError, OSError) as e:
        st.error(f"Could not read report: {e}")
else:
    st.warning("Report not found. Click Run Detection Scan to generate it.")
