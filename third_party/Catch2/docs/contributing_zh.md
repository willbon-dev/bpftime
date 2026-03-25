<a id="top"></a>
# 为 Catch2 贡献

**目录**<br>
[使用 Git(Hub)](#using-github)<br>
[测试你的修改](#testing-your-changes)<br>
[编写文档](#writing-documentation)<br>
[编写代码](#writing-code)<br>
[CoC](#coc)<br>

你想给 Catch2 贡献一些东西吗？太好了！无论是修复 bug、添加新功能、支持更多编译器，还是仅仅修正文档，所有贡献都非常受欢迎，也非常感谢。当然，缺陷报告、其他评论和问题也同样欢迎，但通常来说，把问题发到我们的 [Discord](https://discord.gg/4CWS9zD) 比发到 Issue tracker 更合适。

这一页介绍了一些关于为代码库本身做贡献的指南和实用建议。

## 使用 Git(Hub)

Catch2 v3 的持续开发发生在 `devel` 分支，而 v2 版本的维护更新则在 `v2.x` 分支进行。

提交应该小而原子化。一个提交如果在应用之后，代码库和测试都仍然能按预期工作，那它就是原子的。我们也更偏好较小的提交，因为它们会让之后基于 git 历史的操作更容易，比如二分定位、回滚，或者其他操作。

_提交 pull request 时，请不要包含 amalgamated 分发文件的改动。这意味着不要把它们提交进 git commits！_

在 MR 中处理 review 评论时，请不要立刻 rebase/squash 这些提交。那样会让新改动更难 review，从而拖慢 MR 的合并速度。相反，在处理 review 评论时，应该把新的提交追加到分支上，只在 MR 准备合并时再把它们 squash 到其他提交里。我们建议使用 `git commit --fixup`（或 `--squash`）创建新提交，然后再用 `git rebase --autosquash` 来整理，这样会更方便。

## 测试你的修改

_注意：运行 Catch2 的测试需要 Python3_

Catch2 有多层测试，并会在 CI 中运行。最显而易见的是编译进 `SelfTest` 二进制文件的单元测试。它们随后会被用于 “Approval tests”，后者会通过特定的 reporter 运行 `SelfTest` 中几乎所有测试，然后把生成的输出和已知正确的输出（“Baseline”）进行比较。默认情况下，新测试应该放在这里。

要配置一个只包含基础测试的 Catch2 构建，可以使用 `basic-tests` preset，如下：

```bash
# 假设你在 Catch2 根目录下

cmake -B basic-test-build -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests
```

不过，并不是所有测试都适合写成普通单元测试。例如，检查 Catch2 在要求随机顺序时是否真的随机排序，并且这种随机排序是否对子集不敏感，最好用外部检查脚本写成集成测试。Catch2 的集成测试使用 CTest 编写，可以直接调用命令并用 pass/fail 正则判断，也可以委托给 Python 脚本。

Catch2 正在慢慢增加更多测试类型，目前还包括可构建示例、`ExtraTests` 和 CMake 配置测试。示例是一些小而独立的代码片段，用来展示 Catch2 的特定用法。目前它们默认以“能编译通过”为通过标准。

`ExtraTests` 则是成本较高的测试，我们不希望总是运行它们。这可能是因为它们运行时间长，或者编译时间长，比如测试编译期配置并需要单独编译。

最后，CMake 配置测试会验证你是否通过 CMake 选项设置了 Catch2 的编译期配置选项。

这些测试类别可以分别启用，只需要在配置构建时传入 `-DCATCH_BUILD_EXAMPLES=ON`、`-DCATCH_BUILD_EXTRA_TESTS=ON` 和 `-DCATCH_ENABLE_CONFIGURE_TESTS=ON`。

Catch2 还提供了一个 preset，承诺会启用所有测试类型，名为 `all-tests`。

下面的代码片段会在 `Debug` 编译模式下构建并运行所有测试。

<!-- snippet: catch2-build-and-test -->
<a id='snippet-catch2-build-and-test'></a>
```sh
# 1. 重新生成 amalgamated 分发文件（某些测试会基于它构建）
./tools/scripts/generateAmalgamatedFiles.py

# 2. 配置完整测试构建
cmake -B debug-build -S . -DCMAKE_BUILD_TYPE=Debug --preset all-tests

# 3. 执行实际构建
cmake --build debug-build

# 4. 使用 CTest 运行测试
cd debug-build
ctest -j 4 --output-on-failure -C Debug
```
<sup><a href='/tools/scripts/buildAndTest.sh#L6-L19' title='File snippet `catch2-build-and-test` was extracted from'>snippet source</a> | <a href='#snippet-catch2-build-and-test' title='Navigate to start of snippet `catch2-build-and-test`'>anchor</a></sup>
<!-- endSnippet -->

为了方便起见，上面的命令也放在 `tools/scripts/buildAndTest.sh` 脚本里，可以这样运行：

```bash
cd Catch2
./tools/scripts/buildAndTest.sh
```

Windows 版本脚本位于 `tools\scripts\buildAndTest.cmd`。

如果你添加了新的测试，很可能会看到 `ApprovalTests` 失败。确认输出差异符合预期后，你应该运行 `tools/scripts/approve.py` 来确认它们，并把这些改动一起提交。

## 编写文档

如果你给 Catch2 增加了新功能，就需要相应文档，这样其他人也能使用它。本节整理了一些在更新 Catch2 文档时会用到的技术信息，也包括一些通用建议。

### 技术细节

先说技术细节：

* 如果你新增了一个文档，请使用一个简单的模板。它会提供前面提到的 top anchor，方便链接，同时也会提供回到文档顶部的链接：
```markdown
<a id="top"></a>
# Cool feature

> [Introduced](https://github.com/catchorg/Catch2/pull/123456) in Catch2 X.Y.Z

Text that explains how to use the cool feature.


---

[Home](Readme_zh.md#top)
```

* 不同页面之间的交叉链接应当指向 `top` 锚点，例如 `[link to contributing](contributing_zh.md#top)`。

* 我们在文档中引入了版本标签，用来告诉用户某个功能是在哪个版本中引入的。这意味着新写的文档应该带上一个占位符，发布时会被替换成实际版本。文档中使用了两种占位符风格，你可以按文本需要选择一种（如果不确定，可以看看其他功能的现有版本标签）。
  * `> [Introduced](link-to-issue-or-PR) in Catch2 X.Y.Z` - 这种占位符通常放在小节标题后面
  * `> X (Y and Z) was [introduced](link-to-issue-or-PR) in Catch2 X.Y.Z`
  - 这种占位符用于给某个内容的子部分打标签，例如列表

* 对于有超过 4 个子标题的页面，我们会在页面顶部提供目录（ToC）。由于 GitHub Markdown 不支持自动生成目录，因此这部分需要半手工维护。所以，如果你给某页新增了小节，就应该把它加入 ToC。你可以手动添加，也可以运行 `scripts/` 目录里的 `updateDocumentToC.py` 脚本。

### 内容

接着说一些内容建议：

* 举例说明是很好的。不过，大段内联代码会让文档可读性下降，所以内联示例应该尽量保持简短。对于更复杂、可编译的示例，可以考虑在 `examples/` 中新增 `.cpp` 文件。

* 不要害怕新增页面。当前文档确实偏向长页面，但这很大程度上是历史遗留问题，我们也知道有些页面过大且主题不够聚焦。

* 当你向现有页面添加信息时，请尽量保持格式、风格和修改与页面其余部分一致。

* 任何文档都有多个不同的受众，他们希望从文本中获得不同的信息。可以尽量覆盖的 3 类基本用户是：
  * 初学 Catch2 的用户，需要更细致的使用指导。
  * 需要自定义使用方式的高级用户。
  * 希望获得 Catch2 完整能力参考的专家用户。

## 编写代码

如果你想贡献代码，这一节包含一些简单规则和提示，比如代码格式、应避免的代码结构等等。

### C++ 标准版本

Catch2 目前以 C++14 作为最低支持的 C++ 版本。更高语言版本的特性应该谨慎使用，只有当其收益足以抵消维护成本时才使用。

一个 polyfill 使用的好例子是我们对 `conjunction` 的使用：如果可用，就使用 `std::conjunction`，否则提供我们的实现。
