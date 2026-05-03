# Secure Claude Code Dev Container

この Dev Container は、Claude Code をホストではなくコンテナ内で動かすための設定です。

## 使い方

1. VS Code / Cursor / JetBrains などの Dev Containers 対応 IDE でこのリポジトリを開く。
2. `Dev Containers: Reopen in Container` を実行する。
3. コンテナ内ターミナルで `claude` を起動する。

## セキュリティ方針

- ホストの `~/.ssh`、`~/.aws`、`~/.config/gh`、Docker socket はマウントしない。
- Claude Code の認証・設定は Docker volume `claude-code-config-kuni-musubi` に保存する。
- `.env` / `.env.local` / `secrets/` は Claude Code の `Read` / `Edit` と Bash サンドボックスからブロックする。
- `PreToolUse` フックで、環境変数ダンプ、シークレット読み取り、外部送信系コマンドを追加で拒否する。
- `--dangerously-skip-permissions` は無効化する。

## 注意

`.env.example` は共有サンプルとして読める設定にしています。実シークレットは `.env` や `.env.local` に置き、リポジトリへコミットしないでください。
