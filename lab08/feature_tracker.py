"""
Lab 08 — The Agentic SDLC Loop (Capstone)
===========================================
A feature request tracker. Participants wire up the full agentic loop:
an issue comes in → agent plans → codes → tests → reviews → secures → deploys.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeatureStatus(Enum):
    PROPOSED = "proposed"
    RESEARCHING = "researching"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    REJECTED = "rejected"


@dataclass
class FeatureRequest:
    feature_id: str
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: FeatureStatus = FeatureStatus.PROPOSED
    requested_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    sdlc_log: list[dict] = field(default_factory=list)

    def log_phase(self, phase: str, details: str, agent: str = "human") -> None:
        self.sdlc_log.append({
            "phase": phase,
            "details": details,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
        })

    def advance_to(self, status: FeatureStatus, details: str = "", agent: str = "human") -> None:
        self.log_phase(status.value, details, agent)
        self.status = status


@dataclass
class SDLCPlan:
    feature: FeatureRequest
    research_notes: str = ""
    implementation_plan: list[str] = field(default_factory=list)
    files_to_create: list[str] = field(default_factory=list)
    files_to_modify: list[str] = field(default_factory=list)
    tests_to_write: list[str] = field(default_factory=list)
    security_checks: list[str] = field(default_factory=list)
    review_criteria: list[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high


class FeatureTracker:
    """Tracks features through the SDLC pipeline."""

    def __init__(self):
        self._features: dict[str, FeatureRequest] = {}
        self._plans: dict[str, SDLCPlan] = {}
        self._next_id = 1

    def submit_feature(self, title: str, description: str,
                       priority: Priority = Priority.MEDIUM,
                       requested_by: str = "") -> FeatureRequest:
        feature_id = f"FEAT-{self._next_id:04d}"
        self._next_id += 1
        feature = FeatureRequest(
            feature_id=feature_id,
            title=title,
            description=description,
            priority=priority,
            requested_by=requested_by,
        )
        feature.log_phase("proposed", f"Feature submitted: {title}")
        self._features[feature_id] = feature
        return feature

    def get_feature(self, feature_id: str) -> Optional[FeatureRequest]:
        return self._features.get(feature_id)

    def create_plan(self, feature_id: str) -> Optional[SDLCPlan]:
        feature = self.get_feature(feature_id)
        if feature is None:
            return None
        plan = SDLCPlan(feature=feature)
        self._plans[feature_id] = plan
        feature.advance_to(FeatureStatus.RESEARCHING, "Plan created")
        return plan

    def get_plan(self, feature_id: str) -> Optional[SDLCPlan]:
        return self._plans.get(feature_id)

    def get_pipeline_status(self) -> dict:
        """Returns count of features at each SDLC stage."""
        status_counts = {s.value: 0 for s in FeatureStatus}
        for feature in self._features.values():
            status_counts[feature.status.value] += 1
        return {
            "total_features": len(self._features),
            "pipeline": status_counts,
            "by_priority": self._count_by_priority(),
        }

    def _count_by_priority(self) -> dict:
        counts = {p.value: 0 for p in Priority}
        for feature in self._features.values():
            counts[feature.priority.value] += 1
        return counts

    def get_features_at_stage(self, status: FeatureStatus) -> list[FeatureRequest]:
        return [f for f in self._features.values() if f.status == status]

    def get_sdlc_timeline(self, feature_id: str) -> list[dict]:
        """Returns the full SDLC log for a feature."""
        feature = self.get_feature(feature_id)
        if feature is None:
            return []
        return feature.sdlc_log
