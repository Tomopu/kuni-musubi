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
  自由民主党: [
    "経済成長",
    "地方創生",
    "外交・安全保障",
    "社会保障",
    "子育て支援",
    "憲法改正",
    "防災・国土強靭化",
  ],
  日本維新の会: [
    "社会保険料改革",
    "統治機構改革",
    "副首都構想",
    "教育無償化",
    "保育支援",
    "経済成長",
    "外交・安全保障",
    "憲法改正",
  ],
  国民民主党: [
    "手取り増",
    "減税",
    "社会保険料軽減",
    "経済成長",
    "教育投資",
    "科学技術",
    "安全保障",
    "政治改革",
  ],
  中道改革連合: [
    "生活者重視",
    "経済成長",
    "社会保障改革",
    "現役世代支援",
    "包摂社会",
    "外交・防衛",
    "憲法論議",
    "政治改革",
    "選挙制度改革",
  ],
  立憲民主党: [
    "立憲主義",
    "人権尊重",
    "多様性",
    "共生社会",
    "分配重視の経済",
    "社会保障",
    "危機管理",
    "平和外交",
    "ジェンダー平等",
  ],
  参政党: [
    "教育改革",
    "人づくり",
    "食と健康",
    "医療",
    "環境保全",
    "循環型社会",
    "国のまもり",
    "外国資本規制",
    "移民政策",
  ],
  公明党: [
    "平和外交",
    "教育無償化",
    "子育て支援",
    "高等教育支援",
    "医療費負担軽減",
    "社会保険料軽減",
    "選択的夫婦別姓",
    "外国人との共生",
  ],
  チームみらい: [
    "テクノロジー",
    "政治改革",
    "デジタル民主主義",
    "AI活用",
    "未来志向",
    "社会変化への対応",
    "行政DX",
  ],
  日本共産党: [
    "暮らし重視",
    "物価高対策",
    "賃金・労働",
    "平和外交",
    "人権",
    "政治とカネ",
    "企業・団体献金禁止",
    "学費負担軽減",
    "ジェンダー平等",
  ],
  れいわ新選組: [
    "消費税廃止",
    "最低賃金1500円",
    "奨学金返済負担軽減",
    "公務員増員",
    "一次産業支援",
    "法制度見直し",
    "辺野古新基地反対",
    "脱原発",
  ],
  日本保守党: [
    "食料品消費税ゼロ",
    "減税",
    "再エネ賦課金廃止",
    "移民政策の是正",
    "憲法改正",
    "安全保障",
    "伝統文化",
    "価値観外交",
    "教育制度見直し",
  ],
  社会民主党: [
    "公正な市場経済",
    "労働環境",
    "税財政",
    "社会保障",
    "地方自治",
    "平和主義",
    "ジェンダー平等",
    "環境保護",
    "農林水産業",
    "教育",
  ],
  "減税日本・ゆうこく連合": [
    "消費税廃止",
    "人への投資",
    "社会保障",
    "地域主権",
    "政治改革",
    "行政透明化",
    "立憲主義",
    "専守防衛",
    "核兵器廃絶",
    "恒久平和",
  ],
  無所属: [],
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
