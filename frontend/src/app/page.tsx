import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { HomeView } from "@/features/articles/components/home-view";

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

  return (
    <PageContainer className="py-6">
      <HomeView
        initialCategoryId={initialCategoryId}
        initialPartyId={initialPartyId}
      />
    </PageContainer>
  );
}
