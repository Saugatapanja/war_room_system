"""
War room orchestrator - coordinates agents and synthesizes final decision.
"""

import logging
from datetime import datetime
from typing import List, Dict
from src.models import (
    DashboardData, AgentAnalysis, LaunchDecision, Risk, ActionItem, 
    CommunicationPlan
)
from src.agents import (
    ProductManagerAgent, DataAnalystAgent, MarketingCommsAgent, RiskCriticAgent
)

logger = logging.getLogger(__name__)


class WarRoomOrchestrator:
    """
    Orchestrator that coordinates all agents for the launch decision.
    Manages the workflow: data->agents->synthesis->decision.
    """
    
    def __init__(self):
        self.agents = [
            ProductManagerAgent(),
            DataAnalystAgent(),
            MarketingCommsAgent(),
            RiskCriticAgent()
        ]
        self.agent_analyses: List[AgentAnalysis] = []
        self.final_decision = None
    
    def run_war_room(self, dashboard: DashboardData) -> LaunchDecision:
        """
        Execute the full war room analysis and decision process.
        
        Returns LaunchDecision with structured output.
        """
        logger.info("=" * 80)
        logger.info("STARTING WAR ROOM ANALYSIS")
        logger.info("=" * 80)
        logger.info(f"Feature: {dashboard.feature_description}")
        logger.info(f"Rollout: {dashboard.rollout_percentage * 100}% of users")
        logger.info(f"Date Range: {dashboard.date_range_start} to {dashboard.date_range_end}")
        logger.info("")
        
        # Phase 1: Agent Analysis
        logger.info("PHASE 1: AGENT ANALYSES")
        logger.info("-" * 80)
        self.agent_analyses = []
        for agent in self.agents:
            logger.info(f"\n[{agent.name}] Beginning analysis...")
            analysis = agent.analyze(dashboard)
            self.agent_analyses.append(analysis)
            
            logger.info(f"  Recommendation: {analysis.recommendation.upper()}")
            logger.info(f"  Confidence: {analysis.confidence:.1%}")
            logger.info(f"  Reasoning: {analysis.reasoning}")
            logger.info("")
        
        # Phase 2: Synthesize recommendations
        logger.info("\nPHASE 2: SYNTHESIZING AGENT INPUTS")
        logger.info("-" * 80)
        decision = self._synthesize_decision(dashboard)
        logger.info(f"\nFinal Decision: {decision.decision.upper()}")
        logger.info(f"Overall Confidence: {decision.overall_confidence:.1%}")
        
        return decision
    
    def _synthesize_decision(self, dashboard: DashboardData) -> LaunchDecision:
        """
        Synthesize all agent analyses into final decision.
        """
        # Count recommendations
        rec_counts = {
            "proceed": sum(1 for a in self.agent_analyses if a.recommendation == "proceed"),
            "pause": sum(1 for a in self.agent_analyses if a.recommendation == "pause"),
            "rollback": sum(1 for a in self.agent_analyses if a.recommendation == "rollback")
        }
        
        logger.info(f"  Proceed votes: {rec_counts['proceed']}")
        logger.info(f"  Pause votes: {rec_counts['pause']}")
        logger.info(f"  Rollback votes: {rec_counts['rollback']}")
        
        # Decision logic: prioritize risk/safety
        if rec_counts["rollback"] > 0:
            final_decision = "rollback"
            logger.info("  → Rollback flagged by risk agent - prioritizing safety")
        elif rec_counts["pause"] >= 2:
            final_decision = "pause"
            logger.info("  → Pause consensus (2+ agents) - need more information")
        elif rec_counts["proceed"] >= 2 and rec_counts["rollback"] == 0:
            final_decision = "proceed"
            logger.info("  → Proceed consensus - proceed with caution")
        else:
            # Tiebreaker: favor caution
            final_decision = "pause"
            logger.info("  → Unclear consensus - defaulting to pause (safety first)")
        
        # Calculate overall confidence
        avg_confidence = sum(a.confidence for a in self.agent_analyses) / len(self.agent_analyses)
        
        # Adjust confidence based on consensus
        if rec_counts["rollback"] > 0 and final_decision != "rollback":
            avg_confidence *= 0.7  # Reduce confidence if we're overriding rollback rec
        
        if rec_counts["proceed"] == len(self.agent_analyses):
            avg_confidence = min(1.0, avg_confidence * 1.1)  # Boost if unanimous
        
        # Extract metric drivers
        metric_drivers = self._extract_metric_drivers(dashboard)
        
        # Count feedback sentiment
        feedback_summary = {
            "positive": sum(1 for f in dashboard.feedback if f.sentiment == "positive"),
            "neutral": sum(1 for f in dashboard.feedback if f.sentiment == "neutral"),
            "negative": sum(1 for f in dashboard.feedback if f.sentiment == "negative"),
            "total": len(dashboard.feedback)
        }
        
        # Build rationale
        rationale = self._build_rationale(final_decision, metric_drivers, feedback_summary)
        
        # Identify risks
        risk_register = self._build_risk_register(dashboard)
        
        # Build action plan
        action_plan = self._build_action_plan(final_decision, dashboard)
        
        # Build communication plan
        communication_plan = self._build_communication_plan(final_decision, feedback_summary)
        
        # Confidence factors
        confidence_factors = self._identify_confidence_factors(avg_confidence)
        
        decision = LaunchDecision(
            decision=final_decision,
            timestamp=datetime.now().isoformat(),
            rationale=rationale,
            metric_drivers=metric_drivers,
            feedback_summary=feedback_summary,
            agent_recommendations=self.agent_analyses,
            risk_register=risk_register,
            action_plan=action_plan,
            communication_plan=communication_plan,
            overall_confidence=avg_confidence,
            confidence_factors=confidence_factors
        )
        
        self.final_decision = decision
        return decision
    
    def _extract_metric_drivers(self, dashboard: DashboardData) -> Dict[str, str]:
        """Extract key metric insights."""
        drivers = {}
        
        if "crash_rate" in dashboard.metrics:
            crash_ts = dashboard.metrics["crash_rate"]
            latest = crash_ts.points[-1].value if crash_ts.points else 0
            baseline = crash_ts.baseline
            drivers["crash_rate"] = f"{latest:.1%} (was {baseline:.1%}) - {'+' if latest > baseline else ''}{((latest - baseline) / baseline * 100):.0f}%"
        
        if "d1_retention" in dashboard.metrics:
            ret_ts = dashboard.metrics["d1_retention"]
            latest = ret_ts.points[-1].value if ret_ts.points else 0
            baseline = ret_ts.baseline
            drivers["d1_retention"] = f"{latest:.1%} (was {baseline:.1%}) - {((latest - baseline) / baseline * 100):.0f}%"
        
        if "api_latency_p95" in dashboard.metrics:
            lat_ts = dashboard.metrics["api_latency_p95"]
            latest = lat_ts.points[-1].value if lat_ts.points else 0
            baseline = lat_ts.baseline
            drivers["api_latency_p95"] = f"{latest:.0f}ms (was {baseline:.0f}ms) - +{((latest - baseline) / baseline * 100):.0f}% slower"
        
        if "activation_rate" in dashboard.metrics:
            act_ts = dashboard.metrics["activation_rate"]
            latest = act_ts.points[-1].value if act_ts.points else 0
            baseline = act_ts.baseline
            drivers["activation_rate"] = f"{latest:.1%} (target was {baseline:.1%})"
        
        return drivers
    
    def _build_rationale(self, decision: str, metric_drivers: Dict[str, str], 
                        feedback_summary: Dict) -> str:
        """Build executive summary rationale."""
        
        if decision == "rollback":
            return (f"ROLLBACK RECOMMENDED due to critical issues identified in testing phase. "
                   f"Crash rate elevated to {metric_drivers.get('crash_rate', 'unknown')}, "
                   f"retention declining ({metric_drivers.get('d1_retention', 'unknown')}), "
                   f"and race condition in payment processing poses financial risk. "
                   f"Recommend full rollback, issue remediation, and re-launch in 48-72 hours.")
        
        elif decision == "pause":
            return (f"PAUSE RECOMMENDED for stability hardening. "
                   f"While adoption looks reasonable, elevated crash rate ({metric_drivers.get('crash_rate', 'unknown')}), "
                   f"API latency concerns ({metric_drivers.get('api_latency_p95', 'unknown')}), "
                   f"and {feedback_summary['negative']} negative feedback entries "
                   f"warrant further optimization before full rollout. "
                   f"Recommend 24-48 hour pause for hotfixes and monitoring.")
        
        else:  # proceed
            return (f"PROCEED WITH CAUTION. Feature shows acceptable metrics: "
                   f"activation {metric_drivers.get('activation_rate', 'unknown')}, "
                   f"retention {metric_drivers.get('d1_retention', 'unknown')}. "
                   f"However, continue monitoring: {feedback_summary['negative']} negative feedback entries and "
                   f"elevated latency ({metric_drivers.get('api_latency_p95', 'unknown')}). "
                   f"Be prepared to pause if trends worsen.")
    
    def _build_risk_register(self, dashboard: DashboardData) -> List[Risk]:
        """Build risk register from known issues and analysis."""
        risks = []
        
        for idx, issue in enumerate(dashboard.known_issues):
            risk = Risk(
                risk_id=f"R{idx + 1}",
                title=issue.title,
                description=issue.description,
                likelihood="high" if issue.severity in ["critical", "high"] else "medium",
                impact=issue.severity,
                mitigation=issue.mitigation,
                owner="Engineering Lead"
            )
            risks.append(risk)
        
        # Add data-driven risks
        if "crash_rate" in dashboard.metrics:
            crash_ts = dashboard.metrics["crash_rate"]
            latest_crash = crash_ts.points[-1].value if crash_ts.points else 0
            if latest_crash > 0.02:
                risks.append(Risk(
                    risk_id=f"R{len(risks) + 1}",
                    title="Elevated crash rate trending upward",
                    description=f"Crash rate at {latest_crash:.1%}, up from {crash_ts.baseline:.1%} baseline. "
                               "Trend is worsening, indicating potential deep issue.",
                    likelihood="high",
                    impact="high",
                    mitigation="Implement aggressive monitoring, prepare rollback procedure",
                    owner="Platform Team"
                ))
        
        # Negative feedback risk
        negative_count = sum(1 for f in dashboard.feedback if f.sentiment == "negative")
        if negative_count > 10:
            risks.append(Risk(
                risk_id=f"R{len(risks) + 1}",
                title="Significant customer dissatisfaction",
                description=f"{negative_count} negative feedback entries with repeated crash/latency complaints.",
                likelihood="medium",
                impact="high",
                mitigation="Escalate support, prioritize issue resolution, prepare communication",
                owner="Support Lead"
            ))
        
        return risks
    
    def _build_action_plan(self, decision: str, dashboard: DashboardData) -> List[ActionItem]:
        """Build 24-48 hour action plan."""
        actions = []
        
        if decision == "rollback":
            actions = [
                ActionItem(
                    action_id="A1",
                    description="Initiate immediate rollback process - disable feature flag",
                    owner="Platform Engineering",
                    due_in_hours=1,
                    priority="critical"
                ),
                ActionItem(
                    action_id="A2",
                    description="Investigate race condition in payment processing - create incident ticket",
                    owner="Database Team",
                    due_in_hours=2,
                    priority="critical",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A3",
                    description="Performance analysis on memory leak and query optimization",
                    owner="Engineering Lead",
                    due_in_hours=4,
                    priority="critical",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A4",
                    description="Customer outreach - explain rollback, provide ETA",
                    owner="Customer Success",
                    due_in_hours=2,
                    priority="high",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A5",
                    description="Root cause analysis meeting - all teams, document findings",
                    owner="Product Manager",
                    due_in_hours=8,
                    priority="high"
                ),
                ActionItem(
                    action_id="A6",
                    description="Prepare relaunch strategy with fixes - target 48-72 hour patch",
                    owner="Product Manager",
                    due_in_hours=24,
                    priority="high",
                    dependencies=["A3", "A5"]
                ),
            ]
        
        elif decision == "pause":
            actions = [
                ActionItem(
                    action_id="A1",
                    description="Pause feature rollout - scale back to current 40% of users",
                    owner="Platform Engineering",
                    due_in_hours=2,
                    priority="high"
                ),
                ActionItem(
                    action_id="A2",
                    description="Investigate latency spike - analyze query performance and indexing",
                    owner="Database Team",
                    due_in_hours=4,
                    priority="high",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A3",
                    description="Address memory leak - deploy hotfix as urgent patch",
                    owner="Backend Team",
                    due_in_hours=6,
                    priority="high",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A4",
                    description="Enhanced monitoring - instrument crash/latency/payment metrics",
                    owner="Observability Team",
                    due_in_hours=4,
                    priority="high"
                ),
                ActionItem(
                    action_id="A5",
                    description="Customer communication - transparency on pause, expected fixes",
                    owner="Marketing",
                    due_in_hours=3,
                    priority="high",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A6",
                    description="Stabilization validation - confirm metrics improving for 24 hours",
                    owner="Product Manager",
                    due_in_hours=30,
                    priority="high",
                    dependencies=["A2", "A3"]
                ),
                ActionItem(
                    action_id="A7",
                    description="Approval meeting - decide proceed vs. full rollback based on 24h data",
                    owner="Product Manager",
                    due_in_hours=30,
                    priority="high",
                    dependencies=["A6"]
                ),
            ]
        
        else:  # proceed
            actions = [
                ActionItem(
                    action_id="A1",
                    description="Deploy monitoring alerts - crash rate, latency, payment transactions",
                    owner="Observability Team",
                    due_in_hours=2,
                    priority="high"
                ),
                ActionItem(
                    action_id="A2",
                    description="Begin gradual rollout increase - 40% -> 60% over 12 hours",
                    owner="Platform Engineering",
                    due_in_hours=4,
                    priority="high"
                ),
                ActionItem(
                    action_id="A3",
                    description="Support team readiness - prepare for potential escalations",
                    owner="Support Lead",
                    due_in_hours=2,
                    priority="high"
                ),
                ActionItem(
                    action_id="A4",
                    description="Customer communication - transparency on rollout plan",
                    owner="Marketing",
                    due_in_hours=2,
                    priority="high"
                ),
                ActionItem(
                    action_id="A5",
                    description="Hourly health checks - monitor key metrics during rollout",
                    owner="Product Manager",
                    due_in_hours=12,
                    priority="high",
                    dependencies=["A1"]
                ),
                ActionItem(
                    action_id="A6",
                    description="Kill switch preparation - feature flag configured for rapid disable",
                    owner="Platform Engineering",
                    due_in_hours=2,
                    priority="high"
                ),
                ActionItem(
                    action_id="A7",
                    description="Decision point at 24h - confirm proceed to full rollout or pause",
                    owner="Product Manager",
                    due_in_hours=24,
                    priority="high",
                    dependencies=["A5"]
                ),
            ]
        
        return actions
    
    def _build_communication_plan(self, decision: str, feedback_summary: Dict) -> CommunicationPlan:
        """Build internal and external communication strategy."""
        
        if decision == "rollback":
            return CommunicationPlan(
                internal_message=(
                    "URGENT: We are rolling back the Smart Recommendations feature effective immediately. "
                    "Critical issues identified in production: payment processing race condition, elevated crash rate, and memory leaks. "
                    "All 40% of users currently using the feature will revert to previous experience. "
                    "Engineering team beginning root cause investigation. Relaunch planned for 48-72 hours pending validation."
                ),
                external_message=(
                    "We've temporarily disabled the Smart Recommendations feature to ensure platform stability. "
                    "We identified and are fixing some technical issues that affected a small portion of our users. "
                    "Your experience has been restored to normal, and we'll relaunch an improved version shortly. "
                    "Thank you for your patience and feedback that helped us catch this."
                ),
                channels=["Email", "In-App Notification", "Status Page", "Twitter"],
                audience=["Internal Team", "All Affected Users", "Broader Customer Base"],
                timing="Immediate - within 30 minutes of decision",
                escalation_contact="Chief Product Officer"
            )
        
        elif decision == "pause":
            return CommunicationPlan(
                internal_message=(
                    "Smart Recommendations feature rollout is paused for optimization. "
                    f"Current users (40%) will remain unaffected. Issues identified: latency increase, "
                    "memory leak, and crash rate trending up. Engineering team implementing hotfixes. "
                    "Expect resume decision within 24-48 hours."
                ),
                external_message=(
                    "We're pausing the rollout of Smart Recommendations while we fine-tune performance. "
                    "If you're already using the feature, no changes to your experience. "
                    "We're committed to shipping a high-quality, stable feature to everyone. "
                    "More updates within 24 hours."
                ),
                channels=["Email", "In-App Notification", "Status Page"],
                audience=["Internal Team", "Early Users", "Waiting Users"],
                timing="Within 2 hours of decision",
                escalation_contact="VP of Product"
            )
        
        else:  # proceed
            return CommunicationPlan(
                internal_message=(
                    "Smart Recommendations feature rollout continues. All metrics within acceptable ranges. "
                    "Team will gradually increase from 40% -> 60% -> 100% over 24-48 hours. "
                    "Continue monitoring crash/latency/payment metrics every hour. Prepare to pause if thresholds exceeded. "
                    "Excellent work team!"
                ),
                external_message=(
                    "Smart Recommendations is rolling out to more users. Due to overwhelming early feedback, "
                    "we're gradually expanding access to ensure service quality for everyone. "
                    "If you don't have it yet, you'll get it soon!"
                ),
                channels=["Email", "In-App Notification", "Blog", "Twitter"],
                audience=["Internal Team", "Waiting Users"],
                timing="Within 4 hours of decision",
                escalation_contact="VP of Product"
            )
    
    def _identify_confidence_factors(self, confidence: float) -> Dict[str, str]:
        """Identify what would increase decision confidence."""
        factors = {}
        
        if confidence < 0.7:
            factors["more_data"] = "Extend observation period to 21 days for more stable trend data"
            factors["monitoring"] = "Deploy real-time alerting on crash/latency spikes"
            factors["testing"] = "Run controlled load tests with current production metrics"
        
        if confidence < 0.8:
            factors["stability"] = "Ensure crash rate trending downward for 12+ hours"
            factors["retention"] = "Confirm D1 retention stabilizes above 50%"
            factors["support"] = "Monitor support queue - ensure not overwhelmed"
        
        factors["consensus"] = "Align leadership on risk tolerance and decision threshold"
        factors["communication"] = "Validate messaging with customer success team"
        
        return factors
