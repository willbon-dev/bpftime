# 项目治理

## 审查 Pull Request

Pull Request 在可以合并之前，至少需要两个批准。除了审查技术正确性外，审查者还应当：

* 对于任何新增功能的 PR，检查 PR 是否包含了足够的测试。这是 [CONTRIBUTING.md](../CONTRIBUTING_zh.md) 中的要求。
* 对于任何新增或修改了管理员、eBPF 程序作者或应用程序作者可见功能的 PR，检查文档是否已经充分更新。这也是 [CONTRIBUTING.md](../CONTRIBUTING_zh.md) 中的要求。
* 检查 eBPF for Windows 与 Linux 的公共 API 之间是否存在不必要的差异。
* 熟悉并指出不符合 eBPF for Windows [coding conventions](DevelopmentGuide_zh.md) 的代码。
* 检查错误是否在第一次被发现时就被正确记录，而不是在每一层栈展开时重复记录。

当多个 Pull Request 都已获批时，维护者应按以下优先级合并：

| Pri | Description  | Tags      | Rationale              |
| --- | ------------ | --------- | ---------------------- |
| 1   | Bugs         | bug       | 影响现有用户 |
| 2   | Test bugs    | tests bug | 影响 CI/CD 且可能掩盖优先级 1 的 bug |
| 3   | Additional tests | tests enhancement | 补上后可能暴露优先级 1 的 bug |
| 4   | Documentation | documentation | 不影响 CI/CD，但可能改善可用性 |
| 5   | Dependencies | dependencies | 往往是大量容易处理的工作。保持整体 PR 数量较低能让新加入者和观察者获得更好的印象。 |
| 7   | New features | enhancement | 添加在 github issue 中请求的新功能。尽管这通常优先级低于依赖项，但新贡献者提交的此类 PR 应优先于依赖项。 |
| 8   | Performance optimizations | optimization | 不会改变原本就能工作的内容，但改进确实有助于用户 |
| 9   | Code cleanup | cleanup | 值得做，但通常不会显著影响以上任何类别 |
