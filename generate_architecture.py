import os
import json
import requests
from pathlib import Path

# プロジェクト設定を読み込み
config = {
    "type": "webapp",
    "tech_stack": "react",
    "requirements": "reactでTo doアプリをwebアプリとして作って",
    "features": "basic".split(","),
    "mode": "complete_project"
}

# プロジェクトタイプ別のテンプレート定義
project_templates = {
    "mobile": {
        "structure": [
            "src/components",
            "src/screens", 
            "src/navigation",
            "src/services",
            "src/utils",
            "assets/images",
            "assets/fonts"
        ],
        "files": {
            "package.json": "mobile_package",
            "App.js": "mobile_app",
            "src/navigation/AppNavigator.js": "navigation",
            "src/screens/HomeScreen.js": "home_screen"
        }
    },
    "web": {
        "structure": [
            "src/components",
            "src/pages",
            "src/hooks",
            "src/services", 
            "src/styles",
            "public"
        ],
        "files": {
            "package.json": "web_package",
            "src/App.js": "web_app",
            "src/index.js": "web_index",
            "public/index.html": "web_html"
        }
    },
    "api": {
        "structure": [
            "src/controllers",
            "src/models",
            "src/routes",
            "src/middleware",
            "src/utils",
            "tests"
        ],
        "files": {
            "package.json": "api_package",
            "src/app.js": "api_app",
            "src/server.js": "api_server"
        }
    }
}

def call_claude_api(prompt):
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        raise Exception(f"API Error: {response.status_code}")

def generate_project_structure():
    template = project_templates.get(config["type"], project_templates["web"])
    
    # ディレクトリ構造を作成
    for directory in template["structure"]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
    return template

def generate_files_with_claude(template):
    for file_path, file_type in template["files"].items():
        prompt = f"""
        プロジェクト設定:
        - タイプ: {config["type"]}
        - 技術スタック: {config["tech_stack"]}
        - 要件: {config["requirements"]}
        - 機能: {', '.join(config["features"])}
        
        以下のファイルを生成してください: {file_path}
        ファイルタイプ: {file_type}
        
        要求事項:
        1. 実際に動作するコードを生成
        2. ベストプラクティスに従う
        3. コメントを含める
        4. 設定された機能を反映する
        5. エラーハンドリングを含める
        
        ファイル内容のみを返してください。説明は不要です。
        """
        
        try:
            content = call_claude_api(prompt)
            
            # ディレクトリが存在しない場合は作成
            file_dir = Path(file_path).parent
            file_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Generated: {file_path}")
            
        except Exception as e:
            print(f"Error generating {file_path}: {e}")
            # フォールバック: 基本的なファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"// Generated file: {file_path}\n// TODO: Implement functionality\n")

def generate_documentation():
    prompt = f"""
    以下のプロジェクトの詳細なREADME.mdファイルを生成してください:
    
    プロジェクト設定:
    - タイプ: {config["type"]}
    - 技術スタック: {config["tech_stack"]}
    - 要件: {config["requirements"]}
    - 機能: {', '.join(config["features"])}
    
    README.mdには以下を含めてください:
    1. プロジェクト概要
    2. セットアップ手順
    3. 使用方法
    4. 機能説明
    5. 開発ガイド
    6. ライセンス情報
    
    マークダウン形式で返してください。
    """
    
    try:
        readme_content = call_claude_api(prompt)
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("Generated: README.md")
    except Exception as e:
        print(f"Error generating README: {e}")

# メイン実行
try:
    print("Generating project structure...")
    template = generate_project_structure()
    
    print("Generating files with Claude...")
    generate_files_with_claude(template)
    
    print("Generating documentation...")
    generate_documentation()
    
    # 生成サマリーを作成
    with open("generation_summary.txt", "w", encoding="utf-8") as f:
        f.write(f"Project Type: {config['type']}\n")
        f.write(f"Tech Stack: {config['tech_stack']}\n")
        f.write(f"Features: {', '.join(config['features'])}\n")
        f.write(f"Generation Mode: {config['mode']}\n")
        f.write("\nGeneration completed successfully!")
    
    print("Project generation completed!")
    
except Exception as e:
    print(f"Generation failed: {e}")
    with open("generation_summary.txt", "w") as f:
        f.write(f"Generation failed: {e}")
    raise
