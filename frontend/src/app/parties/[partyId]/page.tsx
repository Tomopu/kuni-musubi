import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  Check,
  ChevronRight,
  ExternalLink,
  Landmark,
} from "lucide-react";
import { MascotImage } from "@/components/ui/mascot-image";
import { PageContainer } from "@/components/layout/page-container";
import { ArticleCard } from "@/features/articles/components/article-card";
import { getPartyDetail } from "@/lib/api/parties-api";

type Props = {
  params: Promise<{ partyId: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { partyId } = await params;
  try {
    const party = await getPartyDetail(partyId);
    return { title: `${party.name} | Kuni-Musubi` };
  } catch {
    return { title: "政党詳細 | Kuni-Musubi" };
  }
}

export default async function PartyDetailPage({ params }: Props) {
  const { partyId } = await params;
  const party = await getPartyDetail(partyId).catch(() => notFound());

  const manifestoPromises = party.manifesto_promises ?? [];
  const mainPolicyCategories = party.main_policy_categories ?? [];
  const latestArticles = party.latest_articles ?? [];
  const partyColor = party.color_hex ?? "var(--color-brand-primary)";

  return (
    <PageContainer
      className="party-detail-page"
      style={{ "--party-color": partyColor } as CSSProperties}
    >
      <Link href="/parties" className="back-link">
        <ArrowLeft size={20} />
        政党一覧へ
      </Link>

      <section className="party-detail-hero">
        <div className="party-detail-hero__title">
          <span className="party-detail-hero__badge">{party.short_name}</span>
          <div>
            <h1>{party.name}</h1>
            <p>{party.short_name}</p>
          </div>
        </div>
        <div className="party-detail-hero__visual">
          <Landmark size={96} strokeWidth={1.4} />
          <MascotImage pose="important" size={76} />
        </div>
      </section>

      <section className="party-metrics">
        <div>
          <span>代表者（党首）</span>
          <strong>{party.leader_name ?? "未確認"}</strong>
        </div>
        <div>
          <span>党成立年</span>
          <strong>{party.founded_year ? `${party.founded_year}年` : "未確認"}</strong>
        </div>
        <div>
          <span>所属議員数</span>
          <strong>{party.total_seats}名</strong>
        </div>
        <div>
          <span>衆議院議席数</span>
          <strong>{party.house_of_representatives_seats ?? 0}議席</strong>
        </div>
        <div>
          <span>参議院議席数</span>
          <strong>{party.house_of_councillors_seats ?? 0}議席</strong>
        </div>
        {party.official_url && (
          <a href={party.official_url} target="_blank" rel="noopener noreferrer">
            <span>公式サイト</span>
            <strong>
              公式サイトへ
              <ExternalLink size={16} />
            </strong>
          </a>
        )}
      </section>

      {(manifestoPromises.length > 0 || party.manifesto_summary) && (
        <section className="detail-card detail-card--manifesto">
          <h2>主な公約</h2>
          {manifestoPromises.length > 0 ? (
            <ol className="manifesto-list">
              {manifestoPromises.map((promise) => (
                <li key={promise}>{promise}</li>
              ))}
            </ol>
          ) : (
            <p>{party.manifesto_summary}</p>
          )}
        </section>
      )}

      <div className="party-detail-grid">
        {party.ideology_summary && (
          <section className="detail-card">
            <h2>党の政治理念</h2>
            <p>{party.ideology_summary}</p>
          </section>
        )}

        {mainPolicyCategories.length > 0 && (
          <section className="detail-card">
            <h2>主な政策タグ</h2>
            <div className="policy-tags">
              {mainPolicyCategories.map((category) => (
                <span key={category}>{category}</span>
              ))}
            </div>
          </section>
        )}
      </div>

      {latestArticles.length > 0 && (
        <section className="related-news">
          <div className="related-news__head">
            <h2>関連ニュース</h2>
            <Link href={`/?party=${party.id}`}>
              もっと見る
              <ChevronRight size={16} />
            </Link>
          </div>
          <div className="article-grid article-grid--related">
            {latestArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </section>
      )}

      <div className="party-news-note">
        <MascotImage pose="greeting" size={58} />
        <span>この政党のニュースは、ホーム画面の「{party.short_name}」タブでも見られます！</span>
        <Check size={18} />
      </div>
    </PageContainer>
  );
}
