# ChatGPT 橙皮书

> 一本写给开发者、独立开发者和 AI 工具重度用户的 ChatGPT 智能体与 Codex 非官方开源指南。

作者 X/Twitter：

- [@Vinkyu567](https://x.com/Vinkyu567)
- [@bozhou_ai](https://x.com/bozhou_ai)

## 这是什么

《ChatGPT 橙皮书》是一份围绕 ChatGPT Work、Codex 及相关实际使用场景整理的中文指南，目标是帮助读者把智能体能力放进真实工作与软件项目中使用。

它不是 OpenAI 官方文档，也不代表官方产品承诺；书中内容主要基于公开能力、实际界面和实战案例整理，适合作为上手路线、工作流参考和案例材料阅读。

## 阅读入口

- [在线阅读](https://bozhoudev.github.io/codex-orange-book/)
- [完整 Markdown 原稿](./ChatGPT橙皮书.md)
- [下载 PDF](https://raw.githubusercontent.com/bozhouDev/codex-orange-book/main/ChatGPT%E6%A9%99%E7%9A%AE%E4%B9%A6.pdf)
- [预览 PDF](./ChatGPT橙皮书.preview.pdf)

## 内容包括

- Codex 的基础认知：它和 ChatGPT、Cursor 等工具的区别。
- 安装、配置与环境准备：Codex App、CLI、IDE Extension、Web / Cloud 等入口。
- 核心能力拆解：Work、Sites、自动化、插件、Skill、MCP、Git / GitHub 工作流、云端运行、记忆系统和 Chrome 扩展。
- 标准工作流：从需求拆解、计划、实现、验证到交付的完整链路。
- 实战案例：用 Codex 制作前端页面、优化功能、搭建管理后台、生成 PPT 和宣传视频。
- 扩展附录：第三方模型接入等非官方玩法记录。

## 仓库结构

```text
.
├── ChatGPT橙皮书.md            # 完整 Markdown 正文
├── ChatGPT橙皮书.pdf           # 完整 PDF
├── ChatGPT橙皮书.preview.pdf   # 便于 GitHub 预览的 PDF
├── index.html                  # PDF 在线阅读器
├── book.html                   # PDF 排版与导出的中间页面
├── cover.html                  # 封面页面
├── assets/images/              # 正文配图
├── site/                       # 可直接部署的完整静态网站
└── tools/                      # PDF、静态网站构建与检查脚本
```

其中 `site/index.html` 是同步完整正文后的静态网站入口；根目录的 `index.html` 主要用于在线打开 PDF。

## 说明

Codex 更新很快，安装方式、模型名称、额度、入口位置和命令参数都可能变化。涉及具体功能、价格和账号能力时，请以 OpenAI 官方文档、Codex 当前版本和你账号实际显示为准。

## License

本项目采用 [MIT License](./LICENSE) 开源。
