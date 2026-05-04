import { readFileSync } from "fs";
import path from "path";

// マスコットポーズシート画像を docs/ から配信する
// process.cwd() は frontend/ を指す
export function GET() {
  try {
    const filePath = path.join(
      process.cwd(),
      "..",
      "docs",
      "product",
      "ui-designs",
      "images",
      "20260503_mascot_pose-sheet_v1.png",
    );
    const buffer = readFileSync(filePath);
    return new Response(buffer, {
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "public, max-age=86400, immutable",
      },
    });
  } catch {
    return new Response("Not found", { status: 404 });
  }
}
