import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  Calendar,
  Heart,
  Link as LinkIcon,
  Star,
  TriangleAlert,
  UsersRound,
} from "lucide-react";
import { getArticleDetail } from "@/lib/api/articles-api";
import { PageContainer } from "@/components/layout/page-container";
import { PartyBadge } from "@/components/ui/party-badge";
import { CategoryTag } from "@/components/ui/category-tag";
import { TextThumbnail } from "@/components/ui/text-thumbnail";
import { ArticleShareActions } from "@/features/articles/components/article-share-actions";
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

type SectionHeadingTone = "good" | "life" | "issue" | "reaction" | "source";

function SectionHeading({
  children,
  icon,
  tone,
}: {
  children: ReactNode;
  icon: ReactNode;
  tone: SectionHeadingTone;
}) {
  return (
    <div className={`article-section-heading article-section-heading--${tone}`}>
      <span className="article-section-heading__icon" aria-hidden="true">
        {icon}
      </span>
      <h2>{children}</h2>
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
    <PageContainer className="article-detail-page py-6">
      {/* 戻るリンク */}
      <Link
        href="/"
        className="article-detail-back-link"
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
      <p className="article-detail-date">
        <Calendar size={16} />
        {formatDate(article.published_at)}
      </p>

      {/* サムネイル */}
      <TextThumbnail
        partyColor={partyColor}
        categoryName={thumbnailText}
        className="w-full h-40 mb-5"
      />

      {/* タイトル */}
      <h1 className="article-detail-title">
        {article.display_title}
      </h1>

      {article.display_content && (
        <div className="article-detail-content">
          {/* 何が良いニュースなのか */}
          <section>
            <SectionHeading icon={<Star size={19} />} tone="good">
              何が Good News なのか？
            </SectionHeading>
            <p>
              {article.display_content.positive_point}
            </p>
          </section>

          {/* 生活への影響 */}
          <section>
            <SectionHeading icon={<Heart size={19} />} tone="life">
              我々の生活への影響
            </SectionHeading>
            <p>
              {article.display_content.life_impact}
            </p>
          </section>

          {/* 残る課題（番号付きリスト） */}
          {article.display_content.remaining_issues.length > 0 && (
            <section>
              <SectionHeading icon={<TriangleAlert size={19} />} tone="issue">
                残る課題
              </SectionHeading>
              <ol className="article-issue-list">
                {article.display_content.remaining_issues.map((issue, i) => (
                  <li key={i}>
                    <span>
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
              <SectionHeading icon={<UsersRound size={19} />} tone="reaction">
                世論・与野党からの評価
              </SectionHeading>
              <p>
                {article.display_content.public_reactions_summary}
              </p>
            </section>
          )}
        </div>
      )}

      {/* 出典・一次情報リンク */}
      {article.sources.length > 0 && (
        <section
          className="article-source-section"
          style={{ borderColor: "var(--color-border)" }}
        >
          <SectionHeading icon={<LinkIcon size={19} />} tone="source">
            出典・一次情報
          </SectionHeading>
          <ul>
            {article.sources.map((source, i) => (
              <li key={i}>
                <a
                  href={source.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {source.source_name ?? source.source_url}
                </a>
                {source.published_at && (
                  <span>
                    {formatDate(source.published_at)}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      <ArticleShareActions title={article.display_title} />

      {/* 参考になったフィードバック */}
      <section className="article-feedback-section">
        <HelpfulButton articleId={article.id} />
      </section>
    </PageContainer>
  );
}
