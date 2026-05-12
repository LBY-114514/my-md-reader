"""Markdown 文件阅读器 — 主入口。"""

import os
import sys
import json
import webview
from webview.menu import Menu, MenuAction, MenuSeparator

from backend import read_file, scan_folder


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
        """打开系统文件选择对话框。"""
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
        """打开系统文件夹选择对话框。"""
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


def _show_error(window, msg):
    """在前端显示错误提示。"""
    window.evaluate_js(f"alert({json.dumps(msg, ensure_ascii=False)})")


def on_open_file(api, window):
    """菜单：打开文件。"""
    result = api.open_file_dialog()
    if not result:
        return
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        _show_error(window, "打开文件失败：返回数据异常")
        return
    if data.get("ok"):
        window.evaluate_js(
            f"loadFileContent({json.dumps(data['path'], ensure_ascii=False)},"
            f" {json.dumps(data['content'], ensure_ascii=False)})"
        )
    else:
        _show_error(window, data.get("error", "打开文件失败"))


def on_open_folder(api, window):
    """菜单：打开文件夹。"""
    result = api.open_folder_dialog()
    if not result:
        return
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        _show_error(window, "打开文件夹失败：返回数据异常")
        return
    if data.get("ok"):
        window.evaluate_js(
            f"loadFolder({json.dumps(data['files'], ensure_ascii=False)},"
            f" {json.dumps(data['folder'], ensure_ascii=False)})"
        )
    else:
        _show_error(window, data.get("error", "打开文件夹失败"))


def on_toggle_sidebar(window):
    """菜单：切换侧边栏。"""
    window.evaluate_js("toggleSidebar()")


def main():
    # 检查命令行参数：是否通过"打开方式"传入文件路径
    startup_file = sys.argv[1] if len(sys.argv) > 1 else None
    if startup_file and not os.path.isfile(startup_file):
        startup_file = None

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

    # 构建菜单
    menu_items = [
        Menu(
            '文件',
            [
                MenuAction('打开文件', lambda: on_open_file(api, window)),
                MenuAction('打开文件夹', lambda: on_open_folder(api, window)),
                MenuSeparator(),
                MenuAction('退出', lambda: window.destroy()),
            ],
        ),
        Menu(
            '视图',
            [
                MenuAction('切换侧边栏', lambda: on_toggle_sidebar(window)),
            ],
        ),
    ]

    # 如果有启动文件，页面加载完成后自动打开
    if startup_file:
        def _open_startup_file():
            path = os.path.abspath(startup_file)
            try:
                content = read_file(path)
                # 先加载同文件夹的 .md 文件列表到侧边栏（不自动打开第一个）
                folder = os.path.dirname(path)
                files = scan_folder(folder)
                if len(files) > 1:
                    window.evaluate_js(
                        f"loadFolder({json.dumps(files, ensure_ascii=False)},"
                        f" {json.dumps(folder, ensure_ascii=False)}, false)"
                    )
                # 再加载目标文件（会后执行，正确高亮侧边栏）
                window.evaluate_js(
                    f"loadFileContent({json.dumps(path, ensure_ascii=False)},"
                    f" {json.dumps(content, ensure_ascii=False)})"
                )
            except Exception as e:
                _show_error(window, f"打开文件失败: {e}")

        window.events.loaded += _open_startup_file

    webview.start(menu=menu_items)


if __name__ == '__main__':
    main()
