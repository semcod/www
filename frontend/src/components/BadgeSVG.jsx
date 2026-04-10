import { gradeColor } from "../constants";

export function BadgeSVG({ grade, score, width = 152 }) {
  const color = gradeColor(grade);
  const labelW = 82;
  const valueText = score != null ? `${grade} · ${score}%` : grade;
  const valueW = width - labelW;

  return (
    <svg width={width} height="20" role="img" style={{ display: "block" }}>
      <defs>
        <linearGradient id="bg" x2="0" y2="100%">
          <stop offset="0" stopColor="#bbb" stopOpacity=".1" />
          <stop offset="1" stopOpacity=".1" />
        </linearGradient>
        <clipPath id="cr"><rect width={width} height="20" rx="3" /></clipPath>
      </defs>
      <g clipPath="url(#cr)">
        <rect width={labelW} height="20" fill="#555" />
        <rect x={labelW} width={valueW} height="20" fill={color} />
        <rect width={width} height="20" fill="url(#bg)" />
      </g>
      <g fill="#fff" textAnchor="middle" fontFamily="Verdana,Geneva,sans-serif" fontSize="11">
        <text x={labelW / 2} y="15" fillOpacity=".3" fill="#010101">code health</text>
        <text x={labelW / 2} y="14">code health</text>
        <text x={labelW + valueW / 2} y="15" fillOpacity=".3" fill="#010101">{valueText}</text>
        <text x={labelW + valueW / 2} y="14">{valueText}</text>
      </g>
    </svg>
  );
}
