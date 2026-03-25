<a id="top"></a>
# 从 v2 迁移到 v3

v3 是 Catch2 的下一个主要版本，并带来了三个重要变化：
 * Catch2 现在拆分成多个头文件
 * Catch2 现在作为静态库编译
 * C++14 是最低要求的 C++ 版本

我们之所以决定从旧的单头文件分发模式转向更标准的库分发模式，有很多原因。最重要的是编译时间，但改成拆分头文件的分发方式也提高了代码库未来的可维护性和可扩展性。例如，v3 增加了一种新的 matcher，而不会影响那些在测试中不使用 matcher 的用户的编译时间。新的模型对 vcpkg 和 Conan 之类的包管理器也更友好。

这次迁移带来的结果是编译时间显著改善，例如在常见场景下，Catch2 的包含开销大约降低了 80%。更容易维护也带来了各种运行时性能改进和新功能的引入。详情请看 [3.0.1 的发布说明](docs/docs/release-notes_zh.md#301)。

_注意，我们仍然提供“一头文件 + 一个翻译单元（TU）”的分发方式，但不把它视为主要支持选项。你也应该预期，使用这种方式时编译时间会更差。_

## 如何把项目从 v2 迁移到 v3

迁移到 v3 有两种基本方式。

1. 使用 `catch_amalgamated.hpp` 和 `catch_amalgamated.cpp`。
2. 把 Catch2 构建成正规的（静态）库，并迁移到分段头文件

做法 1 是下载 `extras` 目录中的 [amalgamated header](/extras/catch_amalgamated.hpp) 和 [amalgamated source](/extras/catch_amalgamated.cpp)，把它们放进你的测试项目里，然后把 include 从 `<catch2/catch.hpp>` 重写成 `"catch_amalgamated.hpp"`（或者其他类似名称，取决于你的路径设置）。

这种方式的缺点是编译时间会增加，至少相较于第二种方式如此；不过它可以让你不用在你选择的构建系统里处理依赖库消费问题。

不过，我们还是推荐做法 2，花些额外时间正确迁移到 v3。这样你就能享受到 v3 版本显著改善的编译时间。基本步骤如下：

1. 如果你使用 Catch2 默认 main，请把 CMakeLists.txt 改为链接 `Catch2WithMain` target。（如果你不用默认 main，就继续链接 `Catch2` target。）如果你使用 pkg-config，把 `pkg-config catch2` 改成 `pkg-config catch2-with-main`。
2. 删除定义了 `CATCH_CONFIG_RUNNER` 或 `CATCH_CONFIG_MAIN` 的 TU，因为它已经不再需要。
3. 把 `#include <catch2/catch.hpp>` 改成 `#include <catch2/catch_all.hpp>`
4. 检查是否一切都能编译通过。你可能需要修改命名空间，或者做其他一些改动（最常见的问题见[迁移过程中可能出问题的地方](#things-that-can-break-during-porting)）。
5. 开始把测试 TU 从包含 `<catch2/catch_all.hpp>` 迁移到更细粒度的 include。你大概率会先从 `<catch2/catch_test_macros.hpp>` 开始，然后再逐步细化。（更多想法见[其他说明](#other-notes)）

## 其他说明

* 主测试 include 现在是 `<catch2/catch_test_macros.hpp>`

* 像 Matchers 或 Generators 这样大的“子部分”都有自己的文件夹，也有自己的“大头文件”，所以如果你只想包含所有 matchers，可以包含 `<catch2/matchers/catch_matchers_all.hpp>`，或者如果你只想包含所有 generators，可以包含 `<catch2/generators/catch_generators_all.hpp>`

## 迁移过程中可能出问题的地方

* Matchers 的命名空间被扁平化并整理过了。

Matchers 不再先在内部命名空间里声明再带到 `Catch` 命名空间中。现在所有 Matchers 都位于 `Catch::Matchers` 命名空间中。

* `Contains` 字符串 matcher 被重命名为 `ContainsSubstring`。

* reporter 接口发生了破坏性变化。

如果你在使用自定义 reporter 或 listener，很可能需要修改它们以适应新的接口。与 v2 不同的是，[接口](reporters_zh.md#top)和[事件](reporter-events_zh.md#top)现在都有文档了。

---

[Home](Readme_zh.md#top)
