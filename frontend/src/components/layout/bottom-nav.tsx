"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = {
  href: string;
  label: string;
  icon: string;
};

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "ホーム", icon: "🏠" },
  { href: "/parties", label: "政党", icon: "🏛️" },
  { href: "/settings", label: "設定", icon: "⚙️" },
  { href: "/about", label: "このアプリについて", icon: "ℹ️" },
];

// ボトムタブバー（mobile/tablet のみ表示）
// lg:hidden で lg 以上では非表示にする
export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 border-t lg:hidden"
      style={{
        backgroundColor: "var(--color-bg-base)",
        borderColor: "var(--color-border)",
        height: "56px",
      }}
    >
      <ul className="h-full flex items-center justify-around">
        {NAV_ITEMS.map((item) => {
          // アクティブ判定: ホームは完全一致、それ以外は前方一致
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                className="flex flex-col items-center justify-center gap-0.5 py-1 w-full transition-colors duration-150"
                style={{
                  color: isActive
                    ? "var(--color-brand-primary)"
                    : "var(--color-text-secondary)",
                }}
              >
                <span className="text-xl leading-none" aria-hidden="true">
                  {item.icon}
                </span>
                <span className="text-xs">{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
