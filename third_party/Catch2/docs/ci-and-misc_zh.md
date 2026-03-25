<a id="top"></a>
# 工具集成（CI、测试运行器等）

**目录**<br>
[持续集成系统](#continuous-integration-systems)<br>
[Bazel 测试运行器集成](#bazel-test-runner-integration)<br>
[底层工具](#low-level-tools)<br>
[CMake](#cmake)<br>

本页介绍 Catch2 与其他相关工具的集成，比如持续集成和第三方测试运行器。

## 持续集成系统

在构建服务器上使用 Catch 时，最重要的方面可能就是使用不同的 reporter。Catch 自带三种 reporter，足以覆盖大多数构建服务器需求，当然也可以增加更多，以便更好地集成某些平台（目前我们也提供 TeamCity、TAP、Automake 和 SonarQube reporter）。

其中两个 reporter 是内置的（XML 和 JUnit），第三个（TeamCity）作为单独头文件提供。未来另外两个也可能会拆分出来，这样对不需要它们的人来说，Catch 的核心会更小。

### XML Reporter
```-r xml```

XML Reporter 会输出 Catch 专用的 XML 格式。

这种格式的优点在于，它与 Catch 的工作方式非常契合（尤其是嵌套 sections 这类更不寻常的特性），而且是完全流式的，也就是说它会边运行边输出，不需要先把所有结果都存起来再开始写。

缺点是，作为 Catch 专用格式，没有现成的构建服务器原生理解它。它可以作为 XSLT 转换的输入，例如转换成 HTML，不过这样就失去了流式输出的优势。

### JUnit Reporter
```-r junit```

JUnit Reporter 会输出一种模仿 JUnit ANT schema 的 XML 格式。

这种格式的优点是，JUnit Ant schema 被大多数构建服务器广泛理解，因此通常可以直接消费，不需要额外工作。

缺点是，这个 schema 是为 JUnit 的工作方式设计的，而这与 Catch 的工作方式有显著差异。另外，这种格式不能流式输出（因为打开的元素会把失败和通过的测试计数作为属性），所以必须等整个测试运行结束后才能写出。

### TeamCity Reporter
```-r teamcity```

TeamCity Reporter 会把 TeamCity service message 写到 stdout。要使用这个 reporter，还需要额外包含一个头文件。

因为它是 TeamCity 专用的，所以它是与 TeamCity 搭配使用的最佳 reporter，但对其他任何用途都完全不合适。它是流式格式（边运行边写），不过测试结果要等一个 suite 完成后才会在 TeamCity 界面中显示（通常是整个测试运行结束）。

### Automake Reporter
```-r automake```

Automake Reporter 会输出 automake 在 `make check` 中期望的 [meta tags](https://www.gnu.org/software/automake/manual/html_node/Log-files-generation-and-test-results-recording.html#Log-files-generation-and-test-results-recording)。

### TAP（Test Anything Protocol）Reporter
```-r tap```

由于 Catch 的测试套件具有增量性质，而且可以运行特定测试，因此我们的 TAP reporter 实现会把 suite 中的测试总数放在最后输出。

### SonarQube Reporter
```-r sonarqube```
[SonarQube Generic Test Data](https://docs.sonarqube.org/latest/analysis/generic-test/) XML format for tests metrics.

## Bazel 测试运行器集成

Catch2 能理解 Bazel 用于控制测试执行的一些环境变量。具体来说，它理解：

 * 通过 `XML_OUTPUT_FILE` 指定 JUnit 输出路径
 * 通过 `TESTBRIDGE_TEST_ONLY` 指定测试过滤
 * 通过 `TEST_SHARD_INDEX`、`TEST_TOTAL_SHARDS` 和 `TEST_SHARD_STATUS_FILE` 指定 test sharding

> 对 `XML_OUTPUT_FILE` 的支持是在 Catch2 3.0.1 中[引入](https://github.com/catchorg/Catch2/pull/2399)的

> 对 `TESTBRIDGE_TEST_ONLY` 和 sharding 的支持是在 Catch2 3.2.0 中引入的

这个集成可以通过 [编译期配置选项](docs/docs/configuration_zh.md#bazel-support)启用，也可以通过把 `BAZEL_TEST` 环境变量设置为 "1" 来启用。

> 对 `BAZEL_TEST` 的支持是在 Catch2 3.1.0 中[引入](https://github.com/catchorg/Catch2/pull/2459)的

## 底层工具

### CodeCoverage 模块（GCOV、LCOV...）

如果你正在使用 GCOV 工具获取代码覆盖率，而且不确定如何将它与 CMake 和 Catch 集成，可以在 https://github.com/fkromer/catch_cmake_coverage 找到一个外部示例。

### pkg-config

Catch2 通过注册自己为 `catch2` 名称，提供了基础的 pkg-config 集成。这意味着在安装 Catch2 之后，你可以使用 `pkg-config` 获取它的 include path：`pkg-config --cflags catch2`。

### gdb 和 lldb 脚本

Catch2 的 `extras` 文件夹里还包含两个简单的调试器脚本：`gdbinit` 用于 `gdb`，`lldbinit` 用于 `lldb`。如果把它们加载到各自的调试器中，它们会在你单步执行代码时自动跳过 Catch2 的内部实现。

## CMake

[由于文档已经有点长，Catch2 的 CMake 集成文档被单独移到了这一页。](docs/docs/cmake-integration_zh.md#top)

---

[Home](Readme_zh.md#top)
