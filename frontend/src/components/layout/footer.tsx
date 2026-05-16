import Link from "next/link";
import { SURVEY_URL } from "@/lib/constants/survey";

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
          <a
            href={SURVEY_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="app-footer__survey-link"
          >
            【お願い】利用者アンケートはこちら
          </a>
        </nav>
      </div>
      <p className="app-footer__copyright">© 2026 Kuni-Musubi</p>
    </footer>
  );
}
