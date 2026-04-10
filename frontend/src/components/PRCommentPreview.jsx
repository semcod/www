export function PRCommentPreview() {
  return (
    <div style={{
      background: "#0d1117", border: "1px solid #30363d", borderRadius: 8,
      padding: 24, fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      fontSize: 14, color: "#e6edf3", maxWidth: 720,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, paddingBottom: 14, borderBottom: "1px solid #21262d" }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%", background: "linear-gradient(135deg, #00e5ff, #00e676)",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 800, color: "#000",
        }}>S</div>
        <div>
          <span style={{ fontWeight: 600, fontSize: 14 }}>semcod-bot</span>
          <span style={{ color: "#7d8590", fontSize: 12, marginLeft: 8 }}>commented 2 minutes ago</span>
        </div>
      </div>

      <h2 style={{ fontSize: 20, margin: "0 0 10px", color: "#e6edf3", fontWeight: 600 }}>
        🟡 AI Review for PR #42 · <strong>B+</strong> (72/100)
      </h2>
      <p style={{ margin: "0 0 18px", color: "#7d8590", fontSize: 13, lineHeight: 1.6 }}>
        Automatically detect bugs, security issues, and improvements in every PR. {" "}
        <a href="#" style={{ color: "#58a6ff" }}>View full report →</a>
      </p>

      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 20 }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #21262d" }}>
            <th style={{ textAlign: "left", padding: "10px 0", color: "#7d8590", fontWeight: 500, fontSize: 12 }}>Metric</th>
            <th style={{ textAlign: "left", padding: "10px 0", color: "#7d8590", fontWeight: 500, fontSize: 12 }}>Value</th>
          </tr>
        </thead>
        <tbody>
          {[
            ["Files changed", "12"],
            ["Additions", "+347"],
            ["Deletions", "-89"],
            ["Complexity (CC̄)", "4.2 → 4.8 ⚠️"],
            ["New duplications", "+2 groups"],
            ["Tests in PR", "⚠️ None"],
            ["Report", "[open full report →](https://semcod.com/report/owner/repo)"],
          ].map(([k, v]) => (
            <tr key={k} style={{ borderBottom: "1px solid #21262d" }}>
              <td style={{ padding: "10px 0", color: "#e6edf3" }}>{k}</td>
              <td style={{ padding: "10px 0", color: "#e6edf3", fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}>{v}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={{ fontSize: 15, margin: "20px 0 10px", color: "#e6edf3" }}>⚠️ Large files (&gt;300 changes)</h3>
      <ul style={{ margin: "0 0 16px", paddingLeft: 20, color: "#e6edf3", lineHeight: 1.8 }}>
        <li><code style={{ background: "#161b22", padding: "2px 8px", borderRadius: 4, fontSize: 13 }}>src/formatters.py</code> — 412 changes</li>
      </ul>

      <h3 style={{ fontSize: 15, margin: "20px 0 10px", color: "#e6edf3" }}>🎯 Suggested fixes</h3>
      <ul style={{ margin: "0 0 16px", paddingLeft: 20, color: "#e6edf3", lineHeight: 1.8 }}>
        <li>Split <code style={{ background: "#161b22", padding: "2px 8px", borderRadius: 4, fontSize: 13 }}>formatters.py</code> — CC=28 (target: ≤10)</li>
        <li>Add tests for new endpoints</li>
        <li>2 new duplications from <code style={{ background: "#161b22", padding: "2px 8px", borderRadius: 4, fontSize: 13 }}>utils/parse.py</code></li>
      </ul>

      <blockquote style={{
        borderLeft: "3px solid #1f6feb", padding: "10px 16px", margin: "16px 0",
        color: "#7d8590", background: "#161b22", borderRadius: "0 6px 6px 0", fontSize: 13,
      }}>
        💡 <strong style={{ color: "#e6edf3" }}>Auto-fix available:</strong> <code style={{ background: "#21262d", padding: "2px 6px", borderRadius: 3 }}>redsl refactor --pr 47 --auto</code> will fix 3 of 5 issues automatically.
      </blockquote>

      <hr style={{ border: "none", borderTop: "1px solid #21262d", margin: "18px 0" }} />
      <sub style={{ color: "#7d8590" }}>
        🔬 <a href="#" style={{ color: "#58a6ff" }}>Semcod</a> · audit: <code style={{ background: "#161b22", padding: "1px 4px", borderRadius: 3 }}>a3f7b2c</code> · <a href="#" style={{ color: "#58a6ff" }}>full report</a> · <a href="#" style={{ color: "#58a6ff" }}>dashboard</a>
      </sub>
    </div>
  );
}
