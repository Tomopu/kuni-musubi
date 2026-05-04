// オンボーディング・設定画面で使用する政党の定数
// バックエンドが未接続の場合にフォールバックとして使用する
export type PartyOption = {
  id: string;
  name: string;
  shortName: string;
};

export const PARTY_OPTIONS: PartyOption[] = [
  { id: "none", name: "特になし", shortName: "なし" },
  { id: "unknown", name: "わからない", shortName: "?" },
  { id: "ldp", name: "自由民主党", shortName: "自民" },
  { id: "cdp", name: "立憲民主党", shortName: "立憲" },
  { id: "ishin", name: "日本維新の会", shortName: "維新" },
  { id: "dpfp", name: "国民民主党", shortName: "国民" },
  { id: "komeito", name: "公明党", shortName: "公明" },
  { id: "jcp", name: "日本共産党", shortName: "共産" },
  { id: "reiwa", name: "れいわ新選組", shortName: "れいわ" },
  { id: "sansei", name: "参政党", shortName: "参政" },
  { id: "sdp", name: "社会民主党", shortName: "社民" },
  { id: "conservative", name: "日本保守党", shortName: "保守" },
  { id: "mirai", name: "チームみらい", shortName: "チみ" },
  { id: "other", name: "その他", shortName: "他" },
];

// 年代の選択肢
export type AgeGroupOption = {
  value: string;
  label: string;
};

export const AGE_GROUP_OPTIONS: AgeGroupOption[] = [
  { value: "10s", label: "10代" },
  { value: "20s", label: "20代" },
  { value: "30s", label: "30代" },
  { value: "40s", label: "40代" },
  { value: "50s", label: "50代" },
  { value: "60s", label: "60代以上" },
  { value: "no_answer", label: "回答しない" },
];

// 関心テーマの選択肢（MVP: 静的定数で管理）
export type CategoryOption = {
  id: string;
  name: string;
};

export const CATEGORY_OPTIONS: CategoryOption[] = [
  { id: "tax", name: "税金" },
  { id: "social_security", name: "社会保障" },
  { id: "wage_labor", name: "賃上げ・労働" },
  { id: "inflation", name: "物価高" },
  { id: "childcare", name: "子育て" },
  { id: "education", name: "教育" },
  { id: "defense", name: "国防" },
  { id: "diplomacy", name: "外交" },
  { id: "immigration", name: "移民・外国人政策" },
  { id: "energy", name: "エネルギー" },
  { id: "regional", name: "地方創生" },
  { id: "constitution", name: "憲法" },
  { id: "monetary", name: "金融政策" },
  { id: "environment", name: "環境" },
  { id: "disaster", name: "防災" },
];
