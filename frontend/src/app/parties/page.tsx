import type { Metadata } from "next";
import Link from "next/link";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { PageContainer } from "@/components/layout/page-container";
import { SemiDonutChart, type ChartSegment } from "@/features/parties/components/semi-donut-chart";

export const metadata: Metadata = {
  title: "政党一覧 | Kuni-Musubi",
};

// PartyResponse[] → ChartSegment[]（議席数 0 の政党は除外）
function toSegments(parties: PartyResponse[], key: "house_of_representatives_seats" | "house_of_councillors_seats"): ChartSegment[] {
  return parties
    .filter((p) => (p[key] ?? 0) > 0)
    .map((p) => ({
      id: p.id,
      name: p.short_name ?? p.name,
      color: p.color_hex ?? "#999999",
      seats: p[key] ?? 0,
    }));
}

// 政党一覧画面（Server Component）
export default async function PartiesPage() {
  let parties: PartyResponse[];
  try {
    parties = await listParties();
  } catch {
    parties = [];
  }

  const totalHR = parties.reduce((sum, p) => sum + (p.house_of_representatives_seats ?? 0), 0);
  const totalHC = parties.reduce((sum, p) => sum + (p.house_of_councillors_seats ?? 0), 0);

  const hrSegments = toSegments(parties, "house_of_representatives_seats");
  const hcSegments = toSegments(parties, "house_of_councillors_seats");

  return (
    <PageContainer className="py-6">
      <h1
        className="text-2xl font-bold mb-6"
        style={{ color: "var(--color-text-primary)" }}
      >
        政党一覧
      </h1>

      {/* 衆参議席半円グラフ */}
      {(totalHR > 0 || totalHC > 0) && (
        <section className="mb-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
          {totalHR > 0 && (
            <SemiDonutChart title="衆議院" total={totalHR} segments={hrSegments} />
          )}
          {totalHC > 0 && (
            <SemiDonutChart title="参議院" total={totalHC} segments={hcSegments} />
          )}
        </section>
      )}

      {/* 政党リスト見出し */}
      <p
        className="text-xs font-medium mb-3"
        style={{ color: "var(--color-text-secondary)" }}
      >
        詳しく知りたい方はこちら
      </p>

      {/* 政党リスト（縦並び） */}
      <ul
        className="border-t"
        style={{ borderColor: "var(--color-border)" }}
      >
        {parties.map((party) => {
          const hr = party.house_of_representatives_seats ?? 0;
          const hc = party.house_of_councillors_seats ?? 0;
          return (
            <li
              key={party.id}
              className="border-b"
              style={{ borderColor: "var(--color-border)" }}
            >
              <Link
                href={`/parties/${party.id}`}
                className="flex items-center gap-3 py-3.5 transition-opacity duration-150 hover:opacity-70"
              >
                <span
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: party.color_hex ?? "#999999" }}
                />
                <span
                  className="flex-1 font-medium text-sm"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  {party.name}
                </span>
                <span
                  className="text-xs flex-shrink-0"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  衆{hr} 参{hc}
                </span>
                <span
                  className="text-xs flex-shrink-0"
                  style={{ color: "var(--color-brand-primary)" }}
                >
                  詳細を見る &gt;
                </span>
              </Link>
            </li>
          );
        })}
      </ul>

      {parties.length === 0 && (
        <p className="text-sm mt-4" style={{ color: "var(--color-text-secondary)" }}>
          政党情報を読み込めませんでした
        </p>
      )}
    </PageContainer>
  );
}
