# PurpleMerit Launch War Room - Multi-Agent Decision System

A sophisticated multi-agent system that simulates cross-functional decision-making during a product launch. The system analyzes mock dashboard metrics and user feedback to produce structured launch decisions: **Proceed**, **Pause**, or **Roll Back**.

## System Overview

### Architecture

The system consists of four specialized agents working in coordination:

- **Product Manager Agent** - Evaluates feature adoption, user impact, and go/no-go decisions
- **Data Analyst Agent** - Performs quantitative analysis: anomaly detection, trends, health scoring
- **Marketing/Comms Agent** - Assesses customer perception and communication readiness  
- **Risk/Critic Agent** - Identifies risks, challenges assumptions, flags uncertainties

A central **Orchestrator** coordinates all agents, synthesizes recommendations, and produces the final structured decision with rationale, risk register, and action plan.

### Key Components

```
war_room_system/
├── src/
│   ├── models.py          # Data structures (metrics, feedback, decision output)
│   ├── tools.py           # Analysis tools (anomaly detection, sentiment analysis, aggregation)
│   ├── agents.py          # Four agent implementations
│   ├── orchestrator.py    # War room coordinator and decision synthesis
│   └── mock_data.py       # Generates realistic 14-day mock dashboard
├── main.py                # Entry point - runs full war room analysis
├── requirements.txt       # Dependencies (none - pure Python)
└── README.md             # This file
```

## Input Data

### 1. Mock Dashboard (`mock_data.py`)

Generates realistic 14-day time series metrics:

- **Activation Rate** - Feature adoption by new users
- **DAU (Daily Active Users)** - Platform usage trends
- **D1 Retention** - User retention after 1 day
- **Crash Rate** - App stability indicator
- **API Latency (p95)** - Performance metric
- **Payment Success Rate** - Transaction reliability

### 2. User Feedback (30+ entries)

Mix of sentiment across categories:
- **Positive**: Love the feature, great UX, fast performance
- **Neutral**: Getting used to it, works okay
- **Negative**: Crashes, latency issues, bugs, data loss

### 3. Known Issues (5+ items)

Pre-identified risks with severity levels:
- Memory leak in feature initialization (HIGH)
- Query optimization issue (HIGH)
- **Race condition in payment processing (CRITICAL)**
- Cache invalidation bug (MEDIUM)
- Rollout config edge cases (LOW)

## Installation

### Prerequisites
- Python 3.7+
- No external dependencies required (uses Python standard library only)

### Setup

```bash
# Clone or download the repository
cd war_room_system

# Verify Python version
python --version

# No pip install needed - pure Python
```
### Optional Gemini LLM Integration

The system can optionally use a Gemini API key for additional reasoning support in each agent.

Supported methods:

- Create a `.env` file in `war_room_system/` with:
  ```bash
  GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
  ```
- Or set the environment variable in your shell:
  ```bash
  # Windows PowerShell
  $env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

  # macOS/Linux
  export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
  ```

When `GEMINI_API_KEY` is available, all agents call Gemini to append supplementary reasoning to their recommendations. If `GEMINI_API_ENDPOINT` is also set, it will override the default Gemini endpoint and can be used for alternate API routes. If no key is configured, the system remains fully functional using its built-in rule-based analysis.
## Quick Start

### Run the War Room Analysis

```bash
# From the war_room_system directory
python main.py
```

### Example Output

The system produces:

1. **Console Output** - Real-time analysis logs and decision summary
2. **JSON File** - `war_room_decision.json` with complete structured output

### What Happens

```
1. Load mock dashboard (metrics, feedback, known issues)
   ↓
2. Run agent analyses in parallel:
   • ProductManager: Adoption & user impact assessment
   • DataAnalyst: Quantitative metrics & anomalies
   • Marketing: Customer perception & comms readiness
   • RiskCritic: Risk identification & assumption challenges
   ↓
3. Synthesize recommendations:
   • Count votes (Proceed / Pause / Rollback)
   • Apply decision logic (prioritize safety)
   • Calculate confidence score
   ↓
4. Generate structured decision with:
   • Final recommendation + rationale
   • Metric drivers + feedback summary
   • Risk register (5+ identified risks)
   • Action plan (24-48 hour tasks)
   • Communication strategy (internal + external)
   • Confidence factors (what would increase confidence)
   ↓
5. Output to console and JSON file
```

## Output Format

### Example Decision Output

```json
{
  "decision": "pause",
  "timestamp": "2024-01-14T15:30:00.123456",
  "overall_confidence": 0.78,
  
  "rationale": "PAUSE RECOMMENDED for stability hardening...",
  
  "metric_drivers": {
    "crash_rate": "2.6% (was 0.5%) - +420%",
    "d1_retention": "44.0% (was 68.0%) - -35%",
    "api_latency_p95": "212ms (was 145ms) - +46% slower"
  },
  
  "feedback_summary": {
    "positive": 5,
    "neutral": 9,
    "negative": 16,
    "total": 30
  },
  
  "agent_recommendations": [
    {
      "agent_name": "ProductManager",
      "recommendation": "pause",
      "confidence": 0.75,
      "reasoning": "..."
    },
    ...
  ],
  
  "risk_register": [
    {
      "risk_id": "R1",
      "title": "Memory leak in feature initialization",
      "severity": "high",
      "likelihood": "high",
      "impact": "high",
      "mitigation": "Hotfix deployed 2024-01-11..."
    },
    ...
  ],
  
  "action_plan": [
    {
      "action_id": "A1",
      "description": "Pause feature rollout...",
      "owner": "Platform Engineering",
      "due_in_hours": 2,
      "priority": "high"
    },
    ...
  ],
  
  "communication_plan": {
    "internal_message": "Pausing rollout for optimization...",
    "external_message": "Pausing while we fine-tune...",
    "channels": ["Email", "In-App", "Status Page"],
    "timing": "Within 2 hours of decision"
  },
  
  "confidence_factors": {
    "more_data": "Extended observation period...",
    "monitoring": "Deploy real-time alerting...",
    "stability": "Confirm crash rate trending downward..."
  }
}
```

## Agent Decision Logic

### Product Manager Agent
- **Data**: Activation rate, crash rate, error rate, user feedback, known issues
- **Analysis**: Feature adoption vs. targets, stability risks, user impact assessment
- **Recommendation Driver**: Adoption + stability + user sentiment

### Data Analyst Agent
- **Data**: All metrics, anomalies, trends, baseline comparisons
- **Analysis**: System health scoring, degrading metrics, data quality assessment
- **Recommendation Driver**: Health score + trend direction + data sufficiency

### Marketing/Comms Agent
- **Data**: User feedback sentiment, themes, critical issues
- **Analysis**: Perception scoring, message themes, stakeholder concerns
- **Recommendation Driver**: Positive sentiment % + critical issue count

### Risk/Critic Agent
- **Data**: Known issues, metric anomalies, feedback, rollout scope
- **Analysis**: Risk severity, assumption challenges, evidence gaps
- **Recommendation Driver**: Critical issue presence + risk count + consensus

### Orchestrator Logic
- **Rollback**: If any critical issues OR (crash rate > 2% AND retention declining)
- **Pause**: If ≥2 agents recommend pause OR 1+ agents recommend rollback
- **Proceed**: If ≥2 agents recommend proceed AND no rollback signals

## Tools & Functions

The system uses programmatic tools called by agents:

### AnomalyDetector
```python
- detect_anomalies(time_series)   # Z-score based anomaly detection
- trend_analysis(time_series)     # Direction & magnitude analysis
```

### SentimentAnalyzer
```python
- summarize_feedback(feedback_list)    # Sentiment distribution & themes
- theme_extraction(feedback_list)      # Extract common themes/keywords
```

### MetricAggregator
```python
- health_score(metrics_dict)           # Overall system health 0-100%
- compare_to_baseline(metrics_dict)    # Delta analysis vs. baseline
```

## Scenario Details

### PurpleMerit Feature: "Smart Recommendations"
- ML-based personalized content suggestions
- Rolled out to 40% of users
- 14-day observation period
- Mixed metrics: adoption climbing but growing stability concerns

### Simulated Situation
- Crash rate **increased from 0.5% to 2.6%** (trending worse)
- D1 retention **declined 35%** (from 68% to 44%)
- API latency **p95 increased 46%** (145ms → 212ms)
- Known critical issue: Race condition in payment processing
- **16/30 feedback entries are negative** (crashes, latency, bugs)

### Expected Output
Based on above scenario, system should recommend **PAUSE** with:
- Identified critical payment processing risk
- Elevated crash rate requiring investigation
- Confidence factor: ~75-80%
- Action plan: Hotfixes, enhanced monitoring, 24-48h validation

## Testing & Validation

### Run the System
```bash
python main.py
```

### Verify Output
Check that output contains:
- ✓ Decision: one of {proceed, pause, rollback}
- ✓ Agent recommendations: 4 agents with confidence scores
- ✓ Metric drivers: Changes compared to baseline
- ✓ Risk register: Critical, high severity issues identified
- ✓ Action plan: Prioritized tasks with owners and timeline
- ✓ Communication plan: Internal + external messaging
- ✓ JSON file: `war_room_decision.json` created

### Sample Console Log
```
================================================================================
                 PurpleMerit Launch War Room - Multi-Agent Decision System
================================================================================

Step 1: Loading mock dashboard data...
  ✓ Loaded 6 metrics, 30 feedback entries
  ✓ 5 known issues identified

Step 2: Initiating war room analysis...

================================================================================
                                  PHASE 1: AGENT ANALYSES
================================================================================

[ProductManager] Beginning analysis...
  [ProductManager] Starting product analysis
  [ProductManager] Analyzing feature adoption metrics
  ...
  Recommendation: PAUSE
  Confidence: 75.0%
  Reasoning: Based on adoption status (below_targets) and user impact (negative)...

[DataAnalyst] Beginning analysis...
...

[MarketingComms] Beginning analysis...
...

[RiskCritic] Beginning analysis...
...
```

## Architecture Highlights

### Separation of Concerns
- **Models**: Clean data structures with serialization
- **Tools**: Reusable analysis functions called by agents
- **Agents**: Independent analysts with specific expertise
- **Orchestrator**: Coordinator managing workflow
- **Main**: Simple entry point

### Traceability
- Every agent logs analysis steps
- Each recommendation includes reasoning
- Console output shows decision flow
- JSON includes full agent recommendations
- Risk register traces source (known issue vs. metric-derived)

### Extensibility
- Easy to add new agents (inherit from `Agent` base class)
- New tools can be added to each agent's arsenal
- Decision logic can be customized in orchestrator
- Mock data can be replaced with real data sources

## Files Structure

```
war_room_system/
├── src/
│   ├── __init__.py           # Package marker
│   ├── models.py             # ~350 lines - Data structures
│   ├── tools.py              # ~280 lines - Analysis functions
│   ├── agents.py             # ~550 lines - Agent implementations
│   ├── orchestrator.py       # ~650 lines - Orchestrator & synthesis
│   └── mock_data.py          # ~280 lines - Mock data generation
├── main.py                   # ~130 lines - Entry point
├── requirements.txt          # No dependencies needed
└── README.md                 # This file
```

**Total: ~2,240 lines of well-documented Python**

## Development & Debugging

### To modify agent logic:
Edit `src/agents.py` - each agent class has clear analysis flow

### To add new metrics:
Edit `src/mock_data.py` - add new `TimeSeries` objects

### To adjust decision thresholds:
Edit `src/orchestrator.py` - modify `_synthesize_decision()` logic

### To add new analysis tools:
Edit `src/tools.py` - add methods to existing analyzer classes

## Performance

- **Execution time**: < 1 second (pure Python, no external calls)
- **Memory footprint**: ~50 MB (mock data + analysis)
- **Scalability**: Easily handles 30+ metrics, 100+ feedback entries

## Future Enhancements

- Real database/API integration for live dashboards
- LLM-based reasoning agents (with API key)
- Web UI for interactive dashboard visualization
- Historical decision tracking and outcome analysis
- A/B test support for feature variants
- Regional/segment-specific analysis

## License

Internal assessment tool for PurpleMerit

## Contact

For questions about system architecture or extensions, refer to README or code comments.

---

**Ready to run**: `python main.py` - produces structured launch decision in JSON format with full reasoning and action plan.
