<a id="top"></a>
# Reporter

Reporter 是 Catch2 大部分输出的自定义点，例如格式化和写出[断言（无论通过还是失败）、sections、测试用例、benchmarks 等](reporter-events_zh.md#top)。

Catch2 默认自带一批 reporter（目前是 8 个），你也可以编写自己的 reporter。由于可以同时启用多个 reporter，你自己的 reporter 甚至不需要处理所有 reporter 事件，只需要处理你关心的那些，比如 benchmarks。

## 使用不同的 reporter

你可以通过运行测试二进制并加上 `--list-reporters` 来查看可用的 reporter。然后你可以通过 [`-r`、`--reporter` 选项](docs/docs/command-line_zh.md#choosing-a-reporter-to-use)加上你想要的 reporter 名称来选择它，例如：

```text
--reporter xml
```

你也可以同时选择多个 reporter。在这种情况下，你应该先阅读[使用多个 reporter 的部分](#multiple-reporters)，避免因此产生意外。

<a id="multiple-reporters"></a>
## 使用多个 reporter

> 支持多个并行 reporter 是在 Catch2 3.0.1 中[引入](https://github.com/catchorg/Catch2/pull/2183)的

Catch2 支持同时使用多个 reporter，并让它们写到不同的目标位置。这样做的两个主要用途是：

* 一次运行同时得到人类友好的输出和机器可解析的输出（例如 JUnit 格式）
* 使用“部分” reporter 做高度专门化的事情，例如让一个 reporter 把 benchmark 结果写成 markdown 表格，而什么别的都不做，同时另一个 reporter 继续输出标准测试结果

指定多个 reporter 的方式如下：
```text
--reporter JUnit::out=result-junit.xml --reporter console::out=-::colour-mode=ansi
```

这告诉 Catch2 使用两个 reporter：`JUnit` reporter 会把机器可读的 XML 输出写到 `result-junit.xml` 文件，而 `console` reporter 会把人类友好的输出写到 stdout，并使用 ANSI 颜色码给输出着色。

当使用多个 reporter（或者一个 reporter 加一个或多个 [event listener](event-listeners_zh.md#top)）时，Catch2 提供给 reporter 的一些自定义点会有相当复杂的语义，尤其是捕获测试用例的 stdout/stderr。

只要至少有一个 reporter（或 listener）要求 Catch2 捕获 stdout/stderr，捕获到的 stdout 和 stderr 就会对所有 reporter 和 listener 可用。

因为这可能会让用户感到意外，所以如果至少有一个激活的 _reporter_ 是非捕获型的，Catch2 会尝试大致模拟非捕获行为：它会在 `testCasePartialEnded` 事件发送给激活的 reporter 和 listener 之前，把捕获到的 stdout/stderr 打印出来。这意味着 stdout/stderr 不再是在测试写入时即时打印，而是在每个测试用例运行结束后批量写出。

## 编写自己的 reporter

你也可以编写自己的自定义 reporter，并告诉 Catch2 使用它。编写 reporter 时，你有两个选择：

* 继承 `Catch::ReporterBase`。这样做时，你需要处理所有[reporter 事件](reporter-events_zh.md#top)。
* 继承 Catch2 中提供的某个 [utility reporter base](#utility-reporter-bases)。

通常我们推荐后者，因为工作量更少。

除了重写单个 reporter 事件的处理外，reporter 还可以使用一些额外的自定义点，下面会说明。

### Utility reporter base

Catch2 目前提供两个 utility reporter base：

* `Catch::StreamingReporterBase`
* `Catch::CumulativeReporterBase`

`StreamingReporterBase` 适用于可以在事件到来时就进行格式化和输出的 reporter。它为所有 reporter 事件提供了（通常为空的）实现，如果你让它处理相关事件，它也会负责保存当前测试运行和测试用例的相关信息。

`CumulativeReporterBase` 则适合那种必须先看到整个测试运行结果，才能开始输出的 reporter，例如 JUnit 和 SonarQube reporter。这种事后处理方式要求在断言结束时就把它字符串化，这样之后才能写出。由于字符串化可能很昂贵，而且不是所有 cumulative reporter 都需要断言，因此这个 base 提供了自定义点，可以分别控制通过和失败的断言是否被保存。

_通常我们建议，如果你重写了这些 base 中的成员函数，最好先调用 base 的实现。这不一定适用于所有情况，但这样更安全也更容易。_

编写自己的 reporter 看起来像这样：

```cpp
#include <catch2/reporters/catch_reporter_streaming_base.hpp>
#include <catch2/catch_test_case_info.hpp>
#include <catch2/reporters/catch_reporter_registrars.hpp>

#include <iostream>

class PartialReporter : public Catch::StreamingReporterBase {
public:
    using StreamingReporterBase::StreamingReporterBase;

    static std::string getDescription() {
        return "Reporter for testing TestCasePartialStarting/Ended events";
    }

    void testCasePartialStarting(Catch::TestCaseInfo const& testInfo,
                                 uint64_t partNumber) override {
        std::cout << "TestCaseStartingPartial: " << testInfo.name << '#' << partNumber << '\n';
    }

    void testCasePartialEnded(Catch::TestCaseStats const& testCaseStats,
                              uint64_t partNumber) override {
        std::cout << "TestCasePartialEnded: " << testCaseStats.testInfo->name << '#' << partNumber << '\n';
    }
};


CATCH_REGISTER_REPORTER("partial", PartialReporter)
```

这会创建一个简单的 reporter，它响应 `testCasePartial*` 事件，并把自己称为 "partial" reporter，因此可以通过 `--reporter partial` 命令行标志调用。

### `ReporterPreferences`

每个 reporter 实例都包含一个 `ReporterPreferences` 实例，它保存了该 reporter 运行时 Catch2 的行为标志。目前有两个自定义选项：

* `shouldRedirectStdOut` - reporter 是否希望处理来自用户代码的 stdout/stderr 输出，或者不处理。这对输出机器可解析结果的 reporter 很有用，例如 JUnit reporter 或 XML reporter。
* `shouldReportAllAssertions` - reporter 是否希望处理通过和失败两种断言的 `assertionEnded` 事件。通常 reporter 不会报告成功的断言，也不需要它们用于输出，但有时目标输出格式即使没有 `-s` 标志也需要显示通过的断言。

### 每个 reporter 的配置

> 每个 reporter 的配置是在 Catch2 3.0.1 中引入的

Catch2 支持按 reporter 进行一些配置。配置选项分为两类：

* Catch2 可识别的选项
* reporter 特定的选项

前者是一小组通用选项，由 Catch2 为 reporter 处理，例如输出文件或 console 颜色模式。后者则需要 reporter 自己处理，不过 key 和 value 可以是任意字符串，只要不包含 `::` 即可。这让 reporter 能在运行时被大幅定制。

reporter 特定选项总是必须以大写字母 `X` 为前缀。

### reporter 的其他预期功能

编写自定义 reporter 时，还有几件事需要记住。它们不一定影响正确性，但会影响 reporter 是否“顺手”。

* Catch2 为用户提供了一个简单的 verbosity 选项。有三个 verbosity 级别："quiet"、"normal" 和 "high"；如果对你的 reporter 输出格式有意义，应该根据这些级别改变输出什么、输出多少。

* Catch2 还会使用 rng-seed。若你想复现某次测试运行，知道种子很重要，因此你的 reporter 应该尽可能报告 rng-seed，只要目标输出格式允许。

* Catch2 还会使用测试过滤器，也就是 test spec。如果存在过滤器，你也应该尽可能报告它，只要目标输出格式允许。

---

[Home](Readme_zh.md#top)
