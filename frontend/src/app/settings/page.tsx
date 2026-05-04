import type { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { SettingsForm } from "@/features/settings/components/settings-form";
import { MascotImage } from "@/components/ui/mascot-image";

export const metadata: Metadata = {
  title: "設定 | Kuni-Musubi",
};

// 設定画面（Server Component）
export default function SettingsPage() {
  return (
    <PageContainer>
      <div className="py-8 max-w-lg mx-auto">
        {/* ヘッダー: タイトル左 + マスコット右 */}
        <div className="flex items-start justify-between gap-4 mb-8">
          <div>
            <h1
              className="text-2xl font-bold mb-1"
              style={{ color: "var(--color-text-primary)" }}
            >
              設定
            </h1>
            <p
              className="text-sm"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Kuni-Musubi の設定をいつでも変更できます。
            </p>
          </div>
          <MascotImage pose="greeting" size={80} />
        </div>

        <SettingsForm />
      </div>
    </PageContainer>
  );
}
