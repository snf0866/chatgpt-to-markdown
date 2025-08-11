# ChatGPT to Markdown

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

ChatGPTの会話を美しいMarkdownファイルとしてエクスポート・保存するツールです。AIとの対話をアーカイブ、共有、整理するのに最適で、自動的な洞察生成機能も搭載しています。

[English README](README.md)

## ✨ 機能

- 🔗 **共有URLから直接エクスポート**: ChatGPTの共有リンクから会話を直接エクスポート
- 📝 **きれいなMarkdown形式**: どんなMarkdownエディタでも使える整形されたファイルを作成
- 🤖 **AI による洞察生成**: OpenAI APIを使用して重要な洞察とタグを自動生成（オプション）
- 🎯 **スマートなコンテンツ抽出**: PlaywrightでJavaScriptレンダリング後のコンテンツを確実に取得
- 🏷️ **自動タグ付け**: 会話を関連するタグで賢く分類
- 📚 **複数のエクスポート形式**: 標準Markdown、Obsidian形式、ブログ記事形式など

## 🚀 クイックスタート

### 前提条件

- Python 3.8以上
- Playwrightブラウザ（自動インストール）
- OpenAI APIキー（オプション、洞察生成用）

### インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/snufkin0866/chatgpt-to-markdown.git
cd chatgpt-to-markdown
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. （オプション）OpenAI APIキーを設定:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 基本的な使い方

ChatGPTの会話をMarkdownにエクスポート:
```bash
python chatgpt_to_markdown.py "https://chatgpt.com/share/..."
```

カスタム出力形式でエクスポート:
```bash
# ブログ記事として保存
python chatgpt_to_markdown.py "https://chatgpt.com/share/..." --format blog

# Obsidian用に保存
python chatgpt_to_markdown.py "https://chatgpt.com/share/..." --format obsidian
```

## 🛠️ 詳細オプション

```bash
# ブラウザウィンドウを表示（デバッグ用）
python chatgpt_to_markdown.py <URL> --show-browser

# カスタムタイムアウト（ミリ秒）
python chatgpt_to_markdown.py <URL> --timeout 60000

# カスタム出力ディレクトリを指定
python chatgpt_to_markdown.py <URL> --output /path/to/output

# AI洞察なしでエクスポート（高速）
python chatgpt_to_markdown.py <URL> --no-insights
```

## 📁 出力フォーマット

このツールはクリーンなMarkdownファイルをエクスポートします：

```markdown
# ChatGPT会話: [トピック]

日付: YYYY-MM-DD
タグ: #chatgpt #tag1 #tag2

## 重要な洞察
- 洞察 1
- 洞察 2
- ...

## 会話

### 👤 ユーザー
[ユーザーメッセージ]

### 🤖 ChatGPT
[アシスタントの応答]

...
```

## 🔧 設定

### 出力ディレクトリ

デフォルトでは、Markdownファイルは現在のディレクトリに保存されます。カスタム出力ディレクトリを指定できます：

```bash
python chatgpt_to_markdown.py <URL> --output ./conversations
```

### OpenAI API設定

このツールはOpenAIのAPIを使用して洞察とタグを生成します。この機能はオプションですが、より良い整理のために推奨されます。

APIキーを環境変数として設定：
```bash
export OPENAI_API_KEY="sk-..."
```

## 🤝 貢献

貢献を歓迎します！ぜひプルリクエストを送ってください。

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを開く

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

- [Playwright](https://playwright.dev/) - 信頼性の高いWebスクレイピング
- [OpenAI API](https://openai.com/api/) - インテリジェントなコンテンツ分析
- [Obsidian](https://obsidian.md/)、[Notion](https://notion.so/)、その他のMarkdownエディタとの互換性

## 🐛 既知の問題とトラブルシューティング

### 共有URLが機能しない？

1. URLが有効な共有リンクであることを確認（プライベートな会話ではない）
2. `--show-browser`を使用してデバッグ
3. `--timeout 60000`でタイムアウトを増やす

### 洞察が生成されない？

- OpenAI APIキーが正しく設定されているか確認
- APIキーに十分なクレジットがあるか確認

## 📮 連絡先

作成者: [@snufkin0866](https://github.com/snufkin0866)

## ⭐ スター履歴

このツールが役立つと思ったら、GitHubでスターを付けてください！