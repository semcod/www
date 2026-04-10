import { C } from "../../../constants";

export function ResultHeader({ selectedRepo, isSandbox, data, reset, activeTab, setActiveTab }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 700 }}>
          <span style={{ color: C.fg3 }}>Report:</span> {selectedRepo?.full_name || selectedRepo?.name || "unknown/repo"}
          {isSandbox && (
            <span style={{
              display: "inline-block",
              marginLeft: 12,
              fontSize: 11,
              color: C.amber,
              background: `${C.amber}15`,
              padding: "2px 8px",
              borderRadius: 4,
              fontWeight: 500,
            }}>🔒 Sandbox</span>
          )}
        </h2>
        {isSandbox && !data.error && (
          <p style={{ fontSize: 13, color: C.fg3, marginTop: 4 }}>
            Public repository analyzed without authentication.
            <a href="#" onClick={(e) => { e.preventDefault(); reset(); }} style={{ color: C.cyan, marginLeft: 8 }}>Install GitHub App for PR reviews →</a>
          </p>
        )}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <button
          onClick={() => setActiveTab(activeTab === 'share' ? null : 'share')}
          style={{
            background: activeTab === 'share' ? "#1DA1F2" : "#1DA1F220",
            border: activeTab === 'share' ? "none" : "1px solid #1DA1F2",
            color: activeTab === 'share' ? "#fff" : "#1DA1F2",
            cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
            fontFamily: "inherit", fontWeight: 600,
          }}
        >𝕏 Share</button>
        <button
          onClick={() => setActiveTab(activeTab === 'json' ? null : 'json')}
          style={{
            background: activeTab === 'json' ? "#8B5CF6" : "#8B5CF620",
            border: activeTab === 'json' ? "none" : "1px solid #8B5CF6",
            color: activeTab === 'json' ? "#fff" : "#8B5CF6",
            cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
            fontFamily: "inherit", fontWeight: 600,
          }}
        >📊 JSON</button>
        <button
          onClick={() => setActiveTab(activeTab === 'llm' ? null : 'llm')}
          style={{
            background: activeTab === 'llm' ? "#10B981" : "#10B98120",
            border: activeTab === 'llm' ? "none" : "1px solid #10B981",
            color: activeTab === 'llm' ? "#fff" : "#10B981",
            cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
            fontFamily: "inherit", fontWeight: 600,
          }}
        >🤖 LLM Prompt</button>
        <button
          onClick={() => setActiveTab(activeTab === 'markdown' ? null : 'markdown')}
          style={{
            background: activeTab === 'markdown' ? "#6366F1" : "#6366F120",
            border: activeTab === 'markdown' ? "none" : "1px solid #6366F1",
            color: activeTab === 'markdown' ? "#fff" : "#6366F1",
            cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
            fontFamily: "inherit", fontWeight: 600,
          }}
        >📝 Markdown</button>
        <button
          onClick={() => setActiveTab(activeTab === 'toon' ? null : 'toon')}
          style={{
            background: activeTab === 'toon' ? "#F59E0B" : "#F59E0B20",
            border: activeTab === 'toon' ? "none" : "1px solid #F59E0B",
            color: activeTab === 'toon' ? "#fff" : "#F59E0B",
            cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
            fontFamily: "inherit", fontWeight: 600,
          }}
        >📄 TOON</button>
        <button onClick={reset} style={{
          background: C.bg3, border: `1px solid ${C.border}`, color: C.fg2,
          cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
          fontFamily: "inherit",
        }}>New audit</button>
      </div>
    </div>
  );
}
