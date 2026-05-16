import type { CSSProperties, ReactNode } from "react";

type PageContainerProps = {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
};

export function PageContainer({ children, className = "", style }: PageContainerProps) {
  return (
    <div className={`app-shell ${className}`} style={style}>
      {children}
    </div>
  );
}
