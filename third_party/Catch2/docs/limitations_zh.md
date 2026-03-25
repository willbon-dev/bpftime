<a id="top"></a>
# 已知限制

随着时间推移，Catch2 的一些限制逐渐显现出来。有些限制是实现细节导致的，难以轻易改变；有些是由于我们缺乏开发资源；还有一些则是第三方 bug。

## 实现层面的限制
### 循环中的 section 嵌套

如果你在循环中使用 `SECTION`，就必须为循环的每次迭代创建不同的名字。推荐做法是把循环计数器包含到 section 名称里，例如：

```cpp
TEST_CASE( "Looped section" ) {
    for (char i = '0'; i < '5'; ++i) {
        SECTION(std::string("Looped section ") + i) {
            SUCCEED( "Everything is OK" );
        }
    }
}
```

或者使用专门为此设计的 `DYNAMIC_SECTION` 宏：

```cpp
TEST_CASE( "Looped section" ) {
    for (char i = '0'; i < '5'; ++i) {
        DYNAMIC_SECTION( "Looped section " << i) {
            SUCCEED( "Everything is OK" );
        }
    }
}
```

### 如果最后一个 section 失败，测试可能会再次运行

如果测试中的最后一个 section 失败，它可能会被再次运行。这是因为 Catch2 会动态发现 `SECTION`，即在它们准备运行时才发现；如果测试用例中的最后一个 section 在执行过程中被中止（例如通过 `REQUIRE` 系列宏），Catch2 就不知道这个测试用例里已经没有更多 section 了，因此必须重新运行该测试用例。

### MinGW/CygWin 编译（链接）极慢

使用 MinGW 编译 Catch2 可能会非常慢，尤其是在链接阶段。就我们所知，这主要是它默认链接器的缺陷造成的。如果你能让 MinGW 改用 `lld`，例如通过 `-fuse-ld=lld`，链接时间就会下降到可接受范围。

## 功能缺失
本节概述一些缺失功能、它们的状态，以及可能的替代方案。

### 线程安全断言

Catch2 的断言宏不是线程安全的。这并不意味着你不能在 Catch 的测试中使用线程，而是说只有单个线程可以与 Catch 的断言和其他宏交互。

这意味着下面这样是可以的：
```cpp
    std::vector<std::thread> threads;
    std::atomic<int> cnt{ 0 };
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&]() {
            ++cnt; ++cnt; ++cnt; ++cnt;
        });
    }
    for (auto& t : threads) { t.join(); }
    REQUIRE(cnt == 16);
```
因为只有一个线程会经过 `REQUIRE` 宏；而下面这样就不行：
```cpp
    std::vector<std::thread> threads;
    std::atomic<int> cnt{ 0 };
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&]() {
            ++cnt; ++cnt; ++cnt; ++cnt;
            CHECK(cnt == 16);
        });
    }
    for (auto& t : threads) { t.join(); }
    REQUIRE(cnt == 16);
```

目前我们没有计划支持线程安全断言。

### 测试中的进程隔离

Catch 不支持在隔离的（fork 出来的）进程中运行测试。虽然未来可能会支持，但 Windows 不支持 fork，只允许完整的进程创建，而且我们也希望尽可能让各平台代码保持一致，这意味着这项工作大概率会耗费大量当前并不具备的开发时间。

### 并行运行多个测试

Catch2 会严格在一个进程中串行执行测试，目前也没有改变这一点的计划。如果你发现测试套件运行时间太长，想让它并行化，就必须让多个进程并排运行。

做到这一点有两种基本方式：
* 你可以把测试拆分成多个二进制，然后并行运行这些二进制
* 你也可以多次运行同一个测试二进制，但在每个进程中执行不同的测试子集

实现后者有多种方式，最简单的是使用 [test sharding](docs/docs/command-line_zh.md#test-sharding)。

## 第三方 bug

本节列出第三方组件中的已知 bug（也就是编译器、标准库、标准运行时）。

### Visual Studio 2017 -- 断言中的原始字符串字面量无法编译

Visual Studio 2017（VC 15）中有一个已知 bug，会导致预处理器尝试字符串化原始字符串字面量时编译出错（即对它应用 `#` 预处理指令）。下面这个片段就足以触发编译错误：

```cpp
#include <catch2/catch_test_macros.hpp>

TEST_CASE("test") {
    CHECK(std::string(R"("\)") == "\"\\");
}
```

Catch2 提供了一个 workaround：允许用户通过定义 `CATCH_CONFIG_DISABLE_STRINGIFICATION` 来禁用原始表达式的字符串化，如下：
```cpp
#define CATCH_CONFIG_DISABLE_STRINGIFICATION
#include <catch2/catch_test_macros.hpp>

TEST_CASE("test") {
    CHECK(std::string(R"("\)") == "\"\\");
}
```

_注意，这会改变输出：_
```
catchwork\test1.cpp(6):
PASSED:
  CHECK( Disabled by CATCH_CONFIG_DISABLE_STRINGIFICATION )
with expansion:
  ""\" == ""\"
```

### Clang/G++ -- 异常后跳过叶子 section
某些版本的 `libc++` 和 `libstdc++`（或它们的运行时）存在一个 bug：`std::uncaught_exception()` 在重新抛出之后会一直返回 `true`，即使当前并没有活动异常。下面这个片段就会在用 `libcxxrt` master 分支编译时跳过 “a” 和 “b” section：
```cpp
#include <catch2/catch_test_macros.hpp>

TEST_CASE("a") {
    CHECK_THROWS(throw 3);
}

TEST_CASE("b") {
    int i = 0;
    SECTION("a") { i = 1; }
    SECTION("b") { i = 2; }
    CHECK(i > 0);
}
```

如果你看到类似的问题，比如某些奇怪的测试路径只在 Clang + `libc++` 下出现，或者只在某个特定版本的 `libstdc++` 下出现，那很可能就是这个问题。目前已知的唯一 workaround 是使用一个固定版本的标准库。

### libstdc++、`_GLIBCXX_DEBUG` 宏和测试随机顺序

如果在定义了 `_GLIBCXX_DEBUG` 宏的情况下，用 `--order rand` 运行基于 libstdc++ 编译的 Catch2 二进制，会触发调试检查并因为自赋值而中止运行。
[这是 libstdc++ 内部的一个已知 bug](https://stackoverflow.com/questions/22915325/avoiding-self-assignment-in-stdshuffle/23691322)

Workaround：在使用开启 debug 的 libstdc++ 编译时，不要使用 `--order rand`。
