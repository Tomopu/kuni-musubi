import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { MascotImage } from "@/components/ui/mascot-image";

export const metadata: Metadata = {
  title: "このアプリについて | Kuni-Musubi",
};

const ABOUT_ITEMS = [
  {
    icon: "🌱",
    title: "Kuni-Musubi について",
    description:
      "「Kuni-Musubi（クニムスビ）」は、分断された国民や政党の意見を結びつけ、日本をひとつのチームとして強くしていくという願いを込めたプロダクトです。",
  },
  {
    icon: "📰",
    title: "ポジティブな政治ニュースをお届けする理由",
    description:
      "SNS には政府や政党への批判的なニュースが溢れ、政治への苦手意識を持つ若年層が増えています。Kuni-Musubi は、各政党の建設的・ポジティブな取り組みに光を当てることで、「政治は自分の生活を良くするためのもの」という視点を取り戻すきっかけを提供します。",
  },
  {
    icon: "⚖️",
    title: "特定政党を応援するアプリではありません",
    description:
      "Kuni-Musubi は、特定の政党・政府・イデオロギーを支持・宣伝するアプリではありません。すべての政党のポジティブな取り組みをバランス良く届けることを目指しています。",
  },
  {
    icon: "🔗",
    title: "残る課題・出典も必ず掲載します",
    description:
      "プロパガンダや無批判な肯定とならないよう、良いニュースだけでなく「残る課題」「世論・与野党の評価」「出典・一次情報リンク」も必ず掲載します。批判的思考を失わずにニュースを読めるよう設計しています。",
  },
  {
    icon: "🔒",
    title: "あなたのデータは端末内にのみ保存されます",
    description:
      "設定した年代・支持政党・関心テーマは、あなたの端末内（ブラウザのローカルストレージ）にのみ保存されます。アカウントを作成する必要はなく、サーバーにプロフィール情報は送信されません。",
  },
  {
    icon: "📊",
    title: "匿名の集計データとして活用する場合があります",
    description:
      "サービス改善のため、どのような年代・テーマへの関心が多いかを、個人を特定できない匿名の集計データとして利用する場合があります。オンボーディングの回答と記事閲覧データを個人単位で結合することはありません。",
  },
  {
    icon: "✨",
    title: "目指すユーザー体験",
    description:
      "日本をより良くできると思えるきっかけを作ること。政治を「怒りや対立だけの世界」ではなく、「生活と未来を良くするための手段」として捉え直せる場所を目指しています。",
  },
];

// このアプリについて画面（Server Component）
export default function AboutPage() {
  return (
    <PageContainer>
      <div className="py-8">
        {/* ヘッダーカード: テキスト左 + マスコット右 */}
        <div
          className="rounded-2xl px-6 py-6 flex items-center gap-4 mb-8"
          style={{ backgroundColor: "#FFF9E6" }}
        >
          <div className="flex-1 min-w-0">
            <h1
              className="text-xl font-bold mb-1.5"
              style={{ color: "var(--color-text-primary)" }}
            >
              このアプリについて
            </h1>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Kuni-Musubi が大切にしていること、
              <br />
              プライバシーの考え方をお伝えします。
            </p>
          </div>
          <MascotImage pose="greeting" size={90} />
        </div>

        {/* 説明カード一覧 */}
        <div className="flex flex-col gap-3">
          {ABOUT_ITEMS.map((item) => (
            <div
              key={item.title}
              className="rounded-xl p-4"
              style={{ backgroundColor: "var(--color-bg-surface)" }}
            >
              <div className="flex gap-3">
                <span
                  className="flex-shrink-0 text-xl leading-snug mt-0.5"
                  aria-hidden="true"
                >
                  {item.icon}
                </span>
                <div>
                  <h2
                    className="text-sm font-semibold mb-1"
                    style={{ color: "var(--color-text-primary)" }}
                  >
                    {item.title}
                  </h2>
                  <p
                    className="text-xs leading-relaxed"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    {item.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* フッターメッセージ */}
        <div
          className="mt-8 rounded-xl py-5 px-4 text-center"
          style={{ backgroundColor: "var(--color-brand-primary)" }}
        >
          <p className="text-sm font-semibold" style={{ color: "#ffffff" }}>
            一緒に、より良い社会をつくっていきましょう！
          </p>
        </div>
      </div>
    </PageContainer>
  );
}
