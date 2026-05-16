# 政策カテゴリシードデータ
# カテゴリ定義は docs/product/20260430_画面設計.md の関心テーマ選択肢を参照

import uuid

POLICY_CATEGORY_SEEDS = [
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000001"),
        "name": "税金",
        "slug": "tax",
        "description": "税制改正、消費税、所得税、法人税などに関するニュース",
        "display_order": 1,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000002"),
        "name": "社会保障",
        "slug": "social-security",
        "description": "年金、医療保険、介護保険、生活保護などに関するニュース",
        "display_order": 2,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000003"),
        "name": "賃上げ・労働",
        "slug": "labor",
        "description": "最低賃金、賃上げ施策、働き方改革などに関するニュース",
        "display_order": 3,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000004"),
        "name": "物価高",
        "slug": "inflation",
        "description": "物価対策、エネルギー補助、食料品価格などに関するニュース",
        "display_order": 4,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000005"),
        "name": "子育て",
        "slug": "childcare",
        "description": "保育所、育児支援、児童手当などに関するニュース",
        "display_order": 5,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000006"),
        "name": "教育",
        "slug": "education",
        "description": "学校教育、奨学金、教育費無償化などに関するニュース",
        "display_order": 6,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000007"),
        "name": "国防",
        "slug": "defense",
        "description": "防衛政策、自衛隊、安全保障などに関するニュース",
        "display_order": 7,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000008"),
        "name": "外交",
        "slug": "diplomacy",
        "description": "外交政策、国際関係、首脳会談などに関するニュース",
        "display_order": 8,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000009"),
        "name": "移民・外国人政策",
        "slug": "immigration",
        "description": "外国人受け入れ、在留資格、多文化共生などに関するニュース",
        "display_order": 9,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000010"),
        "name": "エネルギー",
        "slug": "energy",
        "description": "再生可能エネルギー、原子力、電力政策などに関するニュース",
        "display_order": 10,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000011"),
        "name": "地方創生",
        "slug": "regional-revitalization",
        "description": "地方移住促進、地域振興、過疎対策などに関するニュース",
        "display_order": 11,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000012"),
        "name": "憲法",
        "slug": "constitution",
        "description": "憲法改正、憲法解釈、立憲主義などに関するニュース",
        "display_order": 12,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000013"),
        "name": "金融政策",
        "slug": "monetary-policy",
        "description": "日銀政策、金利、為替、景気対策などに関するニュース",
        "display_order": 13,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000014"),
        "name": "環境",
        "slug": "environment",
        "description": "気候変動対策、カーボンニュートラル、環境規制などに関するニュース",
        "display_order": 14,
    },
    {
        "id": uuid.UUID("22222222-0000-0000-0000-000000000015"),
        "name": "防災",
        "slug": "disaster-prevention",
        "description": "地震対策、防災インフラ、避難体制などに関するニュース",
        "display_order": 15,
    },
]
