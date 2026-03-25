<a id="top"></a>
# 断言宏

**目录**<br>
[自然表达式](#natural-expressions)<br>
[浮点数比较](#floating-point-comparisons)<br>
[异常](#exceptions)<br>
[Matcher 表达式](#matcher-expressions)<br>
[线程安全](#thread-safety)<br>
[带逗号的表达式](#expressions-with-commas)<br>

大多数测试框架都会有一大堆断言宏，用来覆盖各种可能的条件形式（```_EQUALS```、```_NOTEQUALS```、```_GREATER_THAN``` 等等）。

Catch 不一样。因为它会分解自然的 C 风格条件表达式，所以这些形式大多都被简化成一两个你会一直使用的宏。即便如此，它也提供了一整套丰富的辅助宏。下面我们会逐一介绍。

这些宏大多都有两种形式：

## 自然表达式

```REQUIRE``` 系列宏会测试一个表达式，若失败则中止测试用例。
```CHECK``` 系列与之等价，但即使断言失败，执行也会继续留在同一个测试用例中。这对于一组本质上彼此独立的断言很有用，因为你可以看到所有结果，而不是在第一个失败处就停下来。

* **REQUIRE(** _expression_ **)** 和
* **CHECK(** _expression_ **)**

求值表达式并记录结果。如果抛出异常，则会被捕获、报告并计为失败。这是你最常使用的宏。

示例：
```
CHECK( str == "string value" );
CHECK( thisReturnsTrue() );
REQUIRE( i == 42 );
```

以 `!` 开头的表达式不能被分解。如果你有一个可转换为 bool 的类型，并且想断言它为 false，请使用下面两种形式：

* **REQUIRE_FALSE(** _expression_ **)** 和
* **CHECK_FALSE(** _expression_ **)**

注意，对普通 bool 变量没有必要使用这些形式，因为分解它们并没有额外价值。

示例：
```cpp
Status ret = someFunction();
REQUIRE_FALSE(ret); // ret 必须求值为 false，Catch2 还会尽可能打印出 ret 的值
```

### 其他限制

需要注意的是，包含二元逻辑运算符 `&&` 或 `||` 的表达式不能被分解，也不会编译通过。原因在于，无法以一种既保持短路语义又允许表达式分解的方式重载 `&&` 和 `||`；而表达式分解依赖的正是这些重载运算符。

一个典型的重载二元逻辑运算符问题示例是常见的指针惯用法 `p && p->foo == 2`。使用内置的 `&&` 运算符时，只有当 `p` 非空才会解引用它；而使用重载的 `&&` 时，`p` 总会被解引用，因此如果 `p == nullptr` 就会导致段错误。

如果你想测试包含 `&&` 或 `||` 的表达式，有两个选择。

1) 把它包在括号里。括号会强制表达式先求值，这样表达式分解就碰不到它了。

2) 重写表达式。`REQUIRE(a == 1 && b == 2)` 总可以拆成 `REQUIRE(a == 1); REQUIRE(b == 2);`。或者，如果这是测试中常见的模式，可以考虑改用 [Matchers](#matcher-expressions)。至于 `||`，没有简单的改写规则；不过我通常认为，如果你的测试表达式里出现了 `||`, 你应该重新思考一下你的测试。

## 浮点数比较

浮点数比较很复杂，因此[它有自己单独的文档页](comparing-floating-point-numbers_zh.md#top)。

## 异常

* **REQUIRE_NOTHROW(** _expression_ **)** 和
* **CHECK_NOTHROW(** _expression_ **)**

期望在表达式求值过程中不会抛出异常。

* **REQUIRE_THROWS(** _expression_ **)** 和
* **CHECK_THROWS(** _expression_ **)**

期望在表达式求值过程中会抛出异常（任意类型均可）。

* **REQUIRE_THROWS_AS(** _expression_, _exception type_ **)** 和
* **CHECK_THROWS_AS(** _expression_, _exception type_ **)**

期望在表达式求值过程中抛出 _指定类型_ 的异常。注意，_exception type_ 会自动扩展为 `const&`，你不需要自己写。

* **REQUIRE_THROWS_WITH(** _expression_, _string or string matcher_ **)** 和
* **CHECK_THROWS_WITH(** _expression_, _string or string matcher_ **)**

期望抛出的异常在转换成字符串后，与提供的 _string_ 或 _string matcher_ 匹配（见下一节 Matcher）。

例如：
```cpp
REQUIRE_THROWS_WITH( openThePodBayDoors(), Contains( "afraid" ) && Contains( "can't do that" ) );
REQUIRE_THROWS_WITH( dismantleHal(), "My mind is going" );
```

* **REQUIRE_THROWS_MATCHES(** _expression_, _exception type_, _matcher for given exception type_ **)** 和
* **CHECK_THROWS_MATCHES(** _expression_, _exception type_, _matcher for given exception type_ **)**

期望抛出 _exception type_ 类型的异常，并且它满足给定的 matcher（见 [Matchers 文档](docs/docs/matchers_zh.md#top)）。

_请注意，`THROW` 系列断言期望接收的是一个单独的表达式，而不是语句或一系列语句。如果你想检查更复杂的一串操作，可以使用 C++11 lambda 函数。_

```cpp
REQUIRE_NOTHROW([&](){
    int i = 1;
    int j = 2;
    auto k = i + j;
    if (k == 3) {
        throw 1;
    }
}());
```

## Matcher 表达式

为了支持 Matcher，采用了略有不同的形式。Matchers 有[自己的文档页](docs/docs/matchers_zh.md#top)。

* **REQUIRE_THAT(** _lhs_, _matcher expression_ **)** 和
* **CHECK_THAT(** _lhs_, _matcher expression_ **)**

Matcher 可以使用 `&&`、`||` 和 `!` 运算符组合。

## 线程安全

目前 Catch 中的断言不是线程安全的。更多细节以及 workaround，请看[限制页面](limitations_zh.md#thread-safe-assertions)中的相关部分。

## 带逗号的表达式

由于预处理器解析代码时使用的规则与编译器不同，多参数断言（例如 `REQUIRE_THROWS_AS`）在提供的表达式中遇到逗号时会有问题。例如 `REQUIRE_THROWS_AS(std::pair<int, int>(1, 2), std::invalid_argument);` 会编译失败，因为预处理器看到了 3 个参数，而宏只接受 2 个。这里有两种 workaround。

1) 使用 typedef：
```cpp
using int_pair = std::pair<int, int>;
REQUIRE_THROWS_AS(int_pair(1, 2), std::invalid_argument);
```

这个方案总是适用的，但会让代码含义没那么清晰。

2) 用括号包住表达式：
```cpp
TEST_CASE_METHOD((Fixture<int, int>), "foo", "[bar]") {
    SUCCEED();
}
```

这个方案并不总是适用，因为它可能需要在 Catch 一侧做额外改动才能工作。

---

[Home](Readme_zh.md#top)
