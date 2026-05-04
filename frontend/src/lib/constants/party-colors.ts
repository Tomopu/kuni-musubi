// 政党 ID → テーマカラー の対応表
export const PARTY_COLORS: Record<string, string> = {
  ldp: "#E60012", // 自民
  cdp: "#1A3382", // 立憲
  ishin: "#98C93C", // 維新
  dpfp: "#F3C600", // 国民
  komeito: "#0D3370", // 公明
  jcp: "#DF1B22", // 共産
  reiwa: "#E4007F", // れいわ
  sdp: "#00A1E9", // 社民
  sansei: "#EB6100", // 参政
  conservative: "#0073CE", // 保守
  mirai: "#84D6CD", // チームみらい
  reduce_tax: "#3A4075", // 減税
  none: "#999999", // 特になし
};

// 政党カラーを安全に取得する（フォールバック: #999999）
export function getPartyColor(partyId: string): string {
  return PARTY_COLORS[partyId] ?? "#999999";
}
