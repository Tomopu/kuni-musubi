import type { Metadata } from "next";
import Image from "next/image";
import { Sparkles } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { SettingsForm } from "@/features/settings/components/settings-form";

export const metadata: Metadata = {
  title: "設定 | Kuni-Musubi",
};

// 設定画面（Server Component）
export default function SettingsPage() {
  return (
    <PageContainer className="settings-page">
      <div className="app-card onboarding-panel">
        <div className="onboarding-hero">
          <Image
            src="/assets/mascot/mascot-pencil.png"
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
              設定
            </p>
            <h1>Kuni-Musubi の設定</h1>
            <p>
              年代・支持政党・関心テーマをいつでも変更できます。
              ホームに表示するニュースの調整に使われます。
            </p>
          </div>
          <Image
            src="/assets/mascot/mascot-default.png"
            alt=""
            width={116}
            height={116}
            className="onboarding-hero__mascot"
            aria-hidden="true"
            priority
          />
        </div>

        <SettingsForm />
      </div>
    </PageContainer>
  );
}
