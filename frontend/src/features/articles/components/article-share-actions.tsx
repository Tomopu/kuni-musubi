"use client";

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { Check, Link as LinkIcon, MessageCircle, X } from "lucide-react";

type ArticleShareActionsProps = {
  title: string;
};

export function ArticleShareActions({ title }: ArticleShareActionsProps) {
  const [copied, setCopied] = useState(false);
  const [shareUrl, setShareUrl] = useState("");

  const shareText = useMemo(
    () => `${title} | Kuni-Musubi`,
    [title],
  );

  useEffect(() => {
    setShareUrl(window.location.href);
  }, []);

  const encodedUrl = encodeURIComponent(shareUrl);
  const encodedText = encodeURIComponent(shareText);
  const xShareUrl = `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`;
  const lineShareUrl = `https://social-plugins.line.me/lineit/share?url=${encodedUrl}`;

  const handleCopy = async () => {
    if (!shareUrl) return;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  };

  return (
    <section className="article-share-box" aria-label="記事をシェア">
      <Image
        src="/assets/decorations/deco-sparkle.png"
        alt=""
        width={54}
        height={54}
        className="article-share-box__sparkle"
        aria-hidden="true"
      />
      <p className="article-share-box__title">
        友だちにシェアして、一緒に政治の Good News をもっと身近に！
      </p>
      <div className="article-share-box__actions">
        <a
          href={xShareUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="article-share-button article-share-button--x"
        >
          <X size={24} />
          Xでシェア
        </a>
        <a
          href={lineShareUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="article-share-button article-share-button--line"
        >
          <MessageCircle size={26} />
          LINEで送る
        </a>
        <button
          type="button"
          onClick={handleCopy}
          className="article-share-button article-share-button--copy"
        >
          {copied ? <Check size={24} /> : <LinkIcon size={24} />}
          {copied ? "コピーしました" : "リンクをコピー"}
        </button>
      </div>
    </section>
  );
}
