import Link from "next/link";
import Image from "next/image";
import { Info, Landmark, Settings } from "lucide-react";

export function Header() {
  return (
    <header className="app-header">
      <div className="app-header__inner">
        <Link href="/" className="app-logo" aria-label="Kuni-Musubi ホーム">
          <Image
            src="/assets/logo/kuni-musubi-logo.png"
            alt=""
            width={36}
            height={36}
            className="app-logo__image"
            priority
            aria-hidden="true"
          />
          <span>Kuni-Musubi</span>
        </Link>

        <nav className="app-header__nav" aria-label="メインナビゲーション">
          <Link href="/parties" aria-label="政党一覧">
            <Landmark size={18} />
            <span>政党</span>
          </Link>
          <Link href="/about" aria-label="このアプリについて">
            <Info size={20} />
          </Link>
          <Link href="/settings" aria-label="設定">
            <Settings size={20} />
          </Link>
        </nav>
      </div>
    </header>
  );
}
