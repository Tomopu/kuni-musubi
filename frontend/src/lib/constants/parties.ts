// オンボーディング・設定画面で使用する政党の定数
// バックエンドが未接続の場合にフォールバックとして使用する
export type PartyOption = {
  id: string;
  name: string;
  shortName: string;
};

export const LEGACY_PARTY_ID_MAP: Record<string, string> = {
  ldp: "11111111-0000-0000-0000-000000000001",
  cdp: "11111111-0000-0000-0000-000000000002",
  ishin: "11111111-0000-0000-0000-000000000003",
  dpfp: "11111111-0000-0000-0000-000000000004",
  sansei: "11111111-0000-0000-0000-000000000005",
  jcp: "11111111-0000-0000-0000-000000000006",
  reiwa: "11111111-0000-0000-0000-000000000007",
  sdp: "11111111-0000-0000-0000-000000000008",
  mirai: "11111111-0000-0000-0000-000000000009",
  komeito: "11111111-0000-0000-0000-000000000010",
  chudo: "11111111-0000-0000-0000-000000000011",
  conservative: "11111111-0000-0000-0000-000000000012",
  reduce_tax: "11111111-0000-0000-0000-000000000013",
  independent: "11111111-0000-0000-0000-000000000014",
};

export const PARTY_OPTIONS: PartyOption[] = [
  { id: "none", name: "特になし", shortName: "なし" },
  { id: "unknown", name: "わからない", shortName: "?" },
  { id: LEGACY_PARTY_ID_MAP.ldp, name: "自由民主党", shortName: "自民" },
  { id: LEGACY_PARTY_ID_MAP.cdp, name: "立憲民主党", shortName: "立憲" },
  { id: LEGACY_PARTY_ID_MAP.ishin, name: "日本維新の会", shortName: "維新" },
  { id: LEGACY_PARTY_ID_MAP.dpfp, name: "国民民主党", shortName: "国民" },
  { id: LEGACY_PARTY_ID_MAP.komeito, name: "公明党", shortName: "公明" },
  { id: LEGACY_PARTY_ID_MAP.jcp, name: "日本共産党", shortName: "共産" },
  { id: LEGACY_PARTY_ID_MAP.reiwa, name: "れいわ新選組", shortName: "れいわ" },
  { id: LEGACY_PARTY_ID_MAP.sansei, name: "参政党", shortName: "参政" },
  { id: LEGACY_PARTY_ID_MAP.sdp, name: "社会民主党", shortName: "社民" },
  { id: LEGACY_PARTY_ID_MAP.conservative, name: "日本保守党", shortName: "保守" },
  { id: LEGACY_PARTY_ID_MAP.mirai, name: "チームみらい", shortName: "チみ" },
  { id: LEGACY_PARTY_ID_MAP.chudo, name: "中道改革連合", shortName: "中道" },
  { id: LEGACY_PARTY_ID_MAP.reduce_tax, name: "減税日本・ゆうこく連合", shortName: "減ゆ" },
  { id: LEGACY_PARTY_ID_MAP.independent, name: "無所属", shortName: "無所属" },
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
