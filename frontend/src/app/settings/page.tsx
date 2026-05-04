import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { SettingsForm } from "@/features/settings/components/settings-form";

export const metadata: Metadata = {
  title: "設定 | Kuni-Musubi",
};

// 設定画面（Server Component）
// フォーム本体は SettingsForm（Client Component）に委譲する
export default function SettingsPage() {
  return (
    <PageContainer>
      <div className="py-8 max-w-lg mx-auto">
        <h1
          className="text-2xl font-bold mb-1"
          style={{ color: "var(--color-text-primary)" }}
        >
          設定
        </h1>
        <p
          className="text-sm mb-8"
          style={{ color: "var(--color-text-secondary)" }}
        >
          Kuni-Musubi の設定をいつでも変更できます。
        </p>
        <SettingsForm />
      </div>
    </PageContainer>
  );
}
