import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getArticleDetail } from "@/lib/api/articles-api";
import { PageContainer } from "@/components/layout/page-container";
import { PartyBadge } from "@/components/ui/party-badge";
import { CategoryTag } from "@/components/ui/category-tag";
import { TextThumbnail } from "@/components/ui/text-thumbnail";
import { HelpfulButton } from "@/features/articles/components/helpful-button";

type Props = {
  params: Promise<{ articleId: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { articleId } = await params;
  try {
    const article = await getArticleDetail(articleId);
    return { title: `${article.display_title} | Kuni-Musubi` };
  } catch {
    return { title: "記事詳細 | Kuni-Musubi" };
  }
}

function formatDate(isoString: string): string {
  const d = new Date(isoString);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}/${m}/${day}`;
}

// セクション見出し: 左側に緑丸 + テキスト
function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-start gap-2 mb-2">
      <span
        className="flex-shrink-0 w-3.5 h-3.5 rounded-full mt-0.5"
        style={{ backgroundColor: "var(--color-brand-primary)" }}
        aria-hidden="true"
      />
      <h2
        className="text-base font-medium leading-snug"
        style={{ color: "var(--color-text-primary)" }}
      >
        {children}
      </h2>
    </div>
  );
}

// 記事詳細画面（Server Component）
export default async function ArticleDetailPage({ params }: Props) {
  const { articleId } = await params;
  const article = await getArticleDetail(articleId).catch(() => notFound());

  const primaryParty = article.parties[0];
  const partyColor = primaryParty?.color_hex ?? "#999999";
  const thumbnailText = article.thumbnail.text ?? article.categories[0]?.name ?? "";

  return (
    <PageContainer className="py-6">
      {/* 戻るリンク */}
      <Link
        href="/"
        className="inline-flex items-center gap-1 text-sm mb-4 transition-opacity duration-150 hover:opacity-70"
        style={{ color: "var(--color-text-secondary)" }}
      >
        &lt; 記事一覧へ
      </Link>

      {/* タグ（政党 + カテゴリ） */}
      <div className="flex flex-wrap gap-2 mb-1.5">
        {article.parties.map((party) => (
          <PartyBadge
            key={party.id}
            partyId={party.id}
            shortName={party.short_name}
            colorHex={party.color_hex}
            size="sm"
          />
        ))}
        {article.categories.map((category) => (
          <CategoryTag key={category.id} name={category.name} />
        ))}
      </div>

      {/* 公開日 */}
      <p className="text-xs mb-4" style={{ color: "var(--color-text-secondary)" }}>
        {formatDate(article.published_at)}
      </p>

      {/* サムネイル */}
      <TextThumbnail
        partyColor={partyColor}
        categoryName={thumbnailText}
        className="w-full h-40 mb-5"
      />

      {/* タイトル */}
      <h1
        className="text-xl font-medium leading-snug mb-6"
        style={{ color: "var(--color-text-primary)" }}
      >
        {article.display_title}
      </h1>

      {article.display_content && (
        <div className="flex flex-col gap-6">
          {/* 何が良いニュースなのか */}
          <section>
            <SectionHeading>何が良いニュースなのか</SectionHeading>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {article.display_content.positive_point}
            </p>
          </section>

          {/* 生活への影響 */}
          <section>
            <SectionHeading>生活への影響</SectionHeading>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {article.display_content.life_impact}
            </p>
          </section>

          {/* 残る課題（番号付きリスト） */}
          {article.display_content.remaining_issues.length > 0 && (
            <section>
              <SectionHeading>残る課題</SectionHeading>
              <ol className="flex flex-col gap-1.5">
                {article.display_content.remaining_issues.map((issue, i) => (
                  <li
                    key={i}
                    className="flex gap-2 text-sm leading-relaxed"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    <span
                      className="flex-shrink-0 font-medium w-4"
                      style={{ color: "var(--color-brand-primary)" }}
                    >
                      {i + 1}.
                    </span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {/* 世論・与野党からの評価（ドキュメント方針: 表示する） */}
          {article.display_content.public_reactions_summary && (
            <section>
              <SectionHeading>世論・与野党からの評価</SectionHeading>
              <p
                className="text-sm leading-relaxed"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {article.display_content.public_reactions_summary}
              </p>
            </section>
          )}
        </div>
      )}

      {/* 出典・一次情報リンク */}
      {article.sources.length > 0 && (
        <section
          className="mt-6 pt-6 border-t"
          style={{ borderColor: "var(--color-border)" }}
        >
          <SectionHeading>出典・一次情報</SectionHeading>
          <ul className="flex flex-col gap-2 mt-1">
            {article.sources.map((source, i) => (
              <li key={i}>
                <a
                  href={source.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm underline transition-opacity duration-150 hover:opacity-70"
                  style={{ color: "var(--color-brand-primary)" }}
                >
                  {source.source_name ?? source.source_url}
                </a>
                {source.published_at && (
                  <span
                    className="ml-2 text-xs"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    {formatDate(source.published_at)}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* 参考になったフィードバック */}
      <section
        className="mt-6 pt-6 border-t"
        style={{ borderColor: "var(--color-border)" }}
      >
        <HelpfulButton articleId={article.id} />
      </section>
    </PageContainer>
  );
}
