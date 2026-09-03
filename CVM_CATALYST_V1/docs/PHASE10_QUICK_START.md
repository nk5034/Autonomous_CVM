# Phase 10 Quick-Start Guide

## ✅ Status: Complete & Running

Both backend and frontend servers are actively running:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000

## 🚀 Access A/B Testing Dashboard

Open your browser and navigate to:
```
http://localhost:3000/campaigns/ab-testing
```

## 📋 What to Expect

### Page Load
1. Experiment configuration card with fields for campaign ID, experiment name, hypothesis
2. Control group settings (name, traffic %, conversion rate)
3. Variant section showing one or more treatment arms
4. Action buttons: "Run A/B Test Analysis", "Load API Template", "Add Variant"

### How to Test

**Option 1: Use Template (Quickest)**
1. Click "Load API Template" button
2. Click "Run A/B Test Analysis"
3. View KPIs and charts below

**Option 2: Manual Configuration**
1. Set Campaign ID (e.g., 700)
2. Enter Experiment Name (e.g., "Q4 CTA Test")
3. Adjust Control conversion rate if needed (default 0.05)
4. Modify or add variants with expected lift
5. Click "Run A/B Test Analysis"
6. Charts and recommendation appear below

### Expected Results

After running, you'll see:
- **KPI Cards**: Total audience, control conversion, best lift, best confidence
- **Traffic Allocation Chart**: Shows % split between control and variants
- **Conversion Rates**: Rate per arm
- **Relative Lift**: % improvement each variant shows over control
- **Statistical Confidence**: How likely the lift is real (0–100%)
- **Recommendation Panel**: Action (promote_variant, collect_more_data, or keep_control)
- **Performance JSON**: Detailed variant metrics

## 🔌 API Testing (Backend Only)

### Get Template
```bash
curl http://localhost:8000/api/v1/ab-testing/template
```

### Run Analysis
```bash
curl -X POST http://localhost:8000/api/v1/ab-testing/run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": 700,
    "experiment_name": "Q4 CTA Test",
    "hypothesis": "Deadline urgency increases conversion.",
    "audience_size": 100000,
    "confidence_level_target": 0.95,
    "control": {
      "name": "control",
      "traffic_percentage": 0.2,
      "conversion_rate": 0.05
    },
    "variants": [
      {
        "name": "variant_urgency",
        "traffic_percentage": 0.8,
        "conversion_rate": 0.062
      }
    ]
  }'
```

### Expected Response
```json
{
  "experiment_id": "ab_a5546c75c437",
  "arms": [
    {
      "name": "control",
      "allocation": 0.2,
      "audience": 20000,
      "expected_conversions": 1000
    },
    {
      "name": "variant_urgency",
      "allocation": 0.8,
      "audience": 80000,
      "expected_conversions": 4960
    }
  ],
  "variant_performance": [
    {
      "name": "variant_urgency",
      "lift": 0.24,
      "confidence": 1.0,
      "statistically_significant": true,
      "incremental_conversions": 960
    }
  ],
  "recommendation": {
    "action": "promote_variant",
    "rationale": "variant_urgency exceeds confidence target (95.00%) with positive lift and highest incremental conversions.",
    "recommended_variant": "variant_urgency"
  }
}
```

## 🧪 Run Unit Tests

```bash
cd backend
python -m pytest tests/unit/test_ab_testing_service.py tests/unit/test_ab_testing_api.py -v
```

All 3 tests should pass ✅

## 📂 Key Files

**Backend**
- Service Logic: `backend/src/services/ab_testing.py`
- API Endpoints: `backend/src/api/v1/endpoints/ab_testing.py`
- Request/Response Schemas: `backend/src/schemas/ab_testing.py`

**Frontend**
- Dashboard Page: `frontend/src/app/campaigns/ab-testing/page.tsx`
- API Client: `frontend/src/lib/api/abTesting.ts`
- TypeScript Types: `frontend/src/types/abTesting.ts`

**Documentation**
- Phase 10 Details: `docs/PHASE10_AB_TESTING.md`
- API Reference: `docs/api/ab-testing.md`

## 💡 Features Implemented

✅ Control group definition with traffic allocation
✅ Multiple variant support with traffic distribution
✅ Automatic allocation normalization (sums to 100%)
✅ Two-proportion z-test statistical confidence
✅ Relative and absolute lift calculation
✅ P-value and significance determination
✅ Recommendation engine (3 actions)
✅ Dashboard KPIs and charts
✅ Template endpoint for quick start
✅ Full type safety (Python + TypeScript)
✅ Unit test coverage (service + API)

## 🔍 Troubleshooting

**Frontend won't load?**
- Check `http://localhost:3000` is responding
- Run `cd frontend && npm run dev` in a new terminal

**Backend API error?**
- Check `http://localhost:8000/health` returns `{"status": "healthy"}`
- Check `http://localhost:8000/docs` for interactive API docs
- Run tests: `cd backend && python -m pytest tests/unit/test_ab_testing_*.py`

**Data doesn't match expectations?**
- Use "Load API Template" to ensure valid input
- Check console for error messages
- Verify confidence_level_target is 0.0–1.0 (e.g., 0.95 for 95%)

## 📚 Related Pages

- **Artifacts**: `http://localhost:3000/campaigns/artifacts`
- **Simulation**: `http://localhost:3000/campaigns/simulation`
- **Home**: `http://localhost:3000/`

---

**Phase 10 Complete** | Ready for integration testing and feature expansion
