---
app_name: 达梦数据库MCP服务
description: 基于Gradio的达梦数据库MCP服务，提供通过自然语言或直接操作与达梦数据库交互的能力
tags:
  - database
  - dameng
  - mcp
  - sql
  - gradio
---

# 达梦数据库MCP服务

这是一个基于Gradio的达梦数据库MCP（Model Context Protocol）服务，提供了通过自然语言或直接操作与达梦数据库交互的能力。

## 功能特性

1. 列出数据库中的所有表
2. 执行自定义SQL查询
3. 查看表结构信息
4. 直观的Web界面操作

## 服务配置

```json
{
  "server": {
    "port": 7860,
    "host": "0.0.0.0"
  },
  "env": {
    "DM_HOST": "localhost",
    "DM_PORT": "5236",
    "DM_USERNAME": "SYSDBA",
    "DM_PASSWORD": "SYSDBA",
    "DM_DATABASE": ""
  }
}
```

## 安装依赖

```bash
pip install -r requirements.txt
```

如果遇到依赖问题，可以尝试升级相关包：

```bash
pip install pydantic --upgrade
```

## 配置数据库连接

修改 `config.json` 文件中的配置参数：

```json
{
    "dm_host": "localhost",
    "dm_port": "5236",
    "dm_username": "SYSDBA",
    "dm_password": "SYSDBA",
    "dm_database": "",
    "service_host": "0.0.0.0",
    "service_port": 7860,
    "debug": false
}
```

或者通过环境变量配置：
- DM_HOST: 数据库主机地址
- DM_PORT: 数据库端口(默认5236)
- DM_USERNAME: 数据库用户名
- DM_PASSWORD: 数据库密码
- DM_DATABASE: 默认数据库名称

## 启动服务

```bash
python app.py
```

启动后访问 `http://localhost:7860` 即可使用Web界面操作达梦数据库。

如果需要从外部访问，可以使用 `http://<your_ip>:7860` 访问。

## 使用说明

1. **表列表**：点击"列出所有表"按钮，显示数据库中的所有用户表
2. **SQL查询**：在输入框中输入SQL语句，点击"执行查询"按钮执行
3. **表结构**：从下拉列表中选择表名，点击"获取表结构"查看表的字段信息

## 网络问题解决

如果遇到网络连接问题或frp穿透问题，请注意：

1. 程序默认不开启公网分享功能，避免因缺少frp组件导致的错误
2. 如果需要公网访问，可以手动下载frp组件：
   - 下载文件：https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_windows_amd64.exe
   - 重命名为：frpc_windows_amd64_v0.2
   - 移动到：`<your_python_env>/lib/site-packages/gradio/` 目录下

## MCP协议支持

本服务支持MCP协议，可以与大模型平台（如ModelScope）集成，实现智能数据库操作。