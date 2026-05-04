import Link from "next/link";
import type { ArticleCardResponse } from "@/lib/api/articles-api";
import { PartyBadge } from "@/components/ui/party-badge";
import { CategoryTag } from "@/components/ui/category-tag";
import { TextThumbnail } from "@/components/ui/text-thumbnail";

type ArticleCardProps = {
  article: ArticleCardResponse;
};

// 日付を「2026年5月1日」形式にフォーマットする
function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
}

// 記事カードコンポーネント
// カード全体が記事詳細ページへのリンクになる
export function ArticleCard({ article }: ArticleCardProps) {
  // 1. サムネイル用の政党カラーを取得する（最初の政党のカラーを使用）
  const primaryParty = article.parties[0];
  const partyColor = primaryParty?.color_hex ?? "#999999";

  // 2. サムネイル用テキストを取得する（thumbnail.text > 最初のカテゴリ名）
  const thumbnailText =
    article.thumbnail.text ?? article.categories[0]?.name ?? "";

  // 3. 表示するカテゴリを最大2件に制限する
  const displayCategories = article.categories.slice(0, 2);
  const extraCategoryCount = article.categories.length - displayCategories.length;

  return (
    <Link
      href={`/articles/${article.id}`}
      className="block rounded-lg overflow-hidden border transition-colors duration-150 hover:border-current hover:shadow-md"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-bg-base)",
      }}
    >
      {/* サムネイル（テキストベース） */}
      <TextThumbnail
        partyColor={partyColor}
        categoryName={thumbnailText}
        className="w-full h-28"
      />

      {/* カード本体 */}
      <div className="p-3 flex flex-col gap-2">
        {/* 政党バッジ + カテゴリタグ */}
        <div className="flex flex-wrap items-center gap-1.5">
          {article.parties.map((party) => (
            <PartyBadge
              key={party.id}
              partyId={party.id}
              shortName={party.short_name}
              colorHex={party.color_hex}
              size="sm"
            />
          ))}
          {displayCategories.map((category) => (
            <CategoryTag key={category.id} name={category.name} />
          ))}
          {extraCategoryCount > 0 && (
            <span
              className="text-xs"
              style={{ color: "var(--color-text-secondary)" }}
            >
              他{extraCategoryCount}
            </span>
          )}
        </div>

        {/* タイトル */}
        <p
          className="text-sm font-semibold leading-snug line-clamp-3"
          style={{ color: "var(--color-text-primary)" }}
        >
          {article.display_title}
        </p>

        {/* 要約 */}
        <p
          className="text-xs leading-relaxed line-clamp-2"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {article.card_summary}
        </p>

        {/* 日付 */}
        <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
          {formatDate(article.published_at)}
        </p>
      </div>
    </Link>
  );
}
