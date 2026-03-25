<a id="top"></a>
# 命令行

**目录**<br>
[指定要运行哪些测试](#specifying-which-tests-to-run)<br>
[选择使用的 reporter](#choosing-a-reporter-to-use)<br>
[进入调试器](#breaking-into-the-debugger)<br>
[显示成功测试的结果](#showing-results-for-successful-tests)<br>
[在达到一定失败次数后中止](#aborting-after-a-certain-number-of-failures)<br>
[列出可用测试、标签或 reporter](#listing-available-tests-tags-or-reporters)<br>
[把输出发送到文件](#sending-output-to-a-file)<br>
[为一次测试运行命名](#naming-a-test-run)<br>
[省略预期抛出异常的断言](#eliding-assertions-expected-to-throw)<br>
[显示空白字符](#make-whitespace-visible)<br>
[警告](#warnings)<br>
[报告耗时](#reporting-timings)<br>
[从文件加载要运行的测试名](#load-test-names-to-run-from-a-file)<br>
[指定测试用例的运行顺序](#specify-the-order-test-cases-are-run)<br>
[为随机数生成器指定种子](#specify-a-seed-for-the-random-number-generator)<br>
[按照 libIdentify 标准标识框架和版本](#identify-framework-and-version-according-to-the-libidentify-standard)<br>
[继续前等待按键](#wait-for-key-before-continuing)<br>
[跳过所有 benchmark](#skip-all-benchmarks)<br>
[指定收集 benchmark 样本数](#specify-the-number-of-benchmark-samples-to-collect)<br>
[指定 bootstrap 重采样次数](#specify-the-number-of-resamples-for-bootstrapping)<br>
[指定 bootstrap 置信区间](#specify-the-confidence-interval-for-bootstrapping)<br>
[禁用 benchmark 样本的统计分析](#disable-statistical-analysis-of-collected-benchmark-samples)<br>
[指定每个测试预热耗时](#specify-the-amount-of-time-in-milliseconds-spent-on-warming-up-each-test)<br>
[用法](#usage)<br>
[指定要运行的 section](#specify-the-section-to-run)<br>
[把文件名作为标签](#filenames-as-tags)<br>
[覆盖输出着色](#override-output-colouring)<br>
[Test Sharding](#test-sharding)<br>
[允许在没有测试时运行二进制](#allow-running-the-binary-without-tests)<br>
[输出 verbosity](#output-verbosity)<br>

Catch 在完全不带命令行选项的情况下也能很好地工作，但在你希望更细致控制时，下面这些选项就派上用场了。你可以点击下方链接直接跳转到对应选项，或者继续往下浏览所有可用选项。

<a href="#specifying-which-tests-to-run">               `    <test-spec> ...`</a><br />
<a href="#usage">                                       `    -h, -?, --help`</a><br />
<a href="#showing-results-for-successful-tests">        `    -s, --success`</a><br />
<a href="#breaking-into-the-debugger">                  `    -b, --break`</a><br />
<a href="#eliding-assertions-expected-to-throw">        `    -e, --nothrow`</a><br />
<a href="#invisibles">                                  `    -i, --invisibles`</a><br />
<a href="#sending-output-to-a-file">                    `    -o, --out`</a><br />
<a href="#choosing-a-reporter-to-use">                  `    -r, --reporter`</a><br />
<a href="#naming-a-test-run">                           `    -n, --name`</a><br />
<a href="#aborting-after-a-certain-number-of-failures"> `    -a, --abort`</a><br />
<a href="#aborting-after-a-certain-number-of-failures"> `    -x, --abortx`</a><br />
<a href="#warnings">                                    `    -w, --warn`</a><br />
<a href="#reporting-timings">                           `    -d, --durations`</a><br />
<a href="#input-file">                                  `    -f, --input-file`</a><br />
<a href="#run-section">                                 `    -c, --section`</a><br />
<a href="#filenames-as-tags">                           `    -#, --filenames-as-tags`</a><br />

</br>

<a href="#listing-available-tests-tags-or-reporters">   `    --list-tests`</a><br />
<a href="#listing-available-tests-tags-or-reporters">   `    --list-tags`</a><br />
<a href="#listing-available-tests-tags-or-reporters">   `    --list-reporters`</a><br />
<a href="#listing-available-tests-tags-or-reporters">   `    --list-listeners`</a><br />
<a href="#order">                                       `    --order`</a><br />
<a href="#rng-seed">                                    `    --rng-seed`</a><br />
<a href="#libidentify">                                 `    --libidentify`</a><br />
<a href="#wait-for-keypress">                           `    --wait-for-keypress`</a><br />
<a href="#skip-benchmarks">                             `    --skip-benchmarks`</a><br />
<a href="#benchmark-samples">                           `    --benchmark-samples`</a><br />
<a href="#benchmark-resamples">                         `    --benchmark-resamples`</a><br />
<a href="#benchmark-confidence-interval">               `    --benchmark-confidence-interval`</a><br />
<a href="#benchmark-no-analysis">                       `    --benchmark-no-analysis`</a><br />
<a href="#benchmark-warmup-time">                       `    --benchmark-warmup-time`</a><br />
<a href="#colour-mode">                                 `    --colour-mode`</a><br />
<a href="#test-sharding">                               `    --shard-count`</a><br />
<a href="#test-sharding">                               `    --shard-index`</a><br />
<a href=#no-tests-override>                             `    --allow-running-no-tests`</a><br />
<a href=#output-verbosity>                              `    --verbosity`</a><br />

</br>

<a id="specifying-which-tests-to-run"></a>
## 指定要运行哪些测试
<pre>&lt;test-spec> ...</pre>

测试用例、带通配符的测试用例、标签和标签表达式都可以直接作为参数传入。标签会通过方括号来识别。

如果没有提供 test spec，就会运行所有测试用例，但隐藏测试除外。通过给标签加上以点开头（或者仅仅是点本身）的标签即可隐藏测试；在已废弃的做法里，也可以标记为 ```[hide]```，或者把名字写成以 `'./'` 开头。要在命令行中显式指定隐藏测试，可以使用 ```[.]``` 或 ```[hide]```，**不管它们最初是怎么声明的**。

如果 spec 中包含空格，就必须加引号；如果不包含空格，引号可省略。

通配符由测试用例名开头和/或结尾的 `*` 组成，可以匹配任意数量的任意字符（包括 0 个）。

test spec 不区分大小写。

如果某个 spec 以前缀 `exclude:` 或字符 `~` 开头，则表示排除模式。这意味着匹配到该模式的测试会从集合中移除，即使之前某个包含模式已经把它包含进来。后续的包含模式仍然会优先。
包含和排除按从左到右的顺序计算。

测试用例示例：

```
thisTestOnly            匹配名为 'thisTestOnly' 的测试用例
"this test only"        匹配名为 'this test only' 的测试用例
these*                  匹配所有以 'these' 开头的测试
exclude:notThis         匹配除 'notThis' 之外的所有测试
~notThis                匹配除 'notThis' 之外的所有测试
~*private*              匹配所有包含 'private' 的测试之外的所有测试
a* ~ab* abc             匹配所有以 'a' 开头的测试，但排除以 'ab' 开头的测试，`abc` 例外，它会被重新包含
~[tag1]                 匹配除带有 `[tag1]` 标签的所有测试
-# [#somefile]          匹配来自文件 'somefile.cpp' 的所有测试
```

方括号里的名字会被当作标签解析。
一系列标签表示 AND 表达式，而逗号分隔的一系列标签表示 OR 表达式。例如：

<pre>[one][two],[three]</pre>
这会匹配所有同时带有 `[one]` 和 `[two]` 的测试，以及所有带有 `[three]` 的测试。

测试名中包含 `,` 或 `[` 之类特殊字符时，可以在命令行里用 `\` 转义。
`\` 也会转义自身。

<a id="choosing-a-reporter-to-use"></a>
## 选择使用的 reporter

<pre>-r, --reporter &lt;reporter[::key=value]*&gt;</pre>

Reporter 决定 Catch2 的输出内容如何格式化并写出，例如断言、测试、benchmark 等的结果。默认 reporter 叫 “Console reporter”，目标是提供相对详细且对人类友好的输出。

Reporter 也可以单独配置。要向 reporter 传递配置项，只需在 reporter 规格后追加 `::key=value`，可以追加任意多次，例如 `--reporter xml::out=someFile.xml`。

key 要么以 “X” 开头，这样 Catch2 不会解析它们，只会原样传给 reporter；要么是 Catch2 内置的少量选项之一。目前只有两个：["out"](#sending-output-to-a-file) 和 ["colour-mode"](#colour-mode)。

_注意，reporter 仍然可能会检查 X 前缀选项的有效性，如果有问题仍会报错。_

> 通过 `-r`、`--reporter` 传递参数的支持是在 Catch2 3.0.1 中引入的

Catch2 内置了多个 reporter，你可以用 [`--list-reporters`](docs/docs/command-line_zh.md#listing-available-tests-tags-or-reporters) 查看它们的行为。如果你需要提供一种自定义格式，而现有 reporter 都不合适，可以查看 reporter 文档中的[编写自己的 reporter](reporters_zh.md#writing-your-own-reporter)部分。

这个选项可以重复传入，以同时使用多个不同的 reporter。有关最终行为的细节，请参阅 [reporter 文档](reporters_zh.md#multiple-reporters)。还要注意，最多只能有一个 reporter 不带输出文件部分。这个 reporter 会使用“默认”输出目标，基于 [`-o`, `--out`](#sending-output-to-a-file) 选项。

> 同时使用多个不同 reporter 的支持是在 Catch2 3.0.1 中[引入](https://github.com/catchorg/Catch2/pull/2183)的

_注意：目前没有办法在 reporter 规格中转义 `::`，因此 reporter 名称或配置 key/value 里不能包含 `::`。考虑到 `::` 在路径里比较少见（不像 `:`），我们不认为这是个问题。_

<a id="breaking-into-the-debugger"></a>
## 进入调试器
<pre>-b, --break</pre>

在大多数调试器下，Catch2 都可以在测试失败时自动中断到调试器里。这让用户能够在失败时看到测试当前状态。

<a id="showing-results-for-successful-tests"></a>
## 显示成功测试的结果
<pre>-s, --success</pre>

通常你只想看到失败测试的报告。有时查看所有输出也很有用，尤其是当你不确定自己刚加的测试是否真的一次就对了的时候。
要同时看到成功和失败的测试结果，只需传这个选项。注意，不同 reporter 对这个选项的处理方式可能不同。例如 Junit reporter 会不管这个选项如何都记录所有结果。

<a id="aborting-after-a-certain-number-of-failures"></a>
## 在达到一定失败次数后中止
<pre>-a, --abort
-x, --abortx [&lt;failure threshold>]
</pre>

如果一个 ```REQUIRE``` 断言失败，该测试用例会中止，但后续测试用例仍会继续运行。
如果一个 ```CHECK``` 断言失败，甚至当前测试用例都不会中止。

有时这会导致大量失败消息，而你其实只想看前几个。单独使用 ```-a``` 或 ```--abort``` 会在任何断言第一次失败时中止整个测试运行。使用 ```-x``` 或 ```--abortx``` 并跟一个数字，则会在累计那么多次断言失败后中止。

<a id="listing-available-tests-tags-or-reporters"></a>
## 列出可用测试、标签或 reporter
```
--list-tests
--list-tags
--list-reporters
--list-listeners
```

> `--list*` 选项在 Catch2 3.0.1 中变得可由 reporter 自定义

> `--list-listeners` 选项在 Catch2 3.0.1 中加入

`--list-tests` 会列出所有与指定 test spec 匹配的已注册测试。通常这个列表还包括标签，以及一些其他信息，比如源码位置，这取决于 verbosity 和 reporter 的设计。

`--list-tags` 会列出所有与指定 test spec 匹配的已注册测试中的标签。通常这也会包含每个标签匹配的测试数量以及类似信息。

`--list-reporters` 会列出所有可用 reporter 及其描述。

`--list-listeners` 会列出所有已注册 listener 及其描述。

[`--verbosity` 参数](#output-verbosity)会如下修改默认 `--list*` 选项提供的细节级别：

| 选项 | `normal`（默认） | `quiet` | `high` |
|--------------------|---------------------------------|---------------------|-----------------------------------------|
| `--list-tests`     | 测试名和标签             | 仅测试名     | 同 `normal`，外加源码行 |
| `--list-tags`      | 标签和计数                 | 同 `normal`    | 同 `normal`                        |
| `--list-reporters` | reporter 名称和描述 | 仅 reporter 名称 | 同 `normal`                        |
| `--list-listeners` | listener 名称和描述 | 同 `normal`    | 同 `normal`                        |

<a id="sending-output-to-a-file"></a>
## 把输出发送到文件
<pre>-o, --out &lt;filename&gt;
</pre>

使用这个选项可以把所有输出发送到文件，而不是 stdout。你可以把 `-` 作为文件名来显式发送到 stdout（例如在使用多个 reporter 时很有用）。

> 将 `-` 作为文件名的支持是在 Catch2 3.0.1 中引入的

以 `%`（百分号）开头的文件名被 Catch2 保留用于元用途，例如把 `%debug` 作为文件名会打开一个写入平台特定调试/日志机制的流。

Catch2 目前识别 3 个 meta stream：

* `%debug` - 写入平台特定调试/日志输出
* `%stdout` - 写入 stdout
* `%stderr` - 写入 stderr

> 对 `%stdout` 和 `%stderr` 的支持是在 Catch2 3.0.1 中引入的

<a id="naming-a-test-run"></a>
## 为一次测试运行命名
<pre>-n, --name &lt;name for test run></pre>

如果提供了名字，reporter 会用它作为整次测试运行的名字。这在你把输出写到文件时尤其有用，因为你可能需要区分不同的测试运行，例如来自不同 Catch 可执行文件，或者来自同一可执行文件但带不同参数的运行。如果不提供，默认名字就是可执行文件的名字。

<a id="eliding-assertions-expected-to-throw"></a>
## 省略预期抛出异常的断言
<pre>-e, --nothrow</pre>

跳过所有用于测试“是否抛出异常”的断言，例如 ```REQUIRE_THROWS```。

在某些调试环境里，这类异常会带来麻烦，因为它们可能会在异常被抛出时中断（虽然对已处理异常来说通常是可选的）。如果你在排查某些意外情况，这个选项有时会很有帮助。

有时异常的预期发生点并不在专门测试异常的断言里（例如在被测代码内部已经抛出并捕获）。使用 ```-e``` 时，可以通过给测试打上 ```[!throws]``` 标签来整体跳过整个测试用例。

运行这个选项时，所有 throw 检查断言都会被跳过，以免增加额外噪音。要注意这是否会影响后续测试的行为。

<a id="invisibles"></a>
## 显示空白字符
<pre>-i, --invisibles</pre>

如果字符串比较失败是因为空白字符不同，尤其是开头或结尾的空白字符，往往很难看出问题出在哪里。
这个选项会在打印时把制表符和换行符分别转换成 ```\t``` 和 ```\n```。

<a id="warnings"></a>
## 警告
<pre>-w, --warn &lt;warning name></pre>

你可以把 Catch2 的 warning 理解成 C++ 编译器里的 `-Werror`（`/WX`）类似物。它会把某些可疑情况，例如没有断言的 section，提升为错误。因为这些情况有时是有意的，所以默认不会启用 warning，但用户可以选择打开。

你可以一次启用多个 warning。

目前实现了两个 warning：

```
    NoAssertions        // 如果没有遇到任何断言（例如 `REQUIRE`），则使测试用例 / leaf section 失败。
    UnmatchedTestSpec   // 如果任何 CLI test spec 没有匹配到测试，则使测试运行失败。
```

> `UnmatchedTestSpec` 是在 Catch2 3.0.1 中引入的。

<a id="reporting-timings"></a>
## 报告耗时
<pre>-d, --durations &lt;yes/no></pre>

设置为 ```yes``` 时，Catch 会报告每个测试用例的耗时，单位是毫秒。注意，无论测试用例是通过还是失败，它都会报告。还要注意，某些 reporter（例如 Junit）无论这个选项是否设置，都会报告测试用例耗时。

<pre>-D, --min-duration &lt;value></pre>

> `--min-duration` 是在 Catch2 2.13.0 中[引入](https://github.com/catchorg/Catch2/pull/1910)的

设置后，Catch 会报告所有耗时超过 `<value>` 秒的测试用例，单位为毫秒。这个选项会被 `-d yes` 和 `-d no` 覆盖，因此要么报告所有耗时，要么一个都不报。

<a id="input-file"></a>
## 从文件加载要运行的测试名
<pre>-f, --input-file &lt;filename></pre>

提供一个文件名，文件中包含要运行的测试用例名称，每行一个。空行会被跳过。

一种生成这个文件初始版本的有用方式，是把 [`--list-tests`](#listing-available-tests-tags-or-reporters) 和 [`--verbosity quiet`](#output-verbosity) 结合起来。你也可以先用 test spec 把列表过滤到你想要的内容。

<a id="order"></a>
## 指定测试用例的运行顺序
<pre>--order &lt;decl|lex|rand&gt;</pre>

测试用例可以用三种方式排序：

### decl
声明顺序（如果没有提供 `--order` 参数，这是默认顺序）。同一 translation unit 中的测试会按声明顺序排序，不同 TU 的顺序则取决于实现（链接）顺序。

### lex
字典序。测试按名称排序，标签会被忽略。

### rand

随机排序。顺序取决于 Catch2 的随机种子（见 [`--rng-seed`](#rng-seed)），并且对子集稳定。也就是说，只要随机种子固定，只运行部分测试（例如通过标签筛选）不会改变它们的相对顺序。

> 子集稳定性是在 Catch2 v2.12.0 中引入的

既然随机顺序已经变成子集稳定，我们承诺：给定相同的随机种子，只要测试是用相同版本的 Catch2 编译的，那么测试用例顺序在不同平台上也会一致。我们保留在不同 Catch2 版本之间改变测试相对顺序的权利，但这种情况不会太常见。

<a id="rng-seed"></a>
## 为 Random Number Generator 指定种子
<pre>--rng-seed &lt;'time'|'random-device'|number&gt;</pre>

为 Catch2 使用的随机数生成器设置种子。这些随机数生成器会用于例如随机顺序打乱测试。

使用 `time` 作为参数时，Catch2 会通过调用 `std::time(nullptr)` 生成种子。这种随机性很弱，而且如果多次运行二进制的启动时间很接近，可能会生成相同种子。

使用 `random-device` 则会改用 `std::random_device`。如果你的实现提供了可用的 `std::random_device`，通常应优先使用它。Catch2 默认就使用 `std::random_device`。

<a id="libidentify"></a>
## 按照 libIdentify 标准标识框架和版本
<pre>--libidentify</pre>

更多信息和示例请参阅 [LibIdentify 仓库](https://github.com/janwilmans/LibIdentify)。

<a id="wait-for-keypress"></a>
## 继续前等待按键
<pre>--wait-for-keypress &lt;never|start|exit|both&gt;</pre>

这会让可执行文件打印一条消息并等待回车键后再继续，具体是在运行任何测试之前、在所有测试运行结束后，或者两者都等待，取决于参数。

<a id="skip-benchmarks"></a>
## 跳过所有 benchmark
<pre>--skip-benchmarks</pre>

> Catch2 3.0.1 中引入。

这个标志会告诉 Catch2 跳过所有 benchmark 的运行。这里的 benchmark 指的是 `BENCHMARK` 和 `BENCHMARK_ADVANCED` 宏里的代码块，而不是带 `[!benchmark]` 标签的测试用例。

<a id="benchmark-samples"></a>
## 指定收集 benchmark 样本数
<pre>--benchmark-samples &lt;# of samples&gt;</pre>

> Catch2 2.9.0 中引入。

运行 benchmark 时会收集若干“样本”。这些样本是后续统计分析的基础。每个样本会运行一定数量的用户代码迭代次数，而这个次数取决于时钟分辨率，与样本数无关。默认值是 100。

<a id="benchmark-resamples"></a>
## 指定 bootstrap 重采样次数
<pre>--benchmark-resamples &lt;# of resamples&gt;</pre>

> Catch2 2.9.0 中引入。

测量完成后，会对样本执行统计 [bootstrapping]。用于 bootstrapping 的重采样次数是可配置的，默认是 100000。通过 bootstrapping，可以给出均值和标准差的估计值，这些估计值会带上下界，置信区间也可配置，默认是 95%。

 [bootstrapping]: http://en.wikipedia.org/wiki/Bootstrapping_%28statistics%29

<a id="benchmark-confidence-interval"></a>
## 指定 bootstrap 置信区间
<pre>--benchmark-confidence-interval &lt;confidence-interval&gt;</pre>

> Catch2 2.9.0 中引入。

置信区间用于对样本执行统计 bootstrap，以计算均值和标准差的上下界。它必须在 0 和 1 之间，默认是 0.95。

<a id="benchmark-no-analysis"></a>
## 禁用 benchmark 样本的统计分析
<pre>--benchmark-no-analysis</pre>

> Catch2 2.9.0 中引入。

指定这个标志后，不会执行 bootstrap 或任何其他统计分析。相反，只会测量用户代码，并报告样本的简单均值。

<a id="benchmark-warmup-time"></a>
## 指定每个测试预热耗时
<pre>--benchmark-warmup-time</pre>

> Catch2 2.11.2 中引入。

配置每个测试的预热时间。

<a id="usage"></a>
## 用法
<pre>-h, -?, --help</pre>

把命令行参数打印到 stdout。

<a id="run-section"></a>
## 指定要运行的 section
<pre>-c, --section &lt;section name&gt;</pre>

要把执行限制在测试用例中的某个特定 section，可以多次使用这个选项。要进一步缩小到子 section，可以使用多个实例，每个后续实例指定更深一层的嵌套。

例如，如果你有：

<pre>
TEST_CASE( "Test" ) {
  SECTION( "sa" ) {
    SECTION( "sb" ) {
      /*...*/
    }
    SECTION( "sc" ) {
      /*...*/
    }
  }
  SECTION( "sd" ) {
    /*...*/
  }
}
</pre>

那么可以通过：
<pre>./MyExe Test -c sa -c sb</pre>
运行 `sb`

或者通过：
<pre>./MyExe Test -c sd</pre>
仅运行 `sd`

要运行 `sa` 及其子 section（包括 `sb` 和 `sc`），使用：
<pre>./MyExe Test -c sa</pre>

这个特性有一些限制需要注意：
- 被跳过的 section 外部的代码仍然会执行，例如 `TEST_CASE` 中第一个 section 之前的 setup 代码。<br/>
- 截至目前，section 名称不支持通配符。
- 如果你只指定了 section 而没有先缩小到某个测试用例，那么所有测试用例都会被执行（但只会匹配其中的 section）。

<a id="filenames-as-tags"></a>
## 把文件名作为标签
<pre>-#, --filenames-as-tags</pre>

这个选项会给所有测试用例添加一个额外标签。标签形式是 `#` 加上测试用例所在的无限定文件名，并去掉最后一个扩展名。

例如，文件 `tests\SelfTest\UsageTests\BDD.tests.cpp` 中的测试会带上 `[#BDD.tests]` 标签。

<a id="colour-mode"></a>
## 覆盖输出着色
<pre>--colour-mode &lt;ansi|win32|none|default&gt;</pre>

> `--colour-mode` 在 Catch2 3.0.1 中替代了旧的 `--colour` 选项

Catch2 支持两种不同的终端着色方式，默认会尝试合理猜测该使用哪一种实现，以及是否应该使用它（例如在把结果写到文件时，Catch2 会尽量避免输出颜色码）。

`--colour-mode` 允许用户显式指定行为。

* `--colour-mode ansi` 表示始终使用 ANSI 颜色码，即使输出到文件也是如此
* `--colour-mode win32` 表示使用基于 Win32 终端 API 的着色实现
* `--colour-mode none` 表示完全禁用颜色
* `--colour-mode default` 让 Catch2 自行决定

`--colour-mode default` 是默认设置。

<a id="test-sharding"></a>
## Test Sharding
<pre>--shard-count <#number of shards>, --shard-index <#shard index to run></pre>

> Catch2 3.0.1 中引入。

当使用 `--shard-count <#number of shards>` 时，要执行的测试会平均分成给定数量的集合，集合索引从 0 开始。会执行由 `--shard-index <#shard index to run>` 指定的那个集合中的测试。默认 shard 数量是 `1`，默认要运行的索引是 `0`。

_shard index 必须小于 shard 数量。顾名思义，它被视为要运行的 shard 的索引。_

sharding 在你想把测试执行拆分到多个进程中时很有用，Bazel 的 test sharding 就是这么做的。

<a id="no-tests-override"></a>
## 允许在没有测试时运行二进制
<pre>--allow-running-no-tests</pre>

> Catch2 3.0.1 中引入。

默认情况下，如果没有运行任何测试，Catch2 测试二进制会返回非 0 退出码，例如二进制根本没编译测试、提供的 test spec 没匹配到任何测试，或者所有测试都在运行时被跳过。这个标志会覆盖这一行为，使得即使没有测试运行，也会返回 0。

## 输出 verbosity
```
-v, --verbosity <quiet|normal|high>
```

修改 verbosity 可能会改变 Catch2 reporter 输出的细节数量。不过，你应该把 verbosity 级别视为一种 _建议_。并不是所有 reporter 都支持所有 verbosity 级别，例如因为它们的输出格式不能有意义地改变。在这种情况下，这个级别会被忽略。

verbosity 默认是 _normal_。

---

[Home](Readme_zh.md#top)
