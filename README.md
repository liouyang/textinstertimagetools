# AI 驱动的智能批量文章生成与管理系统

## 项目概述

本项目是一个先进的**AI 驱动内容创作平台**，旨在彻底革新批量文章的生成、精炼、配图和发布流程。它深度整合了**大型语言模型 (LLM)** 和**文生图模型**的能力，能够根据用户设定的`主题`、`受众`、`写作风格`、`文章长度`和`关键词`等精细化参数，**智能撰写高质量、富含信息的文章**。

项目的独特之处在于其**智能图像生成与集成能力**。系统能够理解文章内容，并在适当位置自动生成并嵌入**高度相关的 AI 图像**，实现真正的图文并茂。最终，所有生成的文章和配图将被精心组织，并输出为**独立的、易于分享和发布的 HTML 页面**，从而极大地提升了内容生产效率、内容吸引力和发布便捷性。

## 核心功能亮点

* **全链路自动化内容创作**：提供从文章主题构思（如果批量生成）、标题生成、内容撰写、智能配图到最终 HTML 输出的一站式自动化流程。
* **高度可定制化的文章生成**：
    * **主题与受众定义**：精确设定文章主旨及目标读者群体。
    * **多样化写作风格**：支持选择不同的文章风格（如深度分析、科普、新闻报道等）。
    * **灵活控制文章长度**：可根据需求设定文章的字数范围。
    * **关键词优化**：确保生成的文章包含指定关键词，提升内容相关性和 SEO 潜力。
    * **额外要求定制**：支持输入更具体的写作指令和限制，以实现个性化内容输出。
* **智能图文融合**：
    * 系统通过识别文章内容中预设的 `<IMAGE>` 标记，精准判断图片插入位置。
    * 基于标记所在段落的上下文，智能生成相关的图像描述（Prompt），并调用文生图模型生成图片。
    * 生成的图片将直接编码为 Base64 格式嵌入到最终的 HTML 文件中，确保文章内容与图片的一致性和便携性。
* **高效批量处理**：支持一次性生成多篇文章，并对每一篇的生成过程进行独立控制和状态跟踪。
* **清晰的输出管理**：
    * 所有生成的原始文章文本、图片文件和最终的 HTML 文件都会分类保存到指定目录。
    * 提供便捷的界面，直接预览生成的 HTML 文章，或一键打开文章所在的本地目录。
* **用户友好界面**：采用 Streamlit 构建的响应式 Web 界面，使得操作简单直观，无需复杂的编程或命令行知识。
* **API 后端集成**：通过与阿里云 [通义千问 DashScope](https://www.aliyun.com/product/bailian/dashscope) 大模型服务深度集成，确保生成内容的质量、创造性和多样性，同时利用其文生图能力实现智能配图。

## 技术栈

* **核心编程语言**：Python
* **交互式用户界面**：[Streamlit](https://streamlit.io/)
* **大语言模型 (LLM) 集成**：[DashScope SDK](https://help.aliyun.com/document_detail/2711681.html) (用于文章内容与标题生成)
* **文生图模型集成**：[DashScope SDK](https://help.aliyun.com/document_detail/2711681.html) (用于图片生成，特别是文生图模型如通义万相)
* **文件系统操作**：`os`, `shutil`
* **字符串处理与正则**：`re`, `string.Template`
* **数据序列化**：`json`
* **文本格式化**：`markdown` 库 (将 Markdown 转换为 HTML)
* **网络请求**：`requests` (用于图片下载)
* **应用程序打包**：[PyInstaller](https://pyinstaller.org/en/stable/) (通过 `run_app.py` 脚本实现桌面应用打包)

## 项目文件结构
我深表歉意！您之前看到的格式可能是由于显示方式造成的。我已经为您将完整的 Markdown 描述文本准备好，您可以直接复制粘贴。

请将以下内容直接复制，并保存为 README.md 文件到您的项目根目录。记得根据您的实际情况替换掉 [你的项目Git仓库URL] 和准备好 screenshots 文件夹中的截图。

Markdown

# AI 驱动的智能批量文章生成与管理系统

## 项目概述

本项目是一个先进的**AI 驱动内容创作平台**，旨在彻底革新批量文章的生成、精炼、配图和发布流程。它深度整合了**大型语言模型 (LLM)** 和**文生图模型**的能力，能够根据用户设定的`主题`、`受众`、`写作风格`、`文章长度`和`关键词`等精细化参数，**智能撰写高质量、富含信息的文章**。

项目的独特之处在于其**智能图像生成与集成能力**。系统能够理解文章内容，并在适当位置自动生成并嵌入**高度相关的 AI 图像**，实现真正的图文并茂。最终，所有生成的文章和配图将被精心组织，并输出为**独立的、易于分享和发布的 HTML 页面**，从而极大地提升了内容生产效率、内容吸引力和发布便捷性。

## 核心功能亮点

* **全链路自动化内容创作**：提供从文章主题构思（如果批量生成）、标题生成、内容撰写、智能配图到最终 HTML 输出的一站式自动化流程。
* **高度可定制化的文章生成**：
    * **主题与受众定义**：精确设定文章主旨及目标读者群体。
    * **多样化写作风格**：支持选择不同的文章风格（如深度分析、科普、新闻报道等）。
    * **灵活控制文章长度**：可根据需求设定文章的字数范围。
    * **关键词优化**：确保生成的文章包含指定关键词，提升内容相关性和 SEO 潜力。
    * **额外要求定制**：支持输入更具体的写作指令和限制，以实现个性化内容输出。
* **智能图文融合**：
    * 系统通过识别文章内容中预设的 `<IMAGE>` 标记，精准判断图片插入位置。
    * 基于标记所在段落的上下文，智能生成相关的图像描述（Prompt），并调用文生图模型生成图片。
    * 生成的图片将直接编码为 Base64 格式嵌入到最终的 HTML 文件中，确保文章内容与图片的一致性和便携性。
* **高效批量处理**：支持一次性生成多篇文章，并对每一篇的生成过程进行独立控制和状态跟踪。
* **清晰的输出管理**：
    * 所有生成的原始文章文本、图片文件和最终的 HTML 文件都会分类保存到指定目录。
    * 提供便捷的界面，直接预览生成的 HTML 文章，或一键打开文章所在的本地目录。
* **用户友好界面**：采用 Streamlit 构建的响应式 Web 界面，使得操作简单直观，无需复杂的编程或命令行知识。
* **API 后端集成**：通过与阿里云 [通义千问 DashScope](https://www.aliyun.com/product/bailian/dashscope) 大模型服务深度集成，确保生成内容的质量、创造性和多样性，同时利用其文生图能力实现智能配图。

## 技术栈

* **核心编程语言**：Python
* **交互式用户界面**：[Streamlit](https://streamlit.io/)
* **大语言模型 (LLM) 集成**：[DashScope SDK](https://help.aliyun.com/document_detail/2711681.html) (用于文章内容与标题生成)
* **文生图模型集成**：[DashScope SDK](https://help.aliyun.com/document_detail/2711681.html) (用于图片生成，特别是文生图模型如通义万相)
* **文件系统操作**：`os`, `shutil`
* **字符串处理与正则**：`re`, `string.Template`
* **数据序列化**：`json`
* **文本格式化**：`markdown` 库 (将 Markdown 转换为 HTML)
* **网络请求**：`requests` (用于图片下载)
* **应用程序打包**：[PyInstaller](https://pyinstaller.org/en/stable/) (通过 `run_app.py` 脚本实现桌面应用打包)

## 项目文件结构

```bash
.
├── streamlit_app.py           # Streamlit 主应用入口，负责所有UI交互和核心流程编排
├── batch_article_generator.py # 封装批量生成文章的整体流程，包括标题、内容和图片生成调度
├── article_writer.py          # 专门负责调用LLM生成文章内容的模块，处理文章长度、风格等参数
├── wanxiangimg.py             # 专门负责文生图模型调用、图片下载及Base64编码的模块
├── html_generator.py          # 负责将结构化的文章数据（文本+图片）渲染成完整HTML页面的模块
├── local_license_tool.py      # （根据代码，这是一个用于验证许可证或API密钥的本地工具）
├── run_app.py                 # 用于PyInstaller打包和启动应用的辅助脚本
├── templates/                 # 存放HTML模板文件的目录
│   └── article_template.html  # 用于生成文章HTML的基模板
├── generated_images/          # 存储所有AI生成原始图片文件的目录
├── generated_articles_humanized/ # 存储LLM生成原始文章文本的目录
├── generated_output/          # 最终生成的HTML文章页面存放目录
├── .gitignore                 # Git 版本控制忽略规则文件
└── README.md

## 如何运行项目

### 前提条件

* 确保您的系统中已安装 **Python 3.8 或更高版本**。
* 拥有一个有效的 **DashScope API Key**。

### 步骤

1.  **克隆项目仓库**：
    打开终端或命令行工具，执行以下命令：
    ```bash
    git clone [你的项目Git仓库URL]
    cd [你的项目文件夹名称]
    ```

2.  **创建并激活虚拟环境（强烈推荐）**：
    使用虚拟环境可以隔离项目依赖，避免与系统或其他项目冲突。
    ```bash
    python -m venv venv
    # 激活虚拟环境：
    source venv/bin/activate  # macOS / Linux
    # 或 .\venv\Scripts\activate # Windows (在 PowerShell 中)
    # 或 venv\Scripts\activate.bat # Windows (在 Command Prompt 中)
    ```

3.  **安装项目依赖**：
    项目所需的所有库都在 `requirements.txt` 文件中列出。
    ```bash
    pip install -r requirements.txt
    ```
    (如果您没有 `requirements.txt` 文件，可以通过运行 `pip freeze > requirements.txt` 命令生成，或者手动安装 `streamlit`, `dashscope`, `markdown`, `requests` 等核心依赖)。

4.  **配置 DashScope API Key**：
    将您的 DashScope API Key 设置为环境变量 `DASHSCOPE_API_KEY`。这是推荐的安全做法。
    * **macOS / Linux 用户**：
        将以下行添加到您的 shell 配置文件 (`~/.bashrc`, `~/.zshrc` 或 `~/.profile`)，然后运行 `source` 命令使之生效：
        ```bash
        export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # 替换为你的实际API Key
        ```
    * **Windows 用户**：
        通过系统环境变量设置，或者在 PowerShell/CMD 中临时设置：
        ```powershell
        $env:DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # PowerShell
        # 或 set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx # CMD
        ```
    **注意**：请勿将 API Key 直接硬编码在代码文件中并提交到 Git 仓库。

5.  **运行 Streamlit 应用**：
    在已激活虚拟环境的终端中，运行主应用程序脚本：
    ```bash
    streamlit run streamlit_app.py
    ```
    应用将自动在您的默认网络浏览器中打开，通常地址为 `http://localhost:8501`。

## 截图展示

以下是项目的一些关键界面截图，帮助您直观了解其功能和用户体验：

### 1. 主界面：文章生成参数配置
`![image](https://github.com/liouyang/textinstertimagetools/blob/main/screenshots/381753597131_.pic.jpg)`

`![image](https://github.com/liouyang/textinstertimagetools/blob/main/screenshots/391753597145_.pic.jpg)`

### 2. 生成文章示例（HTML 页面预览）
`![image](https://github.com/liouyang/textinstertimagetools/blob/main/screenshots/WeChatb45b5a8f9a40f0b1f64eb3d52fffcbcd.jpg)`

---

**使用指南：**

* 在配置界面输入您的文章生成需求。
* 点击“开始生成”按钮，系统将根据您的设置批量生成文章和图片。
* 生成进度和状态会在界面上实时显示。
* 完成任务后，您可以在下方列表中查看生成的文章，点击链接进行预览，或点击“打开目录”快速访问文件位置。

---