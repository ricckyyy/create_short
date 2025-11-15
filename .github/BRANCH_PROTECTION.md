# ブランチ保護設定ガイド

## GitHub リポジトリ設定手順

### 1. main ブランチの保護

1. GitHubリポジトリページを開く
   https://github.com/ricckyyy/create_short

2. **Settings** タブをクリック

3. 左サイドバー **Branches** をクリック

4. **Add branch protection rule** をクリック

5. 以下の設定を行う:

#### Branch name pattern
```
main
```

#### Protect matching branches

✅ **Require a pull request before merging**
  - ✅ Require approvals: 1
  - ✅ Dismiss stale pull request approvals when new commits are pushed

✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging

✅ **Require conversation resolution before merging**

✅ **Do not allow bypassing the above settings**
  - ⚠️ 管理者も含めて保護（推奨）

6. **Create** をクリック

### 2. develop ブランチの保護（オプション）

同様の手順で `develop` ブランチも保護可能:

#### Branch name pattern
```
develop
```

#### 推奨設定
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging

### 3. タグ保護（オプション）

リリースタグの削除を防ぐ:

1. **Settings** → **Tags** → **Protected tags**
2. **New protected tag** をクリック
3. Pattern: `v*.*.*`
4. **Protect this tag** をクリック

## 現在のブランチ構成

```bash
# ブランチ一覧確認
git branch -a
```

```
* develop          # 開発用メインブランチ
  main            # 本番環境ブランチ
```

## 運用フロー

### 新機能開発
```bash
# develop から feature ブランチ作成
git checkout develop
git checkout -b feature/new-feature

# 開発・コミット
git commit -m "feat: 新機能を追加"

# プッシュ・PR作成
git push origin feature/new-feature
# GitHub で develop ← feature/new-feature の PR 作成
```

### リリース
```bash
# develop を main にマージ（PR経由）
# GitHub で main ← develop の PR 作成
# レビュー・承認後マージ

# タグ付け
git checkout main
git pull origin main
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

## 保護確認

設定後、以下で確認:

```bash
# main に直接 push できないことを確認
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test"
git push origin main
# → エラーが出れば保護成功
```
