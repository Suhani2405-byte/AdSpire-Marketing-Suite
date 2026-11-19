import React, { useEffect, useState } from "react";
import { DollarSign, TrendingUp } from "lucide-react";
import { Doughnut } from "react-chartjs-2";
import { api } from "../api";
import { CHART_COLORS, chartTextColor } from "../utils/charts";

export default function BudgetPlanner() {
  const [amount, setAmount] = useState(3500);
  const [duration, setDuration] = useState(30);
  const [goal, setGoal] = useState("Sales");
  const [industry, setIndustry] = useState("Consumer Electronics & D2C");
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);

  // Debounced so dragging a slider doesn't flood the API; ignores stale responses
  useEffect(() => {
    let cancelled = false;
    const t = setTimeout(async () => {
      try {
        const res = await api.post("/budget/plan", { total_budget: amount, goal, industry, duration_days: duration });
        if (!cancelled) {
          setPlan(res.data);
          setError(null);
        }
      } catch {
        if (!cancelled) setError("Could not calculate the plan. Is the backend running?");
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [amount, duration, goal, industry]);

  const s = plan?.summary;
  const profit = s?.net_profit ?? 0;

  return (
    <div className="budget-workspace-container">
      <div className="studio-hero-center">
        <div className="hero-top-badge">
          <DollarSign size={14} /> BUDGET & ROAS SIMULATOR
        </div>
        <h2>Ad Budget & Revenue Simulator</h2>
        <p>Estimates based on published industry benchmark CPC, CTR and conversion rates. Real results vary.</p>
      </div>

      <div className="studio-card mb-6">
        <div className="budget-sliders-grid">
          <div className="custom-form-group">
            <div className="flex-label-row">
              <label>TOTAL CAMPAIGN BUDGET</label>
              <span className="highlight-metric-val">${amount.toLocaleString()}</span>
            </div>
            <input type="range" min="300" max="30000" step="100" value={amount}
              onChange={(e) => setAmount(Number(e.target.value))} className="modern-range-slider" />
          </div>
          <div className="custom-form-group">
            <div className="flex-label-row">
              <label>CAMPAIGN DURATION</label>
              <span className="highlight-metric-val">{duration} Days</span>
            </div>
            <input type="range" min="7" max="90" step="1" value={duration}
              onChange={(e) => setDuration(Number(e.target.value))} className="modern-range-slider" />
          </div>
          <div className="custom-form-group">
            <label>OPTIMIZATION GOAL</label>
            <select value={goal} onChange={(e) => setGoal(e.target.value)} className="modern-select">
              {["Sales", "Lead Generation", "Brand Awareness", "Product Promotion", "Engagement"].map((g) => <option key={g}>{g}</option>)}
            </select>
          </div>
          <div className="custom-form-group">
            <label>INDUSTRY BENCHMARKS</label>
            <select value={industry} onChange={(e) => setIndustry(e.target.value)} className="modern-select">
              {["Consumer Electronics & D2C", "E-commerce & D2C", "SaaS & B2B Tech", "Fashion & Beauty", "Health & Wellness"].map((i) => <option key={i}>{i}</option>)}
            </select>
          </div>
        </div>
      </div>

      {error && <div className="warning-banner">{error}</div>}

      {s && (
        <div className="kpi-metric-strip">
          <div className="kpi-card-box purple-border">
            <span className="kpi-label">PROJECTED ROAS</span>
            <div className="kpi-number-display">{s.projected_roas}</div>
            <span className="kpi-subtext">Return on ad spend ({duration}d)</span>
          </div>
          <div className="kpi-card-box green-border">
            <span className="kpi-label">PROJECTED REVENUE</span>
            <div className="kpi-number-display">${s.projected_revenue?.toLocaleString()}</div>
            <span className={`kpi-subtext ${profit < 0 ? "negative" : ""}`}>
              Net profit: {profit >= 0 ? "+" : "-"}${Math.abs(profit).toLocaleString()}
            </span>
          </div>
          <div className="kpi-card-box blue-border">
            <span className="kpi-label">DAILY SPEND</span>
            <div className="kpi-number-display">${s.daily_spend?.toLocaleString()}<span className="kpi-unit">/day</span></div>
            <span className="kpi-subtext">{s.daily_conversions || 0} conversions/day</span>
          </div>
          <div className="kpi-card-box amber-border">
            <span className="kpi-label">ESTIMATED CONVERSIONS</span>
            <div className="kpi-number-display">{s.total_conversions?.toLocaleString()}</div>
            <span className="kpi-subtext">Avg CPA ${s.avg_cpa} • Reach {s.total_reach?.toLocaleString()}</span>
          </div>
        </div>
      )}

      {plan?.channels?.length > 0 && (
        <div className="budget-detail-grid mt-6">
          <div className="studio-card">
            <div className="card-top-header">
              <h3>Channel Allocation ({duration}-Day Schedule)</h3>
            </div>
            <div className="table-overflow-wrapper">
              <table className="modern-data-table">
                <thead>
                  <tr>
                    <th>Channel</th><th>Share</th><th>Budget</th><th>Daily</th><th>CPC</th><th>Clicks</th><th>Conversions</th>
                  </tr>
                </thead>
                <tbody>
                  {plan.channels.map((ch) => (
                    <tr key={ch.name}>
                      <td><strong>{ch.name}</strong></td>
                      <td><span className="purple-tag">{ch.percentage}%</span></td>
                      <td>${ch.budget.toLocaleString()}</td>
                      <td><span className="blue-tag">${ch.daily_budget}/day</span></td>
                      <td>${ch.cpc}</td>
                      <td>{ch.estimated_clicks?.toLocaleString()}</td>
                      <td><strong className="text-emerald-400">{ch.estimated_conversions?.toLocaleString()}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="strategic-tips-container mt-6">
              <h4>✦ Strategic Budget Insights</h4>
              <ul>
                {plan.strategic_tips?.map((tip, i) => (
                  <li key={i}>
                    <TrendingUp size={15} className="text-emerald-400" />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="studio-card chart-card">
            <div className="card-top-header">
              <h3>Spend Split</h3>
            </div>
            <div className="chart-box"><Doughnut
              data={{
                labels: plan.channels.map((c) => c.name),
                datasets: [{ data: plan.channels.map((c) => c.budget), backgroundColor: CHART_COLORS, borderWidth: 0 }],
              }}
              options={{
                  maintainAspectRatio: false,
                plugins: {
                  legend: { position: "bottom", labels: { color: chartTextColor } },
                  tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: $${ctx.parsed.toLocaleString()}` } },
                },
                cutout: "62%",
              }}
            /></div>
          </div>
        </div>
      )}
    </div>
  );
}
