import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getPartyDetail } from "@/lib/api/parties-api";
import { PageContainer } from "@/components/layout/page-container";
import { ArticleCard } from "@/features/articles/components/article-card";

type Props = {
  params: Promise<{ partyId: string }>;
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

// 政党詳細画面（Server Component）
export default async function PartyDetailPage({ params }: Props) {
  const { partyId } = await params;
  const party = await getPartyDetail(partyId).catch(() => notFound());

  const totalSeats = party.total_seats;
  const manifestoPromises = party.manifesto_promises ?? [];
  const mainPolicyCategories = party.main_policy_categories ?? [];
  const latestArticles = party.latest_articles ?? [];

  // 3 列議席カードのデータ
  const seatInfo = [
    { label: "議員数", value: totalSeats },
    { label: "衆議院議席数", value: party.house_of_representatives_seats ?? 0 },
    { label: "参議院議席数", value: party.house_of_councillors_seats ?? 0 },
  ];

  // 基本情報のデータ
  const partyMeta = [
    { label: "政党名", value: party.name },
    { label: "代表者", value: party.leader_name },
    { label: "成立年", value: party.founded_year ? `${party.founded_year}年` : null },
  ].filter((item) => item.value != null);

  return (
    <PageContainer className="py-6">
      {/* 戻るリンク */}
      <Link
        href="/parties"
        className="inline-flex items-center gap-1 text-sm mb-4 transition-opacity duration-150 hover:opacity-70"
        style={{ color: "var(--color-text-secondary)" }}
      >
        &lt; 政党一覧へ
      </Link>

      {/* 政党ヘッダー */}
      <div
        className="flex items-center gap-3 mb-5"
        style={{ borderLeft: `4px solid ${party.color_hex ?? "var(--color-brand-primary)"}`, paddingLeft: "0.75rem" }}
      >
        <div>
          <h1
            className="text-2xl font-bold leading-snug"
            style={{ color: "var(--color-text-primary)" }}
          >
            {party.name}
          </h1>
          <p
            className="text-sm mt-0.5"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {party.short_name}
          </p>
        </div>
      </div>

      {/* 議席カード（3列） */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3 mb-4">
        {seatInfo.map(({ label, value }) => (
          <div
            key={label}
            className="rounded-lg p-3 text-center"
            style={{ backgroundColor: "var(--color-bg-surface)" }}
          >
            <p
              className="text-xs mb-1"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {label}
            </p>
            <p
              className="text-2xl font-bold leading-none"
              style={{
                color:
                  label === "議員数"
                    ? (party.color_hex ?? "var(--color-brand-primary)")
                    : "var(--color-text-primary)",
              }}
            >
              {value}
            </p>
            <p
              className="text-xs mt-0.5"
              style={{ color: "var(--color-text-secondary)" }}
            >
              議席
            </p>
          </div>
        ))}
      </div>

      {/* 基本情報 */}
      {partyMeta.length > 0 && (
        <div
          className="grid gap-3 mb-6 sm:grid-cols-3"
        >
          {partyMeta.map(({ label, value }) => (
            <div
              key={label}
              className="rounded-lg p-3"
              style={{ backgroundColor: "var(--color-bg-surface)" }}
            >
              <p
                className="text-xs mb-0.5"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {label}
              </p>
              <p
                className="text-sm font-medium"
                style={{ color: "var(--color-text-primary)" }}
              >
                {value}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* 政治理念 */}
      {party.ideology_summary && (
        <section className="mb-6">
          <h2
            className="text-base font-semibold mb-2"
            style={{ color: "var(--color-text-primary)" }}
          >
            党の政治理念
          </h2>
          <p
            className="text-sm leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {party.ideology_summary}
          </p>
        </section>
      )}

      {/* 主要公約 */}
      {(manifestoPromises.length > 0 || party.manifesto_summary) && (
        <section className="mb-6">
          <h2
            className="text-base font-semibold mb-2"
            style={{ color: "var(--color-text-primary)" }}
          >
            主要政策・公約
          </h2>
          {manifestoPromises.length > 0 ? (
            <ul className="space-y-2">
              {manifestoPromises.map((promise) => (
                <li
                  key={promise}
                  className="text-sm leading-relaxed pl-3 border-l-2"
                  style={{
                    borderColor: party.color_hex ?? "var(--color-border)",
                    color: "var(--color-text-secondary)",
                  }}
                >
                  {promise}
                </li>
              ))}
            </ul>
          ) : (
            <p
              className="text-sm leading-relaxed whitespace-pre-line"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {party.manifesto_summary}
            </p>
          )}
        </section>
      )}

      {/* 主な政策カテゴリ */}
      {mainPolicyCategories.length > 0 && (
        <section className="mb-6">
          <h2
            className="text-base font-semibold mb-2"
            style={{ color: "var(--color-text-primary)" }}
          >
            主な政策カテゴリ
          </h2>
          <div className="flex flex-wrap gap-2">
            {mainPolicyCategories.map((category) => (
              <span
                key={category}
                className="rounded-full px-3 py-1 text-xs"
                style={{
                  backgroundColor: "var(--color-bg-surface)",
                  color: "var(--color-text-secondary)",
                }}
              >
                {category}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* 公式サイトリンク */}
      {party.official_url && (
        <div className="mb-6">
          <p
            className="text-xs mb-1"
            style={{ color: "var(--color-text-secondary)" }}
          >
            公式サイトURL
          </p>
          <a
            href={party.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm underline transition-opacity duration-150 hover:opacity-70"
            style={{ color: "var(--color-brand-primary)" }}
          >
            公式サイトを見る &gt;
          </a>
        </div>
      )}

      {/* 最新ニュース（横スクロール） */}
      {latestArticles.length > 0 && (
        <section
          className="pt-6 border-t"
          style={{ borderColor: "var(--color-border)" }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2
              className="text-base font-semibold"
              style={{ color: "var(--color-text-primary)" }}
            >
              最新ニュース
            </h2>
            <Link
              href={`/?party=${party.id}`}
              className="text-sm transition-opacity duration-150 hover:opacity-70"
              style={{ color: "var(--color-brand-primary)" }}
            >
              もっと見る &gt;
            </Link>
          </div>

          {/* 横スクロールカード */}
          <div
            className="flex gap-3 overflow-x-auto -mx-4 px-4 pb-2"
            style={{ scrollbarWidth: "none" }}
          >
            {latestArticles.map((article) => (
              <div key={article.id} className="flex-shrink-0 w-60">
                <ArticleCard article={article} />
              </div>
            ))}
          </div>
        </section>
      )}
    </PageContainer>
  );
}
