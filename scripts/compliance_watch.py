#!/usr/bin/env python3
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCES = {
    "OFAC": "https://ofac.treasury.gov/sanctions-programs-and-country-information",
    "BIS_EAR": "https://www.bis.gov/regulations/ear",
    "DDTC_ITAR": "https://deccs.pmddtc.state.gov/deccs?id=ddtc_search&q=itar",
    "DCSA_FOCI": "https://www.dcsa.mil/Industrial-Security/Entity-Vetting-Facility-Clearances-FOCI/",
    "FAA_SPACE": "https://www.faa.gov/space/licenses/licensing_process",
    "ITU_SPACE": "https://www.itu.int/ITU-R/space/e-submission",
    "UNOOSA_SPACE_LAW": "https://www.unoosa.org/oosa/SpaceLaw/treaties.html",
    "NIST_CSF": "https://www.nist.gov/cyberframework",
    "CISA": "https://www.cisa.gov/",
}

OUT = Path("artifacts/compliance-watch.json")


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "SonoxoComplianceWatch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            return {
                "ok": 200 <= resp.status < 400,
                "status": resp.status,
                "final_url": resp.geturl(),
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "status": None, "error": str(exc)}


def main() -> int:
    checked_at = datetime.now(timezone.utc).isoformat()
    results = {name: fetch(url) | {"source": url} for name, url in SOURCES.items()}
    failed = sorted(name for name, result in results.items() if not result.get("ok"))
    payload = {
        "checked_at": checked_at,
        "policy": "authoritative-source-availability-and-change-evidence",
        "results": results,
        "failed_sources": failed,
        "status": "attention_required" if failed else "ok",
        "note": "This watcher verifies source availability and records content hashes. It does not by itself determine legal applicability or certify compliance.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
