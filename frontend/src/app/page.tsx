import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { HomeView } from "@/features/articles/components/home-view";

export const metadata: Metadata = {
  title: "ホーム | Kuni-Musubi",
};

// ホーム画面（Server Component）
// 記事一覧の取得・フィルタリングは HomeView（Client Component）に委譲する
export default function HomePage() {
  return (
    <PageContainer className="py-6">
      <HomeView />
    </PageContainer>
  );
}
