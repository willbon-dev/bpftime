<a id="top"></a>
# 教程

**目录**<br>
[获取 Catch2](#getting-catch2)<br>
[编写测试](#writing-tests)<br>
[测试用例和 sections](#test-cases-and-sections)<br>
[BDD 风格测试](#bdd-style-testing)<br>
[数据驱动和类型驱动测试](#data-and-type-driven-tests)<br>
[下一步](#next-steps)<br>

## 获取 Catch2

理想情况下，你应该通过 [CMake 集成](docs/docs/cmake-integration_zh.md#top)来使用 Catch2。Catch2 也提供 pkg-config 文件，以及双文件（header + cpp）分发方式，但本文档会假设你正在使用 CMake。如果你使用的是双文件分发，请记得把包含的头文件替换成 `catch_amalgamated.hpp`。

## 编写测试

我们先从一个非常简单的例子开始（[代码](../examples/010-TestCase.cpp)）。假设你已经写好了一个计算阶乘的函数，现在想测试它（先暂时不考虑 TDD）。

```c++
unsigned int Factorial( unsigned int number ) {
    return number <= 1 ? number : Factorial(number-1)*number;
}
```

```c++
#include <catch2/catch_test_macros.hpp>

unsigned int Factorial( unsigned int number ) {
    return number <= 1 ? number : Factorial(number-1)*number;
}

TEST_CASE( "Factorials are computed", "[factorial]" ) {
    REQUIRE( Factorial(1) == 1 );
    REQUIRE( Factorial(2) == 2 );
    REQUIRE( Factorial(3) == 6 );
    REQUIRE( Factorial(10) == 3628800 );
}
```

这会编译成一个完整的可执行文件，它会响应 [命令行参数](docs/docs/command-line_zh.md#top)。如果你直接运行它而不带任何参数，它会执行所有测试用例（这里就只有一个），报告任何失败，输出通过和失败测试的汇总，并返回失败测试的数量（如果你只想要一个“是否成功”的是/否答案，这很有用）。

不过，上面的测试虽然会通过，但其实有 bug。问题在于 `Factorial(0)` 应该返回 1（根据[定义](https://en.wikipedia.org/wiki/Factorial#Factorial_of_zero)）。我们把这一点加进测试用例：

```c++
TEST_CASE( "Factorials are computed", "[factorial]" ) {
    REQUIRE( Factorial(0) == 1 );
    REQUIRE( Factorial(1) == 1 );
    REQUIRE( Factorial(2) == 2 );
    REQUIRE( Factorial(3) == 6 );
    REQUIRE( Factorial(10) == 3628800 );
}
```

再次编译并运行后，我们会看到一个测试失败。输出大概会像这样：

```
Example.cpp:9: FAILED:
  REQUIRE( Factorial(0) == 1 )
with expansion:
  0 == 1
```

注意输出里既包含了原始表达式 `REQUIRE( Factorial(0) == 1 )`，也包含了 `Factorial` 函数调用返回的实际值 `0`。

我们可以通过稍微修改 `Factorial` 函数来修复这个 bug：
```c++
unsigned int Factorial( unsigned int number ) {
  return number > 1 ? Factorial(number-1)*number : 1;
}
```

### 我们在这里做了什么？

虽然这只是一个简单的测试，但它已经足以展示 Catch2 的一些用法。让我们在继续之前，先花一点时间看看这些点。

* 我们使用 `TEST_CASE` 宏来引入测试用例。这个宏接受一个或两个字符串参数，一个自由格式的测试名称，以及可选的一个或多个标签（更多信息请看[测试用例和 sections](#test-cases-and-sections)）。
* 测试会自动向测试运行器注册，用户不需要再做任何额外事情来确保它被测试框架拾取。_注意你可以通过[命令行](docs/docs/command-line_zh.md#top)运行特定测试或一组测试。_
* 单个测试断言使用 `REQUIRE` 宏编写。它接受一个布尔表达式，并使用表达式模板在内部对其进行分解，这样在测试失败时就能分别输出字符串化结果。

最后一点需要注意的是，还有更多测试宏可用，因为并不是所有有价值的检查都能用简单的布尔表达式来表达。比如，检查某个表达式是否抛出异常可以使用 `REQUIRE_THROWS` 宏。后面会继续介绍。

## 测试用例和 sections

和大多数测试框架一样，Catch2 支持基于类的 fixture 机制，即单个测试是类的方法，而 setup/teardown 可以在类型的构造函数/析构函数中完成。

不过，在 Catch2 中这种方式并不常见，因为更符合 Catch2 风格的测试会使用 _sections_ 在测试代码之间共享 setup 和 teardown 代码。下面通过一个例子来说明（[代码](../examples/100-Fix-Section.cpp)）：

```c++
TEST_CASE( "vectors can be sized and resized", "[vector]" ) {

    std::vector<int> v( 5 );

    REQUIRE( v.size() == 5 );
    REQUIRE( v.capacity() >= 5 );

    SECTION( "resizing bigger changes size and capacity" ) {
        v.resize( 10 );

        REQUIRE( v.size() == 10 );
        REQUIRE( v.capacity() >= 10 );
    }
    SECTION( "resizing smaller changes size but not capacity" ) {
        v.resize( 0 );

        REQUIRE( v.size() == 0 );
        REQUIRE( v.capacity() >= 5 );
    }
    SECTION( "reserving bigger changes capacity but not size" ) {
        v.reserve( 10 );

        REQUIRE( v.size() == 5 );
        REQUIRE( v.capacity() >= 10 );
    }
    SECTION( "reserving smaller does not change size or capacity" ) {
        v.reserve( 0 );

        REQUIRE( v.size() == 5 );
        REQUIRE( v.capacity() >= 5 );
    }
}
```

对于每个 `SECTION`，`TEST_CASE` 都会从头执行一遍。这意味着每次进入某个 section 时，都会重新构造一个向量 `v`，我们知道它的 size 是 5，capacity 至少也是 5，因为进入 section 之前也会先检查这两个断言。每次执行一个测试用例时，只会走到一个叶子 section。

section 也可以嵌套，此时父 section 会被多次进入，每个叶子 section 都会进入一次。嵌套 section 最适合用于多个测试共享一部分 setup 的场景。继续上面的 vector 例子，你可以再增加一个检查，确保 `std::vector::reserve` 不会移除未使用的多余 capacity，如下所示：

```cpp
    SECTION( "reserving bigger changes capacity but not size" ) {
        v.reserve( 10 );

        REQUIRE( v.size() == 5 );
        REQUIRE( v.capacity() >= 10 );
        SECTION( "reserving down unused capacity does not change capacity" ) {
            v.reserve( 7 );
            REQUIRE( v.size() == 5 );
            REQUIRE( v.capacity() >= 10 );
        }
    }
```

另一个理解 section 的方式是：它们是在定义一棵测试路径树。每个 section 代表一个节点，最终的树会以深度优先方式遍历，每条路径只访问一个叶子节点。

section 的嵌套深度没有实际限制，只要你的编译器能处理即可，但要记住，过深的嵌套会让代码难以阅读。根据经验，section 嵌套超过 3 层通常就很难跟踪，也不值得为了减少重复而这样做。

## BDD 风格测试

Catch2 还提供了一些对 BDD 风格测试的基础支持。`TEST_CASE` 和 `SECTIONS` 都有宏别名可用，这样测试代码读起来就像 BDD 规格说明。`SCENARIO` 的作用类似于 `TEST_CASE`，只是会在名字前加上 `"Scenario: "`。然后还有 `GIVEN`、`WHEN`、`THEN`（以及带 `AND_` 前缀的变体），它们的行为类似 `SECTION`，只是宏名会加前缀。

关于这些宏的更多细节，请查看参考文档中的[测试用例和 sections](test-cases-and-sections_zh.md#top)部分，或者看看[用 BDD 宏写成的 vector 示例](../examples/120-Bdd-ScenarioGivenWhenThen.cpp)。

## 数据驱动和类型驱动测试

Catch2 中的测试用例也可以由类型、输入数据，或者两者同时驱动。

更多细节请查看 Catch2 参考文档中的[类型参数化测试用例](test-cases-and-sections_zh.md#type-parametrised-test-cases)或[数据生成器](generators_zh.md#top)。

## 下一步

这一页只是对 Catch2 的一个简要介绍，目的是帮助你快速上手，并展示 Catch2 的基础功能。这里提到的特性已经足以解决很多场景，但还有更多内容。你可以在文档不断扩展的[参考部分](Readme_zh.md#top)中继续阅读这些内容。

---

[Home](Readme_zh.md#top)
