// ポーズシートのスプライト座標（推定値 / 画像幅≈1350px, セル≈150×165px）
// ヘッダー高さ≈35px, キャラクター中心 y≈95px (行内)
type Pose = "greeting" | "thumbsup" | "thinking";

const SHEET_W = 1350;
const COL_W = 150;
const ROW_HEADER_H = 35;
const CHAR_CENTER_Y_IN_CELL = 90;

const POSE_COL: Record<Pose, number> = {
  greeting: 0, // こんにちは!
  thumbsup: 2, // いいね!
  thinking: 4, // 考え中...
};

type MascotImageProps = {
  pose?: Pose;
  size?: number;
  className?: string;
};

export function MascotImage({ pose = "greeting", size = 90, className = "" }: MascotImageProps) {
  const col = POSE_COL[pose];

  // キャラクター中心座標 (シート内絶対値)
  const charCenterX = col * COL_W + COL_W / 2;
  const charCenterY = ROW_HEADER_H + CHAR_CENTER_Y_IN_CELL;

  // background-position: 表示ボックスの中央にキャラクター中心が来るよう計算
  const bgX = -(charCenterX - size / 2);
  const bgY = -(charCenterY - size / 2);

  return (
    <div
      role="img"
      aria-label="Kuni-Musubi キャラクター"
      className={`flex-shrink-0 ${className}`}
      style={{
        width: size,
        height: size,
        backgroundImage: "url('/api/mascot')",
        backgroundSize: `${SHEET_W}px auto`,
        backgroundPosition: `${bgX}px ${bgY}px`,
        backgroundRepeat: "no-repeat",
      }}
    />
  );
}
