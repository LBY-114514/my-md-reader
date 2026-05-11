"""Markdown 文件阅读器 — 后端文件操作模块。"""

import os
from pathlib import Path


def read_file(path: str) -> str:
    """读取文件内容（UTF-8）。

    Args:
        path: 文件绝对路径

    Returns:
        文件文本内容

    Raises:
        FileNotFoundError: 文件不存在
        UnicodeDecodeError: 编码错误（非 UTF-8 文件）
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return file_path.read_text(encoding="utf-8")


def scan_folder(path: str) -> list[dict]:
    """扫描文件夹中所有 .md 文件。

    Args:
        path: 文件夹绝对路径

    Returns:
        按文件名排序的文件信息列表，每项包含 name, path, size (bytes)
    """
    folder = Path(path)
    if not folder.is_dir():
        raise NotADirectoryError(f"不是有效的文件夹: {path}")

    files = []
    for entry in sorted(folder.iterdir(), key=lambda e: e.name.lower()):
        if entry.is_file() and entry.suffix.lower() == ".md":
            files.append({
                "name": entry.name,
                "path": str(entry.resolve()),
                "size": entry.stat().st_size,
            })
    return files


def is_markdown_file(path: str) -> bool:
    """检查路径是否为 .md 文件。"""
    return Path(path).suffix.lower() == ".md"
