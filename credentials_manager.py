#!/usr/bin/env python3
"""
微信公众号API凭证管理工具
用于查看、更新、删除微信公众号API凭证
"""

import os
import sys
import argparse
from pathlib import Path
import getpass
import re

# 环境变量名称
APP_ID_VAR = 'WECHAT_APP_ID'
APP_SECRET_VAR = 'WECHAT_APP_SECRET'

# .env文件路径
ENV_PATH = Path('.env')


def load_env_file():
    """加载.env文件内容"""
    env_content = []
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            env_content = f.readlines()
    return env_content


def save_env_file(env_content):
    """保存.env文件内容"""
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.writelines(env_content)


def get_current_credentials():
    """获取当前凭证"""
    app_id = os.getenv(APP_ID_VAR, '')
    app_secret = os.getenv(APP_SECRET_VAR, '')
    return app_id, app_secret


def view_credentials():
    """查看当前凭证"""
    app_id, app_secret = get_current_credentials()
    
    print("=== 当前微信公众号API凭证 ===")
    if app_id:
        print(f"App ID: {app_id}")
    else:
        print("App ID: 未设置")
    
    if app_secret:
        # 隐藏大部分Secret，只显示前3位和后3位
        hidden_secret = f"{app_secret[:3]}***{app_secret[-3:]}"
        print(f"App Secret: {hidden_secret}")
    else:
        print("App Secret: 未设置")
    
    print(f".env文件存在: {ENV_PATH.exists()}")
    
    return True


def update_credentials():
    """更新凭证"""
    print("=== 更新微信公众号API凭证 ===")
    print("请输入您的微信公众号开发者凭证，用于发布文章到公众号草稿箱。")
    print("您可以在微信公众平台 -> 设置与开发 -> 基本配置中获取这些信息。\n")
    
    # 获取当前凭证
    current_app_id, current_app_secret = get_current_credentials()
    
    # 输入新凭证，支持回车保留当前值
    print(f"当前App ID: {current_app_id or '未设置'}")
    while True:
        app_id_input = input("请输入新的App ID (回车保留当前值): ").strip()
        if not app_id_input:
            app_id = current_app_id
            break
        elif re.match(r'^[a-zA-Z0-9]+$', app_id_input):
            app_id = app_id_input
            break
        print("App ID格式不正确，请输入字母和数字的组合。")
    
    print(f"当前App Secret: {'***' if current_app_secret else '未设置'}")
    while True:
        app_secret_input = getpass.getpass("请输入新的App Secret (回车保留当前值，输入时不显示): ").strip()
        if not app_secret_input:
            app_secret = current_app_secret
            break
        elif len(app_secret_input) > 10:
            app_secret = app_secret_input
            break
        print("App Secret格式不正确，请输入有效的Secret（长度应大于10个字符）。")
    
    # 检查是否有变化
    if app_id == current_app_id and app_secret == current_app_secret:
        print("\n⚠️  凭证未发生变化，无需更新。")
        return False
    
    # 更新环境变量
    if app_id:
        os.environ[APP_ID_VAR] = app_id
    else:
        if APP_ID_VAR in os.environ:
            del os.environ[APP_ID_VAR]
    
    if app_secret:
        os.environ[APP_SECRET_VAR] = app_secret
    else:
        if APP_SECRET_VAR in os.environ:
            del os.environ[APP_SECRET_VAR]
    
    # 更新.env文件
    env_content = load_env_file()
    
    app_id_found = False
    app_secret_found = False
    
    for i, line in enumerate(env_content):
        if line.strip().startswith(f'{APP_ID_VAR}='):
            if app_id:
                env_content[i] = f"{APP_ID_VAR}={app_id}\n"
            else:
                del env_content[i]
            app_id_found = True
        elif line.strip().startswith(f'{APP_SECRET_VAR}='):
            if app_secret:
                env_content[i] = f"{APP_SECRET_VAR}={app_secret}\n"
            else:
                del env_content[i]
            app_secret_found = True
    
    if app_id and not app_id_found:
        env_content.append(f"{APP_ID_VAR}={app_id}\n")
    if app_secret and not app_secret_found:
        env_content.append(f"{APP_SECRET_VAR}={app_secret}\n")
    
    # 保存.env文件
    save_env_file(env_content)
    
    print("\n✅ 凭证更新成功！")
    print(f"App ID: {'已设置' if app_id else '未设置'}")
    print(f"App Secret: {'已设置' if app_secret else '未设置'}")
    
    return True


def delete_credentials():
    """删除凭证"""
    print("=== 删除微信公众号API凭证 ===")
    
    # 获取当前凭证
    app_id, app_secret = get_current_credentials()
    
    if not app_id and not app_secret:
        print("⚠️  没有可删除的凭证。")
        return False
    
    # 确认删除
    confirm = input("确定要删除微信公众号API凭证吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("⚠️  删除操作已取消。")
        return False
    
    # 删除环境变量
    if APP_ID_VAR in os.environ:
        del os.environ[APP_ID_VAR]
    if APP_SECRET_VAR in os.environ:
        del os.environ[APP_SECRET_VAR]
    
    # 删除.env文件中的凭证
    env_content = load_env_file()
    new_env_content = []
    
    for line in env_content:
        if not (line.strip().startswith(f'{APP_ID_VAR}=') or line.strip().startswith(f'{APP_SECRET_VAR}=')):
            new_env_content.append(line)
    
    # 保存.env文件
    save_env_file(new_env_content)
    
    print("\n✅ 凭证删除成功！")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微信公众号API凭证管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 查看凭证命令
    subparsers.add_parser('view', help='查看当前凭证')
    
    # 更新凭证命令
    subparsers.add_parser('update', help='更新凭证')
    
    # 删除凭证命令
    subparsers.add_parser('delete', help='删除凭证')
    
    # 解析参数
    args = parser.parse_args()
    
    # 加载.env文件
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')
    
    # 执行命令
    if args.command == 'view':
        view_credentials()
    elif args.command == 'update':
        update_credentials()
    elif args.command == 'delete':
        delete_credentials()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
