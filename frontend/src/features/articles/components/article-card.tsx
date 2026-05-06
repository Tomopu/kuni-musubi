import Link from "next/link";
import { CategoryTag } from "@/components/ui/category-tag";
import { PartyBadge } from "@/components/ui/party-badge";
import { TextThumbnail } from "@/components/ui/text-thumbnail";
import type { ArticleCardResponse } from "@/lib/api/articles-api";

type ArticleCardProps = {
  article: ArticleCardResponse;
};

function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, "0")}/${String(date.getDate()).padStart(2, "0")}`;
}

export function ArticleCard({ article }: ArticleCardProps) {
  const primaryParty = article.parties[0];
  const partyColor = primaryParty?.color_hex ?? "#999999";
  const thumbnailText =
    article.thumbnail.text ?? article.categories[0]?.name ?? "";
  const displayCategories = article.categories.slice(0, 2);
  const extraCategoryCount = article.categories.length - displayCategories.length;

  return (
    <Link href={`/articles/${article.id}`} className="article-card">
      <TextThumbnail
        partyColor={partyColor}
        categoryName={thumbnailText}
        className="article-card__thumb"
      />

      <div className="article-card__body">
        <div className="article-card__tags">
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
            <span className="article-card__extra">他{extraCategoryCount}</span>
          )}
        </div>

        <p className="article-card__title">{article.display_title}</p>
        <p className="article-card__summary">{article.card_summary}</p>

        <div className="article-card__meta">
          <span>{formatDate(article.published_at)}</span>
        </div>
      </div>
    </Link>
  );
}
