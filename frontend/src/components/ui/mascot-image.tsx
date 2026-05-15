type Pose =
  | "greeting"
  | "thumbsup"
  | "thinking"
  | "megaphone"
  | "search"
  | "important";

const SHEET_W = 1536;

const POSE_CROPS: Record<Pose, { x: number; y: number; size: number }> = {
  greeting: { x: 21, y: 50, size: 150 },
  thumbsup: { x: 404, y: 50, size: 150 },
  thinking: { x: 789, y: 50, size: 150 },
  megaphone: { x: 21, y: 306, size: 150 },
  search: { x: 596, y: 306, size: 150 },
  important: { x: 1365, y: 306, size: 150 },
};

type MascotImageProps = {
  pose?: Pose;
  size?: number;
  className?: string;
};

export function MascotImage({ pose = "greeting", size = 90, className = "" }: MascotImageProps) {
  const crop = POSE_CROPS[pose];

  const scale = size / crop.size;
  const sheetScale = SHEET_W * scale;
  const bgX = -(crop.x * scale);
  const bgY = -(crop.y * scale);

  return (
    <div
      role="img"
      aria-label="Kuni-Musubi キャラクター"
      className={`mascot-image ${className}`}
      style={{
        width: size,
        height: size,
        backgroundImage: "url('/assets/mascot/pose-sheet.png')",
        backgroundSize: `${sheetScale}px auto`,
        backgroundPosition: `${bgX}px ${bgY}px`,
      }}
    />
  );
}
