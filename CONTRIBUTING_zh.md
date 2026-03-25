# 参与贡献 bpftime

bpftime 团队欢迎社区反馈和贡献。
感谢你希望让 bpftime 变得更好！你可以通过多种方式参与进来。

如果你正在寻找一个适合开始贡献的方向，可以：

* 查看 [可用的 issue 模板](https://github.com/eunomia-bpf/bpftime/issues/new/choose)，并浏览 [适合新手的 issue 示例](https://github.com/eunomia-bpf/bpftime/contribute)（或者 [点这里](https://github.com/eunomia-bpf/bpftime/labels/good%20first%20issue)）。

* 浏览 [需要帮助的 issues](https://github.com/eunomia-bpf/bpftime/labels/help%20wanted)。

## 报告问题和建议新特性

如果你发现项目运行不正常，请使用 [Bug Report 模板](https://github.com/eunomia-bpf/bpftime/issues/new?assignees=&labels=bug&template=bug_report.md&title=[BUG]) 提交报告。
如果默认模板不符合你的需要，也可以提交 [Custom Issue Report](https://github.com/eunomia-bpf/bpftime/issues/new?assignees=&labels=&projects=&template=custom.md&title=)，但请为它添加合适的标签。

我们也很愿意听到你关于如何进一步改进 bpftime 的想法，以确保它更符合你的需求。你可以查看 [Issues](https://github.com/eunomia-bpf/bpftime/issues)，看看是否已经有其他人提交了类似反馈。你可以通过点赞已有反馈（用 thumbs up reaction / 评论）来支持，也可以 [提交新的建议](https://github.com/eunomia-bpf/bpftime/labels/feature)。

我们在决定下一步优先做什么时，始终会关注 [Issues](https://github.com/eunomia-bpf/bpftime/issues) 中获得较多点赞的项目。我们会阅读评论，也期待听到你的意见。

## 寻找你可以帮助的问题

想找点事情做？
标有 [`good first issue`](https://github.com/eunomia-bpf/bpftime/labels/good%20first%20issue) 的 issue 是很好的起点。

你也可以查看 [`help wanted`](https://github.com/eunomia-bpf/bpftime/labels/help%20wanted) 标签，寻找其他可以帮助的问题。如果你有兴趣修复某个问题，请留个评论告诉大家，以避免别人重复劳动。

## 我们接受的贡献

我们非常欢迎任何有助于改进最终产品的贡献，尤其是 bug 修复，以及能够直接解决 bpftime 用户高优先级问题的改进。以下是一些通用指南：

### 应该做的

* **DO** 针对每个 Issue 提交一个 Pull Request，并确保在 PR 中关联该 Issue。你可以参考 Pull Request Template。

* **DO** 遵循我们的 [Coding and Style](#style-guidelines) 指南，并尽可能保持代码改动尽量小。

* **DO** 尽可能补充对应测试。

* **DO** 在提交 PR 之前检查代码库其他部分是否也存在同样的问题。

* **DO** 在 Pull Request 中链接你正在处理的 issue。

* **DO** 为你的 Pull Request 写一个清晰的描述。越详细越好。说明为什么要做这个修改，以及为什么选择当前方案。也请写明你做了哪些手动测试来验证变更。

### 不应该做的

* **DO NOT** 把多个修改合并到一个 PR 中，除非它们有相同的根因。

> 提交一个针对已批准 Issue 的 Pull Request，并不意味着它一定会被接受。变更仍然必须满足我们对代码质量、架构和性能的高标准。

## 对代码做修改

### 准备开发环境

要了解如何构建代码并运行测试，请参考 [README](README_zh.md) 中的说明。

### 风格指南

本项目的代码使用了多种不同的编码风格，取决于代码的年代和历史。请尽量保持与周围代码的风格一致。对于新组件，优先采用 [C++ core guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) 中描述的模式。

### 测试

你的改动应当尽可能包含测试，以验证新功能。
代码应当组织成可以独立于 UI 进行单元测试的形式。
如果无法自动化测试，则应使用手动测试用例。

### Git 工作流

项目在 Git 工作流方面的核心原则是：`master` 分支应始终保持健康状态，并且可用于发布。master 上的每个提交都应该在推送后即可部署。为了保证这一点，Pull Request **不能** 直接提交到 master。**每一次修改**都应该在**开发分支**中完成（名字类似 development，例如 `dev`），或者在一个单独分支中完成，分支名应是该修改的简短摘要。

如果你的改动比较复杂，请在提交 PR 之前整理一下分支历史。你可以使用 [git rebase](https://git-scm.com/book/en/v2/Git-Branching-Rebasing) 把修改整理成少量几个 commit，方便我们逐个审查。

在合并 Pull Request 时，我们通常会把你的修改 squash 成一个 commit。确认变更按预期工作之后，该分支可能会被删除，以避免分支污染。如果你的 PR 需要保留为多个独立提交，请提前告诉我们。

### 持续集成

对于这个项目，CI 由 [GitHub Actions](https://github.com/features/actions) 提供，工作流位于 [`.github/workflows` 文件夹](.github/workflows) 中。默认情况下，每次提交到 master 分支时都会自动运行工作流，除非该提交明确要求跳过。

如果你想在某次提交中跳过 CI，可以在提交信息中加入 `[skip ci]` 或 `[ci skip]`。

```bash
# 下面是一个不会触发 CI workflow 的提交信息示例
git commit -m "my normal commit message [skip ci]"
# 或者
git commit -m "my normal commit message [ci skip]"
```

## 审查流程

提交 Pull Request 后，团队成员会审查你的代码。我们会把请求分配给合适的审查者（如果适用）。社区中的任何人都可以参与 review，但最终至少会有一名项目团队成员批准该请求。

通常，审查过程中会出现多轮迭代或讨论。你也可以查看 [过去的 pull request](https://github.com/eunomia-bpf/bpftime/pulls?q=is%3Apr+is%3Aclosed) 了解大致的协作方式。

## 贡献者许可协议

在我们能够审查并接受你的 pull request 之前，你需要先签署 Contributor License Agreement（CLA）。CLA 旨在确保社区可以自由使用你的贡献。签署 CLA 是一个手动流程，而且每个 pull request 都需要单独完成。你可以通过勾选 Pull Request Readiness Checklist 中的相关选项来完成。

### 重要

***勾选上述选项意味着你同意将你的变更和/或代码在整个社区范围内免费使用，并且允许被修改！***

在准备创建 pull request 之前，你不需要先签 CLA。当你的 pull request 创建后，会由一名团队成员进行审查。
