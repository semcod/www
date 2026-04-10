import { C, API } from "../../constants";
import { demoLogin } from "../../api";

export function AuthPhase() {
  const handleLogin = () => {
    window.location.href = `${API}/auth/github`;
  };

  const handleDemoLogin = async () => {
    try {
      const data = await demoLogin();
      if (data.session) {
        localStorage.setItem("semcod_session", data.session);
        window.location.reload();
      }
    } catch (e) {
      // Demo mode not available
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "80px auto", textAlign: "center" }}>
      <div style={{
        width: 64, height: 64, borderRadius: "50%", background: C.bg2,
        border: `1px solid ${C.border}`, display: "flex", alignItems: "center",
        justifyContent: "center", fontSize: 28, margin: "0 auto 24px",
      }}>🔒</div>
      <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>Authorize GitHub</h2>
      <p style={{ fontSize: 14, color: C.fg2, marginBottom: 32, lineHeight: 1.6 }}>
        Semcod needs access to your repositories to run audits and post PR comments.
      </p>

      <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: "20px 24px", marginBottom: 24, textAlign: "left" }}>
        {["Read repository metadata", "Read code for analysis", "Post PR comments"].map(item => (
          <div key={item} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 14, color: C.fg, marginBottom: 12 }}>
            <span style={{ color: C.green }}>✓</span> {item}
          </div>
        ))}
        <div style={{ fontSize: 12, color: C.fg3, marginTop: 16, paddingTop: 16, borderTop: `1px solid ${C.border}` }}>
          No code is stored on our servers. All analysis runs in memory.
        </div>
      </div>

      <button onClick={handleLogin} style={{
        background: C.cyan, color: C.bg, border: "none", borderRadius: 10,
        padding: "14px 32px", fontSize: 15, fontWeight: 700, cursor: "pointer",
        fontFamily: "inherit", width: "100%",
      }}>
        Continue with GitHub →
      </button>

      <button onClick={handleDemoLogin} style={{
        background: "transparent", color: C.fg3, border: `1px solid ${C.border}`, borderRadius: 10,
        padding: "12px 24px", fontSize: 13, fontWeight: 600, cursor: "pointer",
        fontFamily: "inherit", width: "100%", marginTop: 12,
      }}>
        Or try Demo Mode (no GitHub needed)
      </button>
    </div>
  );
}
