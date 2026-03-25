<a id="top"></a>
# 编译期配置

**目录**<br>
[给 Catch 宏加前缀](#prefixing-catch-macros)<br>
[终端颜色](#terminal-colour)<br>
[控制台宽度](#console-width)<br>
[stdout](#stdout)<br>
[Fallback stringifier](#fallback-stringifier)<br>
[默认 reporter](#default-reporter)<br>
[Bazel 支持](#bazel-support)<br>
[C++11 开关](#c11-toggles)<br>
[C++17 开关](#c17-toggles)<br>
[其他开关](#other-toggles)<br>
[启用字符串化](#enabling-stringification)<br>
[禁用异常](#disabling-exceptions)<br>
[覆盖 Catch 的 debug break (`-b`)](#overriding-catchs-debug-break--b)<br>
[静态分析支持](#static-analysis-support)<br>

Catch2 的目标是尽量“开箱即用”，下面这些配置选项大多数都会在编译时根据检测到的环境自动调整。不过，用户也可以通过下面记录的宏和/或同名 CMake 选项来覆盖这些检测。

## 给 Catch 宏加前缀

    CATCH_CONFIG_PREFIX_ALL

为了保持测试代码简洁，Catch 使用较短的宏名（例如 ```TEST_CASE``` 和 ```REQUIRE```）。但这些名字偶尔可能与平台头文件或被测系统中的标识符冲突。这时可以定义上面的标识符。这样所有 Catch 用户宏都会加上 ```CATCH_``` 前缀（例如 ```CATCH_TEST_CASE``` 和 ```CATCH_REQUIRE```）。

## 终端颜色

    CATCH_CONFIG_COLOUR_WIN32     // 强制启用基于 Win32 console API 的着色实现
    CATCH_CONFIG_NO_COLOUR_WIN32  // 强制禁用 ...

是的，Catch2 使用英式拼写 `colour`。

Catch2 会尝试自动检测 Win32 console 着色 API `SetConsoleTextAttribute` 是否可用，如果可用，就会编译进一个基于它的 console 着色实现。

这个选项可用于覆盖自动检测，强制开启或关闭该实现。

## 控制台宽度

    CATCH_CONFIG_CONSOLE_WIDTH = x // 其中 x 是数字

Catch 会把面向控制台的输出格式化到固定字符宽度内。这一点很重要，因为它大量使用缩进，而不受控制的自动换行会破坏格式。
默认假定控制台宽度为 80，但可以通过定义上面的标识符改成其他值。

## stdout

    CATCH_CONFIG_NOSTDOUT

为了支持没有 `std::cout`、`std::cerr` 和 `std::clog` 的平台，Catch 不直接使用它们，而是调用 `Catch::cout`、`Catch::cerr` 和 `Catch::clog`。你可以通过定义 `CATCH_CONFIG_NOSTDOUT` 并自己实现它们来替换其实现，签名如下：

    std::ostream& cout();
    std::ostream& cerr();
    std::ostream& clog();

[你可以在这里看到替换这些函数的示例。](../examples/231-Cfg-OutputStreams.cpp)

## Fallback stringifier

默认情况下，当 Catch 的字符串化机制需要把一个类型转成字符串，而这个类型没有特化 `StringMaker`、没有重载 `operator<<`、不是枚举也不是范围时，它会使用 `"{?}"`。你可以通过定义 `CATCH_CONFIG_FALLBACK_STRINGIFIER` 来指定一个函数名，从而覆盖这一行为。

所有没有提供 `StringMaker` 特化或 `operator<<` 重载的类型都会被传给这个函数（这也包括枚举和 range）。该函数必须返回 `std::string`，并且必须能接受任意类型，例如通过重载实现。

_注意，如果提供的函数没有处理某个需要字符串化的类型，编译会失败。_

## 默认 reporter

Catch 的默认 reporter 可以通过定义宏 `CATCH_CONFIG_DEFAULT_REPORTER` 来修改，值为所需默认 reporter 的字符串字面量。

这意味着把 `CATCH_CONFIG_DEFAULT_REPORTER` 定义为 `"console"`，就等价于开箱即用的默认体验。

## Bazel 支持

如果在编译 Catch2 时定义了 `CATCH_CONFIG_BAZEL_SUPPORT`，就会强制启用对 Bazel 环境变量的支持（正常情况下 Catch2 会先查找 `BAZEL_TEST=1` 环境变量）。

如果你使用的是较老版本的 Bazel，还不支持 `BAZEL_TEST` 环境变量，这会很有用。

> `CATCH_CONFIG_BAZEL_SUPPORT` 在 Catch2 3.0.1 中[引入](https://github.com/catchorg/Catch2/pull/2399)

> `CATCH_CONFIG_BAZEL_SUPPORT` 在 Catch2 3.1.0 中[废弃](https://github.com/catchorg/Catch2/pull/2459)

## C++11 开关

    CATCH_CONFIG_CPP11_TO_STRING // 使用 `std::to_string`

由于我们需要支持一些标准库里没有 `std::to_string` 的平台，因此可以强制 Catch 改用基于 `std::stringstream` 的 workaround。在 Android 以外的平台上，默认使用 `std::to_string`；在 Android 上，默认使用 `stringstream` workaround。和往常一样，你可以通过定义 `CATCH_CONFIG_CPP11_TO_STRING` 或 `CATCH_CONFIG_NO_CPP11_TO_STRING` 来覆盖 Catch 的选择。

## C++17 开关

    CATCH_CONFIG_CPP17_UNCAUGHT_EXCEPTIONS  // 覆盖对 std::uncaught_exceptions（而不是 std::uncaught_exception）支持的检测
    CATCH_CONFIG_CPP17_STRING_VIEW          // 覆盖 std::string_view 支持检测（Catch 默认提供 StringMaker 特化）
    CATCH_CONFIG_CPP17_VARIANT              // 覆盖 std::variant 支持检测（由 CATCH_CONFIG_ENABLE_VARIANT_STRINGMAKER 检查）
    CATCH_CONFIG_CPP17_OPTIONAL             // 覆盖 std::optional 支持检测（由 CATCH_CONFIG_ENABLE_OPTIONAL_STRINGMAKER 检查）
    CATCH_CONFIG_CPP17_BYTE                 // 覆盖 std::byte 支持检测（Catch 默认提供 StringMaker 特化）

> `CATCH_CONFIG_CPP17_STRING_VIEW` 在 Catch2 2.4.1 中[引入](https://github.com/catchorg/Catch2/issues/1376)

Catch 包含基础的编译器/标准库检测，并会在合适时尝试使用一些 C++17 特性。这个自动检测可以通过宏从两个方向手工覆盖：定义上表中的宏可以启用某个特性，而在宏中使用 `_NO_` 则可以禁用它，例如 `CATCH_CONFIG_NO_CPP17_UNCAUGHT_EXCEPTIONS`。

## 其他开关

    CATCH_CONFIG_COUNTER                    // 使用 __COUNTER__ 生成测试用例的唯一名称
    CATCH_CONFIG_WINDOWS_SEH                // 启用 Windows 上的 SEH 处理
    CATCH_CONFIG_FAST_COMPILE               // 牺牲一些（相对较小的）功能来换取更快的编译速度
    CATCH_CONFIG_POSIX_SIGNALS              // 启用 POSIX 信号处理
    CATCH_CONFIG_WINDOWS_CRTDBG             // 启用 Windows CRT Debug Heap 的泄漏检查
    CATCH_CONFIG_DISABLE_STRINGIFICATION    // 禁用原始表达式字符串化
    CATCH_CONFIG_DISABLE                    // 禁用断言和测试用例注册
    CATCH_CONFIG_WCHAR                      // 启用 wchart_t 的使用
    CATCH_CONFIG_EXPERIMENTAL_REDIRECT      // 启用一种新的（实验性）stdout/stderr 捕获方式
    CATCH_CONFIG_USE_ASYNC                  // 在 benchmark 期间强制并行统计处理样本
    CATCH_CONFIG_ANDROID_LOGWRITE           // 使用 android 的日志系统输出调试信息
    CATCH_CONFIG_GLOBAL_NEXTAFTER           // 使用 nextafter{,f,l} 而不是 std::nextafter
    CATCH_CONFIG_GETENV                     // 系统提供可用的 `getenv`

> [`CATCH_CONFIG_ANDROID_LOGWRITE`](https://github.com/catchorg/Catch2/issues/1743) 和 [`CATCH_CONFIG_GLOBAL_NEXTAFTER`](https://github.com/catchorg/Catch2/pull/1739) 在 Catch2 2.10.0 中引入

> `CATCH_CONFIG_GETENV` 在 Catch2 3.2.0 中[引入](https://github.com/catchorg/Catch2/pull/2562)

目前 Catch 只在使用 MSVC 编译时启用 `CATCH_CONFIG_WINDOWS_SEH`，因为某些版本的 MinGW 没有必要的 Win32 API 支持。

`CATCH_CONFIG_POSIX_SIGNALS` 默认开启，除非在 `Cygwin` 下编译 Catch；在 Cygwin 下它默认关闭，但可以通过定义 `CATCH_CONFIG_POSIX_SIGNALS` 强制启用。

`CATCH_CONFIG_GETENV` 默认开启，除非 Catch2 编译在没有可用 `std::getenv` 的平台上（目前是 Windows UWP 和 PlayStation）。

`CATCH_CONFIG_WINDOWS_CRTDBG` 默认关闭。如果启用，Windows CRT 会用于检查内存泄漏，并在测试结束后显示它们。这个选项只在链接默认 main 时有效，而且必须对整个库构建都定义。

`CATCH_CONFIG_WCHAR` 默认开启，但可以禁用。目前它只用于支持 DJGPP cross-compiler。

除了 `CATCH_CONFIG_EXPERIMENTAL_REDIRECT` 外，其他这些开关都可以通过 `_NO_` 形式禁用，例如 `CATCH_CONFIG_NO_WINDOWS_SEH`。

### `CATCH_CONFIG_FAST_COMPILE`
这个编译期标志通过大约 20% 的编译提速来换取断言宏编译速度。做法是对非异常类断言宏（`{REQUIRE`,`CHECK`}{``,`_FALSE`, `_THAT`}）禁用断言局部的 try-catch 块生成。
这会禁用这些断言下抛出异常的翻译，但不应导致误判为通过。

`CATCH_CONFIG_FAST_COMPILE` 必须在链接到同一个测试二进制的所有 translation unit 中要么都定义，要么都不定义。

### `CATCH_CONFIG_DISABLE_STRINGIFICATION`
这个开关用于 VS 2017 bug 的 workaround。详情见[已知限制](limitations_zh.md#visual-studio-2017----raw-string-literal-in-assert-fails-to-compile)。

### `CATCH_CONFIG_DISABLE`
这个开关会从给定文件中移除 Catch 的大部分内容。这意味着 `TEST_CASE` 不会注册，断言也会变成 no-op。适用于把测试放进实现文件（即仅有内部链接的函数）而不是外部文件。

这个功能被视为实验性功能，可能在任何时候发生变化。

_灵感来自 Doctest 的 `DOCTEST_CONFIG_DISABLE`_

## 启用字符串化

默认情况下，Catch 不会字符串化标准库中的某些类型。这是为了避免默认拖入各种标准库头文件。不过，Catch 确实内置了这些支持，可以通过下面这些宏启用：

    CATCH_CONFIG_ENABLE_PAIR_STRINGMAKER     // 为 std::pair 提供 StringMaker 特化
    CATCH_CONFIG_ENABLE_TUPLE_STRINGMAKER    // 为 std::tuple 提供 StringMaker 特化
    CATCH_CONFIG_ENABLE_VARIANT_STRINGMAKER  // 为 std::variant、std::monostate（在 C++17 下）提供 StringMaker 特化
    CATCH_CONFIG_ENABLE_OPTIONAL_STRINGMAKER // 为 std::optional（在 C++17 下）提供 StringMaker 特化
    CATCH_CONFIG_ENABLE_ALL_STRINGMAKERS     // 定义以上所有宏

> `CATCH_CONFIG_ENABLE_VARIANT_STRINGMAKER` 在 Catch2 2.4.1 中[引入](https://github.com/catchorg/Catch2/issues/1380)

> `CATCH_CONFIG_ENABLE_OPTIONAL_STRINGMAKER` 在 Catch2 2.6.0 中[引入](https://github.com/catchorg/Catch2/issues/1510)

## 禁用异常

> Catch2 2.4.0 中引入。

默认情况下，Catch2 使用异常来报告错误，并在 `REQUIRE` 系列断言失败时中止测试。我们也提供了一种实验性的禁用异常支持。Catch2 应该会自动检测自己是否在禁用异常的条件下编译，但你也可以通过定义下面这个宏来强制不使用异常：

    CATCH_CONFIG_DISABLE_EXCEPTIONS

注意，在不使用异常的情况下，存在两个主要限制：

1) 如果出现一个通常会通过异常报告的错误，异常消息会改写到 `Catch::cerr`，然后调用 `std::terminate`。
2) 如果 `REQUIRE` 系列宏失败，active reporter 返回后会调用 `std::terminate`。

还有一个额外的自定义点可以控制异常被抛出时的具体行为。要使用它，请定义：

    CATCH_CONFIG_DISABLE_EXCEPTIONS_CUSTOM_HANDLER

并提供下面这个函数的定义：

```cpp
namespace Catch {
    [[noreturn]]
    void throw_exception(std::exception const&);
}
```

## 覆盖 Catch 的 debug break (`-b`)

> Catch2 2.11.2 中引入。

你可以通过定义 `CATCH_BREAK_INTO_DEBUGGER()` 宏来覆盖 Catch2 进入调试器的代码。如果 Catch2 不认识你的平台，或者平台被误识别，这会很有用。

这个宏会按原样使用，也就是说 `CATCH_BREAK_INTO_DEBUGGER();` 必须能编译，并且必须真的进入调试器。

## 静态分析支持

> Catch2 3.4.0 中引入。

Catch2 的某些部分，例如 `SECTION`，对静态分析工具来说不太好推理。Catch2 可以改变内部实现，帮助静态分析工具理解测试。

Catch2 会自动检测一些静态分析工具（最初实现会检查 clang-tidy 和 Coverity），但你也可以通过下面的宏在任一方向上覆盖其检测：

```
CATCH_CONFIG_EXPERIMENTAL_STATIC_ANALYSIS_SUPPORT     // 强制启用静态分析帮助
CATCH_CONFIG_NO_EXPERIMENTAL_STATIC_ANALYSIS_SUPPORT  // 强制禁用静态分析帮助
```

_顾名思义，这仍然是实验性功能，因此我们不提供向后兼容保证。_

**不要在你打算实际运行的构建里启用这个选项。** 改变后的内部实现不是用来运行的，只是为了“可扫描”。

---

[Home](Readme_zh.md#top)
