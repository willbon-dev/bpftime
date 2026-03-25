<a id="top"></a>
# 在运行时显式跳过、通过和失败测试

## 在运行时跳过测试用例

> Catch2 3.3.0 中引入。

在某些情况下，测试用例可能无法有意义地执行，例如被测系统缺少某些硬件能力。如果所需条件只能在运行时确定，那么通常就不应该把这样的测试用例算作通过或失败，因为它根本无法运行。

为了正确表达这种场景，Catch2 提供了一个显式 _跳过_ 测试用例的方法，即使用 `SKIP` 宏：

```
SKIP( [streamable expression] )
```

示例用法：

```c++
TEST_CASE("copy files between drives") {
    if(getNumberOfHardDrives() < 2) {
        SKIP("at least two hard drives required");
    }
    // ...
}
```

此时测试用例会被报告为 _skipped_，而不是 _passed_ 或 _failed_。

`SKIP` 宏的行为类似于显式的 [`FAIL`](#passing-and-failing-test-cases)，因为它是最后一个会被执行的表达式：

```c++
TEST_CASE("my test") {
    printf("foo");
    SKIP();
    printf("bar"); // 不会打印
}
```

不过，`SKIP` 之前如果有失败的断言，仍然会导致整个测试用例失败：

```c++
TEST_CASE("failing test") {
    CHECK(1 == 2);
    SKIP();
}
```

### 与 Sections 和 Generators 的交互

sections、嵌套 sections，以及来自 [generators](generators_zh.md#top) 的特定输出，都可以单独跳过，其余部分会照常执行：

```c++
TEST_CASE("complex test case") {
  int value = GENERATE(2, 4, 6);
  SECTION("a") {
    SECTION("a1") { CHECK(value < 8); }
    SECTION("a2") {
      if (value == 4) {
        SKIP();
      }
      CHECK(value % 2 == 0);
    }
  }
}
```

这个测试用例会报告 5 个通过的断言；其中 3 个来自 section `a1` 中的三个值，另外 2 个来自 section `a2` 中的值 2 和 4。

注意，一旦某个 section 被跳过，整个测试用例都会被报告为 _skipped_（除非存在失败断言，在这种情况下测试会被报告为 _failed_）。

还要注意，如果一次运行中所有测试用例都被跳过，Catch2 会返回非零退出码，就像没有测试用例运行一样。这个行为可以通过 [--allow-running-no-tests](docs/docs/command-line_zh.md#no-tests-override) 标志覆盖。

### 在 generator 中使用 `SKIP`

你还可以在 generator 的构造函数中使用 `SKIP` 宏，来处理 generator 为空但你又不想让测试用例失败的情况。

## 显式通过和失败测试用例

测试用例也可以在不使用断言的情况下被显式标记为通过或失败，并附带特定消息。这在处理复杂的前置条件/后置条件时很有用，也能在失败时提供有用的错误信息。

* `SUCCEED( [streamable expression] )`

`SUCCEED` 在语义上大体等价于 `INFO( [streamable expression] ); REQUIRE( true );`。
注意，它不会停止后续测试执行，因此不能用来防止后续失败断言被执行。

_实际上，`SUCCEED` 通常用作测试占位符，用来避免[由于缺少断言而导致测试用例失败](docs/docs/command-line_zh.md#warnings)。_

```cpp
TEST_CASE( "SUCCEED showcase" ) {
    int I = 1;
    SUCCEED( "I is " << I );
    // ... execution continues here ...
}
```

* `FAIL( [streamable expression] )`

`FAIL` 在语义上大体等价于 `INFO( [streamable expression] ); REQUIRE( false );`。

_实际上，`FAIL` 通常用于暂时停止执行一个当前已知有问题、但以后必须修复的测试。_

```cpp
TEST_CASE( "FAIL showcase" ) {
    FAIL( "This test case causes segfault, which breaks CI." );
    // ... this will not be executed ...
}
```

---

[Home](Readme_zh.md#top)
