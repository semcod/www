import { C } from "../constants";

export function ProgressSteps({ phase }) {
  const steps = [
    { id: "auth", label: "Connect" },
    { id: "repos", label: "Select" },
    { id: "scanning", label: "Analyze" },
    { id: "value", label: "Insights" },
    { id: "trial", label: "Trial" },
  ];

  const order = ["auth", "repos", "scanning", "value", "trial"];
  const currentIdx = order.indexOf(phase);

  if (!["auth", "repos", "scanning", "value", "trial"].includes(phase)) return null;

  return (
    <div style={{ display: "flex", justifyContent: "center", gap: 0, marginBottom: 40 }}>
      {steps.map(({ id, label }, i, arr) => {
        const stepIdx = order.indexOf(id);
        const done = stepIdx < currentIdx;
        const active = stepIdx === currentIdx;
        return (
          <div key={id} style={{ display: "flex", alignItems: "center" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{
                width: 28, height: 28, borderRadius: "50%", display: "flex",
                alignItems: "center", justifyContent: "center",
                background: done ? C.green : active ? C.cyan : C.bg2,
                border: `2px solid ${done ? C.green : active ? C.cyan : C.border}`,
                fontSize: 12, fontWeight: 700,
                color: done || active ? C.bg : C.fg3,
                margin: "0 auto",
              }}>
                {done ? "✓" : i + 1}
              </div>
              <div style={{ fontSize: 10, color: active ? C.cyan : done ? C.green : C.fg3, marginTop: 4, fontFamily: "'JetBrains Mono', monospace" }}>{label}</div>
            </div>
            {i < arr.length - 1 && (
              <div style={{ width: 32, height: 2, background: done ? C.green : C.bg3, margin: "0 4px 14px" }} />
            )}
          </div>
        );
      })}
    </div>
  );
}
