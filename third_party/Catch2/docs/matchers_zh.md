<a id="top"></a>
# Matchers

**目录**<br>
[使用 Matchers](#using-matchers)<br>
[内置 matchers](#built-in-matchers)<br>
[编写自定义 matchers（旧风格）](#writing-custom-matchers-old-style)<br>
[编写自定义 matchers（新风格）](#writing-custom-matchers-new-style)<br>

Matchers 是受 [Hamcrest](https://en.wikipedia.org/wiki/Hamcrest) 框架启发的一种断言写法，适合处理复杂类型或更复杂属性的测试。Matchers 容易组合，用户也可以编写自己的 matcher，并无缝与 Catch2 提供的 matcher 组合。

## 使用 Matchers

Matchers 最常和 `REQUIRE_THAT` 或 `CHECK_THAT` 宏一起使用。`REQUIRE_THAT` 接受两个参数，第一个是要测试的输入（对象/值），第二个参数是 matcher 本身。

例如，如果要断言某个字符串以 “as a service” 结尾，可以这样写：

```cpp
using Catch::Matchers::EndsWith;

REQUIRE_THAT( getSomeString(), EndsWith("as a service") );
```

单个 matcher 也可以使用 C++ 逻辑运算符 `&&`、`||` 和 `!` 进行组合：

```cpp
using Catch::Matchers::EndsWith;
using Catch::Matchers::ContainsSubstring;

REQUIRE_THAT( getSomeString(),
              EndsWith("as a service") && ContainsSubstring("web scale"));
```

上面的例子断言 `getSomeString` 返回的字符串既以 “as a service” 结尾，又在某处包含 “web scale”。

上面示例使用的两个字符串 matcher 都位于 `catch_matchers_string.hpp` 头文件中，因此编译这些代码还需要 `#include <catch2/matchers/catch_matchers_string.hpp>`。

**重要**：组合运算符不会接管被组合 matcher 对象的所有权。这意味着，如果你把组合后的 matcher 对象保存起来，就必须确保被组合的 matcher 活得比它最后一次使用更久。换句话说，下面这段代码会导致 use-after-free（UAF）：

```cpp
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_string.hpp>

TEST_CASE("Bugs, bugs, bugs", "[Bug]"){
    std::string str = "Bugs as a service";

    auto match_expression = Catch::Matchers::EndsWith( "as a service" ) ||
        (Catch::Matchers::StartsWith( "Big data" ) && !Catch::Matchers::ContainsSubstring( "web scale" ) );
    REQUIRE_THAT(str, match_expression);
}
```

## 内置 matchers

Catch2 提供的每个 matcher 都分成两部分：一个位于 `Catch::Matchers` 命名空间中的工厂函数，以及一个位于更深层命名空间、用户不应直接使用的实际 matcher 类型。上面的例子里我们用了 `Catch::Matchers::Contains`，它是实际 matcher 类型 `Catch::Matchers::StdString::ContainsMatcher` 的工厂函数。

开箱即用，Catch2 提供以下 matcher：

### `std::string` matchers

Catch2 提供 5 个作用于 `std::string` 的 matcher：
* `StartsWith(std::string str, CaseSensitive)`，
* `EndsWith(std::string str, CaseSensitive)`，
* `ContainsSubstring(std::string str, CaseSensitive)`，
* `Equals(std::string str, CaseSensitive)`，以及
* `Matches(std::string str, CaseSensitive)`。

前三个比较直观：如果参数字符串以 `str` 开头、以 `str` 结尾，或者在任意位置包含 `str`，它们就会通过。

`Equals` 只有当参数字符串和 `str` 完全相等时才匹配。

`Matches` 则使用 ECMAScript 正则表达式，把 `str` 与参数字符串做匹配。要注意，这里的匹配是针对整个字符串进行的，也就是说正则 `"abc"` 不会匹配输入字符串 `"abcd"`。如果要匹配 `"abcd"`，你需要写成例如 `"abc.*"`。

第二个参数用于指定是否大小写敏感。默认是大小写敏感。

> `std::string` matchers 位于 `catch2/matchers/catch_matchers_string.hpp`

### Vector matchers

_Vector matchers 已被废弃，改用功能相同的通用 range matchers。_

Catch2 提供 5 个内置 matcher，可用于 `std::vector`。

它们是：

 * `Contains`：检查结果中是否包含指定 vector
 * `VectorContains`：检查结果中是否包含指定元素
 * `Equals`：检查结果是否与某个特定 vector 完全相等（顺序也要一致）
 * `UnorderedEquals`：检查结果在某种排列下是否与指定 vector 相等
 * `Approx`：检查结果是否“近似相等”（顺序敏感，但比较用 `Approx`）于指定 vector
> `Approx` matcher 在 Catch2 2.7.2 中[引入](https://github.com/catchorg/Catch2/issues/1499)

示例：
```cpp
    std::vector<int> some_vec{ 1, 2, 3 };
    REQUIRE_THAT(some_vec, Catch::Matchers::UnorderedEquals(std::vector<int>{ 3, 2, 1 }));
```

这个断言会通过，因为传给 matcher 的元素是 `some_vec` 中元素的一个排列。

> vector matchers 位于 `catch2/matchers/catch_matchers_vector.hpp`

### 浮点数 matchers

Catch2 提供 4 个用于浮点数的 matcher。它们是：

* `WithinAbs(double target, double margin)`，
* `WithinULP(FloatingPoint target, uint64_t maxUlpDiff)`，以及
* `WithinRel(FloatingPoint target, FloatingPoint eps)`。
* `IsNaN()`

> `WithinRel` matcher 在 Catch2 2.10.0 中引入

> `IsNaN` matcher 在 Catch2 3.3.2 中引入。

前三个用于比较两个浮点数。更多细节请阅读[浮点数比较文档](comparing-floating-point-numbers_zh.md#floating-point-matchers)。

`IsNaN` 顾名思义：如果输入是 NaN（Not a Number），它就匹配。和直接 `REQUIRE(std::isnan(x))` 相比，它的好处是：如果检查失败，用 `REQUIRE` 你看不到 `x` 的值，而用 `REQUIRE_THAT(x, IsNaN())` 则能看到。

### 其他 matchers

Catch2 还提供了一些 matcher 和 matcher 工具，它们不太适合归到其他类别里。

第一个是 `Predicate(Callable pred, std::string description)` matcher。它会创建一个 matcher 对象，对给定参数调用 `pred`。`description` 参数允许用户指定该 matcher 在需要时的自描述文本。

要注意，你需要显式指定参数类型，例如：

```cpp
REQUIRE_THAT("Hello olleH",
             Predicate<std::string>(
                 [] (std::string const& str) -> bool { return str.front() == str.back(); },
                 "First and last character should be equal")
);
```

> predicate matcher 位于 `catch2/matchers/catch_matchers_predicate.hpp`

另一个 miscellaneous matcher 工具是异常匹配。

#### 匹配异常

Catch2 提供一个实用宏，用于断言某个表达式会抛出特定类型的异常，并且这个异常具有期望属性。这个宏是 `REQUIRE_THROWS_MATCHES(expr, ExceptionType, Matcher)`。

> `REQUIRE_THROWS_MATCHES` 宏位于 `catch2/matchers/catch_matchers.hpp`

Catch2 目前为异常提供两个 matcher：
* `Message(std::string message)`。
* `MessageMatches(Matcher matcher)`。

> `MessageMatches` 在 Catch2 3.3.0 中[引入](https://github.com/catchorg/Catch2/pull/2570)

`Message` 检查异常通过 `what()` 返回的消息是否与 `message` 完全相等。

`MessageMatches` 会把 matcher 应用到异常通过 `what()` 返回的消息上。这和 `std::string` matchers（例如 `StartsWith`）一起使用时很方便。

示例：
```cpp
REQUIRE_THROWS_MATCHES(throwsDerivedException(),  DerivedException,  Message("DerivedException::what"));
REQUIRE_THROWS_MATCHES(throwsDerivedException(),  DerivedException,  MessageMatches(StartsWith("DerivedException")));
```

注意，上面示例里的 `DerivedException` 必须继承自 `std::exception` 才能工作。

> exception message matcher 位于 `catch2/matchers/catch_matchers_exception.hpp`

### 通用 range Matchers

> 通用 range matcher 在 Catch2 3.0.1 中引入

Catch2 还提供了一些使用新风格 matcher 定义的 matcher，用于处理通用 range-like 类型。它们是：

* `IsEmpty()`
* `SizeIs(size_t target_size)`
* `SizeIs(Matcher size_matcher)`
* `Contains(T&& target_element, Comparator = std::equal_to<>{})`
* `Contains(Matcher element_matcher)`
* `AllMatch(Matcher element_matcher)`
* `AnyMatch(Matcher element_matcher)`
* `NoneMatch(Matcher element_matcher)`
* `AllTrue()`, `AnyTrue()`, `NoneTrue()`
* `RangeEquals(TargetRangeLike&&, Comparator = std::equal_to<>{})`
* `UnorderedRangeEquals(TargetRangeLike&&, Comparator = std::equal_to<>{})`

> `IsEmpty`、`SizeIs`、`Contains` 在 Catch2 3.0.1 中引入

> `All/Any/NoneMatch` 在 Catch2 3.0.1 中引入

> `All/Any/NoneTrue` 在 Catch2 3.1.0 中引入

> `RangeEquals` 和 `UnorderedRangeEquals` matcher 在 Catch2 3.3.0 中[引入](https://github.com/catchorg/Catch2/pull/2377)

`IsEmpty` 基本不需要解释。它会匹配那些根据 `std::empty`，或通过 ADL 找到的 `empty` 自由函数判断为空的对象。

`SizeIs` 用于检查 range 的 size。如果传入的是 `size_t` 参数，它会匹配 size 恰好等于该值的 range。如果构造时传入的是另一个 matcher，它会接受那些 size 被该 matcher 接受的 range。

`Contains` 用于匹配包含某个特定元素的 range。它也有两种变体：一种直接接受期望元素，如果 range 中任意元素等于目标元素就通过；另一种由 matcher 构造，如果 range 中任意元素被该 matcher 接受就通过。

`AllMatch`、`NoneMatch` 和 `AnyMatch` 分别匹配：range 中所有元素、没有元素、或者任意元素匹配给定 matcher 的情况。

`AllTrue`、`NoneTrue` 和 `AnyTrue` 分别匹配：range 中所有元素都为 `true`、没有元素为 `true`、或者任意元素为 `true` 的情况。它对 `bool` range 和显式可转换为 `bool` 的元素 range 都适用。

`RangeEquals` 会把 matcher 构造时提供的 range（“目标 range”）和待测 range 逐元素比较。如果两个 range 的所有元素都比较相等（默认用 `operator==`），就通过。两边 range 的类型不必相同，元素类型也不必相同，只要它们可比较即可（例如可以比较 `std::vector<int>` 和 `std::array<char>`）。

`UnorderedRangeEquals` 与 `RangeEquals` 类似，但顺序不重要。例如 `"1, 2, 3"` 会匹配 `"3, 2, 1"`，但不会匹配 `"1, 1, 2, 3"`。和 `RangeEquals` 一样，`UnorderedRangeEquals` 默认也是用 `operator==` 比较单个元素。

`RangeEquals` 和 `UnorderedRangeEquals` 都可以选择性接受一个谓词，用于逐元素比较容器。

如果想逐元素检查一个容器是否满足某个 matcher，请使用 `AllMatch`。

## 编写自定义 matchers（旧风格）

旧风格 matcher 的写法最早来自 Catch Classic。要创建一个旧风格 matcher，你需要自己定义一个类型，继承自 `Catch::Matchers::MatcherBase<ArgT>`，其中 `ArgT` 是 matcher 所适用的类型。你的类型必须重写两个方法：`bool match(ArgT const&) const` 和 `std::string describe() const`。

顾名思义，`match` 决定传入参数是否被 matcher 接受；`describe` 则提供这个 matcher 的面向人的描述。

我们也建议你像 Catch2 那样提供一个工厂函数，尤其是对模板 matcher 的模板参数推导很有帮助（假设你没有 CTAD）。

综合起来，假设你想写一个 matcher，用来判断给定参数是否落在某个范围内，我们把它叫作 `IsBetweenMatcher<T>`：

```c++
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers.hpp>
// ...


template <typename T>
class IsBetweenMatcher : public Catch::Matchers::MatcherBase<T> {
    T m_begin, m_end;
public:
    IsBetweenMatcher(T begin, T end) : m_begin(begin), m_end(end) {}

    bool match(T const& in) const override {
        return in >= m_begin && in <= m_end;
    }

    std::string describe() const override {
        std::ostringstream ss;
        ss << "is between " << m_begin << " and " << m_end;
        return ss.str();
    }
};

template <typename T>
IsBetweenMatcher<T> IsBetween(T begin, T end) {
    return { begin, end };
}

// ...

TEST_CASE("Numbers are within range") {
    // 推导 matcher 参数类型为 `double`
    CHECK_THAT(3., IsBetween(1., 10.));
    // 推导 matcher 参数类型为 `int`
    CHECK_THAT(100, IsBetween(1, 10));
}
```

显然，上面的代码还可以进一步改进，例如你可能希望对 `T` 是算术类型这一点加上 `static_assert`，或者把 matcher 泛化到任何用户可以提供比较函数对象的类型。

注意，虽然旧风格 matcher 也都能写成新风格，但组合旧风格 matcher 通常编译更快。还要注意，旧风格和新风格 matcher 可以任意组合。

> `MatcherBase` 位于 `catch2/matchers/catch_matchers.hpp`

## 编写自定义 matchers（新风格）

> 新风格 matcher 在 Catch2 3.0.1 中引入

要创建新风格 matcher，你需要自己定义一个类型，继承自 `Catch::Matchers::MatcherGenericBase`。你的类型还需要提供两个方法：`bool match( ... ) const` 和重写的 `std::string describe() const`。

和旧风格不同，新风格的 `match` 成员函数对参数的接收方式没有要求。这意味着参数既可以按值传，也可以按可变引用传，而且 matcher 的 `match` 成员函数甚至可以是模板。

这让你可以写出更复杂的 matcher，例如比较一个 range-like（能响应 `begin` 和 `end`）对象与另一个对象的 matcher，如下例：

```cpp
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_templated.hpp>
// ...

template<typename Range>
struct EqualsRangeMatcher : Catch::Matchers::MatcherGenericBase {
    EqualsRangeMatcher(Range const& range):
        range{ range }
    {}

    template<typename OtherRange>
    bool match(OtherRange const& other) const {
        using std::begin; using std::end;

        return std::equal(begin(range), end(range), begin(other), end(other));
    }

    std::string describe() const override {
        return "Equals: " + Catch::rangeToString(range);
    }

private:
    Range const& range;
};

template<typename Range>
auto EqualsRange(const Range& range) -> EqualsRangeMatcher<Range> {
    return EqualsRangeMatcher<Range>{range};
}

TEST_CASE("Combining templated matchers", "[matchers][templated]") {
    std::array<int, 3> container{{ 1,2,3 }};

    std::array<int, 3> a{{ 1,2,3 }};
    std::vector<int> b{ 0,1,2 };
    std::list<int> c{ 4,5,6 };

    REQUIRE_THAT(container, EqualsRange(a) || EqualsRange(b) || EqualsRange(c));
}
```

需要注意的是，虽然任何旧风格 matcher 都可以改写成新风格 matcher，但组合新风格 matcher 的编译开销通常更高。还要注意，旧风格和新风格 matcher 可以任意组合。

> `MatcherGenericBase` 位于 `catch2/matchers/catch_matchers_templated.hpp`

---

[Home](Readme_zh.md#top)
