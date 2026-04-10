const BUTTONS = [
  { tab: "share",    label: "𝕏 Share",      color: "#1DA1F2" },
  { tab: "json",     label: "📊 JSON",       color: "#8B5CF6" },
  { tab: "llm",      label: "🤖 LLM Prompt", color: "#10B981" },
  { tab: "markdown", label: "📝 Markdown",   color: "#6366F1" },
  { tab: "toon",     label: "📄 TOON",       color: "#F59E0B" },
];

export function DownloadButtons({ activeTab, setActiveTab }) {
  return (
    <>
      {BUTTONS.map(({ tab, label, color }) => {
        const active = activeTab === tab;
        return (
          <button
            key={tab}
            onClick={() => setActiveTab(active ? null : tab)}
            style={{
              background: active ? color : `${color}20`,
              border: active ? "none" : `1px solid ${color}`,
              color: active ? "#fff" : color,
              cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
              fontFamily: "inherit", fontWeight: 600,
            }}
          >{label}</button>
        );
      })}
    </>
  );
}
