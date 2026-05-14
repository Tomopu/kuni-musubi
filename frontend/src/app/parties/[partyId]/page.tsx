import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  BarChart2,
  Building,
  Building2,
  CalendarDays,
  ChevronRight,
  ExternalLink,
  Landmark,
  UserRound,
} from "lucide-react";
import { MascotImage } from "@/components/ui/mascot-image";
import { PageContainer } from "@/components/layout/page-container";
import { ArticleCard } from "@/features/articles/components/article-card";
import { getPartyDetail } from "@/lib/api/parties-api";

type Props = {
  params: Promise<{ partyId: string }>;
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

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { partyId } = await params;
  try {
    const party = await getPartyDetail(partyId);
    return { title: `${party.name} | Kuni-Musubi` };
  } catch {
    return { title: "政党詳細 | Kuni-Musubi" };
  }
}

function normalizeTextList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.flatMap((item) => normalizeTextList(item));
  }
  if (typeof value !== "string") {
    return [];
  }
  const text = value.trim();
  if (!text) {
    return [];
  }
  if (text.startsWith("{") && text.endsWith("}")) {
    return text
      .slice(1, -1)
      .split(",")
      .map((item) => item.replace(/^"|"$/g, "").trim())
      .filter(Boolean);
  }
  if (text.includes("\n")) {
    return text
      .split(/\r?\n/)
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return [text];
}

// "YYYY-MM-DD" を "YYYY年M月D日" 形式に変換する
function formatDateJp(dateStr: string): string {
  const [year, month, day] = dateStr.split("-").map(Number);
  return `${year}年${month}月${day}日`;
}

export default async function PartyDetailPage({ params }: Props) {
  const { partyId } = await params;
  const party = await getPartyDetail(partyId).catch(() => notFound());

  // 1. 表示データを準備する
  const normalizedPolicyPillars = normalizeTextList(party.policy_pillars);
  const normalizedMainPolicyTags = normalizeTextList(party.main_policy_tags);
  const policyPillars = normalizedPolicyPillars.length
    ? normalizedPolicyPillars
    : normalizeTextList(party.manifesto_promises);
  const mainPolicyTags = normalizedMainPolicyTags.length
    ? normalizedMainPolicyTags
    : normalizeTextList(party.main_policy_categories);
  const latestArticles = party.latest_articles ?? [];
  const partyColor = party.color_hex ?? "var(--color-brand-primary)";

  // 2. 議席数の表示値を算出する（どちらかが null の場合は "—"）
  const hor = party.house_of_representatives_seats;
  const hoc = party.house_of_councillors_seats;
  const totalSeatsDisplay =
    hor === null || hoc === null ? "—" : `${hor + hoc}`;
  const horDisplay = hor === null ? "—" : `${hor}`;
  const hocDisplay = hoc === null ? "—" : `${hoc}`;

  // 3. 政策出典リンクテキストを決定する
  const policySourceLinkText =
    party.policy_source_label ?? party.policy_source_type ?? "出典を見る";

  return (
    <PageContainer
      className="party-detail-page"
      style={{ "--party-color": partyColor } as CSSProperties}
    >
      {/* 1. 戻るリンク */}
      <Link href="/parties" className="back-link">
        <ArrowLeft size={20} />
        政党一覧へ
      </Link>

      {/* 2. ヒーローカード */}
      <section className="party-hero-card">
        <div className="party-hero-card__left">
          <div className="party-hero-card__title">
            <span className="party-hero-card__badge">{party.short_name}</span>
            <div className="party-hero-card__names">
              <h1>{party.name}</h1>
            </div>
          </div>
          {party.ideology_summary && (
            <p className="party-hero-card__desc">{party.ideology_summary}</p>
          )}
          <div className="party-hero-card__actions">
            {party.official_url && (
              <a
                href={party.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="party-hero-btn-primary"
              >
                公式サイトへ
                <ExternalLink size={14} />
              </a>
            )}
          </div>
        </div>
        <div className="party-hero-card__right">
          <Landmark
            size={88}
            strokeWidth={1.2}
            className="party-hero-card__landmark"
          />
          <MascotImage pose="important" size={80} />
        </div>
      </section>

      {/* 3. 基本情報カード */}
      <section className="party-metrics">
        <div className="party-metric-card">
          <div className="party-metric-card__icon">
            <UserRound size={20} />
          </div>
          <div className="party-metric-card__body">
            <span className="party-metric-card__label">代表（党首）</span>
            <strong className="party-metric-card__value">
              {party.leader_name ?? "未確認"}
            </strong>
          </div>
        </div>
        <div className="party-metric-card">
          <div className="party-metric-card__icon">
            <CalendarDays size={20} />
          </div>
          <div className="party-metric-card__body">
            <span className="party-metric-card__label">党成立年</span>
            <strong className="party-metric-card__value">
              {party.founded_year ? `${party.founded_year}年` : "未確認"}
            </strong>
          </div>
        </div>
        <div className="party-metric-card">
          <div className="party-metric-card__icon">
            <BarChart2 size={20} />
          </div>
          <div className="party-metric-card__body">
            <span className="party-metric-card__label">衆参会派議席数</span>
            <strong className="party-metric-card__value">
              {totalSeatsDisplay}
              {totalSeatsDisplay !== "—" && (
                <span className="party-metric-card__unit">議席</span>
              )}
            </strong>
          </div>
        </div>
        <div className="party-metric-card">
          <div className="party-metric-card__icon">
            <Building2 size={20} />
          </div>
          <div className="party-metric-card__body">
            <span className="party-metric-card__label">衆議院会派議席数</span>
            <strong className="party-metric-card__value">
              {horDisplay}
              {horDisplay !== "—" && (
                <span className="party-metric-card__unit">議席</span>
              )}
            </strong>
          </div>
        </div>
        <div className="party-metric-card">
          <div className="party-metric-card__icon">
            <Building size={20} />
          </div>
          <div className="party-metric-card__body">
            <span className="party-metric-card__label">参議院会派議席数</span>
            <strong className="party-metric-card__value">
              {hocDisplay}
              {hocDisplay !== "—" && (
                <span className="party-metric-card__unit">議席</span>
              )}
            </strong>
          </div>
        </div>
      </section>

      {/* 4. 政策の柱 */}
      {(policyPillars.length > 0 || party.manifesto_summary) && (
        <section className="detail-card detail-card--manifesto">
          <h2>政策の柱</h2>
          {policyPillars.length > 0 ? (
            <ol className="manifesto-list">
              {policyPillars.map((promise) => (
                <li key={promise}>
                  <span>{promise}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p>{party.manifesto_summary}</p>
          )}
          {/* 政策情報の出典 */}
          {(party.policy_source_url || party.policy_last_checked || party.policy_note) && (
            <div className="policy-source-footer">
              {party.policy_source_url && (
                <a
                  href={party.policy_source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  出典：{policySourceLinkText}
                  <ExternalLink size={14} />
                </a>
              )}
              {party.policy_last_checked && (
                <span>最終確認日：{formatDateJp(party.policy_last_checked)}</span>
              )}
              {party.policy_note && <p>{party.policy_note}</p>}
            </div>
          )}
        </section>
      )}

      {/* 5. 主な政策テーマ */}
      {mainPolicyTags.length > 0 && (
        <section className="detail-card">
          <h2>主な政策テーマ</h2>
          <div className="policy-tags">
            {mainPolicyTags.map((category) => (
              <span key={category}>{category}</span>
            ))}
          </div>
        </section>
      )}

      {/* 6. 関連ニュース */}
      {latestArticles.length > 0 && (
        <section className="related-news">
          <div className="related-news__head">
            <h2>関連ニュース</h2>
            <Link href={`/?party=${party.id}`}>
              もっと見る
              <ChevronRight size={16} />
            </Link>
          </div>
          <div className="article-grid article-grid--related">
            {latestArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </section>
      )}

      {/* 7. 議席数の出典・注記 */}
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
          ※{SEAT_COUNT_METADATA.note}
        </p>
      </div>
    </PageContainer>
  );
}
