# 项目治理

## 审查 Pull Request

Pull Request 至少需要两个批准才能合并。除了审查技术正确性之外，审查者还需要：

* 对于任何添加功能的 PR，检查其是否为该功能提供了足够的测试。这是 [CONTRIBUTING_zh.md](../Contributing_zh.md) 的要求。
* 对于任何以管理员或 eBPF 程序/应用作者可见的方式新增或修改功能的 PR，检查文档是否已充分更新。这也是 [CONTRIBUTING_zh.md](../Contributing_zh.md) 的要求。
* 检查 eBPF for Windows 和 Linux 的公共 API 是否存在不必要的差异。
* 熟悉 eBPF for Windows 的 [coding conventions](DevelopmentGuide_zh.md)，并指出不符合规范的代码。
* 检查错误是否在首次发现时就被适当地记录下来，而不是在调用栈回溯的每一层都重复记录。

当多个 Pull Request 都已通过批准时，维护者应按以下优先级合并：

| Pri | Description  | Tags      | Rationale              |
| --- | ------------ | --------- | ---------------------- |
| 1   | Bugs         | bug       | 影响现有用户 |
| 2   | Test bugs    | tests bug | 会影响 CI/CD 并可能掩盖优先级 1 的 bug 的问题 |
| 3   | Additional tests | tests enhancement | 补上后可能暴露优先级 1 bug 的测试空缺 |
| 4   | Documentation | documentation | 不会影响 CI/CD，但可能改善可用性 |
| 5   | Dependencies | dependencies | 往往能捡到很多低垂的果实。保持 PR 总数较低会给新来者和观察者更好的印象。 |
| 7   | New features | enhancement | 为 GitHub issue 中请求的新功能添加实现。虽然这类 PR 通常低于依赖更新，但来自新贡献者的此类 PR 应优先于依赖更新。 |
| 8   | Performance optimizations | optimization | 不改变已有可用功能，但能提升体验 |
| 9   | Code cleanup | cleanup | 值得做，但通常不会显著影响上述类别 |
