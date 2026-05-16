"use client";

import Image from "next/image";
import { X } from "lucide-react";
import { SURVEY_URL } from "@/lib/constants/survey";
import {
  setSurveyTemporaryDismiss,
  setSurveyPermanentDismiss,
} from "@/lib/storage/survey";

type Props = {
  onClose: () => void;
};

export function SurveyPopup({ onClose }: Props) {
  function handleClose() {
    setSurveyTemporaryDismiss();
    onClose();
  }

  function handlePermanentDismiss() {
    setSurveyPermanentDismiss();
    onClose();
  }

  function handleSurveyClick() {
    // フォームを開いたら7日間は再表示しない
    setSurveyTemporaryDismiss();
  }

  return (
    <div
      className="survey-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="アンケートのお願い"
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
    >
      <div className="survey-popup">
        <button
          className="survey-popup__close"
          onClick={handleClose}
          aria-label="閉じる"
        >
          <X size={18} />
        </button>

        <Image
          src="/assets/mascot/mascot-data.png"
          alt=""
          width={100}
          height={100}
          className="survey-popup__mascot"
          aria-hidden="true"
        />

        <div className="survey-popup__head">
          <h2 className="survey-popup__title">
            よろしければ、<br />感想を聞かせてください！
          </h2>
          <Image
            src="/assets/decorations/deco-emphasis.png"
            alt=""
            width={32}
            height={42}
            className="survey-popup__deco"
            aria-hidden="true"
          />
        </div>

        <p className="survey-popup__body">
          Kuni-Musubi をより良いアプリにしていくため、2分ほどのアンケートにご協力いただけるとうれしいです。
        </p>

        <a
          href={SURVEY_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="survey-popup__btn-primary"
          onClick={handleSurveyClick}
        >
          アンケートに回答する
        </a>

        <button
          className="survey-popup__btn-dismiss"
          onClick={handlePermanentDismiss}
        >
          今後このお願いを表示しない
        </button>
      </div>
    </div>
  );
}
