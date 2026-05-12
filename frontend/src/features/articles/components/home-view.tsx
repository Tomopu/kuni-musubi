"use client";

import type { CSSProperties } from "react";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import {
  ChevronRight,
  LayoutGrid,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import { listArticles, type ArticleCardResponse } from "@/lib/api/articles-api";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { getPreferences, needsOnboarding } from "@/lib/storage/preferences-storage";
import { ArticleCard } from "@/features/articles/components/article-card";

export function HomeView() {
  const router = useRouter();
  const [articles, setArticles] = useState<ArticleCardResponse[]>([]);
  const [parties, setParties] = useState<PartyResponse[]>([]);
  const [selectedPartyId, setSelectedPartyId] = useState<string | null | undefined>(undefined);
  const [heroPartyName, setHeroPartyName] = useState<string | null>(null);
  const [heroPartyId, setHeroPartyId] = useState<string | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [onboardingChecked, setOnboardingChecked] = useState(false);

  useEffect(() => {
    listParties()
      .then(setParties)
      .catch(() => setParties([]));
  }, []);

  useEffect(() => {
    if (needsOnboarding()) {
      router.replace("/onboarding");
      return;
    }

    const partyId = getPreferences().supportedPartyId;
    setSelectedPartyId(null);
    setOnboardingChecked(true);
    if (!partyId || ["none", "unknown", "other"].includes(partyId)) {
      setHeroPartyName(null);
      setHeroPartyId(null);
      return;
    }
    setHeroPartyId(partyId);
  }, [router]);

  useEffect(() => {
    if (!heroPartyId) {
      setHeroPartyName(null);
      return;
    }
    if (parties.length === 0) return;
    const party = parties.find((p) => p.id === heroPartyId);
    setHeroPartyName(party?.name ?? null);
  }, [heroPartyId, parties]);

  const fetchArticles = useCallback(
    async (partyId: string | null, cursor?: string) => {
      try {
        return await listArticles({
          ...(partyId ? { party_id: partyId } : {}),
          sort: "latest",
          limit: "12",
          ...(cursor ? { cursor } : {}),
        });
      } catch {
        return { items: [], next_cursor: null };
      }
    },
    [],
  );

  useEffect(() => {
    if (selectedPartyId === undefined) return;
    setLoading(true);
    fetchArticles(selectedPartyId).then((res) => {
      setArticles(res.items);
      setNextCursor(res.next_cursor);
      setLoading(false);
    });
  }, [selectedPartyId, fetchArticles]);

  const handleLoadMore = async () => {
    if (!nextCursor || loadingMore || selectedPartyId === undefined) return;
    setLoadingMore(true);
    const res = await fetchArticles(selectedPartyId, nextCursor);
    setArticles((prev) => [...prev, ...res.items]);
    setNextCursor(res.next_cursor);
    setLoadingMore(false);
  };

  const hasSelectedParty = heroPartyName !== null;
  const heroParty = heroPartyId ? parties.find((p) => p.id === heroPartyId) : null;
  const heroPartyColor = heroParty?.color_hex ?? "#e60012";
  const heroPartyDetailHref = heroPartyId ? `/parties/${heroPartyId}` : "/parties";
  const selectedPartyName = parties.find((p) => p.id === selectedPartyId)?.name;
  const articleSectionTitle = selectedPartyName
    ? `${selectedPartyName}のニュース`
    : "すべてのニュース";

  if (!onboardingChecked) {
    return <div className="empty-state">読み込み中...</div>;
  }

  return (
    <div className="home-page">
      <section
        className={`home-hero ${hasSelectedParty ? "home-hero--selected" : "home-hero--unset"}`}
        style={
          hasSelectedParty
            ? ({ "--party-color": heroPartyColor } as CSSProperties)
            : undefined
        }
      >
        <div className="home-hero__content">
          <div className="home-hero__copy">
            {hasSelectedParty ? (
              <>
                <span className="home-hero__badge">あなたの支持政党</span>
                <h1>
                  {heroPartyName}の
                  <br />
                  Good News
                </h1>
                <p>
                  あなたの関心テーマに基づき、最新のポジティブな動きをお届けします。
                </p>
                <Link href={heroPartyDetailHref} className="home-hero__link">
                  詳しく見る
                  <ChevronRight size={16} />
                </Link>
              </>
            ) : (
              <>
                <h1>
                  各政党の
                  <br />
                  Good News をお届けします
                </h1>
                <p>
                  あなたの関心テーマに合わせて、前向きなニュースをピックアップします。
                </p>
              </>
            )}
          </div>

          <div className="home-hero__visual">
            <Image
              src="/assets/mascot/mascot-announce.png"
              alt="メガホンを持ったKuni-Musubiキャラクター"
              width={170}
              height={170}
              className="home-hero__mascot"
              priority
            />
            {!hasSelectedParty && (
              <Image
                src="/assets/decorations/deco-paperplane.png"
                alt=""
                width={82}
                height={82}
                className="home-hero__paperplane"
                aria-hidden="true"
              />
            )}
          </div>
        </div>
      </section>

      <section className="party-filter">
        <p className="party-filter__label">政党を選ぶ</p>
        <div className="party-filter__chips">
          <button
            type="button"
            onClick={() => setSelectedPartyId(null)}
            className="chip-button party-chip"
            style={{
              borderColor:
                selectedPartyId === null
                  ? "var(--color-brand-primary)"
                  : "var(--color-border)",
              backgroundColor:
                selectedPartyId === null ? "var(--color-soft-green)" : "#ffffff",
              color:
                selectedPartyId === null
                  ? "var(--color-brand-deep)"
                  : "var(--color-text-secondary)",
            }}
          >
            <LayoutGrid size={14} />
            すべて
          </button>

          {parties.map((party) => {
            const isActive = selectedPartyId === party.id;
            return (
              <button
                key={party.id}
                type="button"
                onClick={() => setSelectedPartyId(party.id)}
                className="chip-button party-chip"
                style={{
                  borderColor: isActive
                    ? (party.color_hex ?? "var(--color-brand-primary)")
                    : "var(--color-border)",
                  backgroundColor:
                    isActive && party.color_hex ? `${party.color_hex}14` : "#ffffff",
                  color: isActive ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                }}
              >
                <span
                  className="dot"
                  style={{ backgroundColor: party.color_hex ?? "#999999" }}
                />
                {party.short_name}
              </button>
            );
          })}
        </div>
      </section>

      <div className="content-section-head">
        <h2>
          <Sparkles size={18} />
          {articleSectionTitle}
        </h2>
        <button type="button" className="sort-pill">
          <SlidersHorizontal size={14} />
          新しい順
        </button>
      </div>

      {loading ? (
        <div className="empty-state">読み込み中...</div>
      ) : articles.length === 0 ? (
        <div className="empty-state">記事が見つかりませんでした</div>
      ) : (
        <>
          <div className="article-grid content-fade">
            {articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>

          {nextCursor && (
            <div className="load-more-wrap">
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="load-more-button"
              >
                {loadingMore ? "読み込み中..." : "もっと見る"}
                <ChevronRight size={16} />
              </button>
            </div>
          )}

          <Link
            href="/parties"
            className="party-guide-banner party-guide-banner--link"
            aria-label="各政党についての説明を見る"
          >
            <Sparkles size={18} />
            <span>各政党についての説明を見る</span>
            <span className="party-guide-banner__arrow" aria-hidden="true">
              <ChevronRight size={18} />
            </span>
            <Image
              src="/assets/mascot/mascot-search.png"
              alt="虫眼鏡を持ったKuni-Musubiキャラクター"
              width={70}
              height={70}
              className="party-guide-banner__mascot"
            />
          </Link>
        </>
      )}
    </div>
  );
}
