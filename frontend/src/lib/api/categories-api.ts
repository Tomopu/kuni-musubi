import { apiGet } from "@/lib/api/client";

// ポリシーカテゴリレスポンス
export type PolicyCategoryResponse = {
  id: string;
  name: string;
  display_order: number;
};

// 1. カテゴリ一覧を取得する
export async function listCategories(): Promise<PolicyCategoryResponse[]> {
  return apiGet<PolicyCategoryResponse[]>("/policy-categories");
}
