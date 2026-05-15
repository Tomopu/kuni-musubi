"use client";

import { useState } from "react";
import {
  SemiDonutChart,
  type ChartSegment,
} from "@/features/parties/components/semi-donut-chart";
import type { PartyResponse } from "@/lib/api/parties-api";

type SeatOverviewProps = {
  parties: PartyResponse[];
  representativeSegments: ChartSegment[];
  councillorSegments: ChartSegment[];
  totalRepresentatives: number;
  totalCouncillors: number;
};

function pct(seats: number, total: number): string {
  if (total <= 0) return "0.0";
  return ((seats / total) * 100).toFixed(1);
}

export function SeatOverview({
  parties,
  representativeSegments,
  councillorSegments,
  totalRepresentatives,
  totalCouncillors,
}: SeatOverviewProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const activeId = hoveredId ?? selectedId;

  function selectParty(id: string) {
    setSelectedId((current) => (current === id ? null : id));
  }

  return (
    <div className="semi-chart-grid">
      <div className="semi-chart-card">
        <SemiDonutChart
          title="衆議院"
          total={totalRepresentatives}
          segments={representativeSegments}
          highlightedId={activeId}
          onHighlight={setHoveredId}
          onSelect={selectParty}
        />
      </div>
      <div className="semi-chart-card semi-chart-card--councillors">
        <SemiDonutChart
          title="参議院"
          total={totalCouncillors}
          segments={councillorSegments}
          highlightedId={activeId}
          onHighlight={setHoveredId}
          onSelect={selectParty}
        />
        <SemiDonutChart
          title="参議院"
          total={totalCouncillors}
          segments={councillorSegments}
          highlightedId={activeId}
          onHighlight={setHoveredId}
          onSelect={selectParty}
          hideLegend
          flipped
          className="semi-donut--mobile-flipped"
        />
      </div>
      <ul className="seat-combined-legend">
        {parties
          .filter((party) => party.total_seats > 0)
          .map((party) => {
            const representatives = party.house_of_representatives_seats ?? 0;
            const councillors = party.house_of_councillors_seats ?? 0;
            const isActive = selectedId === party.id;
            return (
              <li key={party.id}>
                <button
                  type="button"
                  className="seat-combined-legend__button"
                  aria-pressed={isActive}
                  onMouseEnter={() => setHoveredId(party.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  onClick={() => selectParty(party.id)}
                >
                  <span
                    className="seat-combined-legend__dot"
                    style={{ backgroundColor: party.color_hex ?? "#999999" }}
                  />
                  <span className="seat-combined-legend__name">{party.short_name}</span>
                  <span className="seat-combined-legend__chamber">
                    衆{representatives}議席 ({pct(representatives, totalRepresentatives)}%)
                  </span>
                  <span className="seat-combined-legend__chamber">
                    参{councillors}議席 ({pct(councillors, totalCouncillors)}%)
                  </span>
                </button>
              </li>
            );
          })}
      </ul>
    </div>
  );
}
