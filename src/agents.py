"""
Agent implementations for the war room decision system.
Each agent has specific responsibilities and analysis methods.
"""

import json
import logging
from typing import Dict, List
from src.models import (
    DashboardData, AgentAnalysis, KnownIssue, TimeSeries, UserFeedback
)
from src.tools import AnomalyDetector, SentimentAnalyzer, MetricAggregator
from src.llm import GeminiClient

logger = logging.getLogger(__name__)


class Agent:
    """Base agent class."""
    
    def __init__(self, name: str):
        self.name = name
        self.analysis_log = []
        self.llm_client = GeminiClient()
    
    def log_step(self, step: str):
        """Log an analysis step."""
        logger.info(f"[{self.name}] {step}")
        self.analysis_log.append(step)

    def llm_insight(self, prompt: str) -> str:
        """Request a short insight from Gemini if configured."""
        if not self.llm_client.is_configured():
            self.log_step("Gemini API not configured; skipping LLM insight.")
            return ""

        self.log_step("Calling Gemini LLM for additional reasoning")
        try:
            response = self.llm_client.generate_text(prompt)
            self.log_step("Received Gemini LLM insight")
            return response.strip()
        except Exception as exc:
            self.log_step(f"Gemini request failed: {exc}")
            return ""

    def _build_llm_prompt(self, dashboard: DashboardData, analysis: Dict, recommendation: str) -> str:
        """Build a concise prompt for Gemini using the current agent context."""
        analysis_text = json.dumps(analysis, default=str, indent=2)
        if len(analysis_text) > 12000:
            analysis_text = analysis_text[:12000] + "..."

        return (
            f"You are the {self.name} agent in a PurpleMerit launch war room.\n"
            f"Feature: {dashboard.feature_description}\n"
            f"Rollout percentage: {dashboard.rollout_percentage * 100:.0f}%\n"
            f"Recommendation: {recommendation}\n"
            f"Provide a concise supporting rationale, highlight top risks, and suggest any additional actions or communication notes.\n"
            f"Analysis summary:\n{analysis_text}"
        )

    def _append_llm_insight(self, dashboard: DashboardData, analysis: Dict, recommendation: str, reasoning: str) -> str:
        """Append an optional Gemini-generated insight to reasoning if available."""
        prompt = self._build_llm_prompt(dashboard, analysis, recommendation)
        llm_text = self.llm_insight(prompt)
        if llm_text:
            analysis["llm_summary"] = llm_text
            analysis["llm_used"] = True
            return f"{reasoning} LLM note: {llm_text}"
        analysis["llm_used"] = False
        return reasoning


class ProductManagerAgent(Agent):
    """
    Product Manager Agent - defines success criteria, user impact, and go/no-go framing.
    """
    
    def __init__(self):
        super().__init__("ProductManager")
        self.success_criteria = {
            "adoption_rate": 0.15,  # 15% of users should activate feature
            "crash_rate_threshold": 0.02,  # 2% max crash rate
            "negative_feedback_threshold": 0.30,  # 30% negative feedback acceptable
            "retention_impact": -0.05,  # Up to 5% D1 retention loss acceptable
            "payment_success_rate": 0.98  # 98% payment success
        }
    
    def analyze(self, dashboard: DashboardData) -> AgentAnalysis:
        """
        Analyze from product perspective: feature adoption, user impact, market fit.
        """
        self.log_step("Starting product analysis")
        analysis = {}
        
        # 1. Feature adoption analysis
        self.log_step("Analyzing feature adoption metrics")
        if "activation_rate" in dashboard.metrics:
            activation_ts = dashboard.metrics["activation_rate"]
            activation_data = AnomalyDetector.trend_analysis(activation_ts)
            analysis["activation"] = activation_data
            
            latest_activation = activation_ts.points[-1].value if activation_ts.points else 0
            if latest_activation >= self.success_criteria["adoption_rate"]:
                adoption_status = "meeting_targets"
            else:
                adoption_status = "below_targets"
            analysis["adoption_status"] = adoption_status
        
        # 2. Stability assessment
        self.log_step("Assessing system stability")
        stability_risks = []
        
        if "crash_rate" in dashboard.metrics:
            crash_ts = dashboard.metrics["crash_rate"]
            latest_crash = crash_ts.points[-1].value if crash_ts.points else 0
            anomaly_result = AnomalyDetector.detect_anomalies(crash_ts)
            analysis["crash_rate"] = anomaly_result
            
            if latest_crash > self.success_criteria["crash_rate_threshold"]:
                stability_risks.append(f"Crash rate {latest_crash:.2%} exceeds threshold")
        
        if "error_rate" in dashboard.metrics:
            error_ts = dashboard.metrics["error_rate"]
            anomaly_result = AnomalyDetector.detect_anomalies(error_ts)
            analysis["error_rate"] = anomaly_result
        
        analysis["stability_risks"] = stability_risks
        
        # 3. User feedback impact
        self.log_step("Analyzing user feedback impact")
        sentiment_summary = SentimentAnalyzer.summarize_feedback(dashboard.feedback)
        analysis["user_sentiment"] = sentiment_summary
        
        negative_pct = sentiment_summary["sentiment_negative_percent"]
        user_impact = "negative" if negative_pct > self.success_criteria["negative_feedback_threshold"] else "acceptable"
        analysis["user_impact"] = user_impact
        
        # 4. Key user feedback themes
        themes = SentimentAnalyzer.theme_extraction(dashboard.feedback)
        analysis["feedback_themes"] = themes
        
        # 5. Known issues assessment
        self.log_step("Reviewing known issues")
        critical_known_issues = [ki for ki in dashboard.known_issues if ki.severity in ["high", "critical"]]
        analysis["known_issues_critical"] = len(critical_known_issues)
        analysis["known_issues_details"] = [ki.to_dict() for ki in critical_known_issues]
        
        # Decision logic
        self.log_step("Making recommendation")
        
        recommendation = self._make_recommendation(analysis)
        confidence = self._calculate_confidence(analysis)
        
        reasoning = self._build_reasoning(analysis, recommendation)
        reasoning = self._append_llm_insight(dashboard, analysis, recommendation, reasoning)
        
        return AgentAnalysis(
            agent_name=self.name,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _make_recommendation(self, analysis: Dict) -> str:
        """Make go/no-go recommendation based on analysis."""
        # Red flags for rollback
        if analysis.get("known_issues_critical", 0) > 0:
            critical_severity = any(ki["severity"] == "critical" for ki in analysis.get("known_issues_details", []))
            if critical_severity:
                return "rollback"
        
        if analysis.get("user_impact") == "negative" and analysis.get("adoption_status") == "below_targets":
            return "pause"
        
        stability_risks = analysis.get("stability_risks", [])
        if len(stability_risks) > 0:
            return "pause"
        
        # Green flags for proceed
        if (analysis.get("adoption_status") == "meeting_targets" and 
            analysis.get("user_impact") == "acceptable"):
            return "proceed"
        
        return "pause"
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate PM confidence in recommendation."""
        confidence = 0.7  # Base confidence
        
        if analysis.get("adoption_status") == "meeting_targets":
            confidence += 0.15
        
        if analysis.get("user_impact") == "acceptable":
            confidence += 0.10
        
        if analysis.get("stability_risks"):
            confidence -= 0.15
        
        return min(1.0, max(0.0, confidence))
    
    def _build_reasoning(self, analysis: Dict, recommendation: str) -> str:
        """Build qualitative reasoning for recommendation."""
        adoption = analysis.get("adoption_status", "unknown")
        impact = analysis.get("user_impact", "unknown")
        return f"Based on adoption status ({adoption}) and user impact ({impact}), recommending {recommendation}."


class DataAnalystAgent(Agent):
    """
    Data Analyst Agent - analyzes quantitative metrics, trends, anomalies, and confidence bounds.
    """
    
    def __init__(self):
        super().__init__("DataAnalyst")
    
    def analyze(self, dashboard: DashboardData) -> AgentAnalysis:
        """
        Analyze from data perspective: metrics, trends, anomalies, confidence.
        """
        self.log_step("Starting quantitative analysis")
        analysis = {}
        
        # 1. Anomaly detection across all metrics
        self.log_step("Running anomaly detection on all metrics")
        anomalies = {}
        for metric_name, ts in dashboard.metrics.items():
            anomaly_result = AnomalyDetector.detect_anomalies(ts)
            anomalies[metric_name] = anomaly_result
            if anomaly_result["anomaly_count"] > 0:
                self.log_step(f"  Found {anomaly_result['anomaly_count']} anomalies in {metric_name}")
        
        analysis["anomaly_report"] = anomalies
        
        # 2. Trend analysis
        self.log_step("Analyzing trends")
        trends = {}
        degrading_metrics = []
        for metric_name, ts in dashboard.metrics.items():
            trend = AnomalyDetector.trend_analysis(ts)
            trends[metric_name] = trend
            if trend["trend"] == "degrading":
                degrading_metrics.append(metric_name)
        
        analysis["trends"] = trends
        analysis["degrading_metric_count"] = len(degrading_metrics)
        
        # 3. Health score
        self.log_step("Computing system health score")
        health = MetricAggregator.health_score(dashboard.metrics)
        analysis["system_health"] = health
        
        # 4. Baseline comparison
        self.log_step("Comparing to baseline metrics")
        baseline_comparison = MetricAggregator.compare_to_baseline(dashboard.metrics)
        analysis["baseline_comparison"] = baseline_comparison
        
        # 5. Statistical confidence
        self.log_step("Assessing data confidence")
        data_quality = self._assess_data_quality(dashboard)
        analysis["data_quality"] = data_quality
        
        # Decision logic
        self.log_step("Making data-driven recommendation")
        
        recommendation = self._make_recommendation(analysis)
        confidence = self._calculate_confidence(analysis, data_quality)
        
        reasoning = self._build_reasoning(analysis)
        reasoning = self._append_llm_insight(dashboard, analysis, recommendation, reasoning)
        
        return AgentAnalysis(
            agent_name=self.name,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _assess_data_quality(self, dashboard: DashboardData) -> Dict:
        """Assess data quality, sample size, and sufficient data for decisions."""
        data_points_per_metric = [len(ts.points) for ts in dashboard.metrics.values()]
        avg_data_points = sum(data_points_per_metric) / len(data_points_per_metric) if data_points_per_metric else 0
        
        feedback_volume = len(dashboard.feedback)
        
        # Minimum thresholds
        sufficient_metric_data = avg_data_points >= 7  # 7+ days
        sufficient_feedback = feedback_volume >= 20  # 20+ feedback entries
        
        quality_score = 0.8 if sufficient_metric_data else 0.5
        quality_score += 0.2 if sufficient_feedback else 0
        
        return {
            "avg_data_points_per_metric": avg_data_points,
            "total_feedback_entries": feedback_volume,
            "sufficient_metric_data": sufficient_metric_data,
            "sufficient_user_feedback": sufficient_feedback,
            "overall_quality_score": round(quality_score, 2)
        }
    
    def _make_recommendation(self, analysis: Dict) -> str:
        """Make recommendation based on data signals."""
        health = analysis.get("system_health", {})
        health_pct = health.get("overall_health_percent", 50)
        
        degrading_count = analysis.get("degrading_metric_count", 0)
        
        # Rollback if health is poor and metrics degrading
        if health_pct < 50 and degrading_count > 2:
            return "rollback"
        
        # Pause if moderate concerns
        if health_pct < 70 or degrading_count > 0:
            return "pause"
        
        # Proceed if health is good
        if health_pct >= 80:
            return "proceed"
        
        return "pause"
    
    def _calculate_confidence(self, analysis: Dict, data_quality: Dict) -> float:
        """Calculate confidence in data-driven recommendation."""
        quality_score = data_quality.get("overall_quality_score", 0.5)
        confidence = quality_score * 0.5  # Base on data quality
        
        health_pct = analysis.get("system_health", {}).get("overall_health_percent", 50)
        if health_pct > 80:
            confidence += 0.30
        elif health_pct > 60:
            confidence += 0.15
        else:
            confidence += 0.05
        
        degrading_count = analysis.get("degrading_metric_count", 0)
        if degrading_count == 0:
            confidence += 0.15
        
        return min(1.0, max(0.0, confidence))
    
    def _build_reasoning(self, analysis: Dict) -> str:
        """Build reasoning for recommendation."""
        health = analysis.get("system_health", {})
        health_pct = health.get("overall_health_percent", 0)
        rating = health.get("health_rating", "unknown")
        return f"System health at {health_pct}% ({rating}). Recommending based on quantitative metrics."


class MarketingCommsAgent(Agent):
    """
    Marketing/Comms Agent - assesses messaging, customer perception, and communication actions.
    """
    
    def __init__(self):
        super().__init__("MarketingComms")
    
    def analyze(self, dashboard: DashboardData) -> AgentAnalysis:
        """
        Analyze from comms perspective: perception, messaging, and comms readiness.
        """
        self.log_step("Starting communications analysis")
        analysis = {}
        
        # 1. Customer perception analysis
        self.log_step("Analyzing customer perception")
        sentiment = SentimentAnalyzer.summarize_feedback(dashboard.feedback)
        analysis["customer_sentiment"] = sentiment
        
        perception_score = sentiment["sentiment_positive_percent"]
        analysis["perception_score"] = perception_score
        
        # 2. Message themes and concerns
        self.log_step("Extracting communication themes")
        themes = SentimentAnalyzer.theme_extraction(dashboard.feedback)
        analysis["message_themes"] = themes
        
        # 3. Communication readiness
        self.log_step("Assessing communication readiness")
        critical_issues = sentiment.get("critical_issues", [])
        analysis["critical_communication_issues"] = len(critical_issues)
        analysis["critical_issues_list"] = critical_issues[:5]
        
        # 4. Stakeholder concerns
        negative_themes = {k: v for k, v in themes.get("themes", {}).items() 
                          if v["sentiment"]["negative"] > v["sentiment"]["positive"]}
        analysis["stakeholder_concerns"] = list(negative_themes.keys())
        
        # Decision logic
        self.log_step("Making comms recommendation")
        
        recommendation = self._make_recommendation(analysis)
        confidence = self._calculate_confidence(analysis)
        
        reasoning = self._build_reasoning(analysis)
        reasoning = self._append_llm_insight(dashboard, analysis, recommendation, reasoning)
        
        return AgentAnalysis(
            agent_name=self.name,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _make_recommendation(self, analysis: Dict) -> str:
        """Make recommendation based on customer perception."""
        perception_score = analysis.get("perception_score", 0)
        critical_issues = analysis.get("critical_communication_issues", 0)
        
        # If significant negative perception and critical issues, pause for messaging
        if perception_score < 40 and critical_issues > 3:
            return "pause"
        
        # If mostly positive perception, proceed
        if perception_score > 60:
            return "proceed"
        
        # If critical comms issues and negative perception, consider rollback
        if perception_score < 30 and critical_issues > 5:
            return "rollback"
        
        return "pause"
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence in comms recommendation."""
        perception = analysis.get("perception_score", 50)
        
        confidence = 0.5
        
        if perception > 60:
            confidence += 0.30
        elif perception > 40:
            confidence += 0.15
        
        critical_issues = analysis.get("critical_communication_issues", 0)
        if critical_issues == 0:
            confidence += 0.20
        elif critical_issues <= 2:
            confidence += 0.10
        else:
            confidence -= 0.20
        
        return min(1.0, max(0.0, confidence))
    
    def _build_reasoning(self, analysis: Dict) -> str:
        """Build reasoning for comms recommendation."""
        perception = analysis.get("perception_score", 0)
        critical = analysis.get("critical_communication_issues", 0)
        concerns = analysis.get("stakeholder_concerns", [])
        
        return f"Customer perception at {perception}%. {critical} critical comms issues identified. Main concerns: {', '.join(concerns[:3]) if concerns else 'none'}."


class RiskCriticAgent(Agent):
    """
    Risk/Critic Agent - challenges assumptions, highlights risks, and requests additional evidence.
    """
    
    def __init__(self):
        super().__init__("RiskCritic")
    
    def analyze(self, dashboard: DashboardData) -> AgentAnalysis:
        """
        Analyze from risk perspective: identify risks, challenge assumptions, flag uncertainties.
        """
        self.log_step("Starting risk and assumptions analysis")
        analysis = {}
        
        # 1. Known issue severity assessment
        self.log_step("Assessing known issue risks")
        issues_by_severity = {"low": [], "medium": [], "high": [], "critical": []}
        for issue in dashboard.known_issues:
            issues_by_severity[issue.severity].append(issue)
        
        analysis["known_issues_by_severity"] = {
            k: len(v) for k, v in issues_by_severity.items()
        }
        analysis["critical_issues"] = [i.to_dict() for i in issues_by_severity["critical"]]
        analysis["high_issues"] = [i.to_dict() for i in issues_by_severity["high"]]
        
        # 2. Metric-based risk flags
        self.log_step("Identifying metric-based risks")
        risk_flags = []
        
        # Check for anomalies indicating problems
        for metric_name, ts in dashboard.metrics.items():
            anomaly_result = AnomalyDetector.detect_anomalies(ts)
            if anomaly_result["anomaly_count"] > 1:
                risk_flags.append({
                    "metric": metric_name,
                    "risk": f"{anomaly_result['anomaly_count']} anomalies detected",
                    "severity": "medium"
                })
        
        analysis["metric_based_risks"] = risk_flags
        
        # 3. Feedback-based risk indicators
        self.log_step("Extracting risk signals from feedback")
        sentiment = SentimentAnalyzer.summarize_feedback(dashboard.feedback)
        critical_feedback = sentiment.get("critical_issues", [])
        analysis["critical_user_issues"] = critical_feedback
        
        # 4. Rollout scope risk
        self.log_step("Assessing rollout scope risk")
        rollout_pct = dashboard.rollout_percentage
        if rollout_pct > 0.50:
            analysis["rollout_scope_risk"] = "high - over 50% of users exposed"
        elif rollout_pct > 0.20:
            analysis["rollout_scope_risk"] = "medium - 20-50% exposed"
        else:
            analysis["rollout_scope_risk"] = "low - limited exposure"
        
        # 5. Challenge assumptions
        self.log_step("Challenging key assumptions")
        assumptions_challenged = self._challenge_assumptions(dashboard)
        analysis["assumption_challenges"] = assumptions_challenged
        
        # Decision logic
        self.log_step("Making risk-based recommendation")
        
        recommendation = self._make_recommendation(analysis)
        confidence = self._calculate_confidence(analysis)
        
        reasoning = self._build_reasoning(analysis)
        reasoning = self._append_llm_insight(dashboard, analysis, recommendation, reasoning)
        
        return AgentAnalysis(
            agent_name=self.name,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _challenge_assumptions(self, dashboard: DashboardData) -> List[str]:
        """Challenge underlying assumptions in the launch."""
        challenges = []
        
        # Challenge 1: Data sufficiency
        if len(dashboard.feedback) < 30:
            challenges.append("Assumption: Enough user feedback to judge quality. Challenge: Only {len(dashboard.feedback)} entries.")
        
        # Challenge 2: Metric stability
        for metric_name, ts in dashboard.metrics.items():
            if len(ts.points) < 10:
                challenges.append(f"Assumption: {metric_name} is stable. Challenge: Only {len(ts.points)} data points.")
        
        # Challenge 3: Rollout gradient
        if dashboard.rollout_percentage > 0.70:
            challenges.append("Assumption: Gradual rollout provides safety margin. Challenge: 70%+ of users already exposed.")
        
        # Challenge 4: Issue maturation
        for issue in dashboard.known_issues:
            if issue.severity == "critical":
                challenges.append(f"Assumption: {issue.title} can be mitigated. Challenge: Critical issue with no clear resolution.")
        
        return challenges
    
    def _make_recommendation(self, analysis: Dict) -> str:
        """Make conservative, risk-aware recommendation."""
        critical_count = len(analysis.get("critical_issues", []))
        high_count = len(analysis.get("high_issues", []))
        
        # If critical issues exist, rollback
        if critical_count > 0:
            return "rollback"
        
        # If multiple high-severity issues, pause
        if high_count >= 2:
            return "pause"
        
        # If high rollout scope + risks present, pause
        if "high" in analysis.get("rollout_scope_risk", ""):
            if critical_count > 0 or high_count > 0:
                return "pause"
        
        # If many assumption challenges, pause
        challenges = analysis.get("assumption_challenges", [])
        if len(challenges) > 3:
            return "pause"
        
        return "proceed"
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence in risk assessment."""
        confidence = 0.6
        
        critical_count = len(analysis.get("critical_issues", []))
        high_count = len(analysis.get("high_issues", []))
        
        if critical_count == 0:
            confidence += 0.15
        else:
            confidence -= 0.20
        
        if high_count <= 1:
            confidence += 0.15
        elif high_count > 3:
            confidence -= 0.15
        
        challenges = analysis.get("assumption_challenges", [])
        if len(challenges) <= 2:
            confidence += 0.10
        else:
            confidence -= 0.10
        
        return min(1.0, max(0.0, confidence))
    
    def _build_reasoning(self, analysis: Dict) -> str:
        """Build reasoning for risk recommendation."""
        critical = len(analysis.get("critical_issues", []))
        high = len(analysis.get("high_issues", []))
        challenges = len(analysis.get("assumption_challenges", []))
        
        return f"Identified {critical} critical, {high} high severity issues. {challenges} key assumption challenges. Recommending cautious approach."
