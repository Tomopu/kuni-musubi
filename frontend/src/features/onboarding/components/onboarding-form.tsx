"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
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
import {
  getPreferences,
  savePreferences,
  SKIPPED_INTEREST_CATEGORY_ID,
} from "@/lib/storage/preferences-storage";
import {
  AGE_GROUP_OPTIONS,
  PARTY_OPTIONS,
  CATEGORY_OPTIONS,
} from "@/lib/constants/parties";
import { getPartyColor } from "@/lib/constants/party-colors";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";
import { Button } from "@/components/ui/button";

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
    colorHex: getPartyColor(party.id),
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
    const prefs = getPreferences();
    setAgeGroup(prefs.ageGroup);
    setSupportedPartyId(prefs.supportedPartyId);
    setInterestedCategoryIds(
      prefs.interestedCategoryIds.filter((id) => id !== SKIPPED_INTEREST_CATEGORY_ID),
    );
  }, []);

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
      ageGroup: ageGroup ?? "no_answer",
      supportedPartyId: supportedPartyId ?? "unknown",
      interestedCategoryIds:
        interestedCategoryIds.length > 0
          ? interestedCategoryIds
          : [SKIPPED_INTEREST_CATEGORY_ID],
      onboardingCompleted: true,
    });

    router.push("/");
  };

  // 2. スキップしてホームへ遷移する
  const handleSkip = () => {
    savePreferences({
      ageGroup: "no_answer",
      supportedPartyId: "unknown",
      interestedCategoryIds: [SKIPPED_INTEREST_CATEGORY_ID],
      onboardingCompleted: true,
    });
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
        <Image
          src="/assets/mascot/mascot-think.png"
          alt=""
          width={86}
          height={86}
          className="onboarding-step__mascot"
          aria-hidden="true"
        />
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
                className={`chip-button onboarding-chip ${
                  party.name.length >= 12 ? "onboarding-chip--compact" : ""
                }`}
                style={{
                  borderColor: isSelected ? dotColor : "var(--color-border)",
                  backgroundColor: isSelected ? `${dotColor}14` : "#ffffff",
                  color: isSelected
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
                }}
              >
                {hasDot && (
                  <span
                    className="dot"
                    style={{ backgroundColor: dotColor }}
                  />
                )}
                {party.name}
              </button>
            );
          })}
        </div>
        <Image
          src="/assets/mascot/mascot-question.png"
          alt=""
          width={88}
          height={88}
          className="onboarding-step__mascot"
          aria-hidden="true"
        />
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
        <Image
          src="/assets/mascot/mascot-idea.png"
          alt=""
          width={86}
          height={86}
          className="onboarding-step__mascot"
          aria-hidden="true"
        />
      </section>

      <div className="privacy-note">
        <LockKeyhole size={20} />
        <p>
          回答は端末内に保存され、表示内容の調整に使われます。サーバーには送信されません。
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
