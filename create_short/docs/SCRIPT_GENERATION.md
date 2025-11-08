# 台本生成システム解説

## 📝 概要

台本は **4つの方法** で自動生成されます（優先順位順）:

1. ✅ **GitHub Copilot** （環境変数 `GITHUB_TOKEN` が設定されている場合）
2. ✅ **OpenAI GPT-4** （環境変数 `OPENAI_API_KEY` が設定されている場合）
3. ✅ **Anthropic Claude** （環境変数 `ANTHROPIC_API_KEY` が設定されている場合）
4. ✅ **テンプレート** （API未設定の場合のフォールバック）

## 🔄 動作フロー

```
generate_script.py
    ↓
環境変数チェック
    ↓
┌─────────────────────────────┐
│ GITHUB_TOKEN が存在？        │ → YES → GitHub Copilotで生成
└─────────────────────────────┘
    ↓ NO
┌─────────────────────────────┐
│ OPENAI_API_KEY が存在？      │ → YES → GPT-4で生成
└─────────────────────────────┘
    ↓ NO
┌─────────────────────────────┐
│ ANTHROPIC_API_KEY が存在？   │ → YES → Claudeで生成
└─────────────────────────────┘
    ↓ NO
ランダムテンプレートから選択
```

## 🤖 AI生成の仕組み

### 1. GitHub Copilot（推奨！）

```bash
# 環境変数設定
export GITHUB_TOKEN="ghp_xxxx..."

# 生成処理（内部的にはOpenAI互換APIを使用）
requests.post(
    "https://api.githubcopilot.com/chat/completions",
    headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
    json={
        "model": "gpt-4",
        "messages": [...],
        "temperature": 0.9
    }
)
```

**特徴:**
- **GitHub Copilot個人版/Business契約があれば無料で使える！**
- GPT-4相当の高品質
- 追加コスト不要（既存のCopilotサブスクで使用可能）
- OpenAI直接契約より安定している場合がある

**取得方法:**
```bash
# GitHub Personal Access Token を取得
# https://github.com/settings/tokens
# スコープ: read:user, user:email

# または GitHub CLI で自動取得
gh auth token
```

### 2. Anthropic Claude

```python
# 環境変数設定
export OPENAI_API_KEY="sk-xxxx..."

# 生成処理
openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "プロフェッショナルな台本作家として..."},
        {"role": "user", "content": "10行の台本を作成してください..."}
    ],
    temperature=0.9  # 創造性を高める
)
```

**特徴:**
- 高品質な台本生成
- アカウント別にカスタマイズされたプロンプト
- 視聴維持率を意識した構成

### 2. OpenAI GPT-4

```python
# 環境変数設定
export OPENAI_API_KEY="sk-xxxx..."

# 生成処理
openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "プロフェッショナルな台本作家として..."},
        {"role": "user", "content": "10行の台本を作成してください..."}
    ],
    temperature=0.9  # 創造性を高める
)
```

**特徴:**
- 高品質な台本生成
- アカウント別にカスタマイズされたプロンプト
- 視聴維持率を意識した構成

### 3. Anthropic Claude

```python
# 環境変数設定
export ANTHROPIC_API_KEY="sk-ant-xxxx..."

# 生成処理
client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "..."}],
    temperature=0.9
)
```

**特徴:**
- OpenAIと同等の品質
- より自然な日本語表現
- コンテキスト理解が優秀

### 4. テンプレート（フォールバック）

```python
templates = {
    "心理テストラボ": [
        "あなたの隠れた才能、見抜きます\n...",
        "直感で選んでください\n..."
    ],
    # ... 各アカウント2パターン
}
```

**特徴:**
- APIキー不要（完全無料）
- 事前作成済みの台本からランダム選択
- 安定した品質

## 📋 アカウント別プロンプト

### 心理テストラボ

```
【要件】
- 10行（各行が1シーン）
- 冒頭2行で強烈なフックを作る
- 選択肢を提示（例: ①②③）
- 結果を小出しにして引き延ばす
- 最後にCTA（フォロー促進）
- エンゲージメント重視（コメント誘導）

【トーン】
- フレンドリー
- 共感を誘う
- サプライズ要素を入れる
```

### 闇夜の語り部

```
【要件】
- 10行（各行が1シーン）
- 冒頭2行で不気味な雰囲気を作る
- 実体験風のリアリティ
- 徐々に恐怖を高めていく
- クリフハンガー（続きが気になる終わり方）

【トーン】
- シリアス
- 不穏な雰囲気
- リアリティのある描写
```

### 映画紹介

```
【要件】
- 10行（各行が1シーン）
- 冒頭2行で映画の魅力を提示
- 架空の映画でも実在の映画でもOK
- ネタバレ厳禁のティーザー風
- どんでん返しや意外な要素を匂わす

【トーン】
- 情熱的
- 興味を引く
- ネタバレしない配慮
```

## 🚀 使い方

### 現在の状態（テンプレート使用中）

```bash
# 環境変数が未設定なので、テンプレートから選択
./scripts/test_generation.sh
```

**出力例:**
```
⚠️ API未設定。テンプレートから 心理テストラボ の台本を選択...
直感で選んでください
今すぐ行きたい場所は?
①海 ②山 ③街 ④家
...
```

### AI生成を使う場合

#### GitHub Copilot（推奨！）

```bash
# 方法1: GitHub CLI で自動取得
gh auth token

# 方法2: Personal Access Token を手動取得
# https://github.com/settings/tokens
# スコープ: read:user, user:email

# 環境変数設定
export GITHUB_TOKEN="ghp_xxxx..."

# 永続化
echo 'export GITHUB_TOKEN="ghp_xxxx..."' >> ~/.bashrc
source ~/.bashrc

# 動画生成
./scripts/test_generation.sh
```

**出力例:**
```
🤖 GitHub Copilot で 心理テストラボ の台本を生成中...
あなたの深層心理、見抜きます
たった3秒で分かる性格診断
好きな色を直感で選んでください
...（高品質AI生成台本）
```

**メリット:**
- GitHub Copilot契約があれば**追加料金なし**
- 毎月$10のCopilot料金のみ（既に契約済みなら無料）
- OpenAI直接契約より安定
- GPT-4相当の品質

#### OpenAI GPT-4

```bash
# 1. APIキーを取得
https://platform.openai.com/api-keys

# 2. 環境変数設定
export OPENAI_API_KEY="sk-xxxx..."

# 3. 永続化（オプション）
echo 'export OPENAI_API_KEY="sk-xxxx..."' >> ~/.bashrc
source ~/.bashrc

# 4. 動画生成
./scripts/test_generation.sh
```

**出力例:**
```
🤖 OpenAI GPT-4 で 心理テストラボ の台本を生成中...
あなたの本当の性格、当てます
たった1つの質問で見抜けます
今一番欲しいものは何ですか？
...（AI生成の高品質台本）
```

#### Anthropic Claude

```bash
# 1. APIキーを取得
https://console.anthropic.com/

# 2. 環境変数設定
export ANTHROPIC_API_KEY="sk-ant-xxxx..."

# 3. 永続化（オプション）
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxx..."' >> ~/.bashrc

# 4. 動画生成
./scripts/test_generation.sh
```

## 📁 生成ファイル

### 台本の保存先

```
data/scripts/history/
├── script_shinrigaku_20251108_152326.txt  # 心理テストラボ
├── script_kowai_20251108_152326.txt       # 闇夜の語り部
├── script_movie_20251108_152326.txt       # 映画紹介
└── scripts_20251108.json                  # 3アカウント分まとめ
```

### ファイル内容例

**script_shinrigaku_20251108_152326.txt:**
```
直感で選んでください
今すぐ行きたい場所は?
①海 ②山 ③街 ④家
これで性格が丸わかり
①海を選んだあなた
実は自由を求めてますね?
②山の人は冒険家タイプ
③④を選んだ人は?
コメント欄で語り合おう
毎日更新中、フォロー必須
```

## 💰 コスト比較

| 方法 | コスト | 品質 | 多様性 | 備考 |
|------|--------|------|--------|------|
| **テンプレート** | 無料 | 中 | 低（6パターン） | APIキー不要 |
| **GitHub Copilot** | **実質無料** | 高 | 高（毎回異なる） | Copilot契約必要（$10/月） |
| **GPT-4** | ~$0.01/回 | 高 | 高（毎回異なる） | OpenAI契約必要 |
| **Claude** | ~$0.01/回 | 高 | 高（毎回異なる） | Anthropic契約必要 |

### 推奨運用

- **Copilot契約あり**: GitHub Copilot（追加コスト0円）
- **Copilot契約なし（テスト時）**: テンプレート（無料）
- **Copilot契約なし（本番運用）**: GPT-4 または Claude
  - 1日1回 × 3アカウント = 月額 約$1

## 🔧 カスタマイズ

### プロンプトの編集

`generate_script.py` の `ACCOUNT_PROMPTS` を編集:

```python
ACCOUNT_PROMPTS = {
    "新しいアカウント": {
        "system": "あなたは...",
        "prompt": """
        【要件】
        - カスタム要件を追加
        ...
        """
    }
}
```

### テンプレートの追加

```python
templates = {
    "心理テストラボ": [
        "既存テンプレート1",
        "既存テンプレート2",
        "新しいテンプレート3"  # ← 追加
    ]
}
```

## 📊 生成品質の確認

```bash
# 台本ファイルを確認
cat data/scripts/history/script_shinrigaku_*.txt

# メタデータも確認
python show_metadata.py
```

## 🐛 トラブルシューティング

### "API未設定" と表示される

```bash
# 環境変数が設定されているか確認
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# 空の場合は設定
export OPENAI_API_KEY="your-key"
```

### API エラー

```
❌ API エラー: Incorrect API key provided
```

**対処法:**
1. APIキーが正しいか確認
2. クォータが残っているか確認
3. フォールバックが自動起動するので動画生成は継続

## 📚 参考リンク

- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [Anthropic API ドキュメント](https://docs.anthropic.com)
- プロジェクト内: `generate_script.py` のコード
