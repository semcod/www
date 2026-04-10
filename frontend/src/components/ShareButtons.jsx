import { getShareUrls } from "../utils/share";

export function ShareButtons({ scan, repo, size = "default", onClick }) {
  const handleShare = (platform, e) => {
    if (e) {
      e.stopPropagation();
    }
    if (onClick) {
      onClick();
    }
    const shareUrls = getShareUrls(scan, repo);
    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
  };

  const styleBase = {
    border: "none",
    color: "#fff",
    cursor: "pointer",
    fontFamily: "inherit",
    fontWeight: size === "default" ? 500 : 600,
    fontSize: 12,
    padding: size === "default" ? "6px 12px" : "8px 12px",
    borderRadius: 6,
  };

  return (
    <>
      <button
        onClick={(e) => handleShare('twitter', e)}
        style={{ ...styleBase, background: "#1DA1F2" }}
        title="Share on X (Twitter)"
      >
        𝕏
      </button>
      <button
        onClick={(e) => handleShare('linkedin', e)}
        style={{ ...styleBase, background: "#0077B5" }}
        title="Share on LinkedIn"
      >
        in
      </button>
      <button
        onClick={(e) => handleShare('bluesky', e)}
        style={{ ...styleBase, background: "#0085FF" }}
        title="Share on Bluesky"
      >
        🦋
      </button>
    </>
  );
}
