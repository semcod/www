import { config } from "../config";

export function generateShareText(audit, repo) {
  const grade = audit.grade;
  const score = audit.health_score;
  const files = audit.stats?.total_files || 0;
  const lines = audit.stats?.total_lines || 0;
  
  return `🔍 Sprawdziłem jakość kodu repozytorium ${repo}!
  
📊 Wynik: ${grade} (${score}%)
📁 ${files} plików
📝 ${(lines / 1000).toFixed(1)}k linii kodu

Analiza przez @semcod_dev`;
}

export function getShareUrls(audit, repo) {
  const text = encodeURIComponent(generateShareText(audit, repo));
  const url = encodeURIComponent(config.getShareUrl(repo));
  
  return {
    twitter: `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${text}`,
    reddit: `https://reddit.com/submit?url=${url}&title=${encodeURIComponent(`Code Health Report: ${repo} - ${audit.grade} (${audit.health_score}%)`)}`,
    bluesky: `https://bsky.app/intent/compose?text=${text}`,
  };
}
