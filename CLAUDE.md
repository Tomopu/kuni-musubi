# Repository Guidelines

このファイルは、Claude Code が Kuni-Musubi リポジトリで作業するときに必ず参照する開発・運用ルールである。

## 必須ルール

### 既存変更を壊さない

- ユーザーが行った未コミット変更を勝手に戻さない。
- 変更前に関連ファイルを読み、既存の文体・設計・命名に合わせる。
- 目的外のリファクタリングやフォーマット変更を混ぜない。
- 破壊的な Git 操作を行わない。

### ドキュメント駆動で進める

Kuni-Musubi は、まずプロダクト・調査・技術設計を文書化してから実装する。

実装判断に迷った場合は、先に `docs/` 配下の設計を確認する。設計が存在しない、または古い場合は、実装前にドキュメントを追加・更新する。

### センシティブな政治情報を慎重に扱う

Kuni-Musubi は、支持政党や政治的関心に関わる情報を扱う。以下を守る。

- ログインを作らない。
- アカウントを作らない。
- ユーザープロフィールテーブルを作らない。
- 記事保存を作らない。
- 端末間同期を作らない。
- 氏名、メールアドレス、電話番号、住所を収集しない。
- 表示設定は `localStorage` に保存する。
- DB に保存するのは匿名集計イベントのみとする。
- オンボーディングイベントと記事イベントを user ID で結合しない。
- 永続的な匿名 ID、device ID、フィンガープリントを導入しない。

## プロダクト方針

Kuni-Musubi は、各政党の建設的・ポジティブな政治ニュースを届けるプロダクトである。

主な対象は、政治に詳しくなく、SNS で政府や政治への批判的なニュースばかりを見てしまい、政府への信頼感や日本への誇りを持ちにくくなっている若年層である。

重要な UX 方針:

- 政治情報の重さを下げる。
- プロパガンダや政党広告のように見える表現を避ける。
- ポジティブな見せ方と、残る課題・出典リンクの提示を両立する。
- コメント欄は作らない。
- 公開いいね、公開カウント、人気ランキングは作らない。
- `参考になった` は非公開の匿名フィードバックとして扱う。
- MVP では高度な推薦機能を重視しない。

## 重要ドキュメント

作業前に、必要な範囲で以下を確認する。

- プロダクト概要: `docs/product/20260428_プロダクト概要.md`
- ペルソナ: `docs/product/20260429_ペルソナ設定.md`
- 画面設計: `docs/product/20260430_画面設計.md`
- 記事カード設計: `docs/product/20260430_記事カード表示設計.md`
- 記事詳細設計: `docs/product/20260430_記事詳細画面表示設計.md`
- システムアーキテクチャ: `docs/technical/20260430_システムアーキテクチャ.md`
- ソフトウェアアーキテクチャ: `docs/technical/20260501_ソフトウェアアーキテクチャ.md`
- 記事データモデル: `docs/technical/20260501_記事データモデル設計.md`
- API 設計: `docs/technical/20260501_API設計.md`
- LLM 出力スキーマ: `docs/technical/20260501_LLM出力スキーマ設計.md`
- セキュリティ設計: `docs/technical/20260501_セキュリティ設計.md`

各ディレクトリの一覧は以下を参照する。

- `docs/product/README.md`
- `docs/research/README.md`
- `docs/technical/README.md`

## Project Structure

MVP の基本構成は以下とする。

```txt
frontend/   Next.js / TypeScript
backend/    FastAPI / Python
batch/      Python batch workers
docs/       Product, research, and technical documents
.claude/    Claude Code skills and settings
```

### Frontend

Next.js App Router と feature-based architecture を採用する。

```txt
frontend/
  src/
    app/
      onboarding/
      articles/
        [articleId]/
      parties/
        [partyId]/
      settings/
      about/
    features/
      onboarding/
      articles/
      parties/
      settings/
      analytics/
    components/
      ui/
      layout/
    lib/
      api/
      storage/
      constants/
      utils/
```

ルール:

- `app/` は page、layout、metadata、routing を担当する。
- 画面固有の UI・hooks・状態管理は `features/` に置く。
- 汎用 UI は `components/ui/`、レイアウト部品は `components/layout/` に置く。
- API client は `lib/api/` に閉じ込める。
- `localStorage` の読み書きは `lib/storage/` に閉じ込める。
- UI コンポーネントに API fetch や `localStorage` 操作を直接書かない。

### Backend

FastAPI は薄い layered architecture + usecase 構成にする。

```txt
backend/
  app/
    main.py
    api/
    usecases/
    domain/
    infrastructure/
      db/
        session.py
        models.py
        repositories/
    schemas/
```

依存方向:

```txt
api -> usecases -> infrastructure/db/repositories
          |
          v
        domain
```

ルール:

- `api/` は request / response と HTTP status code を扱い、usecase を呼ぶ。
- `api/` から repository を直接呼ばない。
- `usecases/` はアプリケーションの処理手順を置く。
- `domain/` は Kuni-Musubi 固有の概念やルールを置く。
- `infrastructure/` は DB、Repository、外部 API client など技術的詳細を置く。
- `schemas/` は Pydantic schema を置く。
- LLM 処理を API request 時に実行しない。

### Batch

Python batch workers は、記事収集・分類・要約・表示文生成・集計を担当する。

```txt
batch/
  pipelines/
  steps/
  llm/
    prompts/
    schemas/
  scrapers/
```

ルール:

- LLM はバッチで実行し、結果を DB に保存する。
- LLM 出力は schema validation してから保存する。
- 出典 URL と一次情報リンクを保持する。
- 低確信度、検証不能、政治的にセンシティブな生成結果はレビュー対象にする。

## MVP 画面

MVP の画面は以下の 7 つとする。

1. 初回オンボーディング
2. ホーム
3. 設定
4. 記事詳細
5. 政党一覧
6. 政党詳細
7. このアプリについて

新しい画面は、ユーザーが明示的に求めた場合、または画面遷移が明確に簡潔になる場合のみ追加する。

## API 方針

MVP で想定する API:

- `GET /articles`
- `GET /articles/{article_id}`
- `GET /parties`
- `GET /parties/{party_id}`
- `GET /policy-categories`
- `POST /analytics/onboarding`
- `POST /analytics/article-event`

ルール:

- MVP では推薦専用 API を作らない。
- 記事表示は `GET /articles` の政党・カテゴリ絞り込みと新着順/重要順で対応する。
- analytics API は個人識別ではなく匿名集計を目的とする。
- `helpful_click` は非公開の匿名イベントとして扱う。

## セキュリティ

### 入力検証

- request body と query parameter は Pydantic で検証する。
- `party_id`, `category_ids`, `sort`, `limit`, `cursor`, `age_group`, `event_type`, `surface` は allowlist や上限で制限する。
- SQL は文字列連結で組み立てない。
- ORM または parameterized query を使う。

### XSS

- 外部サイト由来のテキストや LLM 出力は信頼しない。
- `dangerouslySetInnerHTML` は原則使わない。
- Markdown や HTML を表示する場合は sanitize する。
- URL は scheme allowlist で検証し、`javascript:` URL を禁止する。

### CORS / CSRF / Rate Limit

- 本番 CORS は Kuni-Musubi の frontend domain に限定する。
- `POST /analytics/*` には rate limit を設ける。
- 不正な payload は Pydantic で拒否する。
- 異常な連続投稿を検知できるようにする。

### 依存関係

Takumi Guard を npm / pnpm / pip / uv のパッケージ取得プロキシとして使う方針とする。

- public registry から直接インストールしない。
- latest version は約 3 日間のディレイ後に取得可能にする。
- lockfile をコミットする。
- CI では lockfile を尊重する。
- 不要な依存を増やさない。
- 依存追加時は必要性、保守状況、ライセンス、脆弱性を確認する。

## Coding Style

### 共通

- 既存の命名規則に合わせる。
- 不要な抽象化を追加しない。
- まず小さく実装し、複雑さが必要になった時点で分割する。
- コメントは、意図や制約がコードだけでは読み取りにくい場合に限って書く。

### TypeScript / React

- ファイル名は kebab-case を基本とする。
- React component は PascalCase。
- hooks は `useXxx`。
- 関数・変数は camelCase。
- 型は PascalCase。
- Server Components を基本とし、状態管理やイベント処理が必要な場合のみ Client Component にする。
- Client Component には必要なファイルだけ `"use client"` を付ける。

### Python

- ファイル名は snake_case。
- 関数・変数は snake_case。
- クラスは PascalCase。
- Pydantic schema は API 入出力の境界で使う。
- DB model と API schema を混同しない。

### Database

- テーブル名は snake_case の複数形。
- カラム名は snake_case。
- ID は原則として UUID を使う。
- 個人識別に使える ID を analytics に導入しない。

## Testing

実装を変更した場合は、影響範囲に応じてテストを追加・実行する。

優先してテストする領域:

- 記事カード・記事詳細の表示ロジック
- localStorage の保存・読込
- API client
- FastAPI の request validation
- repository / usecase
- LLM 出力 schema validation
- analytics event の validation

PR 前または作業完了前に、利用可能な範囲で以下を実行する。

- frontend: lint, typecheck, test
- backend: lint, typecheck, test
- batch: schema validation test, unit test

まだスクリプトが存在しない場合は、実行できなかったことを明記する。

## Documentation Rules

### docs 更新

- `docs/product`, `docs/research`, `docs/technical` のいずれに属するかを判断して配置する。
- 新規ドキュメントを追加したら、該当 README を更新する。
- README の一覧は表ではなく箇条書きにする。
- README の一覧はファイル名の辞書順で並べる。
- 各リンクには、そのドキュメントが何をまとめたものかを 1 行で書く。

### 日付・作成者

ドキュメントには既存形式に合わせてメタ情報を付ける。

```txt
作成者：泉知成
作成日：YYYY年M月D日
更新日：YYYY年M月D日
```

### 方針変更

既存方針を変更する場合は、関連する複数ドキュメントの整合性を確認する。

例:

- 画面設計を変えたら、API 設計・データモデル・システムアーキテクチャへの影響を確認する。
- analytics を変えたら、セキュリティ設計・データモデル・API 設計への影響を確認する。
- LLM 出力を変えたら、記事詳細設計・LLM 出力スキーマ・DB 設計への影響を確認する。

## Claude Skills

`.claude/skills/` には、作業別の追加ルールを置く。

現在のスキル:

- `docs-writer`: docs 配下の作成・更新
- `product-design`: UX、画面設計、MVP スコープ判断
- `security-review`: セキュリティ、匿名集計、依存関係、localStorage、LLM safety

該当する作業では、関連する skill の `SKILL.md` も確認する。

## Git / PR 運用

### 作業開始

- 大きめの実装や複数ファイルにまたがる変更では、作業ブランチまたは worktree の利用を検討する。
- 小さな docs 修正は現在の作業ディレクトリで行ってよい。
- 作業前に `git status` で既存変更を確認する。

### ブランチ名

ブランチ名は、変更内容が一目で分かる短い kebab-case にする。

形式:

```txt
<type>/<short-description>
```

`type` は以下を基本とする。

- `docs`: ドキュメント追加・修正
- `feature`: 新機能
- `fix`: バグ修正
- `refactor`: 振る舞いを変えない整理
- `test`: テスト追加・修正
- `chore`: 設定、依存関係、CI、その他の保守
- `security`: セキュリティ対応

例:

```txt
docs/add-claude-guidelines
docs/update-screen-design
feature/article-card
feature/onboarding-flow
fix/article-event-validation
security/takumi-guard-policy
```

ルール:

- 英小文字、数字、ハイフン、スラッシュのみを使う。
- 日本語、スペース、アンダースコアは使わない。
- 説明部分は 2〜5 語程度に抑える。
- issue 番号がある場合は末尾に付ける。

例:

```txt
feature/article-detail-123
docs/update-api-design-45
```

### コミット

- コミットメッセージは短く具体的にする。
- 無関係な変更を同じコミットに混ぜない。
- 生成物、lockfile、migration などが必要な場合は関連する実装と一緒に扱う。

### PR

PR を作成する場合は、本文に以下を含める。

- 変更概要
- 変更理由
- 影響範囲
- 実行したテスト
- 実行できなかったテスト
- UI 変更がある場合はスクリーンショットまたは確認方法
- DB / schema / env / dependency 変更の有無

GitHub 上の PR 状態を確認してから push / PR 作成を行い、既に merged / closed の PR や古い branch に追加 push しない。

## 迷ったときの判断基準

以下の順で優先する。

1. ユーザーの明示的な指示
2. `docs/` に書かれたプロダクト・技術方針
3. この `CLAUDE.md`
4. 既存コードの近い実装パターン
5. 一般的なベストプラクティス

判断に迷う場合でも、個人識別、政治的嗜好の保存、公開リアクション、コメント欄、リアルタイム LLM 実行に関わる変更は勝手に導入しない。
