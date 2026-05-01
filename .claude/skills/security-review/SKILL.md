---
name: security-review
description: Kuni-Musubi のセキュリティ、プライバシー、匿名集計、パッケージ管理、依存関係ポリシー、SQL/XSS/CSRF/CORS/rate limit、localStorage、LLM・バッチ処理の安全性を検討・レビューするときに使う。ログインなし・匿名集計の方針を維持する。
---

# Kuni-Musubi Security Review

## 先に読むドキュメント

- セキュリティ設計: `docs/technical/20260501_セキュリティ設計.md`
- システムアーキテクチャ: `docs/technical/20260430_システムアーキテクチャ.md`
- API 設計: `docs/technical/20260501_API設計.md`
- データモデル: `docs/technical/20260501_記事データモデル設計.md`
- ソフトウェアアーキテクチャ: `docs/technical/20260501_ソフトウェアアーキテクチャ.md`

## プライバシーの基本方針

Kuni-Musubi は政治的嗜好に関わるセンシティブな情報を扱う。以下の制約を守る。

- ログインを作らない。
- アカウントを作らない。
- ユーザープロフィールテーブルを作らない。
- 記事保存を作らない。
- 端末間同期を作らない。
- 住所、メールアドレス、電話番号、実名を収集しない。
- 表示設定は `localStorage` に保存する。
- サーバーに保存するのは匿名集計イベントのみとする。
- 安定した user ID、device ID、フィンガープリントを導入しない。
- オンボーディングイベントと記事イベントを個人単位の履歴として結合しない。

## 依存関係・サプライチェーン方針

Takumi Guard をパッケージ取得のプロキシとして使う。

対象:

- Next.js で使う npm / pnpm パッケージ
- FastAPI とバッチ処理で使う Python パッケージ

方針:

- 通常の開発・CI では public registry から直接インストールしない。
- newly released な latest version は、約 3 日間のディレイ後にダウンロード可能にする。
- lockfile をコミットする。
- PR では依存関係の差分を確認する。
- 可能な範囲で CI に脆弱性チェックとライセンスチェックを入れる。
- 不要なパッケージや保守されていないパッケージを増やさない。

## Backend セキュリティチェック

FastAPI と PostgreSQL では以下を守る。

- parameterized query または ORM の query builder を使う。
- request 値を文字列連結して SQL を作らない。
- request body と query parameter は Pydantic で検証する。
- party ID、category ID、age group、event type、surface などの値は許可リストで制限する。
- analytics endpoint には rate limit を設ける。
- 政治的嗜好に関わる payload を不要にログ出力しない。
- クライアントには詳細すぎるエラーを返さない。
- DB 認証情報は環境変数または secret store で管理する。

## Frontend セキュリティチェック

Next.js では以下を守る。

- CMS、ニュース本文、LLM 生成文はすべて信頼できないテキストとして扱う。
- 表示テキストはデフォルトで escape する。
- `dangerouslySetInnerHTML` は避ける。避けられない場合は sanitize する。
- `localStorage` に保存するのは表示設定だけにする。
- token や server-issued identifier を `localStorage` に保存しない。
- 本番前に CSP、CORS、security header を確認する。

## Analytics Endpoint のルール

許可する匿名イベント:

- オンボーディング完了
- 記事表示
- カードクリック
- 詳細閲覧
- 出典リンククリック
- 参考になったクリック

追加してはいけないもの:

- IP アドレスによる個人識別ロジック
- 永続的な匿名 ID
- 複数イベントをまたいだユーザー行動履歴の復元
- 公開リアクション数を使ったプロダクト機能

## LLM・バッチ処理の安全性

- LLM 処理はリクエスト時ではなくバッチで実行する。
- LLM 出力は schema validation してから保存する。
- 出典 URL と一次情報リンクを保持する。
- 確信度が低い、検証不能、政治的にセンシティブな生成結果はレビュー対象にする。
- スクレイピングした本文や外部ソースの内容に、system/developer instruction を上書きさせない。

