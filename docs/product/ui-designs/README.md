# UI Design References

このディレクトリは、GPT images などで作成した PNG の UI デザイン参照を置く場所です。
UI Designer サブエージェントは、UI 実装・レビュー時にこのディレクトリの画像と注釈を判断材料として使います。

## ディレクトリ構造

```txt
docs/product/ui-designs/
  README.md
  images/
    20260503_tablet_onboarding-home-selected-home-unset_v1.png
    20260503_tablet_article-detail-parties-party-detail_v1.png
    20260503_tablet_settings-about_v1.png
    20260503_mascot_pose-sheet_v1.png
  notes/
    20260503_tablet_onboarding-home-selected-home-unset_v1.md
    20260503_tablet_article-detail-parties-party-detail_v1.md
    20260503_tablet_settings-about_v1.md
    20260503_mascot_pose-sheet_v1.md
```

## ファイル名ルール

```txt
YYYYMMDD_{viewport}_{left-screen}-{center-screen}-{right-screen}_vN.png
```

例:

```txt
20260503_tablet_onboarding-home-selected-home-unset_v1.png
20260503_tablet_article-detail-parties-party-detail_v1.png
20260503_tablet_settings-about_v1.png
20260503_mascot_pose-sheet_v1.png
```

ルール:

- `YYYYMMDD` は作成日または採用判断日。
- `viewport` は `mobile`、`tablet`、`desktop` のいずれかを基本にする。
- 1枚に複数画面が含まれる場合は、左から右の順で画面名を書く。
- 画面名は英小文字とハイフンで書く。
- 改訂版は `_v2`、`_v3` のように上げる。
- 採用しない案は削除せず、注釈側に `status: rejected` または `status: archived` と書く。
- 画面ではなくマスコット、アイコン、イラストなどの素材参照は、`YYYYMMDD_{asset-type}_{description}_vN.png` の形式にする。

## 画面名

MVP では以下を基本名にします。

- `onboarding`
- `home`
- `settings`
- `article-detail`
- `parties`
- `party-detail`
- `about`

必要に応じて状態名を付けます。

- `home-empty`
- `home-loading`
- `home-filtered`
- `home-selected`
- `home-unset`
- `article-detail-error`
- `settings-updated`

## 今回の画像の命名案

添付された UI デザインはスマートフォン単体というより、タブレット幅の UI カンプとして扱います。
保存する場合は、以下の名前を推奨します。

```txt
images/20260503_tablet_onboarding-home-selected-home-unset_v1.png
notes/20260503_tablet_onboarding-home-selected-home-unset_v1.md

images/20260503_tablet_article-detail-parties-party-detail_v1.png
notes/20260503_tablet_article-detail-parties-party-detail_v1.md

images/20260503_tablet_settings-about_v1.png
notes/20260503_tablet_settings-about_v1.md

images/20260503_mascot_pose-sheet_v1.png
notes/20260503_mascot_pose-sheet_v1.md
```

対応関係:

- `20260503_tablet_onboarding-home-selected-home-unset_v1.png`
  - left: onboarding
  - center: home-selected
  - right: home-unset
- `20260503_tablet_article-detail-parties-party-detail_v1.png`
  - left: article-detail
  - center: parties
  - right: party-detail
- `20260503_tablet_settings-about_v1.png`
  - left: settings
  - right: about
- `20260503_mascot_pose-sheet_v1.png`
  - mascot pose and expression reference

## レスポンシブ展開

タブレット UI カンプは基準デザインとして扱いますが、実装時は以下の viewport も考慮します。

- `mobile`: 1カラムを基本にし、タグ、カード、ボタン、補助情報を折り返しまたは縦積みにする。
- `tablet`: 添付カンプの情報階層、余白、カード密度、文言の温度感を基準にする。
- `desktop`: コンテンツ幅を広げすぎず、必要に応じて2カラム化や補助情報のサイド配置を検討する。

UI Designer サブエージェントは、タブレットカンプをそのまま固定幅で再現するのではなく、スマートフォンとPCでも自然に使えるレスポンシブ UI として判断します。

## 注釈ファイル

PNG と同じ basename の Markdown を `notes/` に置きます。
画像だけでは Claude が意図を読み違えることがあるため、1枚に複数画面が含まれる場合は必ず注釈を付けます。

```markdown
---
status: accepted
priority: primary
image: ../images/20260503_tablet_onboarding-home-selected-home-unset_v1.png
viewport: tablet
source: GPT images
created_at: 2026-05-03
---

# 20260503 tablet onboarding / home-selected / home-unset v1

## 対象画面

- left: onboarding
- center: home-selected
- right: home-unset

## 採用したい意図

- 政治情報の重さを下げる、落ち着いた第一印象。
- 記事カードの情報量を各 viewport で読みやすく抑える。
- タブレットカンプの情報階層を保ちながら、スマートフォンとPCにも自然に展開する。

## 実装時に守ること

- 画像の雰囲気、情報階層、余白、カード密度を優先する。
- 文言はそのまま採用せず、既存 docs とプライバシー方針に合わせて調整する。
- 公開いいね、公開カウント、人気ランキングに見える UI は作らない。

## 未確定・要確認

- カテゴリタグの最大表示数。
- 記事カードのサムネイルを使うかどうか。
```

## UI Designer への期待

UI Designer サブエージェントは、画像をそのまま模写するのではなく、以下を判断します。

- 既存の product docs と矛盾しないか。
- 政党広告やプロパガンダのように見えないか。
- スマートフォン、タブレット、PC の各 viewport で読みやすいか。
- 匿名集計・ログインなし方針を壊していないか。
- Next.js の責務分割に沿って実装できるか。
- アクセシビリティ上の問題がないか。

画像と既存ドキュメントが矛盾する場合は、矛盾点を明示したうえで、推奨判断を報告します。
