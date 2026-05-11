# Markdown 文件阅读器 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个本地桌面 Markdown 文件阅读器，GitHub 风格渲染，支持代码复制和拖拽/文件夹浏览。

**Architecture:** pywebview 桌面窗口嵌入前端页面，Python 后端处理文件操作（读取、文件夹扫描），前端用 marked.js + highlight.js 渲染 Markdown。Python 和 JS 通过 pywebview 的 JS Bridge 通信。

**Tech Stack:** Python 3, pywebview 4.x, marked.js, highlight.js, PyInstaller (打包)

**注：** 所有 Python 命令需在 `forskills` conda 环境中执行。

---

### Task 1: 项目初始化

**目标：** 创建项目骨架，初始化 Git，配置 .gitignore，安装依赖。

**创建文件：**
- `.gitignore`
- `requirements.txt`
- `frontend/` 目录（占位）
- `frontend/libs/` 目录（占位）

- [ ] **Step 1: 初始化 Git 仓库**

```bash
cd "D:/Markdown文件阅读器" && git init
```

- [ ] **Step 2: 创建 .gitignore**

文件内容：
```
__pycache__/
*.pyc
*.pyo
.superpowers/
dist/
build/
*.spec
.conda/
```

- [ ] **Step 3: 创建 requirements.txt**

```
pywebview>=4.0
pyinstaller>=6.0
```

- [ ] **Step 4: 创建前端目录结构**

```bash
mkdir -p frontend/libs
```

- [ ] **Step 5: 安装 Python 依赖**

```bash
conda activate forskills && pip install -r requirements.txt
```

- [ ] **Step 6: 提交**

```bash
git add .gitignore requirements.txt frontend/
git commit -m "chore: init project structure"
```

---

### Task 2: 下载前端库文件

**目标：** 下载 marked.js、highlight.js 及其 GitHub 主题 CSS，本地存放。

**创建文件：**
- `frontend/libs/marked.min.js`
- `frontend/libs/highlight.min.js`
- `frontend/libs/github.min.css`

- [ ] **Step 1: 下载 marked.min.js**

```bash
curl -o frontend/libs/marked.min.js https://cdn.jsdelivr.net/npm/marked/marked.min.js
```

- [ ] **Step 2: 下载 highlight.min.js**

```bash
curl -o frontend/libs/highlight.min.js https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/highlight.min.js
```

- [ ] **Step 3: 下载 github 主题 CSS**

```bash
curl -o frontend/libs/github.min.css https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/styles/github.min.css
```

- [ ] **Step 4: 验证文件已下载**

```bash
ls -la frontend/libs/
```

预期输出：三个文件均存在且大小 > 0。

- [ ] **Step 5: 提交**

```bash
git add frontend/libs/
git commit -m "chore: add frontend libraries (marked.js, highlight.js)"
```

---

### Task 3: 后端文件操作模块 (backend.py)

**目标：** 实现 Python 端的文件读取和文件夹扫描功能，作为 pywebview JS API 暴露给前端。

**创建文件：**
- `backend.py`

- [ ] **Step 1: 创建 backend.py**

```python
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
```

- [ ] **Step 2: 同步验证 — 在 Python 中手动测试**

```bash
conda activate forskills && python -c "
from backend import read_file, scan_folder, is_markdown_file
print('read_file and scan_folder imported successfully')
print('is_markdown_file test.md:', is_markdown_file('test.md'))
print('is_markdown_file test.txt:', is_markdown_file('test.txt'))
"
```

- [ ] **Step 3: 提交**

```bash
git add backend.py
git commit -m "feat: add backend file operations module"
```

---

### Task 4: 前端主页面结构与样式 (index.html)

**目标：** 创建前端 HTML 页面，包含 GitHub 风格的基础 CSS、内容区、侧边栏结构、拖拽区域。

**创建文件：**
- `frontend/index.html`

- [ ] **Step 1: 创建 index.html 基础结构**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Markdown Reader</title>
<link rel="stylesheet" href="libs/github.min.css">
<style>
  /* === 全局 === */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --color-bg: #ffffff;
    --color-text: #1f2328;
    --color-text-secondary: #656d76;
    --color-border: #d0d7de;
    --color-sidebar-bg: #f6f8fa;
    --color-code-bg: #f6f8fa;
    --color-accent: #0969da;
    --max-content-width: 900px;
    --sidebar-width: 260px;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
      Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: var(--color-text);
    background: var(--color-bg);
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  /* === 侧边栏 === */
  #sidebar {
    width: var(--sidebar-width);
    min-width: 200px;
    max-width: 400px;
    background: var(--color-sidebar-bg);
    border-right: 1px solid var(--color-border);
    display: none;
    flex-direction: column;
    overflow: hidden;
    resize: horizontal;
  }

  #sidebar.visible { display: flex; }

  #sidebar-header {
    padding: 12px 16px;
    font-weight: 600;
    font-size: 14px;
    color: var(--color-text-secondary);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  #sidebar-header button {
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 6px;
    cursor: pointer;
    padding: 2px 8px;
    font-size: 14px;
    color: var(--color-text-secondary);
  }

  #sidebar-header button:hover { background: #eaeef2; }

  #file-list {
    list-style: none;
    overflow-y: auto;
    flex: 1;
    padding: 8px 0;
  }

  #file-list li {
    padding: 6px 16px;
    cursor: pointer;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #file-list li:hover { background: #eaeef2; }
  #file-list li.active {
    background: #ddf4ff;
    color: var(--color-accent);
    font-weight: 500;
  }

  /* === 主内容区 === */
  #main {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  /* === 拖拽区域 === */
  #drop-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    color: var(--color-text-secondary);
    border: 2px dashed var(--color-border);
    border-radius: 12px;
    margin: 40px;
    transition: border-color 0.2s, background 0.2s;
    cursor: pointer;
    min-height: 300px;
  }

  #drop-zone.drag-over {
    border-color: var(--color-accent);
    background: #ddf4ff;
  }

  #drop-zone .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.6; }
  #drop-zone .title { font-size: 20px; font-weight: 500; margin-bottom: 8px; }
  #drop-zone .subtitle { font-size: 14px; }

  /* === 内容容器 === */
  #content {
    max-width: var(--max-content-width);
    margin: 0 auto;
    padding: 32px 48px;
    width: 100%;
    display: none;
  }

  #content.visible { display: block; }

  /* === Markdown 内容样式（参考 GitHub） === */
  .markdown-body { font-size: 16px; }

  .markdown-body h1, .markdown-body h2, .markdown-body h3,
  .markdown-body h4, .markdown-body h5, .markdown-body h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
    position: relative;
  }

  .markdown-body h1 {
    font-size: 2em;
    padding-bottom: 0.3em;
    border-bottom: 1px solid var(--color-border);
  }
  .markdown-body h2 {
    font-size: 1.5em;
    padding-bottom: 0.3em;
    border-bottom: 1px solid var(--color-border);
  }
  .markdown-body h3 { font-size: 1.25em; }
  .markdown-body h4 { font-size: 1em; }

  .markdown-body p { margin-bottom: 16px; }

  .markdown-body a { color: var(--color-accent); text-decoration: none; }
  .markdown-body a:hover { text-decoration: underline; }

  .markdown-body ul, .markdown-body ol { margin-bottom: 16px; padding-left: 2em; }
  .markdown-body li { margin-bottom: 4px; }

  .markdown-body blockquote {
    padding: 0 1em;
    color: var(--color-text-secondary);
    border-left: 0.25em solid var(--color-border);
    margin-bottom: 16px;
  }

  .markdown-body table {
    border-collapse: collapse;
    margin-bottom: 16px;
    width: 100%;
  }
  .markdown-body th, .markdown-body td {
    padding: 6px 13px;
    border: 1px solid var(--color-border);
  }
  .markdown-body th { font-weight: 600; background: var(--color-sidebar-bg); }

  .markdown-body hr {
    border: 0;
    height: 0.25em;
    background: var(--color-border);
    margin: 24px 0;
  }

  /* 代码块（未高亮时的基础样式） */
  .markdown-body code {
    background: var(--color-code-bg);
    border-radius: 6px;
    padding: 0.2em 0.4em;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
      "Liberation Mono", monospace;
    font-size: 85%;
  }

  .markdown-body pre {
    background: var(--color-code-bg);
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin-bottom: 16px;
    position: relative;
  }

  .markdown-body pre code {
    background: none;
    padding: 0;
    font-size: 85%;
    line-height: 1.45;
  }

  /* === 复制按钮 === */
  .copy-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    padding: 4px 12px;
    font-size: 12px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    cursor: pointer;
    color: var(--color-text-secondary);
    opacity: 0;
    transition: opacity 0.15s;
  }

  .markdown-body pre:hover .copy-btn { opacity: 1; }
  .copy-btn:hover { background: #eaeef2; }
  .copy-btn.copied { color: #1a7f37; border-color: #1a7f37; }

  /* === 标题锚点 === */
  .anchor-link {
    position: absolute;
    left: -24px;
    top: 0;
    opacity: 0;
    color: var(--color-text-secondary);
    text-decoration: none;
    font-size: 0.85em;
    padding: 0 4px;
    transition: opacity 0.15s;
  }

  .markdown-body h1:hover .anchor-link,
  .markdown-body h2:hover .anchor-link,
  .markdown-body h3:hover .anchor-link,
  .markdown-body h4:hover .anchor-link,
  .markdown-body h5:hover .anchor-link,
  .markdown-body h6:hover .anchor-link { opacity: 1; }

  /* === 响应式 === */
  @media (max-width: 768px) {
    #content { padding: 16px 24px; }
  }
</style>
</head>
<body>

<!-- 侧边栏 -->
<nav id="sidebar">
  <div id="sidebar-header">
    <span id="sidebar-title">文件列表</span>
    <button id="sidebar-toggle" title="收起侧边栏">&lt;</button>
  </div>
  <ul id="file-list"></ul>
</nav>

<!-- 主内容区 -->
<main id="main">
  <!-- 拖拽区域 -->
  <div id="drop-zone">
    <div class="icon">📄</div>
    <div class="title">打开 Markdown 文件</div>
    <div class="subtitle">拖拽 .md 文件到此处，或点击选择文件</div>
  </div>

  <!-- 内容容器 -->
  <div id="content" class="markdown-body"></div>
</main>

<script src="libs/marked.min.js"></script>
<script src="libs/highlight.min.js"></script>
</body>
</html>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add frontend HTML structure and GitHub-like styles"
```

---

### Task 5: 前端 JavaScript 逻辑

**目标：** 实现 Markdown 渲染、代码高亮、复制按钮、锚点链接、拖拽读取、文件列表切换。

**修改文件：**
- `frontend/index.html` — 在 `</body>` 前添加 JS 逻辑

- [ ] **Step 1: 添加 Markdown 渲染和代码高亮逻辑**

在 `</body>` 前（`<script src="libs/highlight.min.js"></script>` 之后）插入：

```html
<script>
// === Markdown 渲染配置 ===
marked.setOptions({
  gfm: true,
  breaks: false,
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (_) {}
    }
    try {
      return hljs.highlightAuto(code).value;
    } catch (_) {}
    return code;
  }
});

// === 状态 ===
let currentFilePath = null;
let currentFolderPath = null;
let fileListData = [];

// === 渲染 Markdown ===
function renderMarkdown(markdownText) {
  const html = marked.parse(markdownText);
  contentEl.innerHTML = html;

  // 给标题加锚点
  contentEl.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
    if (!heading.id) {
      heading.id = generateId(heading.textContent);
    }
    const anchor = document.createElement('a');
    anchor.className = 'anchor-link';
    anchor.href = '#' + heading.id;
    anchor.textContent = '#';
    heading.appendChild(anchor);
  });

  // 给代码块加复制按钮
  contentEl.querySelectorAll('pre').forEach(pre => {
    if (pre.querySelector('.copy-btn')) return;
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = '复制';
    btn.addEventListener('click', function() {
      const code = pre.querySelector('code') || pre;
      navigator.clipboard.writeText(code.textContent).then(() => {
        btn.textContent = '已复制 ✓';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = '复制';
          btn.classList.remove('copied');
        }, 2000);
      }).catch(() => {
        // fallback: 使用 execCommand
        const textarea = document.createElement('textarea');
        textarea.value = code.textContent;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        btn.textContent = '已复制 ✓';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = '复制';
          btn.classList.remove('copied');
        }, 2000);
      });
    });
    pre.appendChild(btn);
  });
}

function generateId(text) {
  return text.toLowerCase().trim()
    .replace(/[^\w一-鿿\s-]/g, '')
    .replace(/\s+/g, '-');
}

// === DOM 引用 ===
const dropZone = document.getElementById('drop-zone');
const contentEl = document.getElementById('content');
const sidebar = document.getElementById('sidebar');
const fileList = document.getElementById('file-list');
const sidebarTitle = document.getElementById('sidebar-title');
const sidebarToggle = document.getElementById('sidebar-toggle');

// === 显示/隐藏拖拽区 ===
function showDropZone(show) {
  dropZone.style.display = show ? 'flex' : 'none';
  if (show) {
    contentEl.classList.remove('visible');
    contentEl.innerHTML = '';
  }
}

function showContent(show) {
  if (show) {
    contentEl.classList.add('visible');
  } else {
    contentEl.classList.remove('visible');
    contentEl.innerHTML = '';
  }
}

// === 侧边栏 ===
sidebarToggle.addEventListener('click', () => {
  sidebar.classList.remove('visible');
});

function showSidebar(files, folderPath) {
  currentFolderPath = folderPath;
  fileListData = files;
  sidebarTitle.textContent = folderPath.split(/[/\\]/).pop() || '文件列表';
  sidebar.classList.add('visible');
  fileList.innerHTML = '';
  files.forEach((file, index) => {
    const li = document.createElement('li');
    li.textContent = file.name;
    li.title = file.path;
    li.addEventListener('click', () => openFileFromList(index));
    fileList.appendChild(li);
  });
}

function openFileFromList(index) {
  const file = fileListData[index];
  if (!file) return;
  // 调用 Python 后端读取文件
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.read_file(file.path).then(content => {
      currentFilePath = file.path;
      showDropZone(false);
      showContent(true);
      renderMarkdown(content);
      // 高亮当前项
      document.querySelectorAll('#file-list li').forEach((li, i) => {
        li.classList.toggle('active', i === index);
      });
    }).catch(err => {
      alert('读取文件失败: ' + err);
    });
  }
}

// === 拖拽处理 ===
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.remove('drag-over');

  const files = e.dataTransfer.files;
  if (files.length === 0) return;

  const file = files[0];
  if (!file.name.toLowerCase().endsWith('.md')) {
    alert('仅支持 .md 文件');
    return;
  }

  const reader = new FileReader();
  reader.onload = function(ev) {
    currentFilePath = file.name;
    showDropZone(false);
    showContent(true);
    renderMarkdown(ev.target.result);
    sidebar.classList.remove('visible');
  };
  reader.readAsText(file, 'UTF-8');
});

// === 点击拖拽区 → 通过 Python 打开文件对话框 ===
dropZone.addEventListener('click', () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.open_file_dialog().then(result => {
      if (!result) return; // 用户取消
      currentFilePath = result.path;
      showDropZone(false);
      showContent(true);
      renderMarkdown(result.content);
      sidebar.classList.remove('visible');
    }).catch(err => {
      console.error('打开文件失败:', err);
    });
  }
});

// === 暴露给 Python 调用的函数 ===
function loadFileContent(filePath, content) {
  currentFilePath = filePath;
  showDropZone(false);
  showContent(true);
  renderMarkdown(content);
}

function loadFolder(fileList, folderPath) {
  showDropZone(false);
  showSidebar(fileList, folderPath);
  if (fileList.length > 0) {
    openFileFromList(0);
  } else {
    showContent(true);
    contentEl.innerHTML = '<p style="text-align:center;color:#656d76;padding:48px;">该文件夹中没有 .md 文件</p>';
  }
}

function showWelcome() {
  showDropZone(true);
  currentFilePath = null;
  sidebar.classList.remove('visible');
}
</script>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add frontend JS logic (render, copy, anchor, drag-drop)"
```

---

### Task 6: Pywebview 主窗口与 JS Bridge (main.py)

**目标：** 创建主 Python 文件，配置 pywebview 窗口、菜单栏，定义 JS API 接口，连接前端。

**创建文件：**
- `main.py`

- [ ] **Step 1: 创建 main.py**

```python
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
```

- [ ] **Step 2: 验证应用能启动**

```bash
conda activate forskills && python main.py
```

预期：打开桌面窗口，显示拖拽区域页面。关闭窗口后继续。

- [ ] **Step 3: 提交**

```bash
git add main.py
git commit -m "feat: add pywebview main window with JS Bridge API"
```

---

### Task 7: 集成菜单栏与打开文件夹功能

**目标：** 完善 main.py，添加菜单栏（打开文件、打开文件夹、切换侧边栏），实现从菜单打开文件夹后前端显示侧边栏。

**修改文件：**
- `main.py` — 添加菜单和文件/文件夹打开流程

- [ ] **Step 1: 更新 main.py，添加菜单栏和完整交互逻辑**

将 `main.py` 替换为以下完整版本：

```python
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


def on_open_file(api, window):
    """菜单：打开文件。"""
    result = api.open_file_dialog()
    if result:
        data = json.loads(result)
        if data.get("ok"):
            window.evaluate_js(
                f"loadFileContent({json.dumps(data['path'])}, {json.dumps(data['content'])})"
            )


def on_open_folder(api, window):
    """菜单：打开文件夹。"""
    result = api.open_folder_dialog()
    if result:
        data = json.loads(result)
        if data.get("ok"):
            window.evaluate_js(
                f"loadFolder({json.dumps(data['files'])}, {json.dumps(data['folder'])})"
            )


def on_toggle_sidebar(window):
    """菜单：切换侧边栏。"""
    window.evaluate_js(
        "document.getElementById('sidebar').classList.toggle('visible')"
    )


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

    # 构建菜单
    menu_items = [
        webview.Menu(
            '文件',
            [
                webview.MenuAction('打开文件', lambda: on_open_file(api, window)),
                webview.MenuAction('打开文件夹', lambda: on_open_folder(api, window)),
                webview.MenuSeparator(),
                webview.MenuAction('退出', lambda: window.destroy()),
            ],
        ),
        webview.Menu(
            '视图',
            [
                webview.MenuAction('切换侧边栏', lambda: on_toggle_sidebar(window)),
            ],
        ),
    ]

    webview.start(menu=menu_items)


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 测试完整流程**

```bash
conda activate forskills && python main.py
```

手动测试：
1. 窗口打开后看到拖拽区域 ✓
2. 菜单 "文件 → 打开文件"，选择一个 .md 文件，内容正确渲染 ✓
3. 菜单 "文件 → 打开文件夹"，选择一个包含 .md 文件的文件夹，侧边栏显示文件列表 ✓
4. 点击侧边栏文件，内容切换 ✓
5. 代码块显示复制按钮，点击复制成功 ✓
6. 标题悬停显示锚点链接 ✓

- [ ] **Step 3: 提交**

```bash
git add main.py
git commit -m "feat: add menu bar and full file/folder interaction flow"
```

---

### Task 8: 修复与打磨

**目标：** 修复集成测试中发现的问题，打磨细节。

- [ ] **Step 1: 确认侧边栏内的"收起"按钮和菜单"切换侧边栏"功能正常**

前端 `#sidebar-header` 中的收起按钮应该隐藏侧边栏，菜单"视图 → 切换侧边栏"可以重新打开。

如需修复前端 JS，添加以下逻辑（如果尚未添加）：

```javascript
// 侧边栏头部也有了收起按钮的引用，在现有代码中确保：
sidebarToggle.addEventListener('click', () => {
  sidebar.classList.remove('visible');
});
```

- [ ] **Step 2: 确认前端文件读取错误时的用户提示**

在 `openFileFromList` 中的 catch 已包含 `alert`，确认无误。

- [ ] **Step 3: 确认拖拽多个文件时仅处理第一个**

前端 drop 事件中已用 `files[0]`，确认无误。

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "fix: sidebar toggle and error handling polish"
```

---

### Task 9: 推送到 GitHub

**目标：** 将代码推送到 GitHub 远程仓库。

- [ ] **Step 1: 查看当前提交历史**

```bash
git log --oneline
```

- [ ] **Step 2: 添加远程仓库**

```bash
git remote add origin https://github.com/LBY-114514/my-md-reader.git
```

- [ ] **Step 3: 推送到 GitHub**

```bash
git push -u origin main
```

如果默认分支名是 `master` 则用：
```bash
git branch -m main
git push -u origin main
```

- [ ] **Step 4: 确认推送成功**

在浏览器打开 https://github.com/LBY-114514/my-md-reader 确认文件已上传。

---

### Task 10: PyInstaller 打包为 .exe

**目标：** 将应用打包为单个 .exe 文件，可独立运行。

- [ ] **Step 1: 确认 PyInstaller 已安装**

```bash
conda activate forskills && pip install pyinstaller
```

- [ ] **Step 2: 创建打包 spec 文件（可选，直接命令行更简单）**

```bash
conda activate forskills && cd "D:/Markdown文件阅读器" && pyinstaller --onefile --windowed --add-data "frontend;frontend" --name "MarkdownReader" main.py
```

参数说明：
- `--onefile`：打包为单个 .exe
- `--windowed`：不显示命令行窗口
- `--add-data "frontend;frontend"`：将 frontend 文件夹嵌入 exe（Windows 用分号分隔）
- `--name "MarkdownReader"`：输出文件名

- [ ] **Step 3: 测试打包后的 .exe**

```bash
ls dist/
```

运行 `dist/MarkdownReader.exe`，确认：
1. 窗口正常打开
2. 拖拽 .md 文件正常工作
3. 菜单打开文件/文件夹正常
4. 代码高亮和复制按钮正常

- [ ] **Step 4: 添加打包配置到 .gitignore（如未添加）**

确认 `.gitignore` 包含：
```
dist/
build/
*.spec
```

- [ ] **Step 5: 提交最终代码**

```bash
git add .
git commit -m "chore: finalize project, add PyInstaller build support"
git push
```
