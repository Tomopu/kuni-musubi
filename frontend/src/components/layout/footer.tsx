import Link from "next/link";

export function Footer() {
  return (
    <footer className="app-footer">
      <div className="app-footer__inner">
        <div>
          <p className="app-footer__brand">Kuni-Musubi</p>
          <p className="app-footer__copy">
            政治や社会の「いいニュース」を、わかりやすく届けます。
          </p>
        </div>
        <nav className="app-footer__nav" aria-label="フッター">
          <Link href="/">ホーム</Link>
          <Link href="/parties">政党一覧</Link>
          <Link href="/about">このアプリについて</Link>
          <Link href="/settings">設定</Link>
        </nav>
      </div>
      <p className="app-footer__copyright">© 2026 Kuni-Musubi</p>
    </footer>
  );
}
