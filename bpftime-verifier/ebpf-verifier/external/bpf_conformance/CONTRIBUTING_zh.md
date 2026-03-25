# 为 BPF Conformance 贡献

我们非常欢迎你帮助 BPF Conformance！以下是我们的贡献指南。

- [行为准则](#code-of-conduct)
- [Bug](#bugs)
- [新功能](#new-features)
- [贡献者许可协议](#contributor-license-agreement)
- [贡献代码](#contributing-code)
  - [测试](#tests)

 ## 行为准则

本项目采用 [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)。
更多信息请参阅 [Microsoft Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
，或通过 [opencode@microsoft.com](mailto:opencode@microsoft.com) 联系我们，提出补充问题或意见。

## Bugs

### 发现 bug 了吗？

首先，**请确保该 bug 尚未被报告**，可以在 GitHub 的
[Issues](https://github.com/Alan-Jowett/bpf_conformance/issues) 中搜索。

如果你发现的是非安全相关 bug，可以通过
[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new) 来帮助我们。
最好的 bug 报告应提供问题的详细描述，以及可可靠复现问题的逐步说明。

我们会尽量在每周的 triage 会议中处理这些 issue。如果无法复现问题，我们会向提交者请求更多信息。
我们会给出 2 周的等待期来补充所需信息，如果在此期间没有回应，issue 将被关闭。如果后来你成功复现了问题，请重新打开 issue 并补充所需信息。

不过，在最理想的情况下，我们更希望你能直接提交一个修复该问题的 Pull Request。

如果你发现的是安全问题，请**不要打开 GitHub Issue**，而应按照
[这些说明](docs/SECURITY_zh.md) 处理。

### 你写了一个修复 bug 的补丁吗？

Fork 这个仓库并进行修改。
然后使用该补丁打开一个新的 GitHub Pull Request。

* 确保 PR 描述清楚说明问题和解决方案。
如适用，请包含相关 issue 编号。

* 在提交之前，请阅读 [Development Guide](docs/DevelopmentGuide_zh.md)
以了解更多编码约定。

## 新功能

你可以通过 [提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new) 来请求新功能。

如果你想实现一个新功能，请先
[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new) 并
说明你的提案，以便社区审查并提供反馈。尽早获得反馈有助于确保你的实现工作会被社区接受。
这也能帮助我们更好地协调工作，减少重复劳动。

## 贡献者许可协议

任何代码提交都需要完成 Contributor License Agreement（CLA）。
简而言之，这份协议证明你授权我们按照项目许可证使用你提交的改动，并且你提交的工作拥有适当的版权归属。你只需要完成一次。更多信息请参阅
https://cla.opensource.microsoft.com/。

## 贡献代码

对于绝大多数非最简单的修改，请先
[提交 GitHub Issue](https://github.com/Alan-Jowett/bpf_conformance/issues/new)，以便社区审查并提供反馈。尽早获得反馈有助于确保你的工作被社区接受。
这也能帮助我们更好地协调工作，减少重复劳动。

如果你想贡献代码，请先判断你要做的工作规模。如果只是很小的修改（语法/拼写或 bug 修复），可以直接开始修复。如果你要提交的是功能或较大规模的代码贡献，请先与维护者讨论，并确保它符合产品路线图。你也可以阅读这两篇关于开源贡献的博客：Miguel de Icaza 的 [Open Source Contribution Etiquette](http://tirania.org/blog/archive/2010/Dec-31.html) 和 Ilya Grigorik 的 [Don't "Push" Your Pull Requests](https://www.igvita.com/2011/12/19/dont-push-your-pull-requests/)。
所有代码提交都会被维护者严格 [review](docs/Governance_zh.md) 和测试，只有在质量和设计/路线图匹配度都达标时才会被合并到源代码中。

对于所有新的 Pull Request，适用以下规则：
- 现有测试应当继续通过。
- 每个已完成的 bug/feature 都需要提供测试。
- 每个面向最终用户可见的功能都需要提供文档。
