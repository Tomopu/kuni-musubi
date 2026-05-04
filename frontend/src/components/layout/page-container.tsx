import type { ReactNode } from "react";

type PageContainerProps = {
  children: ReactNode;
  className?: string;
};

// ページコンテナ: max-w-4xl mx-auto のレイアウト制約
// lg 以上ではボトムナビがないため pb を小さく設定する
export function PageContainer({ children, className = "" }: PageContainerProps) {
  return (
    <div className={`max-w-4xl mx-auto px-4 pb-16 lg:pb-4 ${className}`}>
      {children}
    </div>
  );
}
