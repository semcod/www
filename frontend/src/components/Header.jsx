import { C } from "../lib/config";

export function Header({ tab, setTab, reset }) {
  const tabBtn = (id, label) => (
    <button
      onClick={() => { setTab(id); if (id === "audit") reset(); }}
      style={{
        padding: "12px 20px", cursor: "pointer", fontSize: 13, fontWeight: 600,
        color: tab === id ? C.cyan : C.fg3, background: "transparent", border: "none",
        borderBottom: `2px solid ${tab === id ? C.cyan : "transparent"}`,
        fontFamily: "'JetBrains Mono', monospace", transition: "all 0.2s",
      }}
    >{label}</button>
  );

  return (
    <header style={{
      borderBottom: `1px solid ${C.border}`, padding: "0 24px",
      background: "rgba(5,8,15,0.92)", backdropFilter: "blur(24px)",
      position: "sticky", top: 0, zIndex: 50,
    }}>
      <div style={{ maxWidth: 1000, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 58 }}>
        <span onClick={reset} style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: 18, color: C.cyan, cursor: "pointer" }}>
          semcod<span style={{ color: C.fg3 }}>.dev</span>
        </span>
        <nav style={{ display: "flex" }}>
          {tabBtn("audit", "Audit")}
          {tabBtn("prbot", "PR Bot")}
          {tabBtn("repo", "Repo")}
          {tabBtn("badge", "Badge")}
        </nav>
      </div>
    </header>
  );
}
