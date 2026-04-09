"""
Mock dashboard data for the war room simulation.
Generates realistic but simulated PurpleMerit product launch data.
"""

from datetime import datetime, timedelta
import random
from src.models import (
    TimeSeries, MetricPoint, UserFeedback, KnownIssue, DashboardData
)


def generate_mock_dashboard() -> DashboardData:
    """
    Generate realistic mock dashboard data for a product launch scenario.
    """
    
    # Generate 14-day time series starting from 7 days ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    date_strings = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(15)]
    
    # ============ METRICS ============
    
    # 1. Activation Rate (% of new users who activate feature)
    activation_points = [
        MetricPoint(date_strings[0], 0.08),
        MetricPoint(date_strings[1], 0.10),
        MetricPoint(date_strings[2], 0.12),
        MetricPoint(date_strings[3], 0.14),
        MetricPoint(date_strings[4], 0.16),
        MetricPoint(date_strings[5], 0.15),
        MetricPoint(date_strings[6], 0.17),
        MetricPoint(date_strings[7], 0.18),
        MetricPoint(date_strings[8], 0.16),
        MetricPoint(date_strings[9], 0.14),
        MetricPoint(date_strings[10], 0.12),
        MetricPoint(date_strings[11], 0.11),
        MetricPoint(date_strings[12], 0.09),
        MetricPoint(date_strings[13], 0.08),
        MetricPoint(date_strings[14], 0.07),
    ]
    activation_rate = TimeSeries(
        metric_name="activation_rate",
        points=activation_points,
        unit="fraction",
        baseline=0.10
    )
    
    # 2. DAU (Daily Active Users) - in thousands
    dau_points = [
        MetricPoint(date_strings[0], 450),
        MetricPoint(date_strings[1], 460),
        MetricPoint(date_strings[2], 470),
        MetricPoint(date_strings[3], 480),
        MetricPoint(date_strings[4], 485),
        MetricPoint(date_strings[5], 490),
        MetricPoint(date_strings[6], 495),
        MetricPoint(date_strings[7], 500),
        MetricPoint(date_strings[8], 505),
        MetricPoint(date_strings[9], 510),
        MetricPoint(date_strings[10], 505),
        MetricPoint(date_strings[11], 500),
        MetricPoint(date_strings[12], 495),
        MetricPoint(date_strings[13], 490),
        MetricPoint(date_strings[14], 485),
    ]
    dau = TimeSeries(
        metric_name="dau",
        points=dau_points,
        unit="thousand users",
        baseline=450
    )
    
    # 3. D1 Retention (% users returning after 1 day)
    d1_retention_points = [
        MetricPoint(date_strings[0], 0.68),
        MetricPoint(date_strings[1], 0.67),
        MetricPoint(date_strings[2], 0.66),
        MetricPoint(date_strings[3], 0.65),
        MetricPoint(date_strings[4], 0.64),
        MetricPoint(date_strings[5], 0.63),
        MetricPoint(date_strings[6], 0.62),
        MetricPoint(date_strings[7], 0.60),
        MetricPoint(date_strings[8], 0.58),
        MetricPoint(date_strings[9], 0.55),
        MetricPoint(date_strings[10], 0.52),
        MetricPoint(date_strings[11], 0.50),
        MetricPoint(date_strings[12], 0.48),
        MetricPoint(date_strings[13], 0.46),
        MetricPoint(date_strings[14], 0.44),
    ]
    d1_retention = TimeSeries(
        metric_name="d1_retention",
        points=d1_retention_points,
        unit="fraction",
        baseline=0.68
    )
    
    # 4. Crash Rate (% of sessions with crash)
    crash_rate_points = [
        MetricPoint(date_strings[0], 0.005),
        MetricPoint(date_strings[1], 0.006),
        MetricPoint(date_strings[2], 0.008),
        MetricPoint(date_strings[3], 0.012),
        MetricPoint(date_strings[4], 0.018),
        MetricPoint(date_strings[5], 0.022),
        MetricPoint(date_strings[6], 0.025),
        MetricPoint(date_strings[7], 0.028),
        MetricPoint(date_strings[8], 0.031),
        MetricPoint(date_strings[9], 0.035),
        MetricPoint(date_strings[10], 0.032),
        MetricPoint(date_strings[11], 0.030),
        MetricPoint(date_strings[12], 0.029),
        MetricPoint(date_strings[13], 0.027),
        MetricPoint(date_strings[14], 0.026),
    ]
    crash_rate = TimeSeries(
        metric_name="crash_rate",
        points=crash_rate_points,
        unit="fraction",
        baseline=0.005
    )
    
    # 5. API Latency p95 (milliseconds)
    api_latency_points = [
        MetricPoint(date_strings[0], 145),
        MetricPoint(date_strings[1], 152),
        MetricPoint(date_strings[2], 158),
        MetricPoint(date_strings[3], 165),
        MetricPoint(date_strings[4], 172),
        MetricPoint(date_strings[5], 185),
        MetricPoint(date_strings[6], 195),
        MetricPoint(date_strings[7], 210),
        MetricPoint(date_strings[8], 225),
        MetricPoint(date_strings[9], 240),
        MetricPoint(date_strings[10], 235),
        MetricPoint(date_strings[11], 228),
        MetricPoint(date_strings[12], 220),
        MetricPoint(date_strings[13], 215),
        MetricPoint(date_strings[14], 212),
    ]
    api_latency = TimeSeries(
        metric_name="api_latency_p95",
        points=api_latency_points,
        unit="ms",
        baseline=145
    )
    
    # 6. Payment Success Rate
    payment_success_points = [
        MetricPoint(date_strings[0], 0.985),
        MetricPoint(date_strings[1], 0.984),
        MetricPoint(date_strings[2], 0.982),
        MetricPoint(date_strings[3], 0.980),
        MetricPoint(date_strings[4], 0.978),
        MetricPoint(date_strings[5], 0.975),
        MetricPoint(date_strings[6], 0.972),
        MetricPoint(date_strings[7], 0.970),
        MetricPoint(date_strings[8], 0.968),
        MetricPoint(date_strings[9], 0.967),
        MetricPoint(date_strings[10], 0.968),
        MetricPoint(date_strings[11], 0.970),
        MetricPoint(date_strings[12], 0.971),
        MetricPoint(date_strings[13], 0.972),
        MetricPoint(date_strings[14], 0.973),
    ]
    payment_success_rate = TimeSeries(
        metric_name="payment_success_rate",
        points=payment_success_points,
        unit="fraction",
        baseline=0.985
    )
    
    # ============ USER FEEDBACK ============
    feedback_samples = [
        # Positive feedback
        UserFeedback("2024-01-08 08:30", "positive", "Love the new feature! Makes my workflow so much faster.", "feature"),
        UserFeedback("2024-01-08 10:15", "positive", "Great update, very intuitive interface.", "ux"),
        UserFeedback("2024-01-08 14:22", "positive", "This feature is fantastic, exactly what we needed.", "feature"),
        UserFeedback("2024-01-09 09:00", "positive", "Performance is great, no issues so far.", "performance"),
        UserFeedback("2024-01-09 11:45", "positive", "Excellent addition to the platform.", "feature"),
        
        # Neutral feedback
        UserFeedback("2024-01-08 12:00", "neutral", "Interesting feature, still getting used to it.", "ux"),
        UserFeedback("2024-01-09 15:30", "neutral", "Works okay, but a bit slow sometimes.", "performance"),
        UserFeedback("2024-01-10 08:15", "neutral", "Feature is there, not sure if I'll use it regularly.", "feature"),
        UserFeedback("2024-01-10 16:45", "neutral", "It's fine, nothing special.", "feature"),
        
        # Negative - Performance issues
        UserFeedback("2024-01-10 09:00", "negative", "App keeps crashing when I use the new feature.", "bug"),
        UserFeedback("2024-01-10 10:30", "negative", "Severe latency issues - app is barely usable now.", "performance"),
        UserFeedback("2024-01-10 14:15", "negative", "Getting timeouts repeatedly with new feature.", "bug"),
        UserFeedback("2024-01-11 08:45", "negative", "App crashed 3 times today using new feature.", "crash"),
        UserFeedback("2024-01-11 10:00", "negative", "Latency is terrible, loads taking 5+ seconds.", "performance"),
        UserFeedback("2024-01-11 13:20", "negative", "Same crash issue persists - very frustrating.", "crash"),
        UserFeedback("2024-01-11 15:50", "negative", "Still experiencing crashes, please fix ASAP.", "bug"),
        
        # Negative - Other issues
        UserFeedback("2024-01-11 09:30", "negative", "Feature doesn't work as described in preview.", "bug"),
        UserFeedback("2024-01-11 11:00", "negative", "UI is confusing, not user friendly", "ux"),
        UserFeedback("2024-01-11 16:15", "negative", "Payment failed but was charged anyway.", "bug"),
        UserFeedback("2024-01-12 08:00", "negative", "Lost data when switching to new feature.", "bug"),
        UserFeedback("2024-01-12 10:45", "negative", "Crashes persist despite update. Very disappointed.", "crash"),
        UserFeedback("2024-01-12 14:00", "negative", "Still slow and buggy. Considering canceling subscription.", "bug"),
        
        # Mixed
        UserFeedback("2024-01-12 09:00", "positive", "Great concept but needs optimization.", "feature"),
        UserFeedback("2024-01-09 16:30", "negative", "Too buggy in current state.", "bug"),
        UserFeedback("2024-01-13 08:30", "negative", "Rollout was too aggressive - should have gradual release.", "bug"),
        UserFeedback("2024-01-13 11:00", "positive", "Better today, crashes seem reduced.", "performance"),
        UserFeedback("2024-01-13 14:15", "neutral", "Waiting to see if issues resolve.", "bug"),
        UserFeedback("2024-01-13 16:45", "negative", "Performance still bad in peak hours.", "performance"),
        UserFeedback("2024-01-14 09:15", "negative", "App got slower after the update.", "performance"),
        UserFeedback("2024-01-14 11:30", "positive", "Improvement noticed, fewer crashes today.", "crash"),
        UserFeedback("2024-01-14 13:00", "negative", "Latency spikes every few minutes.", "performance"),
        UserFeedback("2024-01-14 15:45", "negative", "Support queue backed up - no response for 2 hours.", "crash"),
    ]
    
    # ============ KNOWN ISSUES ============
    known_issues = [
        KnownIssue(
            title="Memory leak in feature initialization",
            description="New feature causes gradual memory increase under heavy load, potentially leading to crashes after extended use.",
            severity="high",
            affected_users="Users with sessions >30 min",
            mitigation="Hotfix deployed 2024-01-11. Requires app restart to take effect."
        ),
        KnownIssue(
            title="Query optimization issue causing latency",
            description="Database query in new feature was not properly indexed, causing p95 latency to increase by 50-70ms.",
            severity="high",
            affected_users="All feature users",
            mitigation="Database index created. Should resolve with next deployment."
        ),
        KnownIssue(
            title="Race condition in payment processing",
            description="Under concurrent load, rare race condition causes transaction records to mismatch.",
            severity="critical",
            affected_users="Small % of payment users (~0.5%)",
            mitigation="Code fix identified. Requires careful rollout."
        ),
        KnownIssue(
            title="Cache invalidation bug",
            description="Feature cache not properly invalidating on data updates, causing stale data display.",
            severity="medium",
            affected_users="Users viewing real-time data",
            mitigation="Workaround: manual cache clear. Permanent fix in next sprint."
        ),
        KnownIssue(
            title="Incomplete feature rollout config",
            description="Rollout percentage calculation has edge cases at boundaries.",
            severity="low",
            affected_users="<1% of users",
            mitigation="Non-critical, will be fixed in next release."
        ),
    ]
    
    metrics = {
        "activation_rate": activation_rate,
        "dau": dau,
        "d1_retention": d1_retention,
        "crash_rate": crash_rate,
        "api_latency_p95": api_latency,
        "payment_success_rate": payment_success_rate,
    }
    
    dashboard = DashboardData(
        date_range_start=date_strings[0],
        date_range_end=date_strings[14],
        metrics=metrics,
        feedback=feedback_samples,
        known_issues=known_issues,
        feature_description="New 'Smart Recommendations' feature using ML to personalize user experience with ML-based content suggestions.",
        rollout_percentage=0.40
    )
    
    return dashboard
