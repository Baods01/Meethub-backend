# Meethub 后端部署指南

## 环境要求

- **MySQL**: >= 8.0.42 for win64
- **Python**: >= 3.12.4

## 部署步骤

### 1. 创建虚拟环境

在项目目录下的终端中，使用以下命令创建虚拟环境：

```bash
python -m venv MeethubEnv
```

或

```bash
python3 -m venv MeethubEnv
```

### 2. 激活虚拟环境

在终端中使用以下命令激活虚拟环境：

```bash
MeethubEnv\Scripts\activate
```

### 3. 安装项目依赖

运行以下命令安装所需的第三方库：

```bash
pip install -r requirements.txt
```

或

```bash
pip3 install -r requirements.txt
```



### 4. 配置数据库

#### 4.1 创建数据库

通过 Navicat 或其他 MySQL 客户端工具，在 MySQL 的 root 用户中创建数据库 `meethub_db`。

#### 4.2 初始化数据库结构

运行项目 `sql` 目录下的 `meethub_db.sql` 文件来初始化数据库结构。

#### 4.3 配置数据库连接

编辑项目根目录中的 `settings.py` 文件，修改 root 用户的密码为你的 MySQL 中 root 用户的密码。

### 5. 启动后端服务

在项目目录下的终端中，运行以下命令启动后端服务：

```bash
python main.py
```

后端服务将在 `127.0.0.1:8080` 地址上运行。

建议访问 `http://127.0.0.1:8080/docs` 以获取接口swagger文档

## 预设的超级管理员账户
```bash
username:admin
password:12345678
```