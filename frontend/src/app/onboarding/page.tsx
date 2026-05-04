import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { OnboardingForm } from "@/features/onboarding/components/onboarding-form";

export const metadata: Metadata = {
  title: "はじめに | Kuni-Musubi",
};

// 初回オンボーディング画面（Server Component）
// フォーム本体は OnboardingForm（Client Component）に委譲する
export default function OnboardingPage() {
  return (
    <PageContainer>
      <div className="py-8 max-w-lg mx-auto">
        <div className="text-center mb-8">
          <div className="text-4xl mb-3">🌱</div>
          <h1
            className="text-2xl font-bold mb-2"
            style={{ color: "var(--color-text-primary)" }}
          >
            Kuni-Musubi へようこそ
          </h1>
          <p
            className="text-sm leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            あなたに合ったニュースをお届けするために、いくつか教えてください。
            <br />
            すべてスキップ可能です。
          </p>
        </div>

        <OnboardingForm />
      </div>
    </PageContainer>
  );
}
