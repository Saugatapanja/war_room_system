"""
Data models for the war room launch decision system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from datetime import datetime, date
import json


@dataclass
class MetricPoint:
    """Single metric data point."""
    date: str
    value: float
    
    def to_dict(self):
        return {"date": self.date, "value": self.value}


@dataclass
class TimeSeries:
    """Time series metric data."""
    metric_name: str
    points: List[MetricPoint]
    unit: str
    baseline: float  # Previous value for comparison
    
    def to_dict(self):
        return {
            "metric_name": self.metric_name,
            "points": [p.to_dict() for p in self.points],
            "unit": self.unit,
            "baseline": self.baseline
        }


@dataclass
class UserFeedback:
    """Individual user feedback entry."""
    timestamp: str
    sentiment: Literal["positive", "neutral", "negative"]
    message: str
    category: str  # e.g., "performance", "bug", "feature", "ux"
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "sentiment": self.sentiment,
            "message": self.message,
            "category": self.category
        }


@dataclass
class KnownIssue:
    """Known issue from release notes."""
    title: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    affected_users: str
    mitigation: str
    
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "affected_users": self.affected_users,
            "mitigation": self.mitigation
        }


@dataclass
class DashboardData:
    """Complete mock dashboard data."""
    date_range_start: str
    date_range_end: str
    metrics: Dict[str, TimeSeries]
    feedback: List[UserFeedback]
    known_issues: List[KnownIssue]
    feature_description: str
    rollout_percentage: float
    
    def to_dict(self):
        return {
            "date_range_start": self.date_range_start,
            "date_range_end": self.date_range_end,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "feedback": [f.to_dict() for f in self.feedback],
            "known_issues": [issue.to_dict() for issue in self.known_issues],
            "feature_description": self.feature_description,
            "rollout_percentage": self.rollout_percentage
        }


@dataclass
class AgentAnalysis:
    """Result of an agent's analysis."""
    agent_name: str
    analysis: Dict
    recommendation: Literal["proceed", "pause", "rollback"]
    confidence: float  # 0-1
    reasoning: str
    
    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "analysis": self.analysis,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


@dataclass
class Risk:
    """Identified risk item."""
    risk_id: str
    title: str
    description: str
    likelihood: Literal["low", "medium", "high"]
    impact: Literal["low", "medium", "high", "critical"]
    mitigation: str
    owner: str
    
    def to_dict(self):
        return {
            "risk_id": self.risk_id,
            "title": self.title,
            "description": self.description,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "mitigation": self.mitigation,
            "owner": self.owner
        }


@dataclass
class ActionItem:
    """Action item in the action plan."""
    action_id: str
    description: str
    owner: str
    due_in_hours: int
    priority: Literal["low", "medium", "high", "critical"]
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "action_id": self.action_id,
            "description": self.description,
            "owner": self.owner,
            "due_in_hours": self.due_in_hours,
            "priority": self.priority,
            "dependencies": self.dependencies
        }


@dataclass
class CommunicationPlan:
    """Communication strategy."""
    internal_message: str
    external_message: str
    channels: List[str]
    audience: List[str]
    timing: str
    escalation_contact: str
    
    def to_dict(self):
        return {
            "internal_message": self.internal_message,
            "external_message": self.external_message,
            "channels": self.channels,
            "audience": self.audience,
            "timing": self.timing,
            "escalation_contact": self.escalation_contact
        }


@dataclass
class LaunchDecision:
    """Final launch decision output."""
    decision: Literal["proceed", "pause", "rollback"]
    timestamp: str
    rationale: str
    metric_drivers: Dict[str, str]  # metric_name -> brief analysis
    feedback_summary: Dict[str, int]  # sentiment -> count
    agent_recommendations: List[AgentAnalysis]
    risk_register: List[Risk]
    action_plan: List[ActionItem]
    communication_plan: CommunicationPlan
    overall_confidence: float
    confidence_factors: Dict[str, str]  # what would increase confidence
    
    def to_dict(self):
        return {
            "decision": self.decision,
            "timestamp": self.timestamp,
            "rationale": self.rationale,
            "metric_drivers": self.metric_drivers,
            "feedback_summary": self.feedback_summary,
            "agent_recommendations": [a.to_dict() for a in self.agent_recommendations],
            "risk_register": [r.to_dict() for r in self.risk_register],
            "action_plan": [a.to_dict() for a in self.action_plan],
            "communication_plan": self.communication_plan.to_dict(),
            "overall_confidence": self.overall_confidence,
            "confidence_factors": self.confidence_factors
        }
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)
