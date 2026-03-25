<a id="top"></a>
# 常见问题（FAQ）

**目录**<br>
[如何只在会运行测试时执行全局 setup/teardown？](#how-do-i-run-global-setupteardown-only-if-tests-will-be-run)<br>
[如何在运行不同测试之间清理全局状态？](#how-do-i-clean-up-global-state-between-running-different-tests)<br>
[为什么不能从内置 reporter 派生？](#why-cannot-i-derive-from-the-built-in-reporters)<br>
[Catch2 的 ABI 稳定性策略是什么？](#what-is-catch2s-abi-stability-policy)<br>
[Catch2 的 API 稳定性策略是什么？](#what-is-catch2s-api-stability-policy)<br>
[Catch2 支持并行运行测试吗？](#does-catch2-support-running-tests-in-parallel)<br>
[我可以把 Catch2 编译成动态库吗？](#can-i-compile-catch2-into-a-dynamic-library)<br>
[Catch2 提供什么样的可重复性保证？](#what-repeatability-guarantees-does-catch2-provide)<br>

## 如何只在会运行测试时执行全局 setup/teardown？

编写一个自定义的 [event listener](event-listeners_zh.md#top)，并把全局 setup/teardown 代码放进 `testRun*` 事件里。

## 如何在运行不同测试之间清理全局状态？

编写一个自定义的 [event listener](event-listeners_zh.md#top)，并根据清理需要发生的频率，把清理代码放到 `testCase*` 或 `testCasePartial*` 事件中。

## 为什么不能从内置 reporter 派生？

因为它们本来就不是设计成可被重写的。我们不会在成员函数被重写后仍尝试维护一致的内部状态，而且禁止用户把它们当作基类后，未来就可以按需重构它们。

## Catch2 的 ABI 稳定性策略是什么？

Catch2 不提供任何 ABI 稳定性保证。Catch2 提供的是丰富的 C++ 接口，如果要冻结 ABI，会带来大量没有意义的工作。

Catch2 也不是为动态库分发而设计的，实际上你应该使用同一个编译器二进制把所有内容编译到一起。

## Catch2 的 API 稳定性策略是什么？

Catch2 会尽最大努力遵循 [semver](https://semver.org/)。这意味着，除非递增主版本号，否则我们不会故意引入不向后兼容的改动。

## Catch2 支持并行运行测试吗？

原生不支持。我们认为并行运行测试是外部测试运行器的职责，它也可以负责把测试放到不同进程中运行、支持执行超时等等。

不过，Catch2 提供了一些工具，可以让外部测试运行器更容易完成这项工作。[请参阅我们最佳实践页面中的相关部分](usage-tips_zh.md#parallel-tests)。

## 我可以把 Catch2 编译成动态库吗？

可以，Catch2 支持标准 CMake 的 [`BUILD_SHARED_LIBS` 选项](https://cmake.org/cmake/help/latest/variable/BUILD_SHARED_LIBS.html)。不过，动态库支持是按现状提供的。Catch2 不提供 API 导出注解，因此你只能在默认公共可见性的平台上把它当作动态库使用，或者借助工具强制导出 Catch2 的 API。

## Catch2 提供什么样的可重复性保证？

在不考虑用户代码的情况下，有两个地方适合讨论 Catch2 的可重复性保证。第一个是测试用例的随机打乱，第二个是随机生成器的输出。

自 v2.12.0 起，测试用例的打乱结果可以跨平台复现，而且通常也能跨版本复现，但我们可能会不时打破这一点。例如，我们在 v2.13.4 中打破了与旧版本的可重复性，以便让名字相似的测试用例洗牌得更好。

随机生成器目前依赖平台的 stdlib，具体来说是 `<random>` 中的分布。因此，我们不会提供超出平台自身能力之外的额外保证。**重要：`<random>` 的分布并没有规定必须在不同平台之间保持可重复。**

---

[Home](Readme_zh.md#top)
