import { apiGet } from "@/lib/api/client";
import type { ArticleCardResponse } from "@/lib/api/articles-api";

// 政党情報レスポンス
export type PartyResponse = {
  id: string;
  name: string;
  short_name: string;
  color_hex: string | null;
  house_of_representatives_seats: number | null;
  house_of_councillors_seats: number | null;
  total_seats: number;
  main_policy_categories?: string[];
};

// 政党詳細レスポンス
export type PartyDetailResponse = PartyResponse & {
  founded_year: number | null;
  leader_name: string | null;
  ideology_summary: string | null;
  manifesto_summary: string | null;
  manifesto_promises?: string[];
  main_policy_categories?: string[];
  official_url: string | null;
  latest_articles?: ArticleCardResponse[];
};

// 1. 政党一覧を取得する
export async function listParties(): Promise<PartyResponse[]> {
  return apiGet<PartyResponse[]>("/parties");
}

// 2. 政党詳細を取得する
export async function getPartyDetail(partyId: string): Promise<PartyDetailResponse> {
  return apiGet<PartyDetailResponse>(`/parties/${partyId}`);
}
