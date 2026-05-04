import { apiGet } from "@/lib/api/client";

// 記事に関連する政党情報
export type ArticlePartyInfo = {
  id: string;
  name: string;
  short_name: string;
  color_hex: string;
};

// 記事に関連するカテゴリ情報
export type ArticleCategoryInfo = {
  id: string;
  name: string;
};

// 記事サムネイル情報
export type ArticleThumbnail = {
  type: string;
  text: string | null;
  url: string | null;
};

// 記事カードレスポンス
export type ArticleCardResponse = {
  id: string;
  display_title: string;
  card_summary: string;
  thumbnail: ArticleThumbnail;
  parties: ArticlePartyInfo[];
  categories: ArticleCategoryInfo[];
  published_at: string;
};

// 記事表示コンテンツ（ポジティブポイント・生活影響・世論・課題）
export type ArticleDisplayContent = {
  positive_point: string;
  life_impact: string;
  public_reactions_summary: string | null;
  remaining_issues: string[];
};

// 出典情報
export type ArticleSource = {
  source_name: string | null;
  source_url: string;
  published_at: string | null;
  retrieved_at: string | null;
};

// 記事詳細レスポンス
export type ArticleDetailResponse = ArticleCardResponse & {
  display_content: ArticleDisplayContent | null;
  sources: ArticleSource[];
};

// 記事一覧レスポンス
export type ArticleListResponse = {
  items: ArticleCardResponse[];
  next_cursor: string | null;
};

// 記事一覧取得パラメータ
export type ListArticlesParams = {
  party_id?: string;
  category_id?: string;
  sort?: "latest" | "important";
  limit?: string;
  cursor?: string;
};

// 1. 記事一覧を取得する
export async function listArticles(
  params?: ListArticlesParams,
): Promise<ArticleListResponse> {
  const queryParams: Record<string, string> = {};
  if (params?.party_id) queryParams.party_id = params.party_id;
  if (params?.category_id) queryParams.category_id = params.category_id;
  if (params?.sort) queryParams.sort = params.sort;
  if (params?.limit) queryParams.limit = params.limit;
  if (params?.cursor) queryParams.cursor = params.cursor;

  return apiGet<ArticleListResponse>("/articles", queryParams);
}

// 2. 記事詳細を取得する
export async function getArticleDetail(
  id: string,
): Promise<ArticleDetailResponse> {
  return apiGet<ArticleDetailResponse>(`/articles/${id}`);
}
