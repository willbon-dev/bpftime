<a id="top"></a>

# 发布说明
**目录**<br>
[3.3.2](#332)<br>
[3.3.1](#331)<br>
[3.3.0](#330)<br>
[3.2.1](#321)<br>
[3.2.0](#320)<br>
[3.1.1](#311)<br>
[3.1.0](#310)<br>
[3.0.1](#301)<br>
[2.13.7](#2137)<br>
[2.13.6](#2136)<br>
[2.13.5](#2135)<br>
[2.13.4](#2134)<br>
[2.13.3](#2133)<br>
[2.13.2](#2132)<br>
[2.13.1](#2131)<br>
[2.13.0](#2130)<br>
[2.12.4](#2124)<br>
[2.12.3](#2123)<br>
[2.12.2](#2122)<br>
[2.12.1](#2121)<br>
[2.12.0](#2120)<br>
[2.11.3](#2113)<br>
[2.11.2](#2112)<br>
[2.11.1](#2111)<br>
[2.11.0](#2110)<br>
[2.10.2](#2102)<br>
[2.10.1](#2101)<br>
[2.10.0](#2100)<br>
[2.9.2](#292)<br>
[2.9.1](#291)<br>
[2.9.0](#290)<br>
[2.8.0](#280)<br>
[2.7.2](#272)<br>
[2.7.1](#271)<br>
[2.7.0](#270)<br>
[2.6.1](#261)<br>
[2.6.0](#260)<br>
[2.5.0](#250)<br>
[2.4.2](#242)<br>
[2.4.1](#241)<br>
[2.4.0](#240)<br>
[2.3.0](#230)<br>
[2.2.3](#223)<br>
[2.2.2](#222)<br>
[2.2.1](#221)<br>
[2.2.0](#220)<br>
[2.1.2](#212)<br>
[2.1.1](#211)<br>
[2.1.0](#210)<br>
[2.0.1](#201)<br>
[更早版本](#older-versions)<br>
[更更早版本](#even-older-versions)<br>

## 3.4.0

### 改进
* `VectorEquals` 现在支持只实现 `==` 而不实现 `!=` 的元素 (#2648)
* Catch2 现在支持使用 IAR 编译器编译 (#2651)
* 多项内部性能小优化
* 多项内部编译时间小优化
* XMLReporter 现在会为 INFO 和 WARN 报告位置信息 (#1251)
  * 这会把 XML 格式版本提升到 3
* 文档中补充了 `SKIP` 可在 generator 构造函数中用于处理空 generator 的说明 (#1593)
* 为 `TEST_CASE` 和 `SECTION` 宏添加了实验性的静态分析支持 (#2681)
  * 这两个宏会以一种便于静态分析工具推理 section 路径的方式重新定义
  * 支持由 `CATCH_CONFIG_EXPERIMENTAL_STATIC_ANALYSIS_SUPPORT` 控制，并会自动检测 clang-tidy 和 Coverity
* `*_THROWS`、`*_THROWS_AS` 等宏现在会抑制 GCC 上来自 `__attribute__((warn_unused_result))` 的警告 (#2691)
  * 不像普通的 `[[nodiscard]]`，这个警告不会因为 void cast 而被静默。GCC 是怎么回事？

### 修复
* 修复了 `assertionStarting` 事件在表达式求值之后才发出的问题 (#2678)
* `TEST_CASE` 标签中的错误现在会被友好地报告 (#2650)

### 其他
* `catch_discover_tests` 有了一些改进
  * 新增 `DISCOVERY_MODE` 选项，可让发现在构建后或运行前进行
  * 修复了测试名称中分号和反斜杠的处理 (#2674, #2676)
* meson 构建现在可以禁用测试构建 (#2693)
* meson 构建现在正确把 0.54.1 设为最低支持版本 (#2688)

## 3.3.2

### 改进
* 进一步减少分配
  * compact、console、TAP 和 XML reporter 在多种情况下分配更少
  * 每次进入 `SECTION`/`TEST_CASE` 时少了一次分配
  * 在 stdout/stderr 被捕获时，每次测试退出少了两次分配
* 性能改进
  * section 追踪比 v3.3.0 快 10%-25%
  * 断言处理比 v3.3.0 快 5%-10%
  * 测试用例注册比 v3.3.0 快 1%-2%
  * listener 注册有微小提速
  * `CAPTURE`、`TEST_CASE_METHOD`、`METHOD_AS_TEST_CASE` 和 `TEMPLATE_LIST_TEST_*` 宏有微小提速
* `Contains`、`RangeEquals` 和 `UnorderedRangeEquals` 现在支持 iterator + sentinel 对
* 新增 `IsNaN` matcher
  * 和 `REQUIRE(isnan(x))` 不同，`REQUIRE_THAT(x, IsNaN())` 会显示 `x` 的值
* 抑制了 NVHPC 的 `declared_but_not_referenced` 警告 (#2637)

### 修复
* 修复了 v3.3.1 引入的 section 追踪性能回退
  * 极端情况下会比 v3.3.0 慢大约 4 倍

## 3.3.1

### 改进
* 减少分配并提升性能
  * 具体提升取决于你的 Catch2 用法
  * 例如运行 Catch2 的 SelfTest 二进制会少 8k 次分配
  * 主要收益来自对 `SECTION`，尤其是 sibling `SECTION`，更智能的处理

## 3.3.0

### 改进
* 新增 `MessageMatches` 异常 matcher (#2570)
* 新增 `RangeEquals` 和 `UnorderedRangeEquals` 通用 range matcher (#2377)
* 新增 `SKIP` 宏，可在测试体内跳过测试 (#2360)
  * 所有内置 reporter 都已扩展以正确处理它；自定义 reporter 是否要改取决于实现方式
  * 这里的 `skipTest` reporter 事件与之 **无关**，并且由于几乎没什么用途，已经废弃
* 恢复了在进入调试器功能中对 PPC Mac 的支持 (#2619)
* 让 warning suppression 与 CUDA toolkit pre 11.5 兼容 (#2626)
* 清理了一些静态分析告警

### 修复
* 修复了当 NVCC 作为 MSVC 报告时的宏重定义警告 (#2603)
* 修复了 generator 构造函数里抛异常会导致整个二进制中止的问题 (#2615)
  * 现在只是让测试失败
* 修复了 libstdc++13 下缺失的 transitive include (#2611)

### 其他
* 改善了 Windows 上非 MSVC 编译器构建动态库的支持 (#2630)
* 作为子项目使用时，Catch2 会把生成的 header 放到与主项目分开的目录中 (#2604)

## 3.2.1

### 改进
* 修正了重写后的 decomposer，使其适配更老的（pre 9）GCC 版本 (#2571)
  * **这需要做更大改动才能正确支持 C++20，因此可能还有 bug。**

## 3.2.0

### 改进
* Catch2 现在可以在 PlayStation 上编译 (#2562)
* 新增 `CATCH_CONFIG_GETENV` 编译期开关 (#2562)
  * 这个开关用于控制 Catch2 读取环境变量时是否调用 `std::getenv`
* 新增对更多 Bazel 测试环境变量的支持
  * 现在支持 `TESTBRIDGE_TEST_ONLY` (#2490)
  * 现在支持 sharding 变量 `TEST_SHARD_INDEX`、`TEST_TOTAL_SHARDS`、`TEST_SHARD_STATUS_FILE` (#2491)
* reporter 有一些小改进
  * TAP 和 SonarQube reporter 会输出所使用的测试过滤器
  * XML reporter 现在也会报告其输出格式版本
  * compact reporter 现在使用和 console reporter 相同的 summary 输出 (#878, #2554)
* 新增对只能与字面量 0 比较的类型的断言支持 (#2555)
  * 一个典型例子是 C++20 的 `std::*_ordering` 类型，它们不能与 `int` 变量比较，只能与 `0` 比较
  * 这种支持适用于所有具有此属性的类型，不限于标准库中的那些
  * 这会让大量使用 `REQUIRE` 等宏的文件编译速度下降 2-3%
  * **这需要对 decomposition 做大幅重写，因此可能还有 bug**
* 简化了与 matcher 相关宏的内部实现
  * 这会让大量使用 `REQUIRE_THAT` 等宏的文件编译速度提升约 2%

### 修复
* 清理了一些 warning 和静态分析问题
  * 抑制了模板化测试用例里偶尔出现的 `-Wcomma` 警告 (#2543)
  * 让 `INFO` 的实现细节变成 const (#2564)
  * 让 `MatcherGenericBase` 的拷贝构造函数变成 const (#2566)
* 修复了测试过滤器的序列化，使输出可以 roundtrip
  * 例如 `./tests/SelfTest "aaa bbb", [approx]` 会输出 `Filters: "aaa bbb",[approx]`

### 其他
* Catch2 的构建不再把 `-ffile-prefix-map` 设置泄漏给依赖它的项目 (#2533)

## 3.1.1

### 改进
* 新增 `Catch::getSeed` 函数，用户代码可以用它读取当前 rng-seed
* 更好地检测编译器对 `-ffile-prefix-map` 的支持 (#2517)
* Catch2 的 shared library 现在设置了 `SOVERSION` (#2516)
* `catch2/catch_all.hpp` 便利头不再传递性包含 `windows.h` (#2432, #2526)

### 修复
* 修复了 Universal Windows Platform 上的编译
* 修复了 VxWorks 上的编译 (#2515)
* 修复了 Cygwin 上的编译 (#2540)
* 移除了 reporter 注册中的未使用变量 (#2538)
* 修复了 Windows 动态库的一些符号可见性问题 (#2527)
* 抑制了 `REQUIRE_THROWS*` 宏里的 `-Wuseless-cast` 警告 (#2520, #2521)
  * 这个问题会在可能抛异常的表达式求值为 `void` 时触发
* 修复了 `nvc++` 上的 "warning: storage class is not first" 警告 (#2533)
* 修复了 MacOS 上 `catch_discover_tests` 对 `DL_PATHS` 参数的处理 (#2483)
* 在 `TEMPLATE_TEST_CASE` 中抑制了 `*-avoid-c-arrays` 的 clang-tidy 警告 (#2095, #2536)

### 其他
* 修复了 Catch2 作为动态库构建时的 CMake install 步骤 (#2485)
* 提升最低 CMake 版本到 3.10 (#2523)
  * 未来几次 release 里还会再提升一次最低版本
* 大量文档更新和修复
  * #1444, #2497, #2547, #2549 等
* 新增对 Meson 构建 Catch2 的支持 (#2530, #2539)

## 3.1.0

### 改进
* 改进了对 `--list*` 输出的 reporter 化支持 (#2061, #2163)
* 改进了 `catch_discover_tests` (#2023, #2039)
  * 现在可以指定使用哪个 reporter
  * 现在可以修改输出写到哪里
  * 会尊重 `WORKING_DIRECTORY`
* `ParseAndAddCatchTests` 现在支持 `TEMPLATE_TEST_CASE` 宏 (#2031)
* 各种文档修复和改进 (#2022, #2028, #2034)

## 3.0.1

**Catch2 现在使用静态编译库作为分发模型。**
**这也意味着，如果你想在测试文件中使用 Catch2 的全部功能，需要包含多个头文件。**

你大概会想看看 [迁移文档](migrate-v2-to-v3_zh.md#top)，它是专门为从 v2.x.x 迁移到 v3 发布版本而写的。

### FAQ

* 为什么 Catch2 要拆成多个头文件？
  * 简短答案是：为了未来的扩展性和可伸缩性。长答案比较复杂，可以看我的博客；最基本的原因是，单头文件分发与提供丰富功能是有冲突的。Catch2 还是单头文件时，新增一个 matcher 会给所有人带来编译开销，但实际上只有一部分用户会用到。这意味着在单头文件模型下，新增 Matchers/Generators 等功能的门槛很高，而在新模型里则小得多。
* 未来 Catch2 还会重新分发单头文件版本吗？
  * 不会。不过我们提供 sqlite-style 的 amalgamated 分发选项，也就是你可以只下载一个 .cpp 和一个 header，放到自己的源码旁边。不过这么做的缺点和使用 `catch_all.hpp` 很类似。
* 为什么把 `catch.hpp` 换成 `catch_all.hpp` 会带来这么大的破坏性变化？
  * `catch_all.hpp` 便利头存在两个原因：其一是方便从 Catch2 快速迁移；其二是方便快速用 Catch2 测试东西。把它用于迁移有一个缺点，那就是它很“大”。这意味着包含它会显著拖慢编译时间，所以把它用于迁移应该是用户主动做出的决定，而不该是不知不觉踩进去的坑。

### （可能）破坏性变更
* **Catch2 现在使用静态编译库作为分发模型**
  * **`catch.hpp` 不再可用**
* **Catch2 现在以 C++14 作为最低支持语言版本**
* `ANON_TEST_CASE` 已移除，请改用不带参数的 `TEST_CASE` (#1220)
* `--list*` 命令现在不再返回非零退出码 (#1410)
* `--list-test-names-only` 已移除 (#1190)
  * 应该改用 `--list-tests` 的 verbosity 修饰项
* `--list*` 命令现在通过 reporter 走
  * 顶层 reporter 接口提供了和旧行为兼容的默认实现
  * XmlReporter 输出可被机器解析的 XML
* `TEST_CASE` 的 description 支持已移除
  * 如果第二个参数里除了 tags 还有别的文本，这些文本会被忽略
* 隐藏测试用例不再因为它们不匹配排除标签而被自动包含
  * 以前 `TEST_CASE("A", "[.foo]")` 会因为查询 `~[bar]` 而被包含
* `PredicateMatcher` 不再做 type erasure
  * 这意味着提供的 predicate 类型会成为 `PredicateMatcher` 类型的一部分
* `SectionInfo` 不再包含 section description 成员 (#1319)
  * 你仍然可以写 `SECTION("ShortName", "Long and wordy description")`，但 description 会被丢弃
  * description 类型现在必须是 `const char*` 或可隐式转换为它
* `[!hide]` 标签已移除
  * 请改用 `[.]` 或 `[.foo]`
* 组合 matcher 的 lvalue 不能继续组合
* `REGISTER_TEST_CASE` 宏的使用后面需要加分号
  * 这不会影响 `TEST_CASE` 等宏
* `IStreamingReporter::IsMulti` 成员函数已移除
  * 这几乎不可能影响任何人，因为它本来就是接口里的默认实现，也只在内部使用
* 多个不适合用户扩展的类被设为 final
  * `ListeningReporter` 现在是 `final`
  * 具体 Matchers（例如 `UnorderedEquals` vector matcher）现在是 `final`
  * 所有 Generators 现在都是 `final`
* Matcher 的命名空间被重新整理
  * matcher 类型不再位于深层内部命名空间
  * matcher 工厂函数不再被带入 `Catch` 命名空间
  * 这意味着现在所有对外可见的 matcher 相关功能都位于 `Catch::Matchers` 命名空间
* 定义 `CATCH_CONFIG_MAIN` 将不再在该 TU 中创建 main
  * 请链接 `libCatch2Main.a`，或者使用正确的 CMake/pkg-config target
  * 如果你想写自定义 main，请包含 `catch2/catch_session.hpp`
* `CATCH_CONFIG_EXTERNAL_INTERFACES` 已移除
  * 应该按需包含合适的头文件
* `CATCH_CONFIG_IMPL` 已移除
  * 现在实现编译进静态库
* Event Listener 接口发生了变化
  * `TestEventListenerBase` 已重命名为 `EventListenerBase`
  * `EventListenerBase` 现在直接继承自 `IStreamingReporter`，而不是继承 `StreamingReporterBase`
* `GENERATE` 会衰减其参数 (#2012, #2040)
  * 例如 `auto str = GENERATE("aa", "bb", "cc");` 中的 `str` 会被推导成 `char const*`，而不是 `const char[2]`
* `--list-*` 标志会把输出写到 `-o` 指定的文件
* reporter 接口有很多变化
  * 除 XmlReporter 外，第一方 reporter 的输出应保持不变
  * 新增了一对事件
  * 移除一个废弃事件
  * 基类已重命名
  * 内置 reporter 类层次结构已重做
* 如果用户没有指定，Catch2 会自动生成随机种子
* `--list-tests` 的短参数 `-l` 已移除
  * 这个参数不常用，不值得占用宝贵的单字母空间
* `--list-tags` 的短参数 `-t` 已移除
  * 同上
* `--colour` 选项被 `--colour-mode` 选项替代

### 改进
* Matchers 扩展为支持更多 `match` 签名 (#1307, #1553, #1554, #1843)
  * 包括 templated `match` 成员函数
  * 细节见[重写后的 Matchers 文档](matchers_zh.md#top)
  * Catch2 目前提供了一些 generic matchers，不过在 v3 正式版前还应该更多一些
    * `IsEmpty`、`SizeIs`：检查 range 是否满足特定属性
    * `Contains`：检查 range 是否包含某个元素
    * `AllMatch`、`AnyMatch`、`NoneMatch`：把 matcher 应用于 range 中的元素
* 编译时间显著改善
  * 包含 `catch_test_macros.hpp` 比包含 `catch.hpp` 便宜 80%
* 一些运行时性能优化
  * 下表展示的是 v3 相对 v2 在同一任务上的速度提升

|                   任务                      |  debug build | release build |
|:------------------------------------------- | ------------:| -------------:|
| 运行 100 万次 `REQUIRE(true)`               |  1.10 ± 0.01 |   1.02 ± 0.06 |
| 运行 100 个测试、3^3 个 section、每个 1 个 REQUIRE |  1.27 ± 0.01 |   1.04 ± 0.01 |
| 运行 3000 个测试，无名字、无标签            |  1.29 ± 0.01 |   1.05 ± 0.01 |
| 运行 3000 个测试，有名字、有标签            |  1.49 ± 0.01 |   1.22 ± 0.01 |
| 从 3000 个测试中只运行 1 个，无名字、无标签 |  1.68 ± 0.02 |   1.19 ± 0.22 |
| 从 3000 个测试中只运行 1 个，有名字、有标签 |  1.79 ± 0.02 |   2.06 ± 0.23 |

* POSIX 平台在构造日期字符串时使用 `gmtime_r`，而不是 `gmtime` (#2008, #2165)
* `--list-*` 标志会把输出写到 `-o` 指定的文件 (#2061, #2163)
* `Approx::operator()` 现在正确地是 `const`
* Catch2 内部 helper 变量不再使用保留标识符 (#578)
* `--rng-seed` 现在接受字符串 `"random-device"`，以 `std::random_device` 生成随机种子
* Catch2 现在支持 test sharding (#2257)
  * 你可以要求把测试拆成 N 组，并只运行其中一组
  * 这大大简化了通过外部运行器并行化单个二进制测试的方式
* 内嵌 CLI parser 现在支持可重复调用的 lambda
  * 基于 lambda 的 option parser 可以声明自己可被重复指定
* 新增 `STATIC_CHECK` 宏，类似 `STATIC_REQUIRE` (#2318)
  * 在推迟到运行时的时候，它表现得像 `CHECK`，而不是 `REQUIRE`
* 你现在可以有多个同名测试，只要测试身份的其他部分不同即可 (#1915, #1999, #2175)
  * 测试身份包括测试名、测试标签，以及（如果适用）测试类名
* 新增警告 `UnmatchedTestSpec`，用于在测试 spec 没有匹配测试时报告错误
* `-w`、`--warn` 警告标志现在可以多次提供，以启用多个 warning
* 标签的大小写不敏感处理现在更可靠，而且内存占用更少
* 测试用例和断言计数现在不再可能在 32 位系统上合理地溢出
  * 计数现在在所有平台上都使用 `uint64_t`，而不是 `size_t`
* `-o`、`--out` 输出目标支持 `-` 作为 stdout
  * 你需要写成 `--out=-`，以避免 CLI 因为缺少参数报错
  * 新的 reporter 规格也支持 `-` 作为 stdout
* 现在可以同时运行多个 reporter，并写到不同文件 (#1712, #2183)
  * 为此，`-r`、`--reporter` 标志现在也接受可选输出目标
  * 关于多个 reporter 的完整语义，请查阅 reporter 文档
  * 为了支持新语法，reporter 名称不能再包含 `::`
* console 颜色支持被重写并显著改进
  * 基于 ANSI 颜色码的实现始终可用
  * 颜色实现会尊重其关联流
    * 以前，例如 Win32 实现即使 Catch2 正在写文件，也会修改 console 颜色
  * 颜色 API 能抵抗表达式求值顺序变化
  * 相关 CLI 标志和编译期配置选项都已变化
    * 详情见命令行和编译期配置文档
* 新增对 Bazel 集成的 `XML_OUTPUT_FILE` 环境变量支持 (#2399)
  * 这需要在编译时启用
* 新增 `--skip-benchmarks` 标志，可在不运行任何 `BENCHMARK` 的情况下执行测试 (#2392, #2408)
* 新增通过 `--list-listeners` 列出二进制中所有 listener 的选项

### 修复
* `INFO` 宏不再包含多余的分号 (#1456)
* `--list*` 系列命令行标志现在成功时返回 0 (#1410, #1146)
* benchmark 失败的各种方式现在都会被正确计数并报告
* ULP matcher 现在能正确处理带不同符号的数字比较 (#2152)
* 通用 ADL 找到的运算符不应再破坏 decomposition (#2121)
* reporter 选择现在正确地大小写不敏感
  * 以前它会强制转换成小写名称，这会让带大写字符的 reporter 出错
* cumulative reporter base 现在会把 benchmark 结果和断言结果一起保存
* Catch2 的 SE 处理现在不应再干扰 Windows 上的 ASan (#2334)
* 修复了在重定向 stdout 的测试中 Windows console 颜色处理的问题 (#2345)
* 修复了 `random` generators 一直返回相同值的问题

### 其他变更
* `CATCH_CONFIG_DISABLE_MATCHERS` 不再存在
  * 如果你不想在某个 TU 中使用 Matchers，就不要包含它们的头文件
* `CATCH_CONFIG_ENABLE_CHRONO_STRINGMAKER` 不再存在
  * `<chrono>` 的 `StringMaker` 特化现在总是提供
* Catch2 的 CMake 现在提供 2 个 target：`Catch2` 和 `Catch2WithMain`
  * `Catch2` 是单独的静态编译实现
  * `Catch2WithMain` 还会链接默认 main
* Catch2 的 pkg-config 集成也提供 2 个包
  * `catch2` 是单独的静态编译实现
  * `catch2-with-main` 还会链接默认 main
* 传给 Catch2 的无效 test spec 现在会在测试开始前报告，并且属于硬错误
* 运行 0 个测试（例如二进制为空，或者 test spec 没匹配到任何内容）会返回非 0 退出码
  * `--allow-running-no-tests` 可以覆盖这个行为
  * `NoTests` warning 已移除，因为它已经完全被这个变化覆盖
* Catch2 的编译期配置选项（`CATCH_CONFIG_FOO`）可以通过同名 CMake 选项设置
  * 它们遵循和 C++ define 相同的语义，包括 `CATCH_CONFIG_NO_FOO` 覆盖
    * `-DCATCH_CONFIG_DEFAULT_REPORTER=compact` 会把默认 reporter 改成 "compact"
    * `-DCATCH_CONFIG_NO_ANDROID_LOGWRITE=ON` 会强制关闭 android logwrite
    * `-DCATCH_CONFIG_ANDROID_LOGWRITE=OFF` 不会有任何作用（define 不会存在）

## 2.13.7
### 修复
* benchmark 中补了缺失的 `<iterator>` include (#2231)
* 修复了开启 benchmarking 时的 noexcept 构建 (#2235)
* 修复了支持 C++17 但不支持 C++17 library 的编译器构建 (#2195)
* JUnit 在报告耗时时只使用 3 位小数 (#2221)
* `!mayfail` 标签测试现在会在 JUnit reporter 输出中标记为 `skipped` (#2116)

## 2.13.6
### 修复
* 禁用所有 signal handler 后不再破坏编译 (#2212, #2213)
### 其他
* `catch_discover_tests` 对转义分号 (`;`) 的处理更好了 (#2214, #2215)

## 2.13.5
### 改进
* 改进了 MAC 和 IPHONE 平台检测 (#2140, #2157)
* 为 XLC 16.1.0.1 的 bug 增加 workaround (#2155)
* 新增对伪装成 GCC 的 LCC 的检测 (#2199)
* 修改了 POSIX 信号处理，使其支持更新的 libc (#2178)
  * `MINSIGSTKSZ` 现在不能再在 constexpr 上下文中使用
### 修复
* 修复了在定义 `min` 和 `max` 宏时 benchmark 的编译 (#2159)
  * 不带 `NOMINMAX` 包含 `windows.h` 仍然是很糟糕的主意，不要这么做
### 其他
* 检查 Catch2 是否作为子项目构建的逻辑现在更可靠了 (#2202, #2204)
  * 问题在于如果内部使用的变量名与包含 Catch2 作为子项目的项目里定义的变量同名，就不会被正确覆盖给 Catch2 的 CMake

## 2.13.4
### 改进
* 改进了用于测试用例洗牌的哈希算法 (#2070)
  * 只在最后一个字符不同的 `TEST_CASE` 应该也能正确洗牌
  * 注意，这意味着即使使用同一个 seed，v2.13.4 的测试顺序也会和 2.13.3 不同
### 其他
* 废弃 `ParseAndAddCatchTests` CMake 集成 (#2092)
  * 对 Catch2 提供的所有测试用例变体来说，无法正确实现它；而且已经有更好的方案
  * 请改用 `catch_discover_tests`，它依赖运行时信息来获取可用测试
* 修复了 `catch_discover_tests` 在某些项目结构中使用时会失败的 bug (#2119)
* 新增 Bazel build file
* 在 CMake 中新增了一个实验性的静态库 target

## 2.13.3
### 修复
* 修复了结合 generators 和 section filter（`-c` 选项）时可能出现的无限循环 (#2025)
### 其他
* 修复了 `ParseAndAddCatchTests` 找不到无标签 `TEST_CASE` 的问题 (#2055, #2056)
* `ParseAndAddCatchTests` 支持用于改变 `add_test` 行为的 `CMP0110` policy (#2057)
  * 这是 CMake 3.18.0 中那个短命的改动，它曾暂时破坏 `ParseAndAddCatchTests`

## 2.13.2
### 改进
* 为 AppleClang shadowing bug 实现了 workaround (#2030)
* 为 NVCC ICE 实现了 workaround (#2005, #2027)
### 修复
* 修复了非 MSVC 平台上对 `std::uncaught_exceptions` 支持的检测 (#2021)
* 修复了 Windows 下实验性的 stdout/stderr 捕获 (#2013)
### 其他
* `catch_discover_tests` 得到了显著改进 (#2023, #2039)
  * 现在可以指定使用哪个 reporter
  * 现在可以修改输出写到哪里
  * `WORKING_DIRECTORY` 设置会被尊重
* `ParseAndAddCatchTests` 现在支持 `TEMPLATE_TEST_CASE` 宏 (#2031)
* 多项文档修复和改进 (#2022, #2028, #2034)

## 2.13.1
### 改进
* `ParseAndAddCatchTests` 正确处理 CMake v3.18.0 (#1984)
* 改进了对 `std::byte` 的自动检测 (#1992)
* 简化了模板化测试用例的实现 (#2007)
  * 这应该会对编译吞吐量产生一点正向影响
### 修复
* 自动字符串化 range 时更好地处理 sentinel range (#2004)

## 2.13.0
### 改进
* `GENERATE` 现在可以出现在同一层级嵌套中某个 `SECTION` 之后 (#1938)
  * `GENERATE` 之前的 `SECTION` 不会重复运行，后面的会
* 新增 `-D`/`--min-duration` 命令行标志 (#1910)
  * 如果测试耗时超过该值，就会打印测试名和耗时
  * 这个标志会被 `-d`/`--duration` 覆盖
### 修复
* `TAPReporter` 不再跳过成功断言 (#1983)

## 2.12.4
### 改进
* 新增对 ARM 上 MacOS 的支持 (#1971)

## 2.12.3
### 修复
* 在 for 循环里嵌套的 `GENERATE` 不再创建多个 generator (#1913)
* 修复了 `TEMPLATE_TEST_CASE_SIG` 在 6 个或更多参数时的复制粘贴错误 (#1954)
* 修复了 CLI 参数中处理非 ASCII 字符时可能出现的 UB (#1943)
### 改进
* 单行可以有多个 `GENERATE` 调用
* 改进了对 `fno-except` 的支持，适用于没有异常相关 std 函数 shim 的平台 (#1950)
  * 例如 Green Hills C++ 编译器
* XmlReporter 现在也会报告测试用例级别的统计信息 (#1958)
  * 这是通过一个新元素 `OverallResultsCases` 完成的
### 其他
* 仓库里新增 `.clang-format` 文件 (#1182, #1920)
* 重写了贡献文档
  * 现在应该能更好地解释不同层级的测试等内容

## 2.12.2
### 修复
* 如果 `is_range` 通过 ADL 找到的是已删除函数，就不再编译失败 (#1929)
* 如果表达式里包含非 ASCII 字符，`CAPTURE` 的潜在 UB 已修复 (#1925)
### 改进
* 如果可用，优先使用 `std::invoke_result`，不再使用 `std::result_of` (#1934)
* JUnit reporter 会为测试写出 `status` 属性 (#1899)
* 抑制了 clang-tidy 的 `hicpp-vararg` 警告 (#1921)
  * Catch2 之前就已经抑制了该警告的 `cppcoreguidelines-pro-type-vararg` 别名

## 2.12.1
### 修复
* Vector matchers 现在更好地支持 initializer list 字面量
### 改进
* `CHECK` 和 `REQUIRE` 现在支持 `^`（bitwise xor）

## 2.12.0
### 改进
* 随机顺序运行测试（`--order rand`）被大幅重写 (#1908)
  * 相同 seed 下，现在所有平台都会生成相同顺序
  * 相同 seed 下，如果只选择测试子集运行，测试的相对顺序不会改变
* Vector matchers 支持自定义分配器 (#1909)
* `CHECK` 和 `REQUIRE` 现在支持 `|` 和 `&`（bitwise or/and）
  * 结果类型必须可转换为 `bool`
### 修复
* 修复了 ConsoleReporter 中 benchmark 列宽计算 (#1885, #1886)
* 抑制了断言里的 clang-tidy `cppcoreguidelines-pro-type-vararg` 警告 (#1901)
  * 这是由新的 warning 支持 workaround 触发的误报
* 修复了测试规格解析器在处理带转义的 OR 模式时的 bug (#1905)
### 其他
* 为 IBM XL 的 codegen bug 提供 workaround (#1907)
  * 它会在未求值上下文中为临时对象的 _析构函数_ 生成代码
* 改进了 stdlib 对 `std::uncaught_exceptions` 的支持检测 (#1911)

## 2.11.3
### 修复
* 修复了 MSVC 下断言中 lambda 导致的编译错误

## 2.11.2
### 改进
* GCC 和 Clang 现在会对断言中的可疑代码发出警告 (#1880)
  * 例如 `REQUIRE( int != unsigned int )` 现在会发出 signedness 混用比较警告
  * 这以前在 MSVC 上就能工作，现在 GCC 和当前 Clang 版本也支持了
* “Test filters” 输出的着色现在更稳健了
* `--wait-for-keypress` 现在也接受 `never` 作为选项 (#1866)
* reporter 在报告 benchmark 结果时不再把纳秒四舍五入 (#1876)
* Catch2 的 debug break 现在在使用 Thumb 指令集时也支持 iOS (#1862)
* 现在可以在运行测试二进制时自定义 benchmark 的 warm-up 时间 (#1844)
  * `--benchmark-warmup-time {ms}`
* 用户现在可以指定 Catch2 应该如何进入调试器 (#1846)
### 修复
* 修复了 benchmark 缺失 `<random>` include (#1831)
* 修复了 benchmark 缺失 `<iterator>` include (#1874)
* 隐藏测试用例现在也会按照文档标记为 `[!hide]` (#1847)
* 对 libc 是否提供 `std::nextafter` 的检测得到改进 (#1854)
* `wmain` 的检测不再错误地查找 `WIN32` 宏 (#1849)
  * 现在它只检测 Windows 平台
* 对已经组合过的 matcher 再做组合，不再修改半组合的 matcher 表达式
  * 这个 bug 已经存在大约 2 年了，但没人报告

## 2.11.1
### 改进
* 在 iOS 上支持进入调试器 (#1817)
* 抑制了 `google-build-using-namespace` clang-tidy 警告 (#1799)
### 修复
* Windows 上的 Clang 不再被假定为实现了 MSVC 的传统预处理器 (#1806)
* `ObjectStorage` 在 `const` 上下文中现在行为正确 (#1820)
* `GENERATE_COPY(a, b)` 现在能正确编译 (#1809, #1815)
* benchmark 支持中的一些进一步清理

## 2.11.0
### 改进
* JUnit reporter 输出在失败时现在包含更多细节 (#1347, #1719)
* 新增 SonarQube Test Data reporter (#1738)
  * 它和 TAP、Automake、TeamCity reporter 一样，放在单独头文件里
* `range` generator 现在允许浮点数 (#1776)
* 重写了部分内部实现以提高吞吐量
### 修复
* 单头文件版本现在应该包含完整 benchmark 支持 (#1800)
* `[.foo]` 在命令行中现在能正确解析为 `[.][foo]` (#1798)
* 修复了在 `steady_clock::period` 不是 `std::nano` 的平台上 benchmark 的编译 (#1794)

## 2.10.2
### 改进
* Catch2 现在可以在 `INFINITY` 是 double 的平台上编译 (#1782)
### 修复
* 在 listener 注册期间被抑制的 warning 不再泄漏

## 2.10.1
### 改进
* Catch2 现在会防范来自 `windows.h` 的 `min` 和 `max` 宏 (#1772)
* 模板化测试现在可以在 ICC 下编译 (#1748)
* `WithinULP` matcher 现在使用科学计数法做字符串化 (#1760)
### 修复
* 模板化测试不再触发 `-Wunused-templates` (#1762)
* 抑制了 context getter 中的 clang-analyzer 误报 (#1230, #1735)
### 其他
* 当 Catch2 作为子项目使用时，CMake 不再禁止 in-tree build (#1773, #1774)

## 2.10.0
### 修复
* `TEMPLATE_LIST_TEST_CASE` 现在能正确处理不可拷贝、不可移动类型 (#1729)
* 修复了 Solaris 上由于系统头文件定义 `TT` 宏导致的编译错误 (#1722, #1723)
* `REGISTER_ENUM` 在注册的 enum 太大时现在会编译失败
* 在 C++17 模式下不再使用 `std::is_same_v` (#1757)
* 从文件读取测试 spec 时，修复了对转义特殊字符的解析 (#1767, #1769)
### 改进
* 测试/section spec 中前后空白现在会被忽略
* 写入 Android debug log 现在使用 `__android_log_write`，而不是 `__android_log_print`
* Android 日志支持现在可以在编译期打开/关闭 (#1743)
  * 开关是 `CATCH_CONFIG_ANDROID_LOGWRITE`
* 新增一个返回 range 元素的 generator
  * 通过 `from_range(from, to)` 或 `from_range(container)` 使用
* 新增对不提供 `std::nextafter` 的 CRT 的支持 (#1739)
  * 它们仍然需要提供全局 `nextafter{f,l,}`
  * 通过 `CATCH_CONFIG_GLOBAL_NEXTAFTER` 启用
* 对 `Approx(inf)` 做了特判，使其不会匹配非无限值
  * 严格来说这也许算破坏性变化，但它更符合用户预期
* 当设置了 `--benchmark-no-analysis` 时，通过 Console reporter 输出的 benchmark 内容现在简单得多了 (#1768)
* 新增一个用于检查异常消息的 matcher (#1649, #1728)
  * helper 函数叫 `Message`
  * 异常必须公开继承自 `std::exception`
  * 匹配是精确匹配，包括大小写和空白字符
* 新增一个用于检查浮点数相对相等性的 matcher (#1746)
  * 不像 `Approx`，它在确定允许的 margin 时会同时考虑两边
  * 对 `NaN` 和 `INFINITY` 做了特判，以符合用户预期
  * helper 函数叫 `WithinRel`
* ULP matcher 现在允许两数之间任何可能的距离
* 随机数生成器现在使用 Catch 全局 RNG 实例 (#1734, #1736)
  * 这意味着嵌套的随机数生成器实际上会生成不同数字
### 其他
* 仓库里的 PNG 已优化，以降低通过 git clone 使用 Catch2 的开销
* Catch2 现在使用自己实现的 URBG 概念
  * 未来我们还计划自己实现 `<random>` 里的 distributions，以提供跨平台可重复的随机结果

## 2.9.2

### 修复
* `ChunkGenerator` 现在可以在 chunk 大小为 0 时使用 (#1671)
* 通过 `-c` 参数运行特定 section 时，嵌套 subsection 现在会正确执行 (#1670, #1673)
* Catch2 现在统一使用 `_WIN32` 检测 Windows 平台 (#1676)
* `TEMPLATE_LIST_TEST_CASE` 现在支持非默认可构造的 type list (#1697)
* 修复了 benchmark 在 warmup 期间抛异常时 XMLReporter 的崩溃 (#1706)
* 修复了 CompactReporter 中可能出现的无限循环 (#1715)
* 修复了 `-w NoTests` 在没有匹配到测试时仍然返回 0 的问题 (#1449, #1683, #1684)
* 修复了 ObjC++ 下 matcher 的编译 (#1661)

### 改进
* `RepeatGenerator` 和 `FixedValuesGenerator` 现在在与 `bool` 一起使用时会编译失败 (#1692)
  * 以前它们会在运行时失败。
* Catch2 现在支持 Android debug logging 用于调试输出 (#1710)
* Catch2 现在能识别并为 RTX 平台配置自身 (#1693)
  * 如果你在 RTX 下使用 benchmark，仍然需要传 `--benchmark-no-analysis`
* 移除了用 PGI 编译器编译 Catch2 时出现的 `"storage class is not first"` 警告 (#1717)

### 其他
* 文档现在会标明某个功能是何时引入的 (#1695)
  * 这一标记从 Catch2 v2.3.0 开始提供。
  * `docs/contributing.md` 已更新，向贡献者说明如何为新写的文档补充这些信息
* 其他多项文档改进
  * 修正目录
  * 记录了 `--order` 和 `--rng-seed` 命令行选项
  * benchmark 文档现在明确说明它需要显式启用
  * 记录了 `CATCH_CONFIG_CPP17_OPTIONAL` 和 `CATCH_CONFIG_CPP17_BYTE` 宏
  * 更完整地记录了内置 vector matcher
  * 对 `*_THROWS_MATCHES` 文档做了少量改进
* CMake 配置文件现在不再受 `CMAKE_SIZEOF_VOID_P` 是否在 cache 中影响而改变架构感知 (#1660)
* `CatchAddTests` 现在能正确转义测试名里的 `[` 和 `]` (#1634, #1698)
* 撤回了 `CatchAddTests` 把标签作为 CTest labels 的做法 (#1658)
  * 当测试名太长时，脚本会出问题
  * 覆盖 `LABELS` 会给手动设置它们的用户带来麻烦
  * 如果测试名里有空格，CMake 不允许用户向 `LABELS` 追加内容


## 2.9.1

### 修复
* 修复了在没有 `CATCH_CONFIG_EXTERNAL_INTERFACES`（或实现）时 benchmark 的编译失败


## 2.9.0

### 改进
* 实验性的 benchmark 支持已替换为集成 Nonius 代码 (#1616)
  * 这提供了更完善的微基准测试支持。
  * 由于编译开销，这项功能默认关闭。详细信息见文档。
  * 就向后兼容性而言，这项功能仍被视为实验性，因为我们可能会根据用户反馈调整接口。
* `WithinULP` matcher 现在会显示可接受范围 (#1581)
* 模板化测试用例现在支持 type list (#1627)


## 2.8.0

### 改进
* 模板化测试用例现在不再检查所提供类型是否唯一 (#1628)
  * 这让你可以例如同时测试 `uint32_t`、`uint64_t` 和 `size_t`，而不会编译失败
* 浮点数字符串化的精度现在可以由用户修改 (#1612, #1614)
* 现在提供 `REGISTER_ENUM` 便捷宏，用于为 enum 生成 `StringMaker` 特化
  * 详情见“String conversion”文档
* 新增一组用于模板测试用例的宏，支持使用 NTTP (#1531, #1609)
  * 详情见“Test cases and sections”文档

### 修复
* `UNSCOPED_INFO` 宏现在有了前缀/禁用/前缀+禁用版本 (#1611)
* 启动时报告错误在某些情况下不再导致崩溃 (#1626)

### 其他
* CMake 现在会阻止你尝试在源码目录内构建 (#1636, #1638)
  * 以前它会在构建阶段以一条晦涩的错误信息失败


## 2.7.2

### 改进
* 新增近似 vector matcher (#1499)

### 修复
* 如果没有 filter，就不再显示 filters
* 修复了在 macOS 上使用 Homebrew GCC 时的编译错误 (#1588, #1589)
* 修复了 console reporter 不显示以换行开头消息的问题 (#1455, #1470)
* 修改了 JUnit reporter 的输出，使 rng seed 和 filters 按照 JUnit schema 报告 (#1598)
* 修复了一些冷门 warning 和静态分析问题

### 其他
* `ParseAndAddCatchTests` 的多项改进 (#1559, #1601)
  * 在解析 target 时，它现在会生成 `ParseAndAddCatchTests_TESTS` 属性，用于汇总找到的测试
  * 修复了使用 `OptionalCatchTestLauncher` 变量时找不到测试的问题
  * 包含该脚本后不再会强制修改 `CMAKE_MINIMUM_REQUIRED_VERSION`
  * 解析时会忽略 CMake object library，以避免不必要的警告
* `CatchAddTests` 现在会把测试标签加入对应的 CTest labels (#1600)
* 为我们的构建新增了基础 CPack 支持


## 2.7.1

### 改进
* reporter 现在会打印应用到测试用例上的 filters (#1550, #1585)
* 新增 `GENERATE_COPY` 和 `GENERATE_REF` 宏，可在 generator 表达式中使用变量
  * 由于生命周期问题风险很大，默认的 `GENERATE` 宏仍然不允许使用变量
* `map` generator helper 现在会推导映射后的返回类型 (#1576)

### 修复
* 修复了 ObjC++ 编译 (#1571)
* 修复了 test tag 解析，使 `[.foo]` 现在会被解析为 `[.][foo]`
* 抑制了 Windows 头文件以不同方式定义 SE codes 所导致的 warning (#1575)


## 2.7.0

### 改进
* `TEMPLATE_PRODUCT_TEST_CASE` 现在会在名字里使用结果类型，而不是序号 (#1544)
* Catch2 的单头文件现在严格只包含 ASCII (#1542)
* 新增随机整型/浮点类型 generator
  * 这些类型会在 `random` helper 中自动推导
* 重新加入 RangeGenerator (#1526)
  * RangeGenerator 会返回某个范围内的元素
* 新增 ChunkGenerator 的通用 transform (#1538)
  * ChunkGenerator 会以 n 个元素为一组，从不同 generator 中取出元素
* 新增 `UNSCOPED_INFO` (#415, #983, #1522)
  * 它是 `INFO` 的一种变体，会一直存在到下一条断言或测试用例结束。

### 修复
* 所有对 C stdlib 函数的调用现在都显式加了 `std::` 前缀 (#1541)
  * 从 Clara 引入的代码也一并更新了。
* 运行测试时不再会把指定的输出文件打开两次 (#1545)
  * 这会在目标不是普通文件而是命名管道时引发问题
  * 修复了 CLion/Resharper 与 Catch 的集成
* 修复了老版本 ccache+cmake+clang 组合下的 `-Wunreachable-code` (#1540)
* 修复了 Clang 8 下的 `-Wdefaulted-function-deleted` warning (#1537)
* Catch2 的 type traits 和 helper 现在都正确地位于 `Catch::` 命名空间内 (#1548)
* 修复了失败测试时的 std{out,err} 重定向 (#1514, #1525)
  * 这个 bug 在被报告之前已经存在了一年多

### Contrib
* `ParseAndAddCatchTests` 现在能正确转义测试名中的逗号


## 2.6.1

### 改进
* JUnit reporter 现在也会报告 random seed (#1520, #1521)

### 修复
* TAP reporter 现在会正确格式化带测试名的注释 (#1529)
* `CATCH_REQUIRE_THROWS` 的内部实现已与 `REQUIRE_THROWS` 统一 (#1536)
  * 这修复了使用时可能出现的 `-Wunused-value` 警告
* 修复了使用任何 `--list-*` 选项时可能发生的段错误 (#1533, #1534)


## 2.6.0

**从这个版本开始，data generator 功能被正式支持。**

### 改进
* 新增 `TEMPLATE_PRODUCT_TEST_CASE` (#1454, #1468)
  * 这样你就可以更轻松地测试各种类型组合，详情见文档
* 断言内 `&&` 和 `||` 的错误信息得到了改进 (#1273, #1480)
* 断言内链式比较的错误信息得到了改进 (#1481)
* 为 `std::optional` 新增 `StringMaker` 特化 (#1510)
* generator 接口再次重做 (#1516)
  * 这不再被视为实验性功能，而是完整支持
  * 新接口支持 “Input” generators
  * generator 文档已完整更新
  * 我们还新增了 2 个 generator 示例

### 修复
* 修复了新版本 Clang 上的 `-Wredundant-move` (#1474)
* 在 no-exceptions 模式下，移除了对 `std::current_exception`、`std::rethrow_exception` 的不可达引用 (#1462)
  * 这应该能修复 IAR 的编译问题
* 修复了缺失 `<type_traits>` include 的问题 (#1494)
* 修复了多项静态分析 warning
  * `XmlWriter` 中未恢复的流状态 (#1489)
  * `estimateClockResolution` 中潜在的除零 (#1490)
  * `RunContext` 中未初始化成员 (#1491)
  * `SourceLineInfo` 的移动操作现在标记为 `noexcept`
  * `CATCH_BREAK_INTO_DEBUGGER` 现在始终是函数
* 修复了当用户请求特定 section 时测试用例被执行两次的问题 (#1394, #1492)
* 现在 ANSI 颜色码输出会尊重 `-o` 参数，并同样写入文件 (#1502)
* 修复了除 Clang 之外编译器对 `std::variant` 支持的检测 (#1511)

### Contrib
* `ParseAndAddCatchTests` 学会了使用 `DISABLED` CTest 属性 (#1452)
* `ParseAndAddCatchTests` 现在在测试名前有空白时也能正常工作 (#1493)

### 其他
* 我们为 GitHub 新增了 issue 模板
* `contributing.md` 已更新，以反映当前测试状态 (#1484)


## 2.5.0

### 改进
* 新增通过 `TEMPLATE_TEST_CASE` 支持模板化测试 (#1437)

### 修复
* 通过移除 `MatcherMethod<T*>` 的偏特化，修复了 `PredicateMatcher<const char*>` 的编译
* listener 现在会隐式支持任意 verbosity (#1426)
* 通过引入 `Catch::isnan` polyfill，修复了 Embarcadero builder 下的编译 (#1438)
* 修复了 `CAPTURE` 对非平凡 capture 的断言问题 (#1436, #1448)

### 其他
* 现在应该可以通过 https://bintray.com/catchorg/Catch2 提供第一方 Conan 支持 (#1443)
* 文档新增 “deprecations and planned changes” 章节
  * 其中总结了哪些内容已被弃用，以及在下一个大版本中可能发生变化的内容
* 从这个版本开始，发布的 headers 应当使用 pgp 签名 (#430)
  * KeyID `E29C 46F3 B8A7 5028 6079 3B7D ECC9 C20E 314B 2360`
  * 或 https://codingnest.com/files/horenmar-publickey.asc


## 2.4.2

### 改进
* XmlReporter 现在也会输出运行中使用的 RNG seed (#1404)
* `Catch::Session::applyCommandLine` 现在也接受 `wchar_t` 参数
  * 不过 Catch2 仍然不支持 Unicode。
* 新增 `STATIC_REQUIRE` 宏 (#1356, #1362)
* 即使测试运行过，Catch2 的 singleton 现在也会被清理 (#1411)
  * 这主要用于防止用户自定义 main 时出现误报。
* 通过 `-r` 指定无效 reporter 现在会更早被报告 (#1351, #1422)

### 修复
* 字符串化现在不再假设 `char` 是 signed (#1399, #1407)
  * 这曾导致 `Wtautological-compare` warning。
* `operator<<` 的 SFINAE 不再看到与真正插入操作不同的 overload set (#1403)

### Contrib
* `catch_discover_tests` 现在能正确添加名称中包含逗号的测试 (#1327, #1409)
* 为 `catch_discover_tests` 新增了一个控制测试启动方式的自定义点


## 2.4.1

### 改进
* 为 `std::(w)string_view` 新增 `StringMaker` (#1375, #1376)
* 为 `std::variant` 新增 `StringMaker` (#1380)
  * 这个特性默认禁用，以避免增加编译时开销
* 新增对没有 `std::to_string` 的 cygwin 环境的检测 (#1396, #1397)

### 修复
* `UnorderedEqualsMatcher` 不再错误地接受共享后缀、但并不是目标 vector 的排列的 vector
* `Abort after`（`-x N`）现在不会再被嵌套 `REQUIRES` 超过上限后忽略 (#1391, #1392)


## 2.4.0

**这个版本带来了两个新的实验性功能，generator 支持和 `-fno-exceptions` 支持。
实验性意味着它们不受 semver 常规稳定性保证约束。**

### 改进
* 多项小的运行时性能改进
* `CAPTURE` 宏现在是可变参数的
* 新增 `AND_GIVEN` 宏 (#1360)
* 新增对 data generators 的实验性支持
  * 详情见[相关文档](generators_zh.md#top)
* 新增无异常编译和运行 Catch 的支持
  * 这样做会在一定程度上限制功能
  * 详情见[配置文档](configuration_zh.md#disablingexceptions)

### 修复
* 抑制 Matchers 中的 `-Wnon-virtual-dtor` warning (#1357)
* 抑制 floating point matchers 中的 `-Wunreachable-code` warning (#1350)

### CMake
* 现在可以覆盖用于运行 Catch 测试的 Python 版本 (#1365)
* Catch 现在提供基础设施，用于添加检查编译期配置的测试
* 当 Catch 作为子项目使用时，不再尝试自行安装 (#1373)
* `Catch2ConfigVersion.cmake` 现在生成时与架构无关 (#1368)
  * 这意味着可以把 32 位机器上的安装复制到 64 位机器上使用
  * 这修复了 Catch 的 conan 安装问题


## 2.3.0

**这个版本修改了 CMake 和 pkg-config 集成提供的 include path。**
**在上述场景下，单头文件的正确路径现在是 `<catch2/catch.hpp>`。**
**这一变化也导致仓库内部路径调整，因此单头文件版本现在位于 `single_include/catch2/catch.hpp`，而不是 `single_include/catch.hpp`。**

### 修复
* 修复了 Objective-C++ 构建
* `-Wunused-variable` 的抑制不再从 Clang 下 Catch 的 header 泄漏出去
* 现在可以禁用实验性的新输出捕获实现 (#1335)
  * 这使得 Catch2 能在不提供 `dup` 或 `tmpfile` 等能力的平台上构建。
* JUnit 和 XML reporter 在不使用 `-s` 时不再跳过成功测试 (#1264, #1267, #1310)
  * 详情见“改进”部分

### 改进
* pkg-config 和 CMake 集成已重写
  * 如果你使用它们，新的 include path 是 `#include <catch2/catch.hpp>`
  * CMake 安装现在也会安装 `contrib/` 下的脚本
  * 详情见[新文档](cmake-integration_zh.md#top)
* reporter 现在有一个新的自定义点 `ReporterPreferences::shouldReportAllAssertions`
  * 当它设为 `false` 且测试未使用 `-s` 运行时，成功断言不会发送给 reporter。
  * 默认值为 `false`。
* 新增 `DYNAMIC_SECTION`，一种通过流构造名称的 section 变体
  * 这意味着你可以写 `DYNAMIC_SECTION("For X := " << x)`。


## 2.2.3

**为修复一些 bug，部分行为做了潜在破坏性改变。**
**这意味着即使这是一个补丁版本，它也不一定能直接替代旧版本。**

### 修复
* listener 现在会先于 reporter 被调用
  * 这一直是文档所描述的行为，现在它终于真的这样工作了
* Catch 的 command line 不再接受多个 reporter
  * 这是因为多个 reporter 以前从未正确工作过，还以不明显的方式破坏了东西
  * **这可能是破坏性变化**
* MinGW 现在被检测为不支持 SEH 的 Windows 平台 (#1257)
  * 这意味着 Catch2 在 MinGW 下编译时不再尝试使用 POSIX signal handling
* 修复了使用非 ASCII 字符解析 tag 时可能出现的 UB (#1266)
  * 需要注意的是，Catch2 仍然只支持 ASCII 的测试名/tag 等
* `TEST_CASE_METHOD` 现在可以用于包含逗号的类名 (#1245)
  * 你需要把类名额外包一层括号
* 修复了 POSIX signal handling 的 alt stack 大小不足问题 (#1225)
* 修复了 Android 下由于 C++11 模式缺少 `std::to_string` 导致的编译错误 (#1280)
* 修复了字符串化 machinery 中 `FALLBACK_STRINGIFIER` 的顺序 (#1024)
  * 它原本 intended 用于替代内建 fallback，但实际却在它们 _之后_ 执行。
  * **这可能是破坏性变化**
* 修复了某种类型在 `operator<<` 左侧是模板时导致的编译错误 (#1285, #1306)

### 改进
* 新增一个实验性的输出捕获 (#1243)
  * 这个捕获也可以重定向通过 C API 写出的输出，例如 `printf`
  * 若要启用，请在实现文件中定义 `CATCH_CONFIG_EXPERIMENTAL_REDIRECT`
* 为继承自 `std::exception` 的类新增 fallback stringifier
  * `StringMaker` 特化和 `operator<<` overload 都会优先考虑

### 其他
* `contrib/` 现在包含跳过 Catch 内部实现的 dbg 脚本 (#904, #1283)
  * `gdbinit` 用于 gdb，`lldbinit` 用于 lldb
* `CatchAddTests.cmake` 现在不会再从测试中剥离空白 (#1265, #1281)
* 在线文档现在描述了 `--use-colour` 选项 (#1263)


## 2.2.2

### 修复
* 修复了 `WithinAbs::match()` 误失败的问题 (#1228)
* 修复了 clang-tidy 关于析构函数中 virtual call 的诊断 (#1226)
* 减少了从 header 泄漏出去的 GCC warning 抑制数量 (#1090, #1091)
  * 现在只应有 `-Wparentheses` 还会泄漏。
* 为 benchmark timer calibration 允许的耗时增加了上限 (#1237)
  * 在 `std::chrono::high_resolution_clock` 分辨率较低的平台上，校准过程看起来会卡住
* 修复了字符串化 `unsigned char` 静态数组时的编译错误 (#1238)

### 改进
* XML encoder 现在会把无效 UTF-8 序列转成十六进制 (#1207)
  * 这会影响 xml 和 junit reporter
  * 某些无效 UTF-8 片段仍会保留原样，例如 surrogate pair。这是因为某些 UTF-8 扩展允许它们，比如 WTF-8。
* CLR 对象（`T^`）现在可以被字符串化 (#1216)
  * 这会影响按 C++/CLI 编译的代码
* 新增 `PredicateMatcher`，一种接受任意 predicate 函数的 matcher (#1236)
  * 详情见[文档](matchers_zh.md#top)

### 其他
* CMake 安装的 pkg-config 现在允许 `#include <catch.hpp>` (#1239)
  * 标准化为 `#include <catch2/catch.hpp>` 的计划仍然有效


## 2.2.1

### 修复
* 修复了使用 `std=c++17` 编译 Catch2 并链接 libc++ 时的编译错误 (#1214)
  * Clara（Catch2 的 CLI 解析库）使用了 `std::optional` 但没有显式包含它
* 修复了 Catch2 返回码始终为 0 的问题 (#1215)
  * 用 STL 的话说，"We feel superbad about letting this in"


## 2.2.0

### 修复
* 列出测试时，默认不再列出隐藏测试 (#1175)
  * 这让 `catch_discover_tests` 的 CMake 脚本工作得更好
* 修复了 `<windows.h>` 可能无法被正确包含的回归问题 (#1197)
* 修复了 Catch2 作为子项目时安装 `Catch2ConfigVersion.cmake` 的问题

### 改进
* 新增一个在没有运行任何测试时发出 warning（并退出报错）的选项 (#1158)
  * 用法是 `-w NoTests`
* 新增对 Emscripten 的初步支持 (#1114)
* [新增覆盖 fallback stringifier 的方式](configuration_zh.md#fallback-stringifier) (#1024)
  * 这样项目自有的字符串化 machinery 就可以轻松复用于 Catch
* `Catch::Session::run()` 现在接受 `char const * const *`，因此可以接收字符串字面量数组 (#1031, #1178)
  * 内嵌的 Clara 版本已升级到 v1.1.3
* 多项小的性能改进
* 新增对 DJGPP DOS crosscompiler 的支持 (#1206)


## 2.1.2

### 修复
* 修复了 `-fno-rtti` 下的编译错误 (#1165)
* 修复了 `NoAssertion` warnings
* `operator<<` 现在会在基于 range 的字符串化之前使用 (#1172)
* 修复了 `-Wpedantic` warnings（多余分号和二进制字面量） (#1173)

### 改进
* 新增 `CATCH_VERSION_{MAJOR,MINOR,PATCH}` 宏 (#1131)
* 新增用于 reporter 的 `BrightYellow` 颜色 (#979)
  * 它也被 ConsoleReporter 用于重建后的表达式

### 其他变化
* Catch 现在作为一个 CMake package 和可链接 target 导出 (#1170)

## 2.1.1

### 改进
* 静态数组现在会在 MSVC/GCC/Clang 上像 range 一样被正确字符串化
* 内嵌了较新的 Clara 版本 -- v1.1.1
  * 这应该能修复一些来自 Clara 的 warning
* 支持 MSVC 的 CLR exceptions

### 修复
* 修复了比较运算符不返回 bool 时的编译错误 (#1147)
* 修复了 CLR exceptions 在 translation 阶段把可执行文件炸掉的问题 (#1138)

### 其他变化
* 多项 CMake 变更
  * `NO_SELFTEST` 选项已弃用，请改用 `BUILD_TESTING`
  * Catch 相关 CMake 选项已加上 `CATCH_` 前缀以便命名空间隔离
  * 还有一些简化 Catch2 打包的其他变化


## 2.1.0

### 改进
* 多项性能改进
  * 这是在修复性能回归基础上的进一步提升
* 新增对 PCH 的实验性支持 (#1061)
* `CATCH_CONFIG_EXTERNAL_INTERFACES` 现在会带入 Console、Compact、XML 和 JUnit reporter 的声明
* `MatcherBase` 不再有一个多余的第二模板参数
* 减少了泄漏到用户代码中的 warning 抑制数量
  * g++ 4.x 和 5.x 的 bug 意味着其中一些仍然必须保留

### 修复
* 修复了 Catch classic 的性能回归
  * Catch classic 的一项性能优化 patch 没有被应用到 Catch2
* 修复了 iOS 平台检测 (#1084)
* 修复了同时使用 `g++` 和 `libc++` 时的编译问题 (#1110)
* 修复了单头文件版本下 TeamCity reporter 的编译
  * 为了解决根本问题，我们会在 single_include 文件夹里按版本给 reporter 编号
* XML reporter 现在即使不使用 `-s` 也会报告 `WARN` 消息
* 修复了 `VectorContains` matcher 用 `&&` 组合时的编译问题 (#1092)
* 修复了测试耗时超过 10 秒后溢出的问题 (#1125, #1129)
* 修复了 `std::uncaught_exception` 的弃用 warning (#1124)

### 新功能
* 新的 Matchers
  * 字符串的正则 matcher，`Matches`
  * vector 的 set-equal matcher，`UnorderedEquals`
  * 浮点 matcher，`WithinAbs` 和 `WithinULP`
* 字符串化现在会尝试分解所有容器 (#606)
  * 容器是指通过 ADL 响应 `begin(T)` 和 `end(T)` 的对象。

### 其他变化
* 为确保与最后发布版本兼容，reporter 现在会在 `single_include` 文件夹里按版本编号


## 2.0.1

### 破坏性变化
* 移除对 C++98 的支持
* 移除旧版 reporter 支持
* 移除旧版 generator 支持
  * generator 支持会在稍后以重做后的形式回归
* 移除 `Catch::toString` 支持
  * 新的字符串化 machinery 会优先使用 `Catch::StringMaker` 特化，然后才是 `operator<<` overload
* 移除旧版 `SCOPED_MSG` 和 `SCOPED_INFO` 宏
* 移除 `INTERNAL_CATCH_REGISTER_REPORTER`
  * 注册 reporter 应使用 `CATCH_REGISTER_REPORTER`
* 移除旧版 `[hide]` 标签
  * `[.]`、`[.foo]` 和 `[!hide]` 仍受支持
* 输出到调试器现在会有颜色
* `*_THROWS_AS(expr, exception_type)` 现在会无条件在 exception type 后追加 `const&`
* `CATCH_CONFIG_FAST_COMPILE` 现在也会影响 `CHECK_` 和 `REQUIRE_` 两组断言
  * 这在 `CHECK(throws())` 上最明显：以前它会报告失败、正确字符串化异常并继续；现在它会报告失败并停止执行当前 section。
* 移除已弃用的 matcher 工具函数 `Not`、`AllOf` 和 `AnyOf`
  * 它们已被 `!`、`&&`、`||` 运算符取代，这些运算符更自然，而且没有参数个数限制
* 移除对非 const 比较运算符的支持
  * 非 const 比较运算符是种不该存在的怪物
  * 它们曾破坏函数与函数指针之间的比较支持
* `std::pair` 和 `std::tuple` 不再默认字符串化
  * 这样可以避免在常见路径上拖入 `<tuple>` 和 `<utility>` 头文件
  * 其字符串化可以通过新的配置宏按文件启用
* `Approx` 有了细微差异，并且希望更符合用户预期
  * `Approx::scale` 默认值为 `0.0`
  * `Approx::epsilon` 不再应用于两个被比较值中较大的那个，而只应用于 `Approx` 自身的值
  * `INFINITY == Approx(INFINITY)` 返回 true

### 改进
* reporter 和 listener 可以定义在与 main 文件不同的文件中
  * 该文件必须在包含 `catch.hpp` 之前定义 `CATCH_CONFIG_EXTERNAL_INTERFACES`
* main 之前发生的设定阶段错误现在会被捕获，并在进入 main 后正确报告
  * 如果你自己提供 main，这些错误同样可以被你访问和使用。
* 新增断言宏 `*_THROWS_MATCHES(expr, exception_type, matcher)`
  * 顾名思义，它允许你断言某表达式抛出指定类型的异常，并把异常交给 matcher
* JUnit reporter 不再会对带 section 和不带 section 的测试用例输出显著不同的内容
* 大多数断言现在支持包含逗号的表达式（例如 `REQUIRE(foo() == std::vector<int>{1, 2, 3});`）
* Catch 现在包含实验性的微基准测试支持
  * 示例见 `projects/SelfTest/Benchmark.tests.cpp`
  * 由于该支持是实验性的，它可能在不另行通知的情况下变化
* Catch 使用新的 CLI 解析库（Clara）
  * 用户现在可以很容易地为最终可执行文件添加新的命令行选项
  * 这也带来了一些 `Catch::Session` 接口上的变化
* 通过定义 `CATCH_CONFIG_DISABLE_MATCHERS`，可以把 matcher 的所有部分从某个 TU 中移除
  * 这可以在一定程度上加快编译速度
* 新增 `CATCH_CONFIG_DISABLE` 的实验性实现
  * 受 Doctest 的 `DOCTEST_CONFIG_DISABLE` 启发
  * 可用于在源文件中实现测试
    * 例如匿名命名空间中的函数
  * 会移除所有断言
  * 会阻止 `TEST_CASE` 注册
  * 不注册异常转换器
  * 不注册 reporter
  * 不注册 listener
* reporter/listener 现在会收到 fatal errors 通知
  * 这意味着特定 signal 或 structured exception
  * Reporter/Listener 接口提供默认的空实现，以保持向后兼容
* 现在支持 `std::chrono::duration` 和 `std::chrono::time_point` 的字符串化
  * 需要通过按文件的编译期配置选项启用
* 为 CMake install 命令添加 `pkg-config` 支持

### 修复
* 在 XCode 中运行时不再使用 console 颜色
* 在 reporter base class 中使用显式构造函数
* 清理了 `-Wweak-vtables`、`-Wexit-time-destructors`、`-Wglobal-constructors` warnings
* 支持 Universal Windows Platform (UWP) 编译
  * 为 UWP 编译时会禁用 SEH 处理和着色输出
* 为 libcxxrt 中 `std::uncaught_exception` 的问题实现了 workaround
  * 这些问题会导致 section 遍历不正确
  * 该 workaround 只是部分修复，用户的测试仍可能通过 `throw;` 重新抛出异常而触发问题
* 抑制了 MSVC 下的 C4061 warning

### 内部变更
* 开发版本现在使用 `.cpp` 文件而不是包含实现的 header 文件
  * 这让开发阶段的局部重建快得多
* expression decomposition 层被重写
* evaluation 层被重写
* 新库 TextFlow 被用于文本输出格式化


## 旧版本

### 1.12.x

#### 1.12.2
##### 修复
* 修复了缺失 `<cassert>` include

#### 1.12.1

##### 修复
* 修复了 `ScopedMessage::~ScopedMessage` 中的弃用 warning
* 现在所有 `min` 或 `max` 标识符的使用都会被括号包起来
  * 这样可以避免 Windows 头文件定义 `min` 和 `max` 宏时出问题

#### 1.12.0

##### 修复
* 修复了严格 C++98 模式（即非 gnu++98）和老编译器下的编译 (#1103)
* 即使没有指定 `-s`，`INFO` 消息也会出现在 `xml` reporter 输出中


### 1.11.x

#### 1.11.0

##### 修复
* `REQUIRE_FALSE( expr )` 中的原始表达式现在会被 reporter 正确显示为 `!( expr )` (#1051)
  * 以前括号会缺失，而 `x != y` 会展开成 `!x != x`
* `Approx::Margin` 现在是包含边界的 (#952)
  * 以前文档和意图都说明它是包含边界的，但检查本身不是
  * 这意味着 `REQUIRE( 0.25f == Approx( 0.0f ).margin( 0.25f ) )` 会通过，而不是失败
* `RandomNumberGenerator::result_type` 现在是无符号的 (#1050)

##### 改进
* `__JETBRAINS_IDE__` 宏处理现在改为按 CLion 版本区分 (#1017)
  * 检测到 CLion 2017.3 或更新版本时，会使用 `__COUNTER__` 而不是
* TeamCity reporter 现在会在每次报告后显式 flush 输出流 (#1057)
  * 在某些平台上，重定向流的输出会等到测试结束后才出现
* `ParseAndAddCatchTests` 现在可以把测试文件作为依赖添加到 CMake 配置中
  * 这意味着你不必手动重新运行 CMake 配置步骤来检测新测试

### 1.10.x

#### 1.10.0

##### 修复
* evaluation 层已重写（从 Catch 2 backport）
  * 新层更简单，也修复了一些问题 (#981)
* 修复了 VS 2017 原始字符串字面量字符串化 bug 的 workaround (#995)
* 修复了 `[!shouldfail]` 和 `[!mayfail]` 标签与 section 之间的交互
  * 以前带失败断言的 section 会被标记为 failed，而不是 failed-but-ok

##### 改进
* 新增对 [libidentify](https://github.com/janwilmans/LibIdentify) 的支持
* 新增 “wait-for-keypress” 选项

### 1.9.x

#### 1.9.6

##### 改进
* Catch 的运行时开销显著降低 (#937, #939)
* 新增 `--list-extra-info` cli 选项 (#934)
  * 它会把所有测试连同额外信息一起列出，也就是文件名、行号和描述。

#### 1.9.5

##### 修复
* 真值表达式现在会被正确重建，而不是重建成布尔值 (#914)
* 多项 warning 不再在测试文件中被错误地抑制（即包含 `catch.hpp` 但未定义 `CATCH_CONFIG_MAIN` 或 `CATCH_CONFIG_RUNNER` 的文件）(#871)
* 如果 main 以 C++ 编译但链接到 Objective-C，Catch 不再链接失败 (#855)
* 修复了在决定是否使用 `__COUNTER__` 时对 gcc 版本的错误检测 (#928)
  * 以前任何 minor version 小于 3 的 GCC 都会被错误地归类为不支持 `__COUNTER__`。
* 抑制了即将更新到 MSVC 2017 时因将 `std::uncaught_exception` 标记为弃用而产生的 C4996 warning (#927)

##### 改进
* CMake 集成脚本现在会合并调试信息并以更好的方式注册测试 (#911)
* 多项文档改进

#### 1.9.4

##### 修复
* `CATCH_FAIL` 宏在没有可变参数宏支持时不再导致编译错误
* `INFO` 消息在报告一次后不再被清除

##### 改进和小变更
* Catch 现在在 Windows 且定义了 `UNICODE` 时会使用 `wmain`
  * 注意，Catch 仍然官方只支持 ASCII

#### 1.9.3

##### 修复
* 完成了对早期 Visual Studio 中缺少 `uint64_t` 的修复

#### 1.9.2

##### 改进和小变更
* `Approx` 的所有成员函数现在在 C++11 模式下都接受 strong typedef (#888)
  * 以前 `Approx::scale`、`Approx::epsilon`、`Approx::margin` 和 `Approx::operator()` 不接受。

##### 修复
* QNX 下默认不再启用 POSIX signals (#889)
  * QNX 不支持足够新的（2001 年版）POSIX 规范
* 如果给定测试用例被标记为允许失败，JUnit 不再把异常算作失败。
* `Catch::Option` 的存储现在应该有正确的对齐。
* Catch 不再尝试在 Windows 上定义 `uint64_t` (#862)
  * 这曾在 Cygwin 下引发麻烦

##### 其他
* Catch 现在在 MSVC 2017 下使用 `std:c++latest`（C++17 模式）编译于 CI
* 现在提供了一个 cmake 脚本，可自动把 Catch 测试注册到 ctest。
  * 见 `contrib` 文件夹。

#### 1.9.1

##### 修复
* 默认情况下，意外异常不再被忽略 (#885, #887)

#### 1.9.0

##### 改进和小变更
* Catch 不再尝试确保用户在 `REQUIRE_THROWS_AS` 中传入的 exception type 是常量引用。
  * 这在 `REQUIRE_THROWS_AS` 用于模板函数时会出问题
  * 这实际上回滚了 v1.7.2 中做出的改动
* 当多个 Catch 测试实例被加载到同一个程序中时，Catch 的 `Version` 结构体不再会被二次释放 (#858)
  * 现在它是一个内联函数里的静态变量，而不是一个 `extern` 的结构体。
* 尝试注册无效 tag 或 tag alias 现在会抛出异常，而不是调用 `exit()`
  * 由于这发生在进入 main 之前，程序仍然会中止
  * 后续还会继续改进这一点
* `CATCH_CONFIG_FAST_COMPILE` 现在能把 `REQUIRE*` 断言的编译速度再提升约 15%
  * 代价是禁用了把意外异常转换为文本的功能。
* 当 Catch 使用 C++11 编译时，`Approx` 现在可以由任何能够显式转换为 `double` 的东西构造。
* 捕获的消息现在会在意外异常时打印出来

##### 修复：
* 应该抑制 Catch 内部的 Clang `-Wexit-time-destructors` warning
* 对所有包含 `catch.hpp` 的 TU，GCC 的 `-Wparentheses` 现在都会被抑制。
  * 这实际上回滚了 1.8.0 中做出的改动；当时我们尝试使用基于 `_Pragma` 的抑制方式。理论上它应该只在 Catch 的断言内部生效，但 GCC 在 C++ 模式下对 `_Pragma` 的处理有 bug，导致它并不总是有效。
* 现在可以让 Catch 在检查某个类型是否可以被流输出时，使用基于 C++11 的检查。
  * 这修复了某些情况下不可输出类型拥有可输出的 private base 的问题 (#877)
  * [详情见文档](configuration_zh.md#catch_config_cpp11_stream_insertable_check)

##### 其他说明：
* 我们已经把 VS 2017 加入 CI
* Catch 2 的工作应该很快就会开始


### 1.8.x

#### 1.8.2

##### 改进和小变更
* TAP reporter 现在表现得像始终指定了 `-s`
  * 这应该更符合协议期望的行为。
* Compact reporter 现在会遵守 `-d yes` 参数 (#780)
  * 格式是 `"XXX.123 s: <section-name>"`（始终保留 3 位小数）。
  * 以前它根本不报告耗时。
* XML reporter 现在在 `INFO` 处理上与 Console reporter 行为一致
  * 这意味着如果启用了成功时输出（`-s`），它会在成功时也报告 `INFO` 消息。
  * 以前它只在失败时报告 `INFO` 消息。
* `CAPTURE(expr)` 现在会像断言宏一样对 `expr` 进行字符串化 (#639)
* listener 现在终于被[文档化了](event-listeners_zh.md#top)。
  * listener 提供了一种钩入测试运行事件的方式，包括运行开始和结束、每个测试用例、每个 section 以及每个断言。

##### 修复：
* Catch 不再尝试重建导致 fatal error 的表达式 (#810)
  * 这修复了在处理表达式时可能出现的 signal/SEH 循环，其中 signal 是由 expression decomposition 触发的。
* 修复了 Matchers 中缺少虚析构函数警告 (C4265) (#844)
* `std::string` 现在所有地方都按 `const&` 传递 (#842)
  * 以前有些地方是按值传递的。
* Catch 现在不应再改变 errno (#835)
  * 这是由我们现在采用 workaround 的 libstdc++ bug 导致的。
* Catch 现在提供 `FAIL_CHECK( ... )` 宏 (#765)
  * 和 `FAIL( ... )` 一样，但不会中止测试。
* 像 `fabs`、`tolower`、`memset`、`isalnum` 这样的函数现在都显式加了 `std::` 限定。
* Clara 不再假定第一个参数（二进制名称）一定存在 (#729)
  * 如果缺失，则使用空字符串作为默认值。
* Clara 不再会越过参数字符串多读 1 个字符 (#830)
* 修复了 Objective-C bindings（Matchers）中的回归问题 (#854)

##### 其他说明：
* 我们已经把 VS 2013 和 2015 加入 CI
* Catch Classic (1.x.x) 现在包含了它自己 fork 出来的 Clara 版本（参数解析器）。


#### 1.8.1

##### 修复

在 Cygwin 下关于 `gettimeofday` 的问题 - `#define` 设置得不够早

#### 1.8.0

##### 新功能 / 小变更

* Matchers 有了新的、更简单的（并且已文档化的）接口。
  * Catch 提供字符串和 vector matcher。
  * 详情见 [Matchers 文档](matchers_zh.md#top)。
* console reporter 的测试耗时显示格式变了 (#322)
  * 旧格式：`Some simple comparisons between doubles completed in 0.000123s`
  * 新格式：`xxx.123s: Some simple comparisons between doubles` _（始终恰好 3 位小数）_
* 新增 MSVC + Windows 下的可选泄漏检测 (#439)
  * 通过用 `CATCH_CONFIG_WINDOWS_CRTDBG` 编译 Catch 的 main 来启用
* 引入新的编译期标志 `CATCH_CONFIG_FAST_COMPILE`，用功能换编译速度。
  * 将 debug break 移出测试并放到实现中，使测试编译时间更快（Linux 上约 10%）。
  * _还会有更多变化_
* 新增 [TAP (Test Anything Protocol)](https://testanything.org/) 和 [Automake](https://www.gnu.org/software/automake/manual/html_node/Log-files-generation-and-test-results-recording.html#Log-files-generation-and-test-results-recording) reporter。
  * 这些不在默认单头文件中，需要单独从 GitHub 下载。
  * 详情见 [与构建系统集成的文档](build-systems.md#top)。
* XML reporter 现在会把文件名作为 `Section` 和 `TestCase` tag 的一部分。
* `Approx` 现在支持可选的绝对误差 margin
  * 它也获得了[新文档](docs/docs/assertions_zh.md#top)。

##### 修复
* 消除了评估层中的 C4312（"conversion from int to 'ClassName *"）警告。
* 修复了 VS2013 下的 C4512（"assignment operator could not be generated"）警告。
* 修复了 Cygwin 兼容性问题
  * signal handling 不再默认编译。
  * Catch 内部使用 `gettimeofday` 不应再导致编译错误。
* 改进了 gcc 下 `-Wparentheses` 的抑制 (#674)
  * 用 gcc 4.8 或更新版本编译时，抑制仅限于断言
  * 否则则会对整个 TU 生效
* 修复了 test spec parser 问题（多个 name 中的转义）

##### 其他
* 多项文档修复和改进


### 1.7.x

#### 1.7.2

##### 修复和小改进
Xml：

（严格来说，前两项既是破坏性变化也是修复，而且应该很少有人真正受影响）
* 用 C-escape 编码控制字符，而不是 XML 编码（后者要求 XML 1.1）
* XML 输出回退到 XML 1.0
* 可以通过扩展 XML reporter 提供 stylesheet 引用
* 为 XML Reporter 新增 description 和 tags 属性
* 更早关闭 tags 并更积极地 flush stream，以避免 stdout 插入

其他：
* `REQUIRE_THROWS_AS` 现在会用 `const&` 捕获异常，并报告预期类型
* 在 `SECTION` 中，文件/行号现在属于 `SECTION` 而不是 `TEST_CASE`
* 为 C stdlib 的一些函数添加了 `std::` 限定
* 移除了重新出现的 RTTI (`dynamic_cast`) 使用
* 在其他一些情况下抑制了更多 warning
* Travis 改进

#### 1.7.1

##### 修复：
* 修复了在 `catch.hpp` 中定义 `NOMINMAX` 和 `WIN32_LEAN_AND_MEAN` 的不一致问题。
* 通过让非 MSVC 编译器的 Windows SEH 处理变为可选，修复了旧版 MinGW 编译器下与 SEH 相关的编译错误。
  * 具体细节见[文档](configuration_zh.md#top)。
* 修复了 MinGW 中由不正确编译器检测导致的编译错误。
* 修复了当测试在 signal/structured exception 结束时，XML reporter 有时会留下空输出文件的问题。
* 修复了 XML reporter 不报告捕获的 stdout/stderr 的问题。
* 修复了 Windows SEH 中可能出现的无限递归。
* 修复了因 Catch 的 operator overload 与用户定义模板化 operator 产生歧义而导致的潜在编译错误。

#### 1.7.0

##### 功能 / 变更：
* Catch 现在在处理通过测试用例的通过测试时快了很多
  * 专注于 Catch 开销的微基准从大约 3.4s 降到大约 0.7s。
  * 使用 [JSON for Modern C++](https://github.com/nlohmann/json) 测试套件的真实场景从大约 6 分 25 秒降到大约 4 分 14 秒。
* Catch 现在可以在测试用例内部运行特定 section。
  * 目前支持还比较基础（没有通配符或 tags），详情见[文档](command-line_zh.md#top)。
* Catch 现在既支持 Windows 上的 SEH，也支持 Linux 上的 signals。
  * 接收到 signal 后，Catch 会报告失败断言，然后把 signal 传给之前的 handler。
* Approx 现在可用于和强类型 typedef 比较（仅在 C++11 模式下可用）。
  * 强类型 typedef 指的是可以显式转换为 double 的类型。
* CHECK 宏在发生异常时不再停止执行 section。
* 某些字符（空格、tab 等）现在会更友好地打印。
  * 这意味着 `char c = ' '; REQUIRE(c == '\t');` 会被打印成 `' ' == '\t'`，而不是 ` == 9`。

##### 修复：
* 文本格式化在某些情况下不再尝试访问越界字符。
* THROW 系列断言在表达式包含显式 cast 时不再触发 `-Wunused-value`。
* 在 OS X 上进入调试器再次可用，并且不再要求定义 `DEBUG`。
* 在某些编译器下，如果在断言宏内部使用 lambda，编译不再失败。

##### 其他：
* Catch 的 CMakeLists 现在定义了 install 命令。
* Catch 的 CMakeLists 现在生成启用了 warning 的项目。


### 1.6.x

#### 1.6.1

##### 功能 / 变更：
* Catch 现在支持在 Linux 上进入调试器

##### 修复：
* generators 不再泄漏内存（不过一般来说 generators 仍然不受支持）
* JUnit reporter 现在会报告 UTC 时间戳，而不是 `"tbd"`
* 使用 `CATCH_` 前缀宏时，`CHECK_THAT` 宏现在会正确地定义为 `CATCH_CHECK_THAT`

##### 其他：
* 带重载 `&&` 运算符的类型在断言宏里不再会被求值两次。
* 当 Catch 被 CLion 解析时，会抑制 `__COUNTER__` 的使用
  * 这个改动在编译二进制时不生效
* 现在可以在 Windows 上运行 approval tests
* 如果某个文件存在于 `include` 文件夹中，但没有被列为项目的一部分，CMake 现在会发出 warning
* Catch 现在会在包含 `windows.h` 之前定义 `NOMINMAX` 和 `WIN32_LEAN_AND_MEAN`
  * 如有需要，可以禁用这一点，详情见[文档](configuration_zh.md#top)。

#### 1.6.0

##### Cmake/ projects：
* 把 `CMakeLists.txt` 移到根目录，让它对 CLion 更友好，也便于生成 XCode 和 VS 项目，并移除了手工维护的 XCode 和 VS 项目。

##### 功能 / 变更：
* Approx 现在支持 `>=` 和 `<=`
* 现在可以在命令行的测试名中使用 `\` 转义字符
* 标准化 C++11 功能开关

##### 修复：
* 蓝色 shell 颜色
* `CATCH_CHECK_THROWS` 缺少参数
* 不要在 XML 中编码扩展 ASCII
* 在更多编译器上使用 `std::shuffle`（修复弃用 warning/错误）
* 更一致地使用 `__COUNTER__`（在可用时）

##### 其他：
* 对脚本做了调整和变更，尤其是 approval test 相关脚本，以提升可移植性


<a id="older-versions"></a>
## 更早的版本
在 v1.6.0 之前没有维护发布说明，但你应该可以从 Git 历史中把它们整理出来。

<a id="even-older-versions"></a>
## 更更早的版本
v1.6.0 之前的更早历史同样没有正式维护的发布说明，需要时只能从 Git 历史中回溯。

---

[Home](Readme_zh.md#top)
