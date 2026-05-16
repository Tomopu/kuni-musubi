import { getPartyColor } from "@/lib/constants/party-colors";

type Size = "sm" | "md" | "lg";

type PartyBadgeProps = {
  partyId: string;
  shortName: string;
  size?: Size;
  colorHex?: string;
};

const sizeClasses: Record<Size, string> = {
  sm: "text-xs px-2 py-0.5 rounded-full",
  md: "text-sm px-2.5 py-1 rounded-full",
  lg: "text-base px-3 py-1.5 rounded-full",
};

// 政党カラー背景の丸バッジ（略称表示）
export function PartyBadge({
  partyId,
  shortName,
  size = "md",
  colorHex,
}: PartyBadgeProps) {
  // colorHex が渡された場合はそれを優先し、なければ PARTY_COLORS から取得する
  const color = colorHex ?? getPartyColor(partyId);

  return (
    <span
      className={`inline-block font-medium text-white ${sizeClasses[size]}`}
      style={{ backgroundColor: color }}
    >
      {shortName}
    </span>
  );
}
