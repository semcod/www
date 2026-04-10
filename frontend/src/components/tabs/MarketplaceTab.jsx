import MarketplaceDashboard from "../MarketplaceDashboard.jsx";

export function MarketplaceTab({ sessionToken, user }) {
  const provider = user?.provider || "github";
  return (
    <MarketplaceDashboard token={sessionToken} provider={provider} />
  );
}
