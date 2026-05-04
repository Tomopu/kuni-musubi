"use client";

import { useState } from "react";
import { postArticleEvent } from "@/lib/api/analytics-api";

type HelpfulButtonProps = {
  articleId: string;
};

// 「参考になった」匿名フィードバックボタン（Client Component）
// 反応数は表示しない、送信後はメッセージのみ表示する
export function HelpfulButton({ articleId }: HelpfulButtonProps) {
  const [sent, setSent] = useState(false);

  const handleClick = async () => {
    if (sent) return;
    setSent(true);
    await postArticleEvent({
      event_type: "helpful_click",
      article_id: articleId,
      surface: "article_detail",
    });
  };

  if (sent) {
    return (
      <p className="text-sm" style={{ color: "var(--color-brand-primary)" }}>
        フィードバックをありがとうございます！
      </p>
    );
  }

  return (
    <div>
      <p
        className="text-sm mb-3"
        style={{ color: "var(--color-text-secondary)" }}
      >
        この記事は参考になりましたか？
      </p>
      <button
        type="button"
        onClick={handleClick}
        className="px-5 py-2 rounded-full text-sm border transition-colors duration-150 hover:opacity-80"
        style={{
          borderColor: "var(--color-brand-primary)",
          color: "var(--color-brand-primary)",
        }}
      >
        参考になった
      </button>
    </div>
  );
}
