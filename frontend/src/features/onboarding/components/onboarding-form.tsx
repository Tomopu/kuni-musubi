"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  BadgeHelp,
  BookOpen,
  BriefcaseBusiness,
  Building2,
  GraduationCap,
  HeartPulse,
  Landmark,
  LockKeyhole,
  PiggyBank,
  Shield,
  Sprout,
  WalletCards,
  Zap,
} from "lucide-react";
import { savePreferences } from "@/lib/storage/preferences-storage";
import { postOnboardingEvent } from "@/lib/api/analytics-api";
import {
  AGE_GROUP_OPTIONS,
  PARTY_OPTIONS,
  CATEGORY_OPTIONS,
} from "@/lib/constants/parties";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { Button } from "@/components/ui/button";
import { MascotImage } from "@/components/ui/mascot-image";

// 番号付きバッジ（緑丸 + 白数字）
function NumberBadge({ n }: { n: number }) {
  return (
    <span
      className="onboarding-step__number"
      aria-hidden="true"
    >
      {n}
    </span>
  );
}

const CATEGORY_ICONS = [
  PiggyBank,
  HeartPulse,
  WalletCards,
  Zap,
  Sprout,
  GraduationCap,
  Shield,
  Landmark,
  Building2,
  Zap,
  BriefcaseBusiness,
  BookOpen,
  WalletCards,
  Sprout,
  BadgeHelp,
];

type PartySelectOption = {
  id: string;
  name: string;
  shortName: string;
  colorHex: string | null;
};

const DEFAULT_PARTY_OPTIONS: PartySelectOption[] = [
  { id: "none", name: "特になし", shortName: "なし", colorHex: "#999999" },
  { id: "unknown", name: "わからない", shortName: "?", colorHex: "#999999" },
];

function toPartyOptions(parties: PartyResponse[]): PartySelectOption[] {
  return [
    ...DEFAULT_PARTY_OPTIONS,
    ...parties.map((party) => ({
      id: party.id,
      name: party.name,
      shortName: party.short_name,
      colorHex: party.color_hex,
    })),
  ];
}

function fallbackPartyOptions(): PartySelectOption[] {
  return PARTY_OPTIONS.map((party) => ({
    id: party.id,
    name: party.name,
    shortName: party.shortName,
    colorHex: null,
  }));
}

// オンボーディングフォーム（1画面縦スクロール）
// ステップ分割なし: 年代・支持政党・関心テーマを一度に表示する
export function OnboardingForm() {
  const router = useRouter();
  const [ageGroup, setAgeGroup] = useState<string | null>(null);
  const [supportedPartyId, setSupportedPartyId] = useState<string | null>(null);
  const [interestedCategoryIds, setInterestedCategoryIds] = useState<string[]>([]);
  const [partyOptions, setPartyOptions] = useState<PartySelectOption[]>(fallbackPartyOptions);

  useEffect(() => {
    let cancelled = false;
    void listParties()
      .then((parties) => {
        if (!cancelled) setPartyOptions(toPartyOptions(parties));
      })
      .catch(() => {
        if (!cancelled) setPartyOptions(fallbackPartyOptions());
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // 1. オンボーディングを完了してホームへ遷移する
  const handleComplete = () => {
    savePreferences({
      ageGroup,
      supportedPartyId,
      interestedCategoryIds,
      onboardingCompleted: true,
    });

    const partyStatus =
      supportedPartyId === "none"
        ? "none"
        : supportedPartyId === "unknown"
          ? "unknown"
          : supportedPartyId === null
            ? "skipped"
            : "selected";

    void postOnboardingEvent({
      age_group: ageGroup,
      selected_party_id: partyStatus === "selected" ? supportedPartyId : null,
      selected_party_status: partyStatus,
      interest_category_ids: interestedCategoryIds,
    });

    router.push("/");
  };

  // 2. スキップしてホームへ遷移する
  const handleSkip = () => {
    savePreferences({ onboardingCompleted: true });
    router.push("/");
  };

  // 3. 関心テーマのトグル処理
  const toggleCategory = (id: string) => {
    setInterestedCategoryIds((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id],
    );
  };

  return (
    <div className="onboarding-form">
      <section className="onboarding-step onboarding-step--age">
        <div className="onboarding-step__head">
          <NumberBadge n={1} />
          <h2>
            年代を教えてください
          </h2>
          <span>
            （任意です）
          </span>
        </div>
        <div className="chip-grid">
          {AGE_GROUP_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setAgeGroup(option.value)}
              className="chip-button onboarding-chip"
              style={{
                borderColor:
                  ageGroup === option.value
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                backgroundColor:
                  ageGroup === option.value ? "var(--color-brand-primary)" : "transparent",
                color:
                  ageGroup === option.value ? "#ffffff" : "var(--color-text-primary)",
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
        <MascotImage pose="thinking" size={72} className="onboarding-step__mascot" />
      </section>

      <section className="onboarding-step onboarding-step--party">
        <div className="onboarding-step__head">
          <NumberBadge n={2} />
          <h2>
            支持政党を教えてください
          </h2>
          <span>
            （任意です）
          </span>
        </div>
        <div className="chip-grid">
          {partyOptions.map((party) => {
            const isSelected = supportedPartyId === party.id;
            const dotColor = party.colorHex ?? "#999999";
            const hasDot = party.id !== "none" && party.id !== "unknown";
            return (
              <button
                key={party.id}
                type="button"
                onClick={() => setSupportedPartyId(party.id)}
                className="chip-button onboarding-chip"
                style={{
                  borderColor: isSelected ? "var(--color-brand-primary)" : "var(--color-border)",
                  backgroundColor: isSelected ? "var(--color-brand-primary)" : "transparent",
                  color: isSelected ? "#ffffff" : "var(--color-text-primary)",
                }}
              >
                {hasDot && (
                  <span
                    className="dot"
                    style={{ backgroundColor: isSelected ? "rgba(255,255,255,0.8)" : dotColor }}
                  />
                )}
                {party.name}
              </button>
            );
          })}
        </div>
        <MascotImage pose="greeting" size={78} className="onboarding-step__mascot" />
      </section>

      <section className="onboarding-step onboarding-step--category">
        <div className="onboarding-step__head">
          <NumberBadge n={3} />
          <h2>
            関心のあるテーマを教えてください
          </h2>
          <span>
            （複数可）
          </span>
        </div>
        <div className="chip-grid chip-grid--categories">
          {CATEGORY_OPTIONS.map((category, index) => {
            const isSelected = interestedCategoryIds.includes(category.id);
            const Icon = CATEGORY_ICONS[index % CATEGORY_ICONS.length];
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => toggleCategory(category.id)}
                className="chip-button onboarding-chip"
                style={{
                  borderColor: isSelected
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                  backgroundColor: isSelected
                    ? "var(--color-brand-primary)"
                    : "transparent",
                  color: isSelected ? "#ffffff" : "var(--color-text-primary)",
                }}
              >
                <Icon size={14} />
                {category.name}
              </button>
            );
          })}
        </div>
      </section>

      <div className="privacy-note">
        <LockKeyhole size={20} />
        <p>
          回答は端末内に保存され、表示内容の調整に使われます。また、サービス改善のため、個人を特定できない匿名の集計データとして利用する場合があります。
          <Link
            href="/about"
            className="privacy-note__link"
          >
            このアプリの考え方を見る
          </Link>
        </p>
      </div>

      <div className="onboarding-actions">
        <button
          type="button"
          onClick={handleSkip}
          className="onboarding-actions__skip"
        >
          今はスキップする
        </button>
        <Button variant="primary" size="md" onClick={handleComplete} className="onboarding-actions__next">
          次へ
        </Button>
      </div>
    </div>
  );
}
