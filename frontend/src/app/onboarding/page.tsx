import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { OnboardingForm } from "@/features/onboarding/components/onboarding-form";
import { MascotImage } from "@/components/ui/mascot-image";

export const metadata: Metadata = {
  title: "はじめに | Kuni-Musubi",
};

// 初回オンボーディング画面（Server Component）
export default function OnboardingPage() {
  return (
    <PageContainer>
      <div className="py-6 max-w-lg mx-auto">
        {/* ヒーローカード: テキスト左 + マスコット右 */}
        <div
          className="rounded-2xl px-6 py-6 flex items-center gap-4 mb-8"
          style={{ backgroundColor: "#FFF9E6" }}
        >
          <div className="flex-1 min-w-0">
            <h1
              className="text-xl font-bold mb-1.5"
              style={{ color: "var(--color-text-primary)" }}
            >
              Kuni-Musubi へようこそ！
            </h1>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--color-text-secondary)" }}
            >
              あなたに合ったニュースをお届けするために、いくつか教えてください。すべてスキップ可能です。
            </p>
          </div>
          <MascotImage pose="greeting" size={96} />
        </div>

        <OnboardingForm />
      </div>
    </PageContainer>
  );
}
