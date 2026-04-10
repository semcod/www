import { C } from "../../../constants";

export function ErrorResult({ error, isSandbox }) {
  return (
    <div style={{
      background: `${C.red}15`, border: `1px solid ${C.red}`, borderRadius: 10,
      padding: "20px 24px", marginBottom: 28,
    }}>
      <div style={{ fontSize: 16, fontWeight: 600, color: C.red, marginBottom: 8 }}>
        ⚠️ Analysis failed
      </div>
      <p style={{ fontSize: 14, color: C.fg2, margin: 0 }}>{error}</p>
      {isSandbox && (
        <p style={{ fontSize: 13, color: C.fg3, marginTop: 12 }}>
          Make sure the repository is public and accessible.
          Private repositories require GitHub authentication.
        </p>
      )}
    </div>
  );
}
