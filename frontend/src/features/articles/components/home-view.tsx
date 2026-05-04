"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { getPreferences } from "@/lib/storage/preferences-storage";
import { listArticles, type ArticleCardResponse } from "@/lib/api/articles-api";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { ArticleCard } from "@/features/articles/components/article-card";

// ホーム画面のビューコンポーネント（Client Component）
// localStorage から設定を読み、ヒーローバナー・記事一覧・政党フィルターを表示する
export function HomeView() {
  const [articles, setArticles] = useState<ArticleCardResponse[]>([]);
  const [parties, setParties] = useState<PartyResponse[]>([]);
  const [selectedPartyId, setSelectedPartyId] = useState<string | null>(null);
  // 支持政党（ヒーローバナー用）
  const [heroPartyName, setHeroPartyName] = useState<string | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  // 1. 政党一覧を取得する
  useEffect(() => {
    listParties()
      .then(setParties)
      .catch(() => setParties([]));
  }, []);

  // 2. DB 由来の政党一覧から支持政党名を解決する
  useEffect(() => {
    const prefs = getPreferences();
    const partyId = prefs.supportedPartyId;
    if (!partyId || partyId === "none" || partyId === "unknown" || partyId === "other") {
      setHeroPartyName(null);
      return;
    }
    setHeroPartyName(parties.find((p) => p.id === partyId)?.name ?? null);
  }, [parties]);

  // 3. 記事一覧を取得する
  const fetchArticles = useCallback(
    async (partyId: string | null, cursor?: string) => {
      try {
        const res = await listArticles({
          ...(partyId ? { party_id: partyId } : {}),
          sort: "latest",
          limit: "12",
          ...(cursor ? { cursor } : {}),
        });
        return res;
      } catch {
        return { items: [], next_cursor: null };
      }
    },
    [],
  );

  // 4. タブ切り替え時に記事を再取得する
  useEffect(() => {
    setLoading(true);
    fetchArticles(selectedPartyId).then((res) => {
      setArticles(res.items);
      setNextCursor(res.next_cursor);
      setLoading(false);
    });
  }, [selectedPartyId, fetchArticles]);

  // 5. 追加読み込みを行う
  const handleLoadMore = async () => {
    if (!nextCursor || loadingMore) return;
    setLoadingMore(true);
    const res = await fetchArticles(selectedPartyId, nextCursor);
    setArticles((prev) => [...prev, ...res.items]);
    setNextCursor(res.next_cursor);
    setLoadingMore(false);
  };

  const hasSelectedParty = heroPartyName !== null;
  const selectedPartyName = parties.find((p) => p.id === selectedPartyId)?.name;
  const articleSectionTitle = selectedPartyName
    ? `${selectedPartyName}のニュース`
    : "すべてのニュース";

  return (
    <div>
      {/* ヒーローバナー */}
      <div
        className="rounded-2xl overflow-hidden mb-6"
        style={{
          backgroundColor: hasSelectedParty
            ? "var(--color-brand-primary)"
            : "var(--color-bg-surface)",
        }}
      >
        <div className="px-5 py-5 flex items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            {hasSelectedParty ? (
              /* 支持政党あり: 政党名 + Good News */
              <>
                <p
                  className="text-sm font-medium mb-0.5"
                  style={{ color: "rgba(255,255,255,0.85)" }}
                >
                  {heroPartyName}の
                </p>
                <p className="text-2xl font-bold mb-2" style={{ color: "#ffffff" }}>
                  Good News
                </p>
                <p className="text-xs mb-3" style={{ color: "rgba(255,255,255,0.75)" }}>
                  あなたに合った情報をお届けします
                </p>
                <Link
                  href="/parties"
                  className="text-xs underline transition-opacity duration-150 hover:opacity-80"
                  style={{ color: "rgba(255,255,255,0.9)" }}
                >
                  各政党の詳細を見る &gt;
                </Link>
              </>
            ) : (
              /* 政党未設定: 全政党 Good News */
              <>
                <p
                  className="text-sm font-medium mb-0.5"
                  style={{ color: "var(--color-brand-primary)" }}
                >
                  各政党の
                </p>
                <p
                  className="text-xl font-bold mb-2"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  Good News をお届けします
                </p>
                <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                  あなたの関心テーマに合わせて表示をカスタマイズできます
                </p>
              </>
            )}
          </div>

          {/* マスコットプレースホルダー */}
          <div
            className="flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center text-3xl select-none"
            aria-hidden="true"
            style={{
              backgroundColor: hasSelectedParty
                ? "rgba(255,255,255,0.2)"
                : "var(--color-bg-muted)",
            }}
          >
            🌱
          </div>
        </div>
      </div>

      {/* 政党フィルターチップ */}
      <div className="mb-6">
        <p
          className="text-xs font-medium mb-2"
          style={{ color: "var(--color-text-secondary)" }}
        >
          政党を選択
        </p>
        <div
          className="flex gap-2 overflow-x-auto pb-1 -mx-4 px-4"
          style={{ scrollbarWidth: "none" }}
        >
          {/* すべて */}
          <button
            type="button"
            onClick={() => setSelectedPartyId(null)}
            className="flex-shrink-0 px-3 py-1.5 rounded-full text-sm border transition-colors duration-150"
            style={{
              borderColor:
                selectedPartyId === null
                  ? "var(--color-brand-primary)"
                  : "var(--color-border)",
              backgroundColor:
                selectedPartyId === null ? "var(--color-brand-primary)" : "transparent",
              color: selectedPartyId === null ? "#ffffff" : "var(--color-text-secondary)",
            }}
          >
            すべて
          </button>

          {/* 各政党チップ: 色ドット + 略称 */}
          {parties.map((party) => {
            const isActive = selectedPartyId === party.id;
            return (
              <button
                key={party.id}
                type="button"
                onClick={() => setSelectedPartyId(party.id)}
                className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-colors duration-150"
                style={{
                  borderColor: isActive
                    ? (party.color_hex ?? "var(--color-brand-primary)")
                    : "var(--color-border)",
                  backgroundColor:
                    isActive && party.color_hex ? `${party.color_hex}18` : "transparent",
                  color: isActive
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
                }}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: party.color_hex ?? "#999999" }}
                />
                {party.short_name}
              </button>
            );
          })}
        </div>
      </div>

      {/* 記事グリッドヘッダー */}
      <div className="flex items-center justify-between mb-3">
        <h2
          className="text-base font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          {articleSectionTitle}
        </h2>
      </div>

      {/* 記事グリッド */}
      {loading ? (
        <div
          className="text-center py-12 text-sm"
          style={{ color: "var(--color-text-secondary)" }}
        >
          読み込み中...
        </div>
      ) : articles.length === 0 ? (
        <div
          className="text-center py-12 text-sm"
          style={{ color: "var(--color-text-secondary)" }}
        >
          記事が見つかりませんでした
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>

          {nextCursor && (
            <div className="text-center mt-8">
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="px-6 py-2.5 rounded-full text-sm border transition-colors duration-150 disabled:opacity-50"
                style={{
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-secondary)",
                }}
              >
                {loadingMore ? "読み込み中..." : "もっと読む"}
              </button>
            </div>
          )}

          <div className="text-center mt-6">
            <Link
              href="/parties"
              className="text-sm transition-opacity duration-150 hover:opacity-70"
              style={{ color: "var(--color-text-secondary)" }}
            >
              各政党についての説明を見る &gt;
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
