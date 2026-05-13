import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ChevronRight, Sparkles } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { SeatOverview } from "@/features/parties/components/seat-overview";
import type { ChartSegment } from "@/features/parties/components/semi-donut-chart";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";

export const metadata: Metadata = {
  title: "政党一覧 | Kuni-Musubi",
};

const FALLBACK_POLICY_CATEGORIES_BY_NAME: Record<string, string[]> = {
  自由民主党: ["安全保障", "経済成長", "憲法改正"],
  日本維新の会: ["行財政改革", "難民等認定制度改革", "地方自治"],
  国民民主党: ["税制・財政（減税）", "社会保障軽減", "憲法改正"],
  中道改革連合: ["教育", "女性政策", "行政改革"],
  立憲民主党: ["労働・雇用", "多様性尊重", "ジェンダー平等"],
  参政党: ["教育", "食・健康", "国民負担軽減"],
  公明党: ["子育て支援", "社会保障", "平和外交"],
  チームみらい: ["テクノロジー政策", "教育", "行政DX"],
  日本共産党: ["消費税減税", "社会保障", "平和外交"],
  れいわ新選組: ["消費税廃止", "社会保障", "反緊縮"],
  日本保守党: ["保守政策", "安全保障", "移民政策"],
  社会民主党: ["福祉", "平和主義", "労働"],
  "減税日本・ゆうこく連合": ["減税", "地方自治", "行政改革"],
  無所属: ["地域政策", "個別政策", "議会活動"],
};

function toSegments(
  parties: PartyResponse[],
  seatKey: "house_of_representatives_seats" | "house_of_councillors_seats",
): ChartSegment[] {
  return parties
    .map((party) => ({
      id: party.id,
      name: party.short_name,
      color: party.color_hex ?? "#999999",
      seats: party[seatKey] ?? 0,
    }))
    .filter((party) => party.seats > 0);
}

export default async function PartiesPage() {
  let parties: PartyResponse[];
  try {
    parties = await listParties();
  } catch {
    parties = [];
  }

  const representativeSegments = toSegments(parties, "house_of_representatives_seats");
  const councillorSegments = toSegments(parties, "house_of_councillors_seats");
  const totalRepresentatives = representativeSegments.reduce((sum, party) => sum + party.seats, 0);
  const totalCouncillors = councillorSegments.reduce((sum, party) => sum + party.seats, 0);

  return (
    <PageContainer className="parties-page">
      <section className="parties-overview">
        <Image
          src="/assets/decorations/deco-wakaba.png"
          alt=""
          width={116}
          height={116}
          className="parties-overview__decor parties-overview__decor--wakaba"
          aria-hidden="true"
        />
        <Image
          src="/assets/decorations/deco-paperplane.png"
          alt=""
          width={126}
          height={100}
          className="parties-overview__decor parties-overview__decor--paperplane"
          aria-hidden="true"
        />
        <div className="parties-overview__intro">
          <h1>政党一覧</h1>
          <p>2026年5月時点の衆議院・参議院の議席分布</p>
        </div>

        {(totalRepresentatives > 0 || totalCouncillors > 0) && (
          <SeatOverview
            parties={parties}
            representativeSegments={representativeSegments}
            councillorSegments={councillorSegments}
            totalRepresentatives={totalRepresentatives}
            totalCouncillors={totalCouncillors}
          />
        )}

        <p className="parties-overview__note">
          ※ 議席数は各党の公式発表や関連資料をもとに集計した参考値です。
        </p>
      </section>

      <section className="party-list-section">
        <h2>政党を選んで、詳しい情報を見てみよう</h2>
        <div className="party-list">
          {parties.map((party) => {
            const representatives = party.house_of_representatives_seats ?? 0;
            const councillors = party.house_of_councillors_seats ?? 0;
            const categories =
              party.main_policy_categories?.length
                ? party.main_policy_categories.slice(0, 3)
                : FALLBACK_POLICY_CATEGORIES_BY_NAME[party.name] ?? [];

            return (
              <Link
                key={party.id}
                href={`/parties/${party.id}`}
                className="party-row"
                style={
                  {
                    "--party-color": party.color_hex ?? "var(--color-brand-primary)",
                  } as CSSProperties
                }
              >
                <span
                  className={`party-row__mark ${
                    party.short_name.length >= 3 ? "party-row__mark--compact" : ""
                  }`}
                >
                  {party.short_name}
                </span>
                <span className="party-row__summary">
                  <span className="party-row__name">{party.name}</span>
                </span>
                <span className="party-row__seats">
                  <b>{party.total_seats}</b>
                  <span>議席</span>
                  <em>衆{representatives} / 参{councillors}</em>
                </span>
                <span className="party-row__tags">
                  {categories.map((category) => (
                    <span key={category}>{category}</span>
                  ))}
                </span>
                <ChevronRight className="party-row__arrow" size={20} />
              </Link>
            );
          })}
        </div>
      </section>

      <div className="party-guide-banner">
        <span className="party-guide-banner__icon" aria-hidden="true">
          <Sparkles size={18} />
        </span>
        <span className="party-guide-banner__text">
          政党ごとの理念や政策をもっと詳しく見てみましょう！
        </span>
        <Image
          src="/assets/mascot/mascot-search.png"
          alt=""
          width={118}
          height={118}
          className="party-guide-banner__mascot"
          aria-hidden="true"
        />
      </div>

      {parties.length === 0 && (
        <p className="empty-state">政党情報を読み込めませんでした</p>
      )}
    </PageContainer>
  );
}
