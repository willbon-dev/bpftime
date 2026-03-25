<a id="top"></a>
# Reporter 事件

**目录**<br>
[测试运行事件](#test-running-events)<br>
[Benchmark 事件](#benchmarking-events)<br>
[列表事件](#listings-events)<br>
[杂项事件](#miscellaneous-events)<br>

Reporter 事件是用户代码的一个自定义点。它们会被 [reporters](reporters_zh.md#top) 用来定制 Catch2 的输出，也会被 [event listeners](event-listeners_zh.md#top) 用来在某些条件下执行进程内操作。

Catch2 目前共有 21 个 reporter 事件，分为 4 个不同的事件组：
* 测试运行事件（10 个事件）
* benchmarking 事件（4 个）
* 列表事件（3 个）
* 杂项事件（4 个）

## 测试运行事件

测试运行事件总是成对出现，也就是说每个 `fooStarting` 事件都会有一个 `fooEnded` 事件。这意味着 10 个测试运行事件实际上由 5 对事件组成：

* `testRunStarting` 和 `testRunEnded`，
* `testCaseStarting` 和 `testCaseEnded`，
* `testCasePartialStarting` 和 `testCasePartialEnded`，
* `sectionStarting` 和 `sectionEnded`，
* `assertionStarting` 和 `assertionEnded`

### `testRun` 事件

```cpp
void testRunStarting( TestRunInfo const& testRunInfo );
void testRunEnded( TestRunStats const& testRunStats );
```

`testRun` 事件包住整个测试运行。`testRunStarting` 会在第一个测试用例执行前发出，`testRunEnded` 会在所有测试用例执行完之后发出。

### `testCase` 事件

```cpp
void testCaseStarting( TestCaseInfo const& testInfo );
void testCaseEnded( TestCaseStats const& testCaseStats );
```

`testCase` 事件包住某个特定测试用例的一次 _完整_ 运行。测试用例内部的单次运行，例如由于 `SECTION` 或 `GENERATE` 导致的多次执行，会由不同的事件处理。

### `testCasePartial` 事件

> Catch2 3.0.1 中引入

```cpp
void testCasePartialStarting( TestCaseInfo const& testInfo, uint64_t partNumber );
void testCasePartialEnded(TestCaseStats const& testCaseStats, uint64_t partNumber );
```

`testCasePartial` 事件包住某个特定测试用例的一次 _部分_ 运行。这意味着对于任意测试用例，这些事件可能会被发出多次，例如由于多个 leaf section。

在和 `testCase` 事件的嵌套关系上，`testCasePartialStarting` 永远不会在对应的 `testCaseStarting` 之前发出，而 `testCasePartialEnded` 也总会在对应的 `testCaseEnded` 之前发出。

### `section` 事件

```cpp
void sectionStarting( SectionInfo const& sectionInfo );
void sectionEnded( SectionStats const& sectionStats );
```

`section` 事件只会在激活的 `SECTION` 上发出，也就是那些实际进入的 sections。当前这次测试运行中被跳过的 sections 不会触发事件。

_注意，测试用例总是包含一个隐式 section。这个 section 的事件会在对应的 `testCasePartialStarting` 事件之后发出。_

### `assertion` 事件

```cpp
void assertionStarting( AssertionInfo const& assertionInfo );
void assertionEnded( AssertionStats const& assertionStats );
```

`assertionStarting` 会在断言里的表达式被捕获或求值之前发出，而 `assertionEnded` 会在之后发出。这意味着，像 `REQUIRE(a + b == c + d)` 这样的断言，Catch2 会先发出 `assertionStarting` 事件，然后计算 `a + b` 和 `c + d`，接着捕获它们的结果、计算比较结果，最后发出 `assertionEnded` 事件。

## Benchmarking 事件

> Catch2 2.9.0 中引入。

```cpp
void benchmarkPreparing( StringRef name ) override;
void benchmarkStarting( BenchmarkInfo const& benchmarkInfo ) override;
void benchmarkEnded( BenchmarkStats<> const& benchmarkStats ) override;
void benchmarkFailed( StringRef error ) override;
```

由于 benchmark 的生命周期稍微复杂一些，所以 benchmarking 事件有自己独立的类别，尽管它们也可以被看作与 `assertion*` 事件平行。你应该预期运行一个 benchmark 至少会触发上面这些事件中的 2 个。

为了理解下面的说明，请先阅读 [benchmarking 文档](benchmarks_zh.md#top)。

* `benchmarkPreparing` 事件会在环境探测结束后发出，但在用户代码第一次被估算之前发出。
* `benchmarkStarting` 事件会在用户代码完成估算后发出，但此时还没有真正开始 benchmark。
* `benchmarkEnded` 事件会在用户代码完成 benchmark 后发出，并包含 benchmark 结果。
* `benchmarkFailed` 事件会在估算或 benchmark 本身失败时发出。

## 列表事件

> Catch2 3.0.1 中引入。

列表事件对应的是测试二进制以 `--list-foo` 标志运行时发生的事件。

当前共有 3 个列表事件，分别对应 reporter、tests 和 tags。注意，它们并不是互斥的。

```cpp
void listReporters( std::vector<ReporterDescription> const& descriptions );
void listTests( std::vector<TestCaseHandle> const& tests );
void listTags( std::vector<TagInfo> const& tagInfos );
```

## 杂项事件

```cpp
void reportInvalidTestSpec( StringRef unmatchedSpec );
void fatalErrorEncountered( StringRef error );
void noMatchingTestCases( StringRef unmatchedSpec );
```

这些是一些一次性的事件，不太适合归到其他类别里。

`reportInvalidTestSpec` 会对每个[测试规格命令行参数](docs/docs/command-line_zh.md#specifying-which-tests-to-run)发出一次，只要该参数没有被解析成有效的 spec。

`fatalErrorEncountered` 会在 Catch2 的 POSIX 信号处理或 Windows SE handler 接收到致命信号/异常时发出。

`noMatchingTestCases` 会对每个用户提供但没有匹配到任何已注册测试的测试规格发出一次。

---

[Home](Readme_zh.md#top)
