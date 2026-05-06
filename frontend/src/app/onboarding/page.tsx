import type { Metadata } from "next";
import Image from "next/image";
import { Sparkles } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { OnboardingForm } from "@/features/onboarding/components/onboarding-form";

export const metadata: Metadata = {
  title: "はじめに | Kuni-Musubi",
};

// 初回オンボーディング画面（Server Component）
export default function OnboardingPage() {
  return (
    <PageContainer className="onboarding-page">
      <div className="app-card onboarding-panel">
        <div className="onboarding-hero">
          <Image
            src="/assets/mascot/mascot-default.png"
            alt=""
            width={118}
            height={118}
            className="hidden sm:block onboarding-hero__mascot"
            aria-hidden="true"
            priority
          />
          <div className="onboarding-hero__text">
            <p className="eyebrow">
              <Sparkles size={15} />
              はじめに
            </p>
            <h1>Kuni-Musubi へようこそ！</h1>
            <p>
              あなたに合ったニュースをお届けするために、いくつか質問にお答えください。
              すべてスキップ可能です。
            </p>
          </div>
          <Image
            src="/assets/mascot/mascot-cheer.png"
            alt=""
            width={116}
            height={116}
            className="onboarding-hero__mascot"
            aria-hidden="true"
            priority
          />
        </div>

        <OnboardingForm />
      </div>
    </PageContainer>
  );
}
