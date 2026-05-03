# 開発用 README

このドキュメントは、Kuni-Musubi を Claude Code の Docker サンドボックスで開発するための手順をまとめたものです。

## 目的

Claude Code をホスト環境で直接動かすのではなく、Dev Container 内で起動します。

これにより、Claude Code がアクセスできる範囲を作業ディレクトリ中心に限定し、ホスト側の `~/.ssh`、`~/.aws`、GitHub CLI 認証情報、Docker socket などへ直接触れない構成にします。

## 前提

- Docker Desktop
- VS Code、Cursor、または Dev Containers 対応 IDE
- Dev Containers 拡張機能

ターミナルだけで起動したい場合は、追加で Dev Containers CLI を使います。

```bash
npm install -g @devcontainers/cli
```

## 推奨: IDE から起動する

1. Docker Desktop を起動する。
2. このリポジトリを VS Code / Cursor で開く。
3. Command Palette を開く。
4. `Dev Containers: Reopen in Container` を実行する。
5. 初回 build が完了するまで待つ。
6. コンテナ内ターミナルを開く。
7. `claude` を実行する。

```bash
claude
```

初回起動時は Claude Code のログインが必要になる場合があります。認証情報はホストではなく、Docker volume `claude-code-config-kuni-musubi` に保存されます。

## CLI から起動する

IDE を使わずに Dev Container を立ち上げる場合は、リポジトリルートで以下を実行します。

```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . zsh
```

コンテナ内に入ったら Claude Code を起動します。

```bash
claude
```

## コンテナ内での作業ディレクトリ

Dev Container 内では、このリポジトリは以下に配置されます。

```text
/workspace/kuni-musubi
```

通常の開発コマンドはこのディレクトリで実行します。

## アプリケーションの起動

バックエンドと DB は Docker Compose で起動します。

```bash
docker compose up -d
```

フロントエンドを起動します。

```bash
cd frontend
npm install
npm run dev
```

アクセス先:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

## サンドボックス設定の場所

Claude Code 用の設定は以下にあります。

- `.claude/settings.json`
- `.claude/hooks/pre_tool_use_guard.py`
- `.devcontainer/devcontainer.json`
- `.devcontainer/managed-settings.json`

`.claude/settings.json` はリポジトリ共有の Claude Code 設定です。

`.devcontainer/managed-settings.json` は Dev Container build 時に `/etc/claude-code/managed-settings.json` へ配置される管理ポリシーです。

## ブロックしている操作

代表的には以下をブロックします。

- `.env` / `.env.local` / `.env.production` などの読み取り・編集
- `secrets/` 配下の読み取り・編集
- `~/.ssh`、`~/.aws`、`~/.config/gh` などの読み取り・編集
- Docker socket へのアクセス
- `env` / `printenv` / `set` による環境変数の一括表示
- `curl` / `wget` / `ssh` / `scp` / `rsync` / `nc` などの外部送信系コマンド
- `rm -rf /` や `sudo` など、ホストやコンテナを壊しやすいコマンド

依存追加、Docker 操作、`git commit` / `git push` などは実行時に確認する設定です。

## 実シークレットの扱い

`.env.example` は共有サンプルとして読める設定です。

実シークレットは以下のようなファイルに置き、コミットしないでください。

- `.env`
- `.env.local`
- `backend/.env`
- `batch/.env`
- `frontend/.env.local`

Claude Code に読ませたくない情報は、そもそも作業ディレクトリに置かない運用が最も確実です。

## コンテナを作り直す

Dev Container 設定を変更した場合は、IDE から以下を実行します。

```text
Dev Containers: Rebuild Container
```

CLI で作り直す場合:

```bash
devcontainer up --workspace-folder . --remove-existing-container
```

## Claude Code の認証情報を消す

Claude Code の設定 volume を削除すると、コンテナ内の Claude Code 認証情報も消えます。

```bash
docker volume rm claude-code-config-kuni-musubi
```

削除後、次回 `claude` 起動時に再ログインが必要です。

## 注意

Docker サンドボックスはプロンプトインジェクションを完全に防ぐものではありません。攻撃が成功した場合の被害範囲を狭めるための仕組みです。

安全性を上げるため、以下を守ってください。

- ホストの `~/.ssh` や `~/.aws` を Dev Container にマウントしない。
- `/var/run/docker.sock` を Dev Container にマウントしない。
- 実シークレットをリポジトリへ置かない。
- 不審な依存追加や外部通信は許可しない。
- `--dangerously-skip-permissions` を使わない。
