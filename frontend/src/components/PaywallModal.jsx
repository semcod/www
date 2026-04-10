import { C } from "../constants";

const PLANS = [
  {
    key: "pro",
    name: "Pro",
    billing: "monthly",
    price: "$9",
    period: "/month",
    annualNote: "or $81/year (25% off)",
    features: ["Unlimited scans", "Trend API access", "Scan diff & proposals", "Scheduled scans"],
    highlight: true,
  },
  {
    key: "pro",
    name: "Pro Annual",
    billing: "annual",
    price: "$6.75",
    period: "/month",
    annualNote: "billed $81/year",
    features: ["Everything in Pro", "Best value — save $27/year"],
    highlight: false,
  },
];

function PlanCard({ plan, onSelect, loading }) {
  return (
    <div
      style={{
        flex: 1,
        background: plan.highlight ? `${C.cyan}18` : C.bg2,
        border: `2px solid ${plan.highlight ? C.cyan : C.border}`,
        borderRadius: 12,
        padding: "24px 20px",
        display: "flex",
        flexDirection: "column",
        gap: 12,
      }}
    >
      <div style={{ fontSize: 13, fontWeight: 700, color: plan.highlight ? C.cyan : C.fg2, textTransform: "uppercase", letterSpacing: 1 }}>
        {plan.name}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
        <span style={{ fontSize: 32, fontWeight: 800, color: C.fg }}>{plan.price}</span>
        <span style={{ fontSize: 13, color: C.fg3 }}>{plan.period}</span>
      </div>
      <div style={{ fontSize: 11, color: C.fg3 }}>{plan.annualNote}</div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 6 }}>
        {plan.features.map((f) => (
          <li key={f} style={{ fontSize: 13, color: C.fg2, display: "flex", gap: 6 }}>
            <span style={{ color: C.green }}>✓</span>
            {f}
          </li>
        ))}
      </ul>
      <button
        onClick={() => onSelect(plan.key, plan.billing)}
        disabled={loading}
        style={{
          marginTop: "auto",
          padding: "12px 0",
          background: plan.highlight ? C.cyan : C.bg3,
          color: plan.highlight ? C.bg : C.fg,
          border: `1px solid ${plan.highlight ? C.cyan : C.border}`,
          borderRadius: 8,
          fontSize: 14,
          fontWeight: 700,
          cursor: loading ? "not-allowed" : "pointer",
          fontFamily: "inherit",
          opacity: loading ? 0.7 : 1,
        }}
      >
        {loading ? "Redirecting…" : "Upgrade →"}
      </button>
    </div>
  );
}

export function PaywallModal({ billingStatus, onSelect, onDismiss, loading }) {
  if (!billingStatus) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: 24,
      }}
      onClick={onDismiss}
    >
      <div
        style={{
          background: C.bg1,
          border: `1px solid ${C.border}`,
          borderRadius: 16,
          padding: "32px 28px",
          maxWidth: 560,
          width: "100%",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🔒</div>
          <h2 style={{ fontSize: 20, fontWeight: 800, margin: "0 0 8px" }}>
            Weekly scan limit reached
          </h2>
          <p style={{ fontSize: 14, color: C.fg2, margin: 0 }}>
            You've used <strong style={{ color: C.fg }}>{billingStatus.scans_this_week}</strong> of{" "}
            <strong style={{ color: C.fg }}>{billingStatus.scans_per_week}</strong> free scans this week.
            Upgrade to Pro for unlimited scans.
          </p>
        </div>

        <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
          {PLANS.map((plan) => (
            <PlanCard
              key={`${plan.key}-${plan.billing}`}
              plan={plan}
              onSelect={onSelect}
              loading={loading}
            />
          ))}
        </div>

        <div style={{ textAlign: "center" }}>
          <button
            onClick={onDismiss}
            style={{
              background: "transparent",
              border: "none",
              color: C.fg3,
              cursor: "pointer",
              fontSize: 13,
              fontFamily: "inherit",
            }}
          >
            Maybe later — continue with free plan
          </button>
        </div>
      </div>
    </div>
  );
}
