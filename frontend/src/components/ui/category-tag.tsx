type CategoryTagProps = {
  name: string;
};

// カテゴリ名のグレー背景タグ
export function CategoryTag({ name }: CategoryTagProps) {
  return (
    <span
      className="inline-block text-xs px-2 py-0.5 rounded"
      style={{
        backgroundColor: "var(--color-bg-muted)",
        color: "var(--color-text-secondary)",
      }}
    >
      {name}
    </span>
  );
}
