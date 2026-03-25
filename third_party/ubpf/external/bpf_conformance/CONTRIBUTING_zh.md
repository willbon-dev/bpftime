# 为 BPF Conformance 做贡献

我们很欢迎你帮助 BPF Conformance！下面是贡献指南。

- [行为准则](#code-of-conduct)
- [Bug](#bugs)
- [新功能](#new-features)
- [贡献者许可协议](#contributor-license-agreement)
- [代码贡献](#contributing-code)
  - [测试](#tests)

## 行为准则

本项目采用 [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)。
如需了解更多信息，请参见 [Microsoft Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)，
或者通过 [opencode@microsoft.com](mailto:opencode@microsoft.com) 发送更多问题或意见。

## Bug

### 发现了 bug？

首先，请通过在 GitHub 的 [Issues](https://github.com/Alan-Jowett/bpf_conformance/issues) 中搜索，**确认这个 bug 之前没有被报告过**。

如果你发现的是非安全相关 bug，可以通过[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new) 来帮助我们。
最好的 bug 报告应当提供问题的详细描述，以及能够可靠复现问题的逐步说明。

我们会尽量在每周的 triage 会议中处理这些问题。若我们无法复现该问题，我们会向你请求更多信息。
对所请求信息的等待期为 2 周；如果届时仍没有回复，Issue 将被关闭。如果你后来确实拿到了复现方法，请重新打开 Issue 并补充所需信息。

不过，如果条件允许，我们也欢迎你直接提交一个修复该 bug 的 Pull Request。

如果你发现的是安全问题，请**不要打开 GitHub Issue**，而应按照 [这些说明](docs/SECURITY_zh.md) 处理。

### 你写了一个修复 bug 的补丁？

Fork 这个仓库并完成修改。
然后带着补丁打开一个新的 GitHub Pull Request。

* 确保 PR 描述清楚地说明了问题和解决方案。
如果适用，请带上相关 issue 编号。

* 提交前，请先阅读 [Development Guide](docs/DevelopmentGuide_zh.md) 以了解更多编码规范。

## 新功能

你可以通过[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new) 来请求一个新功能。

如果你想实现一个新功能，请先[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new)，
并说明你的提议，以便社区可以审查并提供反馈。尽早获得反馈有助于确保你的实现工作会被接受。
这也能帮助我们更好地协调工作，减少重复劳动。

## 贡献者许可协议

对于任何代码提交，你都需要完成一份贡献者许可协议（CLA）。
简而言之，这份协议说明你授权我们按项目许可证条款使用你提交的变更，并且你确认所提交的工作拥有适当的版权。
你只需要完成一次。更多信息请见 https://cla.opensource.microsoft.com/。

## 贡献代码

对于除最简单修改之外的所有变更，请先[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new)，
以便社区可以审查并提供反馈。尽早获得反馈有助于确保你的工作会被接受。
这也能帮助我们更好地协调工作，并尽量减少重复劳动。

如果你想贡献代码，请先确定你想贡献的内容规模。如果只是小修改（语法/拼写或 bug 修复），可以直接开始着手修复。
如果你要提交的是功能或较大规模的代码贡献，请先与维护者讨论，并确保它符合产品路线图。
你也可以先阅读下面两篇关于开源贡献的博客：
[Open Source Contribution Etiquette](http://tirania.org/blog/archive/2010/Dec-31.html)（Miguel de Icaza）和
[Don't "Push" Your Pull Requests](https://www.igvita.com/2011/12/19/dont-push-your-pull-requests/)（Ilya Grigorik）。
所有代码提交都会经过维护者严格的[审查](docs/Governance_zh.md)和测试，只有在质量和设计/路线图匹配度都达标时才会合并到源码中。

对于所有新的 Pull Request，适用以下规则：
- 现有测试应当继续通过。
- 每个已完成的 bug/feature 都需要提供测试。
- 每个对终端用户可见的功能都需要提供文档。
