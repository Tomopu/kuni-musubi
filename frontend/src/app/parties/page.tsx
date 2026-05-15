import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ChevronRight, ExternalLink, Sparkles } from "lucide-react";
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

// 議席数の出典・注記メタデータ
const SEAT_COUNT_METADATA = {
  note: "議席数は、衆議院・参議院が公表する会派別所属議員数をもとにしています。政党所属議員数や選挙時の獲得議席数とは一致しない場合があります。",
  sources: [
    {
      name: "衆議院ホームページ「会派名及び会派別所属議員数」",
      url: "https://www.shugiin.go.jp/",
    },
    {
      name: "参議院ホームページ「会派別所属議員数一覧」",
      url: "https://www.sangiin.go.jp/",
    },
  ],
  lastChecked: "2026-05-13",
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

// "YYYY-MM-DD" を "YYYY年M月D日" 形式に変換する
function formatDateJp(dateStr: string): string {
  const [year, month, day] = dateStr.split("-").map(Number);
  return `${year}年${month}月${day}日`;
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
          <h1>
            <Image
              src="/assets/decorations/deco-wakaba.png"
              alt=""
              width={34}
              height={34}
              className="parties-overview__title-icon"
              aria-hidden="true"
            />
            政党ごとの会派議席数
          </h1>
          <p>2026年5月時点の衆議院・参議院の会派議席数分布</p>
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
          ※ {SEAT_COUNT_METADATA.note}
        </p>
      </section>

      <section className="party-list-section">
        <h2>政党一覧</h2>

        <div className="party-guide-banner">
          <span className="party-guide-banner__icon" aria-hidden="true">
            <Sparkles size={18} />
          </span>
          <span className="party-guide-banner__text">
            政党を選んで、詳しい情報を見てみよう！
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

        <div className="party-list">
          {parties.map((party) => {
            const representatives = party.house_of_representatives_seats ?? 0;
            const councillors = party.house_of_councillors_seats ?? 0;
            const categories =
              party.main_policy_tags?.length
                ? party.main_policy_tags.slice(0, 3)
                : party.main_policy_categories?.length
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

      {parties.length === 0 && (
        <p className="empty-state">政党情報を読み込めませんでした</p>
      )}

      <div className="seat-count-footnote">
        <div className="seat-count-footnote__sources">
          <p>出典：</p>
          {SEAT_COUNT_METADATA.sources.map((source) => (
            <a
              key={source.url}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {source.name}
              <ExternalLink size={12} />
            </a>
          ))}
        </div>
        <p className="seat-count-footnote__date">
          最終確認日：{formatDateJp(SEAT_COUNT_METADATA.lastChecked)}
        </p>
        <p className="seat-count-footnote__note">
          ※ {SEAT_COUNT_METADATA.note}
        </p>
      </div>
    </PageContainer>
  );
}
