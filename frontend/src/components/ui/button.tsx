import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "outline" | "ghost";
type Size = "sm" | "md" | "lg";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
};

const variantStyles: Record<Variant, string> = {
  primary:
    "text-white transition-colors duration-150 hover:opacity-90 active:opacity-80",
  outline:
    "bg-transparent border transition-colors duration-150 hover:bg-opacity-10 active:bg-opacity-20",
  ghost:
    "bg-transparent border-transparent transition-colors duration-150 hover:opacity-70",
};

const sizeStyles: Record<Size, string> = {
  sm: "text-sm px-3 py-1.5 rounded",
  md: "text-base px-4 py-2 rounded-md",
  lg: "text-lg px-6 py-3 rounded-lg",
};

// 汎用ボタンコンポーネント
export function Button({
  variant = "primary",
  size = "md",
  className = "",
  style,
  children,
  ...props
}: ButtonProps) {
  const variantStyle =
    variant === "primary"
      ? { backgroundColor: "var(--color-brand-primary)", color: "#ffffff" }
      : variant === "outline"
        ? {
            borderColor: "var(--color-brand-primary)",
            color: "var(--color-brand-primary)",
          }
        : { color: "var(--color-text-secondary)" };

  return (
    <button
      className={`inline-flex items-center justify-center font-medium cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      style={{ ...variantStyle, ...style }}
      {...props}
    >
      {children}
    </button>
  );
}
