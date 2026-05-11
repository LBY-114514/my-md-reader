"""Markdown 文件阅读器 — 主入口。"""

import os
import sys
import json
import webview

from backend import read_file, scan_folder, is_markdown_file


def get_frontend_path():
    """获取前端文件夹路径，兼容开发环境和 PyInstaller 打包。"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'frontend')


class MarkdownReaderApi:
    """暴露给前端 JS 的 API，通过 pywebview JS Bridge 调用。"""

    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def read_file(self, path: str) -> str:
        """读取 .md 文件内容。"""
        try:
            return read_file(path)
        except Exception as e:
            return f"__ERROR__:{str(e)}"

    def scan_folder(self, path: str) -> str:
        """扫描文件夹，返回 JSON 格式的文件列表。"""
        try:
            files = scan_folder(path)
            return json.dumps({"ok": True, "files": files, "folder": path})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    def open_file_dialog(self) -> str:
        """打开系统文件选择对话框，读取文件并返回内容。"""
        file_types = ('Markdown 文件 (*.md)',)
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG, file_types=file_types
        )
        if not result:
            return ""

        file_path = result[0] if isinstance(result, (list, tuple)) else result
        try:
            content = read_file(file_path)
            return json.dumps({
                "ok": True,
                "path": file_path,
                "name": os.path.basename(file_path),
                "content": content,
            })
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    def open_folder_dialog(self) -> str:
        """打开系统文件夹选择对话框，扫描并返回 .md 文件列表。"""
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return ""

        folder_path = result[0] if isinstance(result, (list, tuple)) else result
        try:
            files = scan_folder(folder_path)
            return json.dumps({
                "ok": True,
                "files": files,
                "folder": folder_path,
            })
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})


def main():
    api = MarkdownReaderApi()
    frontend_dir = get_frontend_path()
    index_path = os.path.join(frontend_dir, 'index.html')

    window = webview.create_window(
        title='Markdown Reader',
        url=index_path,
        js_api=api,
        width=1200,
        height=800,
        min_size=(600, 400),
    )
    api.set_window(window)

    webview.start()


if __name__ == '__main__':
    main()
