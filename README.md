# saisai_app
チーム開発用のアプリです。

## 開発環境のセットアップ

Python **3.11** を使用します。以下は、リポジトリをすでにclone済みの方向けの手順です。  
VS Codeで `saisai_app` フォルダを開き、そのフォルダのターミナルで実行してください。

### 1. 仮想環境を作成・有効化

仮想環境の作成は初回のみです。すでにこのプロジェクト用のPython 3.11の `.venv` がある場合は、有効化だけ行ってください。

**Windows（ターミナル：PowerShell）**

まず `python --version` を実行し、`Python 3.11.x` と表示されることを確認してください。その後、以下を実行します。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Mac（ターミナル）**

まず `python3 --version` を実行し、`Python 3.11.x` と表示されることを確認してください。その後、以下を実行します。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

`python`（Macは `python3`）が見つからない、または3.11以外の場合は、作成前にチームでPythonの環境を確認してください。仮想環境は、コマンドで呼び出したPythonのバージョンで作成されます。

有効化後、ターミナルに `(.venv)` が表示されることを確認します。

```bash
python --version
```

`Python 3.11.x` と表示されればOKです。

### 2. ライブラリをインストール

Windows・Mac共通です。仮想環境を有効にした状態で実行してください。

```bash
python -m pip install -r requirements.txt
python -m pip check
```

インストールがエラーなく終了し、最後に `No broken requirements found.` と表示されれば、依存関係の確認は完了です。

### 3. secrets.tomlを作成

APIキーなどの秘密情報は `.streamlit/secrets.toml` に設定します。

リポジトリ内の `secrets.toml.sample` を参考に、プロジェクト直下の `.streamlit` フォルダ内に `secrets.toml` を作成してください。

```text
saisai_app/
├── .streamlit/
│   └── secrets.toml
├── secrets.toml.sample
└── ...
```

`secrets.toml` には以下の内容を設定します。

```toml
# 「.streamlit」フォルダ配下にsecrets.tomlを作り、以下の変数を設定してください

OPENAI_API_KEY = "XXX"

# 以下はこれから必要な場面が生じたときに順次設定してください。
SUPABASE_URL = "XXX"
SUPABASE_KEY = "XXX"

redirect_uri = "XXX"
cookie_secret = "XXX"
client_id = "XXX"
client_secret = "XXX"
server_metadata_url = "XXX"
```

現時点では、まず以下の `OPENAI_API_KEY` の `XXX` を**自分が使用する実際のOpenAI APIキー**に変更してください。（secrets.toml.sampleではなく、自身のsecrets.tomlに追加してください！）

```toml
OPENAI_API_KEY = "実際のOpenAI APIキー"
```

その他の以下の項目については、今後SupabaseやGoogle認証などで必要になったタイミングで順次設定します。

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `redirect_uri`
- `cookie_secret`
- `client_id`
- `client_secret`
- `server_metadata_url`

> **注意**
>
> `secrets.toml` にはAPIキーなどの秘密情報が含まれるため、**Gitにはcommit・pushしないでください。**
>
> `.streamlit/secrets.toml` は `.gitignore` の対象にしておきます。  
> チームで設定項目を共有する場合は、実際のキーを記載せず `secrets.toml.sample` を更新してください。

### 4. AIチャット接続テスト

ターミナルで以下を実行し、アプリを起動します。

```bash
streamlit run app.py
```

ブラウザでアプリが開いたら、チャット欄に任意のメッセージを入力してください。

AIから返答が返ってくれば、`secrets.toml` に設定した `OPENAI_API_KEY` を使って正常にOpenAI APIへ接続できています。

## 2回目以降

作業を始める前に、**SourceTreeで作業するブランチを確認し、必要に応じてPullして最新の状態にします。**

その後、VS Codeでターミナルを開き、仮想環境を有効化します。

`requirements.txt` が更新されている場合は、Pull後に以下を実行してください。

```bash
python -m pip install -r requirements.txt
python -m pip check
```

- `.venv/` は各自のPCで作成し、Gitにはcommitしません。`.venv` は `.gitignore` の対象になっています。
- `.streamlit/secrets.toml` も各自のPCで作成し、Gitにはcommitしません。
- エラーが出た場合は、最後のエラーメッセージをチームに共有してください。

## 新しいライブラリを追加して共有する場合

プロジェクト専用の仮想環境を有効にして、**SourceTreeで現在の作業ブランチを確認してから**作業します。

### 1. インストール・動作確認

例として `plotly` を追加する場合です。実際に追加するライブラリ名に置き換えてください。

```bash
python -m pip install plotly
python -m pip check
```

続けてアプリを起動し、追加したライブラリを使う機能が動くことを確認します。

```bash
python -m streamlit run app.py
```

確認後は `Ctrl+C` で終了します。起動ファイル名が異なる場合は `app.py` を置き換えてください。

### 2. requirements.txtを更新

**Windows（PowerShell）**

```powershell
python -m pip freeze > requirements.txt
```

**Mac**

```bash
python -m pip freeze > requirements.txt
```

どちらも仮想環境内のライブラリ一覧でファイル全体を上書きします。

WindowsはPowerShellのバージョンによる保存形式の違いを避けるため、UTF-8を指定しています。

既存のコメントは消え、直接インストールしたライブラリだけでなく、間接的に必要なライブラリも記録されます。

### 3. SourceTreeで変更を確認してcommit・push（実態と合っていないかもしれないので今後微修正します）

`requirements.txt` を更新したら、SourceTreeで変更内容を確認します。

1. **現在のブランチを確認する**
   - SourceTree左側の「ブランチ」から、意図した作業ブランチを選択していることを確認します。

2. **変更されたファイルを確認する**
   - SourceTreeの「ファイルステータス」を開きます。
   - `requirements.txt` が変更されていることを確認します。
   - ライブラリを使用するために変更したPythonファイルなどもあわせて確認します。

3. **変更内容を確認する**
   - `requirements.txt` を選択し、追加・削除された内容を確認します。
   - Jupyterなど今回使わないライブラリが大量に追加されている場合は、正しい仮想環境を使用しているか確認してください。

4. **commitするファイルをステージする**
   - `requirements.txt` を「Indexにステージしたファイル」へ追加します。
   - ライブラリを使用するために変更したPythonファイルなども、一緒にステージします。

5. **commitする**
   - commitメッセージに変更内容を記載します。

   例：

   ```text
   plotlyを追加
   ```

6. **pushする**
   - commit後、SourceTree上部の「プッシュ」をクリックします。
   - 現在の作業ブランチを選択し、リモートリポジトリへPushします。

作業ブランチをPushした場合は、必要に応じてGitHubでPull Request（PR）を作成し、チームで確認して共有ブランチに取り込みます。

**Pushしただけでは、他のブランチには変更は反映されません。**

### 4. 他のメンバーの対応

他のメンバーは、SourceTreeで変更が取り込まれた共有ブランチに切り替え、**Pullして最新の状態にします。**

その後、VS Codeでプロジェクトを開き、各自の仮想環境を有効化して以下を実行します。

```bash
python -m pip install -r requirements.txt
python -m pip check
```

受け取っただけのメンバーが、毎回 `pip freeze` を実行する必要はありません。

※ `requirements.txt` の行を削除しても、すでに仮想環境にインストールされているライブラリは自動では削除されません。不要なライブラリが仮想環境に残っていると、次に `pip freeze` を実行した際に再び `requirements.txt` に記録されます。

また、Windows専用パッケージなどが追加された場合は、他のOSでもインストールできるか確認してください。