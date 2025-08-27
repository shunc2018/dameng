import dmPython
import json
import os
from typing import List, Dict, Any
import gradio as gr


class DamengMCPService:
    def __init__(self, config_file="config.json"):
        # 读取配置文件
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.host = os.getenv("DM_HOST", config.get("dm_host", "localhost"))
            self.port = os.getenv("DM_PORT", config.get("dm_port", "5236"))
            self.username = os.getenv("DM_USERNAME", config.get("dm_username", "SYSDBA"))
            self.password = os.getenv("DM_PASSWORD", config.get("dm_password", "SYSDBA"))
            self.database = os.getenv("DM_DATABASE", config.get("dm_database", ""))
        else:
            # 如果没有配置文件，使用环境变量或默认值
            self.host = os.getenv("DM_HOST", "localhost")
            self.port = os.getenv("DM_PORT", "5236")
            self.username = os.getenv("DM_USERNAME", "SYSDBA")
            self.password = os.getenv("DM_PASSWORD", "SYSDBA")
            self.database = os.getenv("DM_DATABASE", "")
        
        self.connection = None

    def connect(self) -> bool:
        """连接到达梦数据库"""
        try:
            self.connection = dmPython.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                schema=self.database
            )
            return True
        except Exception as e:
            print(f"连接数据库失败: {e}")
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def list_tables(self) -> List[str]:
        """列出数据库中的所有表"""
        if not self.connection:
            if not self.connect():
                return ["连接数据库失败"]

        try:
            cursor = self.connection.cursor()
            # 查询用户表，排除系统表
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM USER_TABLES 
                WHERE TABLE_NAME NOT LIKE 'SYS%' 
                ORDER BY TABLE_NAME
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception as e:
            return [f"查询表列表失败: {str(e)}"]

    def execute_query(self, query: str) -> Dict[str, Any]:
        """执行SQL查询"""
        if not self.connection:
            if not self.connect():
                return {"error": "连接数据库失败"}

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # 如果是查询语句
            if query.strip().upper().startswith("SELECT"):
                # 获取列名
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    cursor.close()
                    
                    # 转换为可显示的格式
                    data = []
                    for row in rows:
                        data.append(list(row))
                    
                    return {
                        "columns": columns,
                        "data": data,
                        "row_count": len(data)
                    }
                else:
                    cursor.close()
                    return {
                        "message": "查询执行成功，无返回数据"
                    }
            else:
                # 对于非查询语句，提交更改
                self.connection.commit()
                row_count = cursor.rowcount
                cursor.close()
                return {
                    "message": f"执行成功，影响行数: {row_count}"
                }
        except Exception as e:
            return {"error": f"执行查询失败: {str(e)}"}

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        if not self.connection:
            if not self.connect():
                return {"error": "连接数据库失败"}

        try:
            cursor = self.connection.cursor()
            
            # 获取表字段信息
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, NULLABLE, DATA_DEFAULT
                FROM USER_TAB_COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY COLUMN_ID
            """)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append(list(row))
                
                cursor.close()
                
                return {
                    "columns": columns,
                    "data": data
                }
            else:
                cursor.close()
                return {"message": "无表结构信息"}
        except Exception as e:
            return {"error": f"获取表信息失败: {str(e)}"}


# 创建全局服务实例
mcp_service = DamengMCPService()


def list_tables_interface():
    """Gradio接口：列出所有表"""
    tables = mcp_service.list_tables()
    return tables


def query_interface(sql_query):
    """Gradio接口：执行SQL查询"""
    if not sql_query.strip():
        return None, ["请输入SQL查询语句"]
    
    result = mcp_service.execute_query(sql_query)
    
    if "error" in result:
        return None, [result["error"]]
    elif "message" in result:
        return None, [result["message"]]
    else:
        # 返回查询结果
        if result["data"]:
            return result["data"], result["columns"]
        else:
            return [["无数据"]], ["结果"]


def table_info_interface(table_name):
    """Gradio接口：获取表结构信息"""
    if not table_name:
        return None, ["请选择一个表"]
    
    result = mcp_service.get_table_info(table_name)
    
    if "error" in result:
        return None, [result["error"]]
    elif "message" in result:
        return None, [result["message"]]
    else:
        if result["data"]:
            return result["data"], result["columns"]
        else:
            return [["无数据"]], ["结果"]


# 创建Gradio界面
with gr.Blocks(title="达梦数据库MCP服务") as demo:
    gr.Markdown("# 达梦数据库MCP服务")
    gr.Markdown("基于Gradio的达梦数据库操作界面，支持查询表、执行SQL等功能。")
    
    with gr.Tab("表列表"):
        with gr.Row():
            with gr.Column():
                list_btn = gr.Button("列出所有表")
                table_list = gr.JSON(label="表列表")
                
        list_btn.click(
            fn=list_tables_interface,
            outputs=table_list
        )
    
    with gr.Tab("SQL查询"):
        with gr.Row():
            with gr.Column():
                sql_input = gr.Textbox(
                    label="SQL查询语句",
                    placeholder="请输入SQL查询语句，例如: SELECT * FROM TABLE_NAME LIMIT 10",
                    lines=5
                )
                query_btn = gr.Button("执行查询")
                
            with gr.Column():
                query_output = gr.Dataframe(label="查询结果")
                query_status = gr.Textbox(label="状态信息")
                
        query_btn.click(
            fn=query_interface,
            inputs=sql_input,
            outputs=[query_output, query_status]
        )
    
    with gr.Tab("表结构"):
        with gr.Row():
            with gr.Column():
                # 先获取表列表
                tables = mcp_service.list_tables()
                table_selector = gr.Dropdown(
                    choices=tables if tables else [],
                    label="选择表"
                )
                refresh_table_btn = gr.Button("刷新表列表")
                table_info_btn = gr.Button("获取表结构")
                
            with gr.Column():
                table_info_output = gr.Dataframe(label="表结构信息")
                table_info_status = gr.Textbox(label="状态信息")
                
        refresh_table_btn.click(
            fn=list_tables_interface,
            outputs=table_selector
        )
        
        table_info_btn.click(
            fn=table_info_interface,
            inputs=table_selector,
            outputs=[table_info_output, table_info_status]
        )

if __name__ == "__main__":
    # 读取服务配置
    if os.path.exists("config.json"):
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        service_host = config.get("service_host", "0.0.0.0")
        service_port = config.get("service_port", 7860)
    else:
        service_host = os.getenv("SERVICE_HOST", "0.0.0.0")
        service_port = int(os.getenv("SERVICE_PORT", "7860"))
    
    demo.launch(server_name=service_host, server_port=service_port)