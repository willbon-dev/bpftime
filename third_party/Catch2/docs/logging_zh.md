<a id="top"></a>
# 日志宏

测试用例运行期间可以记录额外消息。注意，使用 `INFO` 记录的消息是有作用域的，因此如果失败发生在消息声明之前的作用域中，这些消息不会被报告。示例如下：

```cpp
TEST_CASE("Foo") {
    INFO("Test case start");
    for (int i = 0; i < 2; ++i) {
        INFO("The number is " << i);
        CHECK(i == 0);
    }
}

TEST_CASE("Bar") {
    INFO("Test case start");
    for (int i = 0; i < 2; ++i) {
        INFO("The number is " << i);
        CHECK(i == i);
    }
    CHECK(false);
}
```
当 "Foo" 测试用例中的 `CHECK` 失败时，会打印两条消息：
```
Test case start
The number is 1
```
当 "Bar" 测试用例中的最后一个 `CHECK` 失败时，只会打印一条消息：`Test case start`。

## 无局部作用域的日志

> [Introduced](https://github.com/catchorg/Catch2/issues/1522) in Catch2 2.7.0.

`UNSCOPED_INFO` 类似于 `INFO`，但有两个关键区别：

- 无作用域消息的生命周期不受其自身作用域限制。
- 无作用域消息只会被后续遇到的第一个断言报告一次，而不管该断言的结果如何。

换句话说，`UNSCOPED_INFO` 的生命周期由后续断言（或测试用例/section 结束，取先发生者）决定，而 `INFO` 的生命周期由其自身作用域决定。

这些差异使这个宏很适合用于报告 helper 函数或内部作用域中的信息。示例如下：

```cpp
void print_some_info() {
    UNSCOPED_INFO("Info from helper");
}

TEST_CASE("Baz") {
    print_some_info();
    for (int i = 0; i < 2; ++i) {
        UNSCOPED_INFO("The number is " << i);
    }
    CHECK(false);
}

TEST_CASE("Qux") {
    INFO("First info");
    UNSCOPED_INFO("First unscoped info");
    CHECK(false);

    INFO("Second info");
    UNSCOPED_INFO("Second unscoped info");
    CHECK(false);
}
```

"Baz" 测试用例会打印：
```
Info from helper
The number is 0
The number is 1
```

对于 "Qux" 测试用例，第一个 `CHECK` 失败时会打印两条消息：
```
First info
First unscoped info
```

"First unscoped info" 消息会在第一次 `CHECK` 之后被清除，而 "First info" 消息会一直保留到测试用例结束。因此，当第二个 `CHECK` 失败时，会打印三条消息：
```
First info
Second info
Second unscoped info
```

## 流式宏

所有这些宏都允许像 `std::ostream`、`std::cout` 等那样，使用插入运算符（```<<```）来流式输出异构值序列。

例如：
```c++
INFO( "The number is " << i );
```

（注意这里没有最前面的 ```<<``` - 插入序列是放在括号里的。）
这些宏有三种形式：

**INFO(** _message expression_ **)**

消息会被记录到缓冲区里，但只会在下一次记录了日志的断言时报告。这样你就可以记录失败时的上下文信息，而不会在成功运行测试时显示出来（对 console reporter 而言，且不带 `-s`）。消息会在其作用域结束时从缓冲区移除，因此例如可以在循环中使用。

_注意在 Catch2 2.x.x 中，`INFO` 即使没有分号结尾也可以使用，因为宏内部已经包含了一个尾部分号。这个分号会在下一个主版本中移除。强烈建议你在 `INFO` 宏后面仍然写上分号。_

**UNSCOPED_INFO(** _message expression_ **)**

> [Introduced](https://github.com/catchorg/Catch2/issues/1522) in Catch2 2.7.0.

与 `INFO` 类似，但消息不受自身作用域限制：它们会在每次断言、section 或测试用例之后从缓冲区移除，取先发生者。

**WARN(** _message expression_ **)**

消息总会被报告，但不会导致测试失败。

**FAIL(** _message expression_ **)**

消息会被报告，测试用例会失败。

**FAIL_CHECK(** _message expression_ **)**

与 `FAIL` 相同，但不会中止测试

## 快速捕获变量或表达式的值

**CAPTURE(** _expression1_, _expression2_, ... **)**

有时你只想记录某个变量或表达式的值。为了方便起见，我们提供了 `CAPTURE` 宏，它可以接受变量或表达式，并输出该变量/表达式以及捕获时的值。

例如，`CAPTURE( theAnswer );` 会记录消息 "theAnswer := 42"，而：
```cpp
int a = 1, b = 2, c = 3;
CAPTURE( a, b, c, a + b, c > b, a == 1);
```
会总共记录 6 条消息：
```
a := 1
b := 2
c := 3
a + b := 3
c > b := true
a == 1 := true
```

你也可以捕获在括号中使用逗号的表达式（例如函数调用）、方括号或花括号中的表达式。要正确捕获包含模板参数列表的表达式（换句话说，它在尖括号之间包含逗号），需要把表达式再包一层括号：
`CAPTURE( (std::pair<int, int>{1, 2}) );`

---

[Home](Readme_zh.md#top)
