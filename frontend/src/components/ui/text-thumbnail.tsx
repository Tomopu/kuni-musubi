type TextThumbnailProps = {
  partyColor: string;
  categoryName?: string;
  className?: string;
};

// テキストベースのサムネイル表示
// MVP では実写写真なし。政党カラー背景 + カテゴリ名テキストで表示する
export function TextThumbnail({
  partyColor,
  categoryName,
  className = "",
}: TextThumbnailProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-lg ${className}`}
      style={{ backgroundColor: partyColor }}
      aria-hidden="true"
    >
      {categoryName && (
        <span className="text-white text-sm font-medium px-2 text-center leading-tight">
          {categoryName}
        </span>
      )}
    </div>
  );
}
