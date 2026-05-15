import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { HomeView } from "@/features/articles/components/home-view";
import { listArticles } from "@/lib/api/articles-api";
import { listCategories } from "@/lib/api/categories-api";
import { listParties } from "@/lib/api/parties-api";

type Props = {
  searchParams?: Promise<{
    category?: string | string[];
    party?: string | string[];
  }>;
};

export const metadata: Metadata = {
  title: "ホーム | Kuni-Musubi",
};

// ホーム画面（Server Component）
// 記事一覧の取得・フィルタリングは HomeView（Client Component）に委譲する
export default async function HomePage({ searchParams }: Props) {
  const params = await searchParams;
  const party = params?.party;
  const category = params?.category;
  const initialPartyId = Array.isArray(party) ? party[0] : party;
  const initialCategoryId = Array.isArray(category) ? category[0] : category;
  const [parties, categories, articleList] = await Promise.all([
    listParties().catch(() => []),
    listCategories().catch(() => []),
    listArticles({
      ...(initialPartyId ? { party_id: initialPartyId } : {}),
      ...(initialCategoryId ? { category_ids: initialCategoryId } : {}),
      sort: "latest",
      limit: "12",
    }).catch(() => ({ items: [], next_cursor: null })),
  ]);

  return (
    <PageContainer className="py-6">
      <HomeView
        initialArticles={articleList.items}
        initialCategories={categories}
        initialCategoryId={initialCategoryId}
        initialNextCursor={articleList.next_cursor}
        initialParties={parties}
        initialPartyId={initialPartyId}
      />
    </PageContainer>
  );
}
