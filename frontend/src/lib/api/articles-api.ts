import { API_BASE_URL } from "@/lib/constants";

export type ArticleCardThumbnail = {
  type: "none" | "text" | "manual_image" | "category_default";
  text: string | null;
  url: string | null;
};

export type ArticleCardParty = {
  id: string;
  name: string;
  short_name: string;
};

export type ArticleCard = {
  id: string;
  display_title: string;
  card_summary: string;
  thumbnail: ArticleCardThumbnail;
  parties: ArticleCardParty[];
  categories: string[];
  published_at: string;
};

export type ArticlesResponse = {
  items: ArticleCard[];
  next_cursor: string | null;
};

export type ArticlesQuery = {
  party_id?: string;
  category_ids?: string[];
  sort?: "latest" | "important";
  limit?: number;
  cursor?: string;
};

export async function fetchArticles(
  query: ArticlesQuery = {}
): Promise<ArticlesResponse> {
  const params = new URLSearchParams();
  if (query.party_id) params.set("party_id", query.party_id);
  if (query.category_ids?.length)
    params.set("category_ids", query.category_ids.join(","));
  if (query.sort) params.set("sort", query.sort);
  if (query.limit) params.set("limit", String(query.limit));
  if (query.cursor) params.set("cursor", query.cursor);

  const res = await fetch(`${API_BASE_URL}/articles?${params}`);
  if (!res.ok) throw new Error(`GET /articles failed: ${res.status}`);
  return res.json();
}

export async function fetchArticleDetail(articleId: string): Promise<unknown> {
  const res = await fetch(`${API_BASE_URL}/articles/${articleId}`);
  if (!res.ok)
    throw new Error(`GET /articles/${articleId} failed: ${res.status}`);
  return res.json();
}
