import type { Metadata } from "next";
import Link from "next/link";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { PageContainer } from "@/components/layout/page-container";

export const metadata: Metadata = {
  title: "政党一覧 | Kuni-Musubi",
};

// 衆参合計議席数から CSS conic-gradient 文字列を生成する（ドーナツチャート用）
function buildConicGradient(parties: PartyResponse[], totalSeats: number): string {
  if (totalSeats === 0) return "transparent";
  const stops: string[] = [];
  let acc = 0;
  for (const party of parties) {
    const seats = party.total_seats;
    if (seats === 0) continue;
    const start = (acc / totalSeats) * 100;
    acc += seats;
    const end = (acc / totalSeats) * 100;
    stops.push(
      `${party.color_hex ?? "#999999"} ${start.toFixed(1)}% ${end.toFixed(1)}%`,
    );
  }
  return `conic-gradient(${stops.join(", ")})`;
}

// 政党一覧画面（Server Component）
export default async function PartiesPage() {
  let parties: PartyResponse[];
  try {
    parties = await listParties();
  } catch {
    parties = [];
  }

  const totalSeats = parties.reduce(
    (sum, p) => sum + p.total_seats,
    0,
  );

  const conicGradient = buildConicGradient(parties, totalSeats);

  return (
    <PageContainer className="py-6">
      <h1
        className="text-2xl font-bold mb-6"
        style={{ color: "var(--color-text-primary)" }}
      >
        政党一覧
      </h1>

      {/* 議席ドーナツチャート */}
      {totalSeats > 0 && (
        <section className="mb-8 flex flex-col items-center">
          {/* ドーナツ本体 */}
          <div className="relative w-44 h-44">
            <div
              className="w-full h-full rounded-full"
              style={{ background: conicGradient }}
            />
            {/* 中央の穴 + 合計議席数 */}
            <div
              className="absolute inset-0 m-auto w-28 h-28 rounded-full flex flex-col items-center justify-center"
              style={{ backgroundColor: "var(--color-bg-base)" }}
            >
              <span
                className="text-2xl font-bold leading-none"
                style={{ color: "var(--color-text-primary)" }}
              >
                {totalSeats}
              </span>
              <span
                className="text-xs mt-0.5"
                style={{ color: "var(--color-text-secondary)" }}
              >
                議席（合計）
              </span>
            </div>
          </div>

          {/* 凡例 */}
          <div className="flex flex-wrap justify-center gap-x-4 gap-y-1.5 mt-4 max-w-sm">
            {parties
              .filter(
                (p) =>
                  p.total_seats > 0,
              )
              .map((party) => (
                <div key={party.id} className="flex items-center gap-1.5">
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: party.color_hex ?? "#999999" }}
                  />
                  <span
                    className="text-xs"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    {party.short_name}
                  </span>
                </div>
              ))}
          </div>
        </section>
      )}

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
