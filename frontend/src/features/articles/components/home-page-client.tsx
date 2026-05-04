"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getPreferences } from "@/lib/storage/preferences-storage";
import {
  listArticles,
  type ArticleCardResponse,
  type ArticleListResponse,
} from "@/lib/api/articles-api";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { PARTY_OPTIONS } from "@/lib/constants/parties";
import { ArticleCard } from "@/features/articles/components/article-card";
import { Button } from "@/components/ui/button";
import { PageContainer } from "@/components/layout/page-container";

// 記事スケルトンカード
function ArticleSkeleton() {
  return (
    <div
      className="rounded-lg overflow-hidden border animate-pulse"
      style={{ borderColor: "var(--color-border)" }}
    >
      <div className="w-full h-28" style={{ backgroundColor: "var(--color-bg-muted)" }} />
      <div className="p-3 flex flex-col gap-2">
        <div className="h-4 rounded" style={{ backgroundColor: "var(--color-bg-muted)", width: "40%" }} />
        <div className="h-4 rounded" style={{ backgroundColor: "var(--color-bg-muted)" }} />
        <div className="h-4 rounded" style={{ backgroundColor: "var(--color-bg-muted)", width: "80%" }} />
        <div className="h-3 rounded" style={{ backgroundColor: "var(--color-bg-muted)", width: "30%" }} />
      </div>
    </div>
  );
}

// ホームページメインコンテンツ（Client Component）
export function HomePageClient() {
  const router = useRouter();
  const [selectedPartyId, setSelectedPartyId] = useState<string>("all");
  const [articles, setArticles] = useState<ArticleCardResponse[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parties, setParties] = useState<PartyResponse[]>([]);
  const [supportedPartyId, setSupportedPartyId] = useState<string | null>(null);
  const [heroPartyName, setHeroPartyName] = useState<string | null>(null);
  const [heroColor, setHeroColor] = useState<string>("#F5F5DC");

  // 1. 初期化処理: オンボーディング未完了ならリダイレクト
  useEffect(() => {
    const prefs = getPreferences();
    if (!prefs.onboardingCompleted) {
      router.replace("/onboarding");
      return;
    }
    setSupportedPartyId(prefs.supportedPartyId);

    // ヒーローバナーの情報を設定する
    if (
      prefs.supportedPartyId &&
      prefs.supportedPartyId !== "none" &&
      prefs.supportedPartyId !== "unknown"
    ) {
      const partyOption = PARTY_OPTIONS.find((p) => p.id === prefs.supportedPartyId);
      setHeroPartyName(partyOption?.name ?? null);
    }
  }, [router]);

  // 2. 政党一覧を取得する
  useEffect(() => {
    listParties()
      .then(setParties)
      .catch(() => {
        // 政党一覧取得失敗時はフォールバック（エラーは表示しない）
      });
  }, []);

  // 3. ヒーローバナーのカラーを更新する
  useEffect(() => {
    if (supportedPartyId && parties.length > 0) {
      const party = parties.find((p) => p.id === supportedPartyId);
      if (party?.color_hex) {
        setHeroColor(party.color_hex);
      }
    }
  }, [supportedPartyId, parties]);

  // 4. 記事一覧を取得する
  const fetchArticles = useCallback(
    async (partyId: string, cursor?: string) => {
      try {
        const params: Parameters<typeof listArticles>[0] = {
          limit: "20",
        };
        if (partyId !== "all") {
          params.party_id = partyId;
        }
        if (cursor) {
          params.cursor = cursor;
        }
        const result: ArticleListResponse = await listArticles(params);
        return result;
      } catch {
        throw new Error("記事の取得に失敗しました");
      }
    },
    [],
  );

  // 5. 政党タブ変更時に記事を再取得する
  useEffect(() => {
    setLoading(true);
    setError(null);
    setArticles([]);
    setNextCursor(null);

    fetchArticles(selectedPartyId)
      .then((result) => {
        setArticles(result.items);
        setNextCursor(result.next_cursor);
      })
      .catch((err: Error) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [selectedPartyId, fetchArticles]);

  // 6. もっと読む（カーソルページネーション）
  const handleLoadMore = async () => {
    if (!nextCursor || loadingMore) return;
    setLoadingMore(true);
    try {
      const result = await fetchArticles(selectedPartyId, nextCursor);
      setArticles((prev) => [...prev, ...result.items]);
      setNextCursor(result.next_cursor);
    } catch {
      // ロードエラーは静かに無視する
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <PageContainer>
      <div className="py-6">
        {/* ヒーローバナー */}
        <div
          className="rounded-xl p-6 mb-6 text-white"
          style={{ backgroundColor: heroPartyName ? heroColor : "#4CAF50" }}
        >
          <p className="text-lg font-bold">
            {heroPartyName
              ? `${heroPartyName}のGood Newsをお届け`
              : "各政党のGood Newsをお届け"}
          </p>
          <p className="text-sm opacity-80 mt-1">
            各政党の建設的な取り組みをポジティブに伝えます
          </p>
        </div>

        {/* 政党一覧への導線 */}
        <div className="mb-4 text-right">
          <Link
            href="/parties"
            className="text-sm transition-colors duration-150 hover:opacity-70"
            style={{ color: "var(--color-brand-primary)" }}
          >
            各政党についての説明 &gt;
          </Link>
        </div>

        {/* 政党タブ（横スクロール） */}
        <div className="overflow-x-auto pb-2 mb-4 -mx-4 px-4">
          <div className="flex gap-2 w-max">
            {/* 「すべて」タブ */}
            <button
              type="button"
              onClick={() => setSelectedPartyId("all")}
              className="px-4 py-1.5 rounded-full text-sm border whitespace-nowrap transition-colors duration-150"
              style={{
                borderColor:
                  selectedPartyId === "all"
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                backgroundColor:
                  selectedPartyId === "all"
                    ? "var(--color-brand-primary)"
                    : "transparent",
                color:
                  selectedPartyId === "all"
                    ? "#ffffff"
                    : "var(--color-text-primary)",
              }}
            >
              すべて
            </button>

            {/* 政党タブ一覧 */}
            {parties.map((party) => (
              <button
                key={party.id}
                type="button"
                onClick={() => setSelectedPartyId(party.id)}
                className="px-4 py-1.5 rounded-full text-sm border whitespace-nowrap transition-colors duration-150"
                style={{
                  borderColor:
                    selectedPartyId === party.id
                      ? party.color_hex ?? "var(--color-brand-primary)"
                      : "var(--color-border)",
                  backgroundColor:
                    selectedPartyId === party.id
                      ? party.color_hex ?? "var(--color-brand-primary)"
                      : "transparent",
                  color:
                    selectedPartyId === party.id
                      ? "#ffffff"
                      : "var(--color-text-primary)",
                }}
              >
                {party.short_name}
              </button>
            ))}
          </div>
        </div>

        {/* エラー表示 */}
        {error && (
          <div
            className="rounded-lg p-4 mb-4 text-sm"
            style={{
              backgroundColor: "var(--color-bg-surface)",
              color: "var(--color-text-secondary)",
            }}
          >
            {error}
          </div>
        )}

        {/* 記事グリッド */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => (
                <ArticleSkeleton key={i} />
              ))
            : articles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
        </div>

        {/* 記事が0件のとき */}
        {!loading && !error && articles.length === 0 && (
          <div
            className="text-center py-12 text-sm"
            style={{ color: "var(--color-text-secondary)" }}
          >
            現在表示できる記事がありません
          </div>
        )}

        {/* もっと読むボタン */}
        {nextCursor && !loading && (
          <div className="flex justify-center mt-6">
            <Button
              variant="outline"
              size="md"
              onClick={handleLoadMore}
              disabled={loadingMore}
            >
              {loadingMore ? "読み込み中..." : "もっと読む"}
            </Button>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
