import os

# 项目结构定义
project_structure = {
    "your_project_name": [
        "app/__init__.py",
        "app/api/__init__.py",
        "app/api/endpoints/__init__.py",
        "app/api/endpoints/example.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/crud/__init__.py",
        "app/db/__init__.py",
        "app/db/base_class.py",
        "app/db/session.py",
        "app/models/__init__.py",
        "app/models/example_model.py",
        "app/schemas/__init__.py",
        "app/schemas/example_schema.py",
        "app/main.py",
        "scripts/start-reload.sh",
        "scripts/docker-entrypoint.sh",
        "scripts/start-reload.sh",
        "tests/__init__.py",
        "tests/test_api/__init__.py",
        "tests/test_db/__init__.py",
        "tests/test_models/__init__.py",
        "docker-compose.yaml",
        "Dockerfile",
        "requirements.txt",
        "README.md",
    ]
}

# 创建文件的函数
def create_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as fp:
        pass

# 遍历项目结构并创建文件或目录
def create_project_structure(structure):
    for directory, files in structure.items():
        for file_path in files:
            create_file(os.path.join(directory, file_path))
        print(f"Project structure '{directory}' is created.")

# 脚本入口点
if __name__ == "__main__":
    create_project_structure(project_structure)
    print("Project structure generation is complete.")