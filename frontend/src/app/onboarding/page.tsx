import type { Metadata } from "next";
import { Sparkles } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { OnboardingForm } from "@/features/onboarding/components/onboarding-form";
import { MascotImage } from "@/components/ui/mascot-image";

export const metadata: Metadata = {
  title: "はじめに | Kuni-Musubi",
};

// 初回オンボーディング画面（Server Component）
export default function OnboardingPage() {
  return (
    <PageContainer className="onboarding-page">
      <div className="app-card onboarding-panel">
        <div className="onboarding-hero">
          <MascotImage pose="greeting" size={106} className="hidden sm:block" />
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
          <MascotImage pose="thumbsup" size={104} />
        </div>

        <OnboardingForm />
      </div>
    </PageContainer>
  );
}
