import type { Metadata } from "next";
import Image from "next/image";
import {
  BarChart3,
  HeartHandshake,
  Link2,
  LockKeyhole,
  Newspaper,
  Scale,
  Sparkles,
  Sprout,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";

export const metadata: Metadata = {
  title: "このアプリについて | Kuni-Musubi",
};

type AboutItem = {
  Icon: LucideIcon;
  tone: "green" | "blue" | "yellow" | "pink" | "mint" | "purple" | "orange";
  title: string;
  description: string;
};

const ABOUT_ITEMS: AboutItem[] = [
  {
    Icon: Sprout,
    tone: "green",
    title: "Kuni-Musubi について",
    description:
      "「Kuni-Musubi（クニムスビ）」は、分断された国民や政党の意見を結びつけ、日本をひとつのチームとして強くしていくという願いを込めたプロダクトです。",
  },
  {
    Icon: Newspaper,
    tone: "blue",
    title: "ポジティブな政治ニュースをお届けする理由",
    description:
      "SNS には政府や政党への批判的なニュースが溢れ、政治への苦手意識を持つ若年層が増えています。Kuni-Musubi は、各政党の建設的・ポジティブな取り組みに光を当てることで、「政治は自分の生活を良くするためのもの」という視点を取り戻すきっかけを提供します。",
  },
  {
    Icon: Scale,
    tone: "yellow",
    title: "特定政党を応援するアプリではありません",
    description:
      "Kuni-Musubi は、特定の政党・政府・イデオロギーを支持・宣伝するアプリではありません。すべての政党のポジティブな取り組みをバランス良く届けることを目指しています。",
  },
  {
    Icon: Link2,
    tone: "pink",
    title: "残る課題・出典も必ず掲載します",
    description:
      "プロパガンダや無批判な肯定とならないよう、良いニュースだけでなく「残る課題」「世論・与野党の評価」「出典・一次情報リンク」も必ず掲載します。批判的思考を失わずにニュースを読めるよう設計しています。",
  },
  {
    Icon: LockKeyhole,
    tone: "mint",
    title: "あなたのデータは端末内にのみ保存されます",
    description:
      "設定した年代・支持政党・関心テーマは、あなたの端末内（ブラウザのローカルストレージ）にのみ保存されます。アカウントを作成する必要はなく、サーバーにプロフィール情報は送信されません。",
  },
  {
    Icon: BarChart3,
    tone: "purple",
    title: "匿名の集計データとして活用する場合があります",
    description:
      "サービス改善のため、どのような年代・テーマへの関心が多いかを、個人を特定できない匿名の集計データとして利用する場合があります。オンボーディングの回答と記事閲覧データを個人単位で結合することはありません。",
  },
  {
    Icon: Sparkles,
    tone: "orange",
    title: "目指すユーザー体験",
    description:
      "日本をより良くできると思えるきっかけを作ること。政治を「怒りや対立だけの世界」ではなく、「生活と未来を良くするための手段」として捉え直せる場所を目指しています。",
  },
];

// このアプリについて画面（Server Component）
export default function AboutPage() {
  return (
    <PageContainer>
      <div className="about-page">
        <section className="about-hero">
          <Image
            src="/assets/decorations/deco-wakaba.png"
            alt=""
            width={112}
            height={112}
            className="about-hero__decor about-hero__decor--wakaba"
            aria-hidden="true"
          />
          <Image
            src="/assets/decorations/deco-paperplane.png"
            alt=""
            width={120}
            height={96}
            className="about-hero__decor about-hero__decor--paperplane"
            aria-hidden="true"
          />
          <div className="about-hero__text">
            <h1>このアプリについて</h1>
            <p>
              Kuni-Musubi が大切にしていること、
              <br />
              プライバシーの考え方をお伝えします。
            </p>
          </div>
          <div className="about-hero__visual" aria-hidden="true">
            <Image
              src="/assets/mascot/mascot-pencil.png"
              alt=""
              width={132}
              height={132}
              className="about-hero__mascot"
              priority
            />
          </div>
        </section>

        <div className="about-items">
          {ABOUT_ITEMS.map(({ Icon, tone, title, description }) => (
            <article key={title} className="about-card">
              <span
                className={`about-card__icon about-card__icon--${tone}`}
                aria-hidden="true"
              >
                <Icon size={22} strokeWidth={2.2} />
              </span>
              <div className="about-card__body">
                <h2>{title}</h2>
                <p>{description}</p>
              </div>
            </article>
          ))}
        </div>

        <section className="about-closing">
          <Image
            src="/assets/decorations/deco-sparkle.png"
            alt=""
            width={104}
            height={104}
            className="about-closing__decor"
            aria-hidden="true"
          />
          <span className="about-closing__icon" aria-hidden="true">
            <HeartHandshake size={26} strokeWidth={2.1} />
          </span>
          <div className="about-closing__text">
            <h2>一緒に、より良い社会をつくっていきましょう！</h2>
            <p>
              ニュースを少し前向きに読み解きながら、自分の暮らしと政治のつながりを見つけていける場所を育てていきます。
            </p>
          </div>
        </section>
      </div>
    </PageContainer>
  );
}
