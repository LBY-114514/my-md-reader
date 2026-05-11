# Markdown Reader

一个本地桌面 Markdown 文件阅读器，GitHub 风格的渲染效果，代码块可以一键复制。

## 功能

- **GitHub 风格渲染** — 标题、表格、引用块、代码块都和 GitHub 显示效果一致
- **代码语法高亮** — 自动识别编程语言，多种语言支持
- **一键复制代码** — 鼠标悬停代码块，右上角出现复制按钮
- **标题锚点链接** — 鼠标悬停标题出现 # 图标，点击可定位到对应位置
- **拖拽打开** — 把 .md 文件直接拖进窗口即可阅读
- **文件夹浏览** — 打开文件夹后左侧出现文件列表，点击切换阅读

## 使用方式

### 方式一：直接运行 .exe（推荐）

从 [Releases](https://github.com/LBY-114514/my-md-reader/releases) 页面下载 `MarkdownReader.exe`，双击运行即可，无需安装 Python。

### 方式二：从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/LBY-114514/my-md-reader.git
cd my-md-reader

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python main.py
```

依赖仅 `pywebview`，Windows 11 自带 WebView2 运行时，无需额外安装。

## 操作说明

| 操作 | 方法 |
|------|------|
| 打开单个文件 | 拖拽 .md 文件到窗口，或菜单 `文件 → 打开文件` |
| 打开文件夹 | 菜单 `文件 → 打开文件夹`，选择包含 .md 文件的目录 |
| 切换文件 | 在左侧文件列表点击文件名 |
| 显示/隐藏侧边栏 | 菜单 `视图 → 切换侧边栏` |
| 复制代码 | 鼠标悬停代码块，点击右上角"复制"按钮 |
| 跳转到标题 | 鼠标悬停标题，点击左侧 # 图标 |

## 界面说明

启动后是一个拖拽区域，拖入 .md 文件或点击即可打开。

打开文件夹后，左侧会出现文件列表（蓝色高亮为当前文件），右侧是 Markdown 渲染内容。

## 技术栈

- Python + [pywebview](https://pywebview.flowrl.com/) — 桌面窗口
- [marked.js](https://marked.js.org/) — Markdown 解析
- [highlight.js](https://highlightjs.org/) — 代码语法高亮
- [PyInstaller](https://pyinstaller.org/) — 打包为 .exe

## 自行打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "frontend;frontend" --name "MarkdownReader" main.py
```

打包结果在 `dist/MarkdownReader.exe`。
