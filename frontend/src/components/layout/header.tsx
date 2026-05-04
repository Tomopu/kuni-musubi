import Link from "next/link";

// ヘッダーコンポーネント
// 全 viewport: ロゴ（左）+ ℹ️⚙️ アイコン（右）
// lg 以上: アイコンに加えてホーム・政党のテキストリンクも表示（ボトムナブがないため）
export function Header() {
  return (
    <header
      className="sticky top-0 z-40 border-b"
      style={{
        backgroundColor: "var(--color-bg-base)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* ロゴ */}
        <Link
          href="/"
          className="font-bold text-lg transition-opacity duration-150 hover:opacity-70"
          style={{ color: "var(--color-brand-primary)" }}
        >
          Kuni-Musubi
        </Link>

        {/* 右側ナビ */}
        <div className="flex items-center gap-1">
          {/* デスクトップのみ: ホーム・政党テキストリンク（ボトムナブが lg:hidden のため） */}
          <nav className="hidden lg:flex items-center gap-4 mr-2">
            <Link
              href="/"
              className="text-sm font-medium transition-opacity duration-150 hover:opacity-70"
              style={{ color: "var(--color-text-primary)" }}
            >
              ホーム
            </Link>
            <Link
              href="/parties"
              className="text-sm font-medium transition-opacity duration-150 hover:opacity-70"
              style={{ color: "var(--color-text-primary)" }}
            >
              政党
            </Link>
          </nav>

          {/* 全 viewport: このアプリについて */}
          <Link
            href="/about"
            aria-label="このアプリについて"
            className="w-9 h-9 flex items-center justify-center rounded-lg text-base transition-opacity duration-150 hover:opacity-70"
            style={{ color: "var(--color-text-secondary)" }}
          >
            ℹ️
          </Link>

          {/* 全 viewport: 設定 */}
          <Link
            href="/settings"
            aria-label="設定"
            className="w-9 h-9 flex items-center justify-center rounded-lg text-base transition-opacity duration-150 hover:opacity-70"
            style={{ color: "var(--color-text-secondary)" }}
          >
            ⚙️
          </Link>
        </div>
      </div>
    </header>
  );
}
