"use client";

import { useState } from "react";

export type ChartSegment = {
  id: string;
  name: string;
  color: string;
  seats: number;
};

type SemiDonutChartProps = {
  title: string;
  total: number;
  segments: ChartSegment[];
};

// fraction (0 = 左端, 1 = 右端) → SVG 上半円の座標
// 左端 = 9時, 頂点 = 12時, 右端 = 3時 方向（時計回り）
function polar(cx: number, cy: number, r: number, f: number): { x: number; y: number } {
  const a = Math.PI * (1 - f);
  return { x: cx + r * Math.cos(a), y: cy - r * Math.sin(a) };
}

// 半円ドーナツの1セグメント SVG パスを生成する
function segPath(
  cx: number,
  cy: number,
  outerR: number,
  innerR: number,
  s: number,
  e: number,
): string {
  if (e - s <= 0) return "";
  const large = 0;
  const os = polar(cx, cy, outerR, s);
  const oe = polar(cx, cy, outerR, e);
  const ie = polar(cx, cy, innerR, e);
  const is = polar(cx, cy, innerR, s);
  const f = (v: number) => v.toFixed(2);
  return [
    `M${f(os.x)},${f(os.y)}`,
    `A${outerR},${outerR},0,${large},1,${f(oe.x)},${f(oe.y)}`,
    `L${f(ie.x)},${f(ie.y)}`,
    `A${innerR},${innerR},0,${large},0,${f(is.x)},${f(is.y)}Z`,
  ].join(" ");
}

// 半円ドーナツグラフ（衆議院 / 参議院それぞれに使用）
export function SemiDonutChart({ title, total, segments }: SemiDonutChartProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // SVG レイアウト定数
  const VB_W = 300;
  const VB_H = 185;
  const CX = 150;
  const CY = 172;
  const OUTER_R = 136;
  const INNER_R = 78;
  const LABEL_R = OUTER_R + 15; // % ラベルの半径
  const GAP = 0.005; // セグメント間の隙間（fraction）

  const MIN_LABEL_PCT = 5; // ラベルを表示する最小割合(%)
  const TOOLTIP_W = 136;
  const TOOLTIP_H = 44;

  // セグメントをビルドする（seats > 0 のみ）
  type Built = ChartSegment & {
    startFrac: number;
    endFrac: number;
    midFrac: number;
    pct: string;
  };

  const active = segments.filter((s) => s.seats > 0);
  const hasGap = active.length > 1;
  const built: Built[] = [];
  let acc = 0;
  for (const seg of active) {
    const span = seg.seats / total;
    const gap = hasGap && span > GAP ? GAP / 2 : 0;
    const s = acc + gap;
    const e = acc + span - gap;
    const m = acc + span / 2;
    built.push({ ...seg, startFrac: s, endFrac: e, midFrac: m, pct: ((seg.seats / total) * 100).toFixed(1) });
    acc += span;
  }

  // ホバー中セグメントのツールチップ座標を計算する
  const hovered = hoveredId ? built.find((s) => s.id === hoveredId) : null;
  let ttX = CX;
  let ttY = 8;
  if (hovered) {
    const mid = polar(CX, CY, (OUTER_R + INNER_R) / 2, hovered.midFrac);
    ttX = Math.max(TOOLTIP_W / 2 + 4, Math.min(mid.x, VB_W - TOOLTIP_W / 2 - 4));
    ttY = Math.max(mid.y - TOOLTIP_H - 10, 4);
  }

  return (
    <div>
      <svg
        viewBox={`0 0 ${VB_W} ${VB_H}`}
        className="w-full"
        aria-label={`${title} 議席分布グラフ`}
      >
        {/* セグメント */}
        {built.map((seg) => {
          const d = segPath(CX, CY, OUTER_R, INNER_R, seg.startFrac, seg.endFrac);
          const labelPt = polar(CX, CY, LABEL_R, seg.midFrac);
          const showLabel = parseFloat(seg.pct) >= MIN_LABEL_PCT;
          const isHovered = seg.id === hoveredId;

          return (
            <g
              key={seg.id}
              onMouseEnter={() => setHoveredId(seg.id)}
              onMouseLeave={() => setHoveredId(null)}
              style={{ cursor: "pointer" }}
            >
              <path
                d={d}
                fill={seg.color}
                style={{
                  opacity: hoveredId !== null && !isHovered ? 0.55 : 1,
                  transition: "opacity 0.15s",
                }}
              />
              {showLabel && (
                <text
                  x={labelPt.x}
                  y={labelPt.y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize="8"
                  fontWeight="700"
                  fill={seg.color}
                  style={{ pointerEvents: "none", userSelect: "none" }}
                >
                  {seg.pct}%
                </text>
              )}
            </g>
          );
        })}

        {/* 直径ベースライン */}
        <line
          x1={CX - OUTER_R}
          y1={CY}
          x2={CX + OUTER_R}
          y2={CY}
          stroke="var(--color-border)"
          strokeWidth="1.5"
        />

        {/* 中央テキスト: 院名 + 合計議席 */}
        <text
          x={CX}
          y={CY - 44}
          textAnchor="middle"
          fontSize="11"
          fill="var(--color-text-secondary)"
          style={{ userSelect: "none" }}
        >
          {title}
        </text>
        <text
          x={CX}
          y={CY - 22}
          textAnchor="middle"
          fontSize="26"
          fontWeight="700"
          fill="var(--color-text-primary)"
          style={{ userSelect: "none" }}
        >
          {total}
        </text>
        <text
          x={CX}
          y={CY - 7}
          textAnchor="middle"
          fontSize="9"
          fill="var(--color-text-secondary)"
          style={{ userSelect: "none" }}
        >
          議席
        </text>

        {/* ツールチップ（ホバー時） */}
        {hovered && (
          <g style={{ pointerEvents: "none" }}>
            <rect
              x={ttX - TOOLTIP_W / 2}
              y={ttY}
              width={TOOLTIP_W}
              height={TOOLTIP_H}
              rx={6}
              fill="rgba(26,26,26,0.92)"
            />
            <text
              x={ttX}
              y={ttY + 16}
              textAnchor="middle"
              fontSize="10"
              fontWeight="700"
              fill="#ffffff"
              style={{ userSelect: "none" }}
            >
              {hovered.name}
            </text>
            <text
              x={ttX}
              y={ttY + 31}
              textAnchor="middle"
              fontSize="9"
              fill="rgba(255,255,255,0.85)"
              style={{ userSelect: "none" }}
            >
              {hovered.seats}議席（{hovered.pct}%）
            </text>
          </g>
        )}
      </svg>

      {/* 凡例（政党名 + 議席数 + %） */}
      <ul className="mt-1 px-1 space-y-0.5">
        {built.map((seg) => (
          <li
            key={seg.id}
            className="flex items-center gap-2 py-0.5 rounded cursor-pointer"
            style={{
              backgroundColor:
                hoveredId === seg.id ? `${seg.color}18` : "transparent",
              transition: "background-color 0.12s",
            }}
            onMouseEnter={() => setHoveredId(seg.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <span
              className="flex-shrink-0 w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: seg.color }}
            />
            <span
              className="flex-1 text-xs leading-none"
              style={{ color: "var(--color-text-primary)" }}
            >
              {seg.name}
            </span>
            <span
              className="text-xs tabular-nums flex-shrink-0"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {seg.seats}
            </span>
            <span
              className="text-xs tabular-nums w-10 text-right flex-shrink-0 font-medium"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {seg.pct}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
