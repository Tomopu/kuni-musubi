"use client";

import { useState } from "react";
import Image from "next/image";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { postArticleEvent } from "@/lib/api/analytics-api";

type HelpfulButtonProps = {
  articleId: string;
};

// 「参考になった」匿名フィードバックボタン（Client Component）
// 反応数は表示しない、送信後はメッセージのみ表示する
export function HelpfulButton({ articleId }: HelpfulButtonProps) {
  const [sent, setSent] = useState<"helpful" | "unhelpful" | null>(null);

  const handleClick = async (reaction: "helpful" | "unhelpful") => {
    if (sent) return;
    setSent(reaction);
    await postArticleEvent({
      event_type: reaction === "helpful" ? "helpful_click" : "unhelpful_click",
      article_id: articleId,
      surface: "article_detail",
    });
  };

  return (
    <div className="article-feedback-card">
      <div className="article-feedback-card__head">
        <p>
          この記事は参考になりましたか？
          <span>(反応は公開されません)</span>
        </p>
        <Image
          src="/assets/mascot/mascot-cheer.png"
          alt=""
          width={118}
          height={118}
          className="article-feedback-card__mascot"
          aria-hidden="true"
        />
      </div>
      {sent && (
        <p className="article-feedback-card__thanks">
          フィードバックをありがとうございます！
        </p>
      )}
      <div className="article-feedback-card__actions">
        <button
          type="button"
          onClick={() => handleClick("helpful")}
          disabled={sent !== null}
          className="article-feedback-button article-feedback-button--good"
        >
          <ThumbsUp size={23} />
          参考になった
        </button>
        <button
          type="button"
          onClick={() => handleClick("unhelpful")}
          disabled={sent !== null}
          className="article-feedback-button article-feedback-button--bad"
        >
          <ThumbsDown size={23} />
          そう思わなかった
        </button>
      </div>
    </div>
  );
}
