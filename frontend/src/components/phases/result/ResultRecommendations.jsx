import { RecommendationCard } from "../../ui";

export function ResultRecommendations({ recommendations }) {
  return (
    <>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Recommendations</h3>
      <div style={{ display: "grid", gap: 12 }}>
        {recommendations.map((rec, i) => (
          <RecommendationCard key={i} rec={rec} index={i} />
        ))}
      </div>
    </>
  );
}
