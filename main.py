"""
Main entry point for the war room launch decision system.
Orchestrates the multi-agent analysis and produces structured output.
"""

import logging
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mock_data import generate_mock_dashboard
from src.orchestrator import WarRoomOrchestrator
from src.llm import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution."""
    
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 78 + "║")
    logger.info("║" + " PurpleMerit Launch War Room - Multi-Agent Decision System ".center(78) + "║")
    logger.info("║" + " " * 78 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    logger.info("\n")
    
    # Step 0: Load environment variables from .env
    logger.info("Step 0: Loading environment variables from .env...")
    load_dotenv()
    dashboard = generate_mock_dashboard()
    logger.info(f"  ✓ Loaded {len(dashboard.metrics)} metrics, {len(dashboard.feedback)} feedback entries")
    logger.info(f"  ✓ {len(dashboard.known_issues)} known issues identified\n")
    
    # Step 2: Run war room
    logger.info("Step 2: Initiating war room analysis...")
    orchestrator = WarRoomOrchestrator()
    decision = orchestrator.run_war_room(dashboard)
    
    # Step 3: Output results
    logger.info("\n" + "=" * 80)
    logger.info("FINAL DECISION OUTPUT")
    logger.info("=" * 80 + "\n")
    
    # Pretty print decision summary
    logger.info(f"Decision: {decision.decision.upper()}")
    logger.info(f"Timestamp: {decision.timestamp}")
    logger.info(f"Overall Confidence: {decision.overall_confidence:.1%}\n")
    
    logger.info("RATIONALE:")
    logger.info(f"  {decision.rationale}\n")
    
    logger.info("KEY METRIC DRIVERS:")
    for metric, analysis in decision.metric_drivers.items():
        logger.info(f"  • {metric}: {analysis}")
    logger.info("")
    
    logger.info("FEEDBACK SUMMARY:")
    fs = decision.feedback_summary
    logger.info(f"  Positive: {fs['positive']} | Neutral: {fs['neutral']} | Negative: {fs['negative']} (Total: {fs['total']})")
    logger.info("")
    
    logger.info("AGENT RECOMMENDATIONS:")
    for rec in decision.agent_recommendations:
        logger.info(f"  • {rec.agent_name}: {rec.recommendation.upper()} " +
                   f"(confidence: {rec.confidence:.0%})")
    logger.info("")
    
    logger.info(f"TOP RISKS ({len(decision.risk_register)} identified):")
    for risk in decision.risk_register[:5]:
        logger.info(f"  • [{risk.risk_id}] {risk.title}")
        logger.info(f"    Severity: {risk.impact.upper()} | Mitigation: {risk.mitigation[:50]}...")
    logger.info("")
    
    logger.info(f"ACTION PLAN (Next 24-48 hours: {len(decision.action_plan)} items):")
    critical_actions = [a for a in decision.action_plan if a.priority == "critical"]
    for action in critical_actions[:3]:
        logger.info(f"  • [{action.action_id}] {action.description}")
        logger.info(f"    Owner: {action.owner} | Due: {action.due_in_hours}h | Priority: {action.priority.upper()}")
    if len(decision.action_plan) > 3:
        logger.info(f"  ... and {len(decision.action_plan) - 3} more actions")
    logger.info("")
    
    logger.info("COMMUNICATION PLAN:")
    logger.info(f"  Internal: {decision.communication_plan.internal_message[:100]}...")
    logger.info(f"  External: {decision.communication_plan.external_message[:100]}...")
    logger.info(f"  Channels: {', '.join(decision.communication_plan.channels)}")
    logger.info("")
    
    logger.info("CONFIDENCE DRIVERS:")
    for factor, explanation in decision.confidence_factors.items():
        logger.info(f"  • {factor}: {explanation}")
    logger.info("")
    
    # Step 4: Full JSON output
    logger.info("\n" + "=" * 80)
    logger.info("FULL STRUCTURED OUTPUT (JSON)")
    logger.info("=" * 80 + "\n")
    
    json_output = decision.to_json()
    logger.info(json_output)
    
    # Save to file
    output_file = Path(__file__).parent / "war_room_decision.json"
    with open(output_file, 'w') as f:
        f.write(json_output)
    
    logger.info(f"\n✓ Full decision saved to: {output_file}\n")
    
    return decision


if __name__ == "__main__":
    decision = main()
