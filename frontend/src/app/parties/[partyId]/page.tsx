import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  Check,
  ChevronRight,
  ExternalLink,
  Landmark,
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

function splitIdeologySummary(summary: string): string[] {
  const normalized = summary
    .split(/\n|。|、(?=「)|(?<=」)/)
    .map((item) => item.replace(/^[・\s]+/, "").trim())
    .filter(Boolean);
  return normalized.length > 0 ? normalized : [summary];
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
  const policyHeadline = party.policy_headline ?? party.ideology_summary;
  const headlineItems = policyHeadline
    ? splitIdeologySummary(policyHeadline)
    : [];

  // 2. 議席数の表示値を算出する（どちらかが null の場合は "—"）
  const hor = party.house_of_representatives_seats;
  const hoc = party.house_of_councillors_seats;
  const totalSeatsDisplay =
    hor === null || hoc === null ? "—" : `${hor + hoc}議席`;
  const horDisplay = hor === null ? "—" : `${hor}議席`;
  const hocDisplay = hoc === null ? "—" : `${hoc}議席`;

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

      {/* 2. ヒーローエリア */}
      <section className="party-detail-hero">
        <div className="party-detail-hero__title">
          <span className="party-detail-hero__badge">{party.short_name}</span>
          <div>
            <h1>{party.name}</h1>
            <p>{party.short_name}</p>
          </div>
        </div>
        <div className="party-detail-hero__visual">
          <Landmark size={96} strokeWidth={1.4} />
          <MascotImage pose="important" size={76} />
        </div>
      </section>

      {/* 3. 基本情報カード */}
      <section className="party-metrics">
        <div>
          <span>代表者（党首）</span>
          <strong>{party.leader_name ?? "未確認"}</strong>
        </div>
        <div>
          <span>党成立年</span>
          <strong>{party.founded_year ? `${party.founded_year}年` : "未確認"}</strong>
        </div>
        <div>
          <span>衆参会派議席数</span>
          <strong>{totalSeatsDisplay}</strong>
        </div>
        <div>
          <span>衆議院会派議席数</span>
          <strong>{horDisplay}</strong>
        </div>
        <div>
          <span>参議院会派議席数</span>
          <strong>{hocDisplay}</strong>
        </div>
        {party.official_url && (
          <a
            href={party.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="party-official-link"
          >
            <span>公式サイト</span>
            <strong>
              公式サイトへ
              <ExternalLink size={16} />
            </strong>
          </a>
        )}
      </section>

      {/* 4. 掲げるスローガン */}
      {policyHeadline && (
        <section className="detail-card">
          <h2>掲げるスローガン</h2>
          <ul className="ideology-list">
            {headlineItems.map((item) => (
              <li key={item}>
                <Check size={17} />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* 5. 政策の柱 */}
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

      {/* 6. 主な政策テーマ */}
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

      {/* 7. 関連ニュース */}
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

      {/* 8. 議席数の出典・注記 */}
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
