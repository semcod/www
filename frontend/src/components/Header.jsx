import { C } from "../constants";

export function Header({ tab, setTab, reset, user, doLogout }) {
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
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span onClick={reset} style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: 18, color: C.cyan, cursor: "pointer" }}>
            semcod<span style={{ color: C.fg3 }}>.dev</span>
          </span>
          <a
            href="/docs/"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize: 11, color: C.fg3, textDecoration: "none",
              padding: "4px 8px", borderRadius: 4,
              background: C.bg2, border: `1px solid ${C.border}`,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            📖 Docs
          </a>
        </div>
        <nav style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {tabBtn("audit", "Audit")}
          {tabBtn("recent", "Ostatnie Skany")}
          {tabBtn("prbot", "PR Bot")}
          {tabBtn("repo", "Repo")}
          {tabBtn("badge", "Badge")}
          {tabBtn("ecosystem", "Ecosystem")}
          {tabBtn("marketplace", "Marketplace")}
          {user && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: 16, paddingLeft: 16, borderLeft: `1px solid ${C.border}` }}>
              <img src={user.avatar_url} alt={user.login} style={{ width: 28, height: 28, borderRadius: "50%", border: `1px solid ${C.border}` }} />
              <span style={{ fontSize: 12, color: C.fg2, fontFamily: "'JetBrains Mono', monospace" }}>{user.login}</span>
              <button onClick={doLogout} style={{
                fontSize: 11, color: C.fg3, background: C.bg2, border: `1px solid ${C.border}`,
                borderRadius: 4, padding: "4px 8px", cursor: "pointer", fontFamily: "'JetBrains Mono', monospace",
              }}>Logout</button>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
