<a id="top"></a>
# 废弃项与即将到来的变化

本页记录 Catch2 中当前的废弃项和即将到来的计划变更。两者的区别在于：废弃功能将会被移除，而计划中的功能变更则意味着该功能行为会改变，但仍然存在。显然，这两者都属于破坏性变更，因此至少要到下一个主版本发布时才会发生。

### `ParseAndAddCatchTests.cmake`

使用 `ParseAndAddCatchTests.cmake` 的 CMake/CTest 集成已经废弃，因为它可以被 `Catch.cmake` 替代，后者提供 `catch_discover_tests` 函数，可以通过命令行接口直接从 CMake target 中获取测试，而不必用正则表达式解析 C++ 代码。

### `CATCH_CONFIG_BAZEL_SUPPORT`

Catch2 支持在识别到自己处于 Bazel 测试环境时，写出 Bazel JUnit XML 文件。最初没有办法准确探测环境信息，因此添加了 `CATCH_CONFIG_BAZEL_SUPPORT` 这个开关。现在它已经废弃。Bazel 现在会导出 `BAZEL_TEST=1` 这样的环境变量。Catch2 现在会直接检查环境，而不是依赖构建配置。

### `IEventLister::skipTest( TestCaseInfo const& testInfo )`

这个事件（包括派生类中的实现，比如 `ReporterBase`）已经废弃，并将在下一个主版本中移除。它当前会在所有不会执行的测试用例上调用，这些测试用例是由于测试运行被中止而跳过的（使用 `--abort` 或 `--abortx`）。不过，对于[使用 `SKIP` 宏显式跳过的测试](skipping-passing-failing_zh.md#top)，**不会**调用它。

---

[Home](Readme_zh.md#top)
