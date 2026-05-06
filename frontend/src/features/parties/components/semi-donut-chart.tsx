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
  hideLegend?: boolean;
  flipped?: boolean;
  highlightedId?: string | null;
  onHighlight?: (id: string | null) => void;
  onSelect?: (id: string) => void;
  className?: string;
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
  flipped: boolean,
): string {
  if (e - s <= 0) return "";
  const large = 0;
  const point = flipped
    ? (r: number, f: number) => {
        const a = Math.PI * (1 - f);
        return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
      }
    : (r: number, f: number) => polar(cx, cy, r, f);
  const os = point(outerR, s);
  const oe = point(outerR, e);
  const ie = point(innerR, e);
  const is = point(innerR, s);
  const outerSweep = flipped ? 0 : 1;
  const innerSweep = flipped ? 1 : 0;
  const f = (v: number) => v.toFixed(2);
  return [
    `M${f(os.x)},${f(os.y)}`,
    `A${outerR},${outerR},0,${large},${outerSweep},${f(oe.x)},${f(oe.y)}`,
    `L${f(ie.x)},${f(ie.y)}`,
    `A${innerR},${innerR},0,${large},${innerSweep},${f(is.x)},${f(is.y)}Z`,
  ].join(" ");
}

// 半円ドーナツグラフ（衆議院 / 参議院それぞれに使用）
export function SemiDonutChart({
  title,
  total,
  segments,
  hideLegend = false,
  flipped = false,
  highlightedId,
  onHighlight,
  onSelect,
  className = "",
}: SemiDonutChartProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const activeId = highlightedId ?? hoveredId;

  // SVG レイアウト定数
  const VB_W = 300;
  const VB_H = 185;
  const CX = 150;
  const CY = flipped ? 13 : 172;
  const OUTER_R = 136;
  const INNER_R = 78;
  const LABEL_R = OUTER_R + 15; // % ラベルの半径
  const GAP = 0.005; // セグメント間の隙間（fraction）

  const MIN_LABEL_PCT = 5; // ラベルを表示する最小割合(%)
  const TOOLTIP_W = 136;
  const TOOLTIP_H = 44;
  const titleY = flipped ? CY + 18 : CY - 66;
  const totalY = flipped ? CY + 50 : CY - 34;
  const seatsY = flipped ? CY + 64 : CY - 18;

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
  const hovered = activeId ? built.find((s) => s.id === activeId) : null;
  let ttX = CX;
  let ttY = 8;
  if (hovered) {
    const mid = flipped
      ? (() => {
          const a = Math.PI * (1 - hovered.midFrac);
          return {
            x: CX + ((OUTER_R + INNER_R) / 2) * Math.cos(a),
            y: CY + ((OUTER_R + INNER_R) / 2) * Math.sin(a),
          };
        })()
      : polar(CX, CY, (OUTER_R + INNER_R) / 2, hovered.midFrac);
    ttX = Math.max(TOOLTIP_W / 2 + 4, Math.min(mid.x, VB_W - TOOLTIP_W / 2 - 4));
    ttY = Math.max(mid.y - TOOLTIP_H - 10, 4);
  }

  return (
    <div className={`semi-donut ${flipped ? "semi-donut--flipped" : ""} ${className}`}>
      <svg
        viewBox={`0 0 ${VB_W} ${VB_H}`}
        className="semi-donut__svg"
        aria-label={`${title} 議席分布グラフ`}
      >
        {/* セグメント */}
        {built.map((seg) => {
          const d = segPath(CX, CY, OUTER_R, INNER_R, seg.startFrac, seg.endFrac, flipped);
          const labelPt = flipped
            ? (() => {
                const a = Math.PI * (1 - seg.midFrac);
                return { x: CX + LABEL_R * Math.cos(a), y: CY + LABEL_R * Math.sin(a) };
              })()
            : polar(CX, CY, LABEL_R, seg.midFrac);
          const showLabel = parseFloat(seg.pct) >= MIN_LABEL_PCT;
          const isHovered = seg.id === activeId;

          return (
            <g
              key={seg.id}
              onMouseEnter={() => {
                setHoveredId(seg.id);
                onHighlight?.(seg.id);
              }}
              onMouseLeave={() => {
                setHoveredId(null);
                onHighlight?.(null);
              }}
              onClick={() => onSelect?.(seg.id)}
              style={{ cursor: "pointer" }}
            >
              <path
                d={d}
                fill={seg.color}
                style={{
                  opacity: activeId !== null && !isHovered ? 0.35 : 1,
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
                  fontWeight="500"
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
          y={titleY}
          textAnchor="middle"
          fontSize="11"
          fill="var(--color-text-secondary)"
          style={{ userSelect: "none" }}
        >
          {title}
        </text>
        <text
          x={CX}
          y={totalY}
          textAnchor="middle"
          fontSize="26"
          fontWeight="500"
          fill="var(--color-text-primary)"
          style={{ userSelect: "none" }}
        >
          {total}
        </text>
        <text
          x={CX}
          y={seatsY}
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
              fontWeight="500"
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
      {!hideLegend && (
        <ul className="semi-donut__legend">
          {built.map((seg) => (
            <li
              key={seg.id}
              className="semi-donut__legend-item"
              style={{
                backgroundColor:
                  activeId === seg.id ? `${seg.color}18` : "transparent",
                transition: "background-color 0.12s",
              }}
              onMouseEnter={() => {
                setHoveredId(seg.id);
                onHighlight?.(seg.id);
              }}
              onMouseLeave={() => {
                setHoveredId(null);
                onHighlight?.(null);
              }}
              onClick={() => onSelect?.(seg.id)}
            >
              <span
                className="semi-donut__legend-dot"
                style={{ backgroundColor: seg.color }}
              />
              <span
                className="semi-donut__legend-name"
                style={{ color: "var(--color-text-primary)" }}
              >
                {seg.name}
              </span>
              <span
                className="semi-donut__legend-seats"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {seg.seats}
              </span>
              <span
                className="semi-donut__legend-pct"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {seg.pct}%
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
