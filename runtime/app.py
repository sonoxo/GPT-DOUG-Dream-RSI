import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_PATH = APP_ROOT / "ecosystem" / "ontology" / "gptdoug-all-kinds.yaml"

app = FastAPI(
    title="GPTDoug ALL KINDS Swarm",
    version="0.1.0",
    description="Governed swarm orchestration surface for Dream-RSI + Zyra + XUNIA + Palantir-compatible ontology adapters.",
)

MAX_AGENTS = max(1, int(os.getenv("GPTDOUG_MAX_PARALLEL_AGENTS", "32")))
RULE = "gptdougALLKINDSFOREVERRULE"
PARENT_RULE = "ForeverRuleGPTDOUGLLMMAXMIMIXK"

ROLES = [
    "ontology_mapper",
    "repository_mapper",
    "documentation_agent",
    "compliance_mapper",
    "evaluator",
    "critic",
    "provenance_agent",
    "security_reviewer",
    "integration_agent",
]

class SwarmRequest(BaseModel):
    objective: str = Field(min_length=3, max_length=4000)
    requested_agents: int | None = Field(default=None, ge=1, le=10000)
    repositories: list[str] = []
    jurisdictions: list[str] = []

class ComplianceRequest(BaseModel):
    system_name: str
    jurisdictions: list[str] = []
    use_case: str
    risk_tier: str | None = None

@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "gptdoug-all-kinds-swarm",
        "rule": RULE,
        "parent_rule": PARENT_RULE,
        "status": "online",
        "max_parallel_agents": MAX_AGENTS,
        "palantir_adapter": "configured-by-environment",
    }

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/ontology")
def ontology() -> dict[str, Any]:
    if not ONTOLOGY_PATH.exists():
        raise HTTPException(status_code=404, detail="ontology manifest missing")
    return {
        "name": RULE,
        "format": "yaml",
        "source": str(ONTOLOGY_PATH.relative_to(APP_ROOT)),
        "content": ONTOLOGY_PATH.read_text(encoding="utf-8"),
    }

@app.post("/swarm/plan")
def swarm_plan(request: SwarmRequest) -> dict[str, Any]:
    requested = request.requested_agents or MAX_AGENTS
    count = min(requested, MAX_AGENTS)
    workers = [
        {
            "agent_id": f"agent-{i+1:03d}",
            "role": ROLES[i % len(ROLES)],
            "authority": "proposal-and-evaluation-only",
        }
        for i in range(count)
    ]
    return {
        "run_id": str(uuid.uuid4()),
        "rule": RULE,
        "objective": request.objective,
        "repositories": request.repositories,
        "jurisdictions": request.jurisdictions,
        "parallel_agents": count,
        "workers": workers,
        "pipeline": [
            "ingest_context",
            "branch_candidates",
            "parallel_exploration",
            "evaluate_candidates",
            "security_and_compliance_review",
            "retain_diverse_winners",
            "record_lineage",
            "dream_replay",
            "improve_policy",
        ],
        "promotion": "review-required",
    }

@app.post("/compliance/map")
def compliance_map(request: ComplianceRequest) -> dict[str, Any]:
    return {
        "system": request.system_name,
        "use_case": request.use_case,
        "risk_tier": request.risk_tier or "unassessed",
        "jurisdictions": request.jurisdictions,
        "status": "scope-required-before-compliance-claim",
        "workflow": [
            "identify_applicable_authorities",
            "retrieve_current_official_rules",
            "map_obligations_to_controls",
            "collect_evidence",
            "evaluate_controls",
            "human_review_when_required",
            "release_or_block",
            "continuous_change_monitoring",
        ],
    }

@app.get("/palantir/deployment-plan")
def palantir_deployment_plan() -> dict[str, Any]:
    host = os.getenv("PALANTIR_FOUNDRY_HOST")
    ontology_rid = os.getenv("PALANTIR_ONTOLOGY_RID")
    configured = bool(host and ontology_rid)
    return {
        "configured": configured,
        "host_present": bool(host),
        "ontology_rid_present": bool(ontology_rid),
        "secret_present": bool(os.getenv("PALANTIR_TOKEN")),
        "required_objects": [
            "AI_System", "Agent", "Swarm", "Organization", "Agency", "Repository",
            "Production", "Model", "Dataset", "Document", "Policy", "Regulation",
            "Control", "Evaluation", "Evidence", "Incident", "HumanApproval"
        ],
        "note": "Actual Foundry ontology mutation requires a connected authorized Palantir session or deployment credentials supplied outside source control.",
    }
