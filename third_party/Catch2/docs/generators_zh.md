<a id="top"></a>
# 数据生成器

> Catch2 2.6.0 中引入。

数据生成器（也称为 _data driven/parametrized test cases_）让你可以在不同输入值上复用同一组断言。在 Catch2 中，这意味着它们会尊重 `TEST_CASE` 和 `SECTION` 宏的顺序与嵌套关系，而且它们的嵌套 section 会针对 generator 中的每个值运行一次。

最好的解释方式是看一个例子：
```cpp
TEST_CASE("Generators") {
    auto i = GENERATE(1, 3, 5);
    REQUIRE(is_odd(i));
}
```

上面的 "Generators" `TEST_CASE` 会被进入 3 次，`i` 的值依次为 1、3、5。`GENERATE` 也可以在同一作用域中多次使用，此时结果是各个 generator 元素的笛卡尔积。也就是说，下面这个片段中的测试用例会运行 6 次（2*3）。

```cpp
TEST_CASE("Generators") {
    auto i = GENERATE(1, 2);
    auto j = GENERATE(3, 4, 5);
}
```

Catch2 中的 generator 由两部分组成：`GENERATE` 宏及其自带的 generators，以及允许用户实现自定义 generator 的 `IGenerator<T>` 接口。

## 结合 `GENERATE` 和 `SECTION`

`GENERATE` 可以被看作一个隐式 `SECTION`，它从 `GENERATE` 所在的位置一直延伸到作用域末尾。它可以带来多种效果。下面是最简单的用法：这里 `SECTION` "one" 会运行 4 次（2*2），`SECTION` "two" 会运行 6 次（2*3）。

```cpp
TEST_CASE("Generators") {
    auto i = GENERATE(1, 2);
    SECTION("one") {
        auto j = GENERATE(-3, -2);
        REQUIRE(j < i);
    }
    SECTION("two") {
        auto k = GENERATE(4, 5, 6);
        REQUIRE(i != k);
    }
}
```

section 的具体顺序会是 "one", "one", "two", "two", "two", "one"...

`GENERATE` 引入一个虚拟 `SECTION` 这一事实，也可以用来让某个 generator 只重放部分 `SECTION`，而不必显式添加一个 `SECTION`。例如，下面的代码会报告 3 个断言，因为 "first" section 运行一次，而 "second" section 运行两次。

```cpp
TEST_CASE("GENERATE between SECTIONs") {
    SECTION("first") { REQUIRE(true); }
    auto _ = GENERATE(1, 2);
    SECTION("second") { REQUIRE(true); }
}
```

这可能会导致相当复杂的测试流。比如，下面这个测试会报告 14 个断言：

```cpp
TEST_CASE("Complex mix of sections and generates") {
    auto i = GENERATE(1, 2);
    SECTION("A") {
        SUCCEED("A");
    }
    auto j = GENERATE(3, 4);
    SECTION("B") {
        SUCCEED("B");
    }
    auto k = GENERATE(5, 6);
    SUCCEED();
}
```

> 可以把 `GENERATE` 放在两个 `SECTION` 之间，这一能力是在 Catch2 2.13.0 中引入的。

## 提供的 generators

Catch2 自带的 generator 功能由三部分组成：

* `GENERATE` 宏，用于把 generator 表达式整合进测试用例
* 2 个基础 generator
  * `SingleValueGenerator<T>` -- 只包含单个元素
  * `FixedValuesGenerator<T>` -- 包含多个元素
* 5 个修改其他 generator 的通用 generator
  * `FilterGenerator<T, Predicate>` -- 过滤掉 predicate 返回 `false` 的元素
  * `TakeGenerator<T>` -- 取 generator 的前 `n` 个元素
  * `RepeatGenerator<T>` -- 将 generator 的输出重复 `n` 次
  * `MapGenerator<T, U, Func>` -- 返回把 `Func` 作用在另一个 generator 元素上的结果
  * `ChunkGenerator<T>` -- 返回 generator 中按 `n` 个元素分块的结果（位于 `std::vector` 中）
* 4 个特定用途 generator
  * `RandomIntegerGenerator<Integral>` -- 生成给定范围内的随机整数
  * `RandomFloatGenerator<Float>` -- 生成给定范围内的随机浮点数
  * `RangeGenerator<T>(first, last)` -- 生成 `[first, last)` 算术范围内的所有值
  * `IteratorGenerator<T>` -- 复制并返回某个迭代器范围内的值

> `ChunkGenerator<T>`、`RandomIntegerGenerator<Integral>`、`RandomFloatGenerator<Float>` 和 `RangeGenerator<T>` 是在 Catch2 2.7.0 中引入的。

> `IteratorGenerator<T>` 是在 Catch2 2.10.0 中引入的。

这些 generator 还带有相关的辅助函数，可以推导它们的类型，让使用起来更方便。它们是：

* `value(T&&)` 对应 `SingleValueGenerator<T>`
* `values(std::initializer_list<T>)` 对应 `FixedValuesGenerator<T>`
* `table<Ts...>(std::initializer_list<std::tuple<Ts...>>)` 对应 `FixedValuesGenerator<std::tuple<Ts...>>`
* `filter(predicate, GeneratorWrapper<T>&&)` 对应 `FilterGenerator<T, Predicate>`
* `take(count, GeneratorWrapper<T>&&)` 对应 `TakeGenerator<T>`
* `repeat(repeats, GeneratorWrapper<T>&&)` 对应 `RepeatGenerator<T>`
* `map(func, GeneratorWrapper<T>&&)` 对应 `MapGenerator<T, U, Func>`（把 `U` 映射到 `T`，由 `Func` 推导）
* `map<T>(func, GeneratorWrapper<U>&&)` 对应 `MapGenerator<T, U, Func>`（把 `U` 映射到 `T`）
* `chunk(chunk-size, GeneratorWrapper<T>&&)` 对应 `ChunkGenerator<T>`
* `random(IntegerOrFloat a, IntegerOrFloat b)` 对应 `RandomIntegerGenerator` 或 `RandomFloatGenerator`
* `range(Arithmetic start, Arithmetic end)` 对应步长为 `1` 的 `RangeGenerator<Arithmetic>`
* `range(Arithmetic start, Arithmetic end, Arithmetic step)` 对应自定义步长的 `RangeGenerator<Arithmetic>`
* `from_range(InputIterator from, InputIterator to)` 对应 `IteratorGenerator<T>`
* `from_range(Container const&)` 对应 `IteratorGenerator<T>`

> `chunk()`、`random()` 和两个 `range()` 函数都是在 Catch2 2.7.0 中引入的。

> `from_range` 是在 Catch2 2.10.0 中引入的。

> 用于浮点数的 `range()` 是在 Catch2 2.11.0 中引入的。

它们可以像下面的例子那样使用，从而创建一个返回 100 个奇数随机数的 generator：

```cpp
TEST_CASE("Generating random ints", "[example][generator]") {
    SECTION("Deducing functions") {
        auto i = GENERATE(take(100, filter([](int i) { return i % 2 == 1; }, random(-100, 100))));
        REQUIRE(i > -100);
        REQUIRE(i < 100);
        REQUIRE(i % 2 == 1);
    }
}
```

除了把 generator 注册到 Catch2 之外，`GENERATE` 宏还有另一个用途，那就是提供一种简单方式来生成最基础的 generator。就像本页第一个例子中那样，我们写了 `auto i = GENERATE(1, 2, 3);`。这种写法会把三个字面量分别转换成单独的 `SingleValueGenerator<int>`，然后把它们都放进一个会拼接其他 generator 的特殊 generator 中。它也可以和其他 generator 一起作为参数使用，例如 `auto i = GENERATE(0, 2, take(100, random(300, 3000)));`。这在你已经知道某些输入有问题、想单独或优先测试它们时非常有用。

**出于安全考虑，你不能在 `GENERATE` 宏内部使用变量。这样做是因为 generator 表达式的生命周期会 _长于_ 外层作用域，因此捕获引用是危险的。如果你需要在 generator 表达式里使用变量，请务必考虑清楚生命周期影响，并使用 `GENERATE_COPY` 或 `GENERATE_REF`。**

> `GENERATE_COPY` 和 `GENERATE_REF` 是在 Catch2 2.7.1 中引入的。

你还可以通过在宏的第一个参数中使用 `as<type>` 来覆盖推导出的类型。这在处理字符串字面量时很有用，如果你希望它们以 `std::string` 的形式出现：

```cpp
TEST_CASE("type conversion", "[generators]") {
    auto str = GENERATE(as<std::string>{}, "a", "bb", "ccc");
    REQUIRE(str.size() > 0);
}
```

## Generator 接口

你还可以通过继承 `IGenerator<T>` 接口来实现自己的 generator：

```cpp
template<typename T>
struct IGenerator : GeneratorUntypedBase {
    // via GeneratorUntypedBase:
    // 尝试把 generator 移动到下一个元素。
    // 如果成功（也就是还有下一个可读取的元素），返回 true
    virtual bool next() = 0;

    // 前置条件：
    // generator 要么是刚构造的，要么上一次 next() 调用返回了 true
    virtual T const& get() const = 0;

    // 返回一个友好的字符串，显示当前 generator 元素
    // 不一定要重写，IGenerator 提供了默认实现
    virtual std::string stringifyImpl() const;
};
```

不过，要想在 `GENERATE` 内部使用自定义 generator，它必须被包装在 `GeneratorWrapper<T>` 中。
`GeneratorWrapper<T>` 是 `Catch::Detail::unique_ptr<IGenerator<T>>` 的值包装器。

关于如何实现自己的 generator 的完整示例，请查看 Catch2 的示例，特别是
[Generators: Create your own generator](../examples/300-Gen-OwnGenerator.cpp)。

### 处理空 generator

generator 接口假定 generator 至少总有一个元素。但这并不总是成立，比如当 generator 依赖外部数据文件时，文件可能丢失。

这有两种处理方式，取决于你是否希望这算作错误。

* 如果空 generator **是** 错误，就在构造函数里抛出异常。
* 如果空 generator **不是** 错误，就在构造函数里使用 [`SKIP`](skipping-passing-failing_zh.md#skipping-test-cases-at-runtime)。

---

[Home](Readme_zh.md#top)
