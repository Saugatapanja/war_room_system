"""
Analysis tools used by agents to process dashboard data.
"""

import statistics
from typing import List, Dict, Tuple
from src.models import TimeSeries, UserFeedback


class AnomalyDetector:
    """Detects anomalies in time series metrics."""
    
    @staticmethod
    def detect_anomalies(time_series: TimeSeries, threshold_std: float = 2.0) -> Dict:
        """
        Detect anomalies using statistical methods (Z-score).
        
        Args:
            time_series: TimeSeries object
            threshold_std: Number of standard deviations to flag as anomaly
            
        Returns:
            Dict with anomaly info
        """
        values = [p.value for p in time_series.points]
        
        if len(values) < 2:
            return {"anomalies": [], "mean": values[0] if values else 0}
        
        mean = statistics.mean(values)
        try:
            std_dev = statistics.stdev(values)
        except:
            std_dev = 0
        
        anomalies = []
        for i, point in enumerate(time_series.points):
            if std_dev > 0:
                z_score = abs((point.value - mean) / std_dev)
                if z_score > threshold_std:
                    anomalies.append({
                        "date": point.date,
                        "value": point.value,
                        "z_score": z_score,
                        "deviation": "high" if point.value > mean else "low"
                    })
        
        return {
            "metric": time_series.metric_name,
            "mean": mean,
            "std_dev": std_dev,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies)
        }
    
    @staticmethod
    def trend_analysis(time_series: TimeSeries) -> Dict:
        """
        Analyze trend direction and magnitude.
        
        Returns:
            Dict with trend info
        """
        if len(time_series.points) < 2:
            return {"trend": "insufficient_data"}
        
        values = [p.value for p in time_series.points]
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        change_pct = ((avg_second - avg_first) / avg_first * 100) if avg_first != 0 else 0
        
        if change_pct > 10:
            trend = "improving"
        elif change_pct < -10:
            trend = "degrading"
        else:
            trend = "stable"
        
        return {
            "metric": time_series.metric_name,
            "trend": trend,
            "change_percent": round(change_pct, 2),
            "first_half_avg": round(avg_first, 2),
            "second_half_avg": round(avg_second, 2),
            "baseline": time_series.baseline
        }


class SentimentAnalyzer:
    """Analyzes user feedback sentiment."""
    
    @staticmethod
    def summarize_feedback(feedback_list: List[UserFeedback]) -> Dict:
        """
        Summarize feedback by sentiment and category.
        
        Returns:
            Dict with sentiment distribution and issue themes
        """
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        category_breakdown = {}
        critical_issues = []
        
        for feedback in feedback_list:
            sentiment_counts[feedback.sentiment] += 1
            
            if feedback.category not in category_breakdown:
                category_breakdown[feedback.category] = {
                    "count": 0,
                    "positive": 0,
                    "negative": 0,
                    "examples": []
                }
            
            category_breakdown[feedback.category]["count"] += 1
            if feedback.sentiment == "positive":
                category_breakdown[feedback.category]["positive"] += 1
            elif feedback.sentiment == "negative":
                category_breakdown[feedback.category]["negative"] += 1
                if len(category_breakdown[feedback.category]["examples"]) < 3:
                    category_breakdown[feedback.category]["examples"].append(feedback.message)
            
            # Flag critical issues (negative feedback in critical categories)
            if feedback.sentiment == "negative" and feedback.category in ["bug", "crash", "performance"]:
                critical_issues.append({
                    "category": feedback.category,
                    "message": feedback.message,
                    "timestamp": feedback.timestamp
                })
        
        total = len(feedback_list)
        
        return {
            "total_feedback": total,
            "sentiment_distribution": sentiment_counts,
            "sentiment_negative_percent": round((sentiment_counts["negative"] / total * 100) if total > 0 else 0, 1),
            "sentiment_positive_percent": round((sentiment_counts["positive"] / total * 100) if total > 0 else 0, 1),
            "category_breakdown": category_breakdown,
            "critical_issues": critical_issues,
            "critical_issue_count": len(critical_issues)
        }
    
    @staticmethod
    def theme_extraction(feedback_list: List[UserFeedback]) -> Dict:
        """
        Extract common themes from feedback.
        
        Returns:
            Dict with theme counts and patterns
        """
        themes = {}
        keywords_to_track = ["crash", "slow", "bug", "feature", "love", "hate", "error", 
                            "latency", "timeout", "broken", "excellent", "great", "poor"]
        
        for feedback in feedback_list:
            message_lower = feedback.message.lower()
            for keyword in keywords_to_track:
                if keyword in message_lower:
                    if keyword not in themes:
                        themes[keyword] = {"count": 0, "sentiment": {"positive": 0, "neutral": 0, "negative": 0}}
                    themes[keyword]["count"] += 1
                    themes[keyword]["sentiment"][feedback.sentiment] += 1
        
        # Sort by frequency
        sorted_themes = sorted(themes.items(), key=lambda x: x[1]["count"], reverse=True)
        
        return {
            "themes": dict(sorted_themes[:10]),  # Top 10 themes
            "total_unique_themes": len(themes)
        }


class MetricAggregator:
    """Aggregates metrics into high-level insights."""
    
    @staticmethod
    def health_score(metrics_dict: Dict[str, TimeSeries]) -> Dict:
        """
        Calculate overall system health score based on key metrics.
        
        Returns:
            Dict with health indicators
        """
        score_components = {}
        weights = {
            "crash_rate": 0.20,
            "error_rate": 0.15,
            "retention": 0.20,
            "dau": 0.15,
            "api_latency": 0.15,
            "payment_success_rate": 0.15
        }
        
        # Normalize each metric to a 0-1 score
        for metric_name, time_series in metrics_dict.items():
            if not time_series.points:
                continue
                
            latest_value = time_series.points[-1].value
            baseline = time_series.baseline
            
            # Different metrics have different "good" directions
            if "crash" in metric_name or "error" in metric_name or "latency" in metric_name:
                # Lower is better
                if latest_value <= baseline:
                    component_score = min(1.0, 1.0 - (latest_value / baseline if baseline > 0 else 1.0))
                else:
                    component_score = max(0, 1.0 - ((latest_value - baseline) / baseline if baseline > 0 else 0))
            else:
                # Higher is better
                if latest_value >= baseline:
                    component_score = min(1.0, latest_value / baseline if baseline > 0 else 1.0)
                else:
                    component_score = max(0, latest_value / baseline if baseline > 0 else 0)
            
            score_components[metric_name] = round(component_score, 2)
        
        # Weighted average
        total_score = 0
        total_weight = 0
        for metric, weight in weights.items():
            if metric in score_components:
                total_score += score_components[metric] * weight
                total_weight += weight
        
        overall_health = round((total_score / total_weight * 100) if total_weight > 0 else 0, 1)
        
        return {
            "overall_health_percent": overall_health,
            "health_rating": "good" if overall_health >= 80 else "moderate" if overall_health >= 60 else "poor",
            "component_scores": score_components
        }
    
    @staticmethod
    def compare_to_baseline(metrics_dict: Dict[str, TimeSeries]) -> Dict:
        """
        Compare current metrics to baseline (pre-launch).
        
        Returns:
            Dict showing deltas and impact areas
        """
        comparison = {}
        
        for metric_name, time_series in metrics_dict.items():
            if time_series.points:
                current = time_series.points[-1].value
                baseline = time_series.baseline
                
                if baseline != 0:
                    change_pct = ((current - baseline) / baseline) * 100
                else:
                    change_pct = 0
                
                # Determine if this is good or bad
                if "crash" in metric_name or "error" in metric_name or "latency" in metric_name:
                    impact = "positive" if change_pct < 0 else "negative"
                else:
                    impact = "positive" if change_pct > 0 else "negative"
                
                comparison[metric_name] = {
                    "baseline": baseline,
                    "current": current,
                    "change_percent": round(change_pct, 2),
                    "impact": impact
                }
        
        return {
            "metric_comparisons": comparison,
            "positive_metrics": sum(1 for v in comparison.values() if v["impact"] == "positive"),
            "negative_metrics": sum(1 for v in comparison.values() if v["impact"] == "negative")
        }
