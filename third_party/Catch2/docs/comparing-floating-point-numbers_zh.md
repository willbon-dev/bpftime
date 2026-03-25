<a id="top"></a>
# 使用 Catch2 比较浮点数

如果你对浮点数不够熟悉，它们可能会很反直觉。这一点也适用于浮点数的（不）相等比较。

本页假设你对浮点数以及不同类型比较的含义已经有一定理解，并且只介绍 Catch2 提供了哪些功能来帮助你比较浮点数。如果你还没有这些基础知识，我们建议你先学习一下浮点数及其比较方式，例如[阅读这篇博客](https://codingnest.com/the-little-things-comparing-floating-point-numbers/)。

## 浮点数 matcher

```
#include <catch2/matchers/catch_matchers_floating_point.hpp>
```

[Matchers](docs/docs/matchers_zh.md#top) 是 Catch2 中比较浮点数的首选方式。我们提供了 3 种：

* `WithinAbs(double target, double margin)`，
* `WithinRel(FloatingPoint target, FloatingPoint eps)`，以及
* `WithinULP(FloatingPoint target, uint64_t maxUlpDiff)`。

> `WithinRel` matcher 是在 Catch2 2.10.0 中引入的

和所有 matcher 一样，你可以把多个浮点数 matcher 组合在一个断言里。例如，如果要检查某个计算结果与已知正确值相差不超过 0.1%，或者足够接近 0（精确到小数点后 5 位），我们可以写成：

```cpp
    REQUIRE_THAT( computation(input),
        Catch::Matchers::WithinRel(expected, 0.001)
     || Catch::Matchers::WithinAbs(0, 0.000001) );
```

### WithinAbs

`WithinAbs` 会创建一个 matcher，接受与 `target` 的差值小于等于 `margin` 的浮点数。由于 `float` 可以转换成 `double` 而不损失精度，因此这里只有 `double` 重载。

```cpp
REQUIRE_THAT(1.0, WithinAbs(1.2, 0.2));
REQUIRE_THAT(0.f, !WithinAbs(1.0, 0.5));
// 注意，对 WithinAbs 而言 infinity == infinity
REQUIRE_THAT(INFINITY, WithinAbs(INFINITY, 0));
```

### WithinRel

`WithinRel` 会创建一个 matcher，接受与 `target` _近似相等_、容差为 `eps` 的浮点数。具体来说，当
`|arg - target| <= eps * max(|arg|, |target|)` 时，它就会匹配。如果你没有指定 `eps`，默认使用 `std::numeric_limits<FloatingPoint>::epsilon * 100`。

```cpp
// 注意，WithinRel 的比较是对称的，不像 Approx。
REQUIRE_THAT(1.0, WithinRel(1.1, 0.1));
REQUIRE_THAT(1.1, WithinRel(1.0, 0.1));
// 注意，对 WithinRel 而言 infinity == infinity
REQUIRE_THAT(INFINITY, WithinRel(INFINITY));
```

### WithinULP

`WithinULP` 会创建一个 matcher，接受与 `target` 值相差不超过 `maxUlpDiff`
[ULP](https://en.wikipedia.org/wiki/Unit_in_the_last_place) 的浮点数。简单来说，这意味着匹配值和 `target` 之间最多只有 `maxUlpDiff - 1` 个可表示浮点数。

在 Catch2 中使用 ULP matcher 时，需要记住 Catch2 对 ULP 距离的解释与 `std::nextafter` 等函数略有不同。

Catch2 的 ULP 计算满足以下关系：
  * `ulpDistance(-x, x) == 2 * ulpDistance(x, 0)`
  * `ulpDistance(-0, 0) == 0`（由上式得到）
  * `ulpDistance(DBL_MAX, INFINITY) == 1`
  * `ulpDistancE(NaN, x) == infinity`

**重要**：`WithinULP` matcher 要求平台对浮点数使用 [IEEE-754](https://en.wikipedia.org/wiki/IEEE_754) 表示。

```cpp
REQUIRE_THAT( -0.f, WithinULP( 0.f, 0 ) );
```

## `Approx`

```
#include <catch2/catch_approx.hpp>
```

**我们强烈不建议在新代码中使用 `Approx`。**
你应该改用浮点数 matcher。

Catch2 还提供了另一种处理浮点数比较的方式：`Approx`。它是一个带重载比较运算符的特殊类型，可以在标准断言中使用，例如：

```cpp
REQUIRE(0.99999 == Catch::Approx(1));
```

`Approx` 支持四种比较运算符：`==`、`!=`、`<=`、`>=`，也可以与基于 `double` 的强类型一起使用。它可以通过三个自定义点支持相对比较和 margin 比较。注意，这里的语义始终是 _或_：只要相对比较或绝对 margin 比较有一个通过，整个比较就通过。

`Approx` 的缺点在于，它有一些问题，如果不破坏向后兼容，就无法修复。因为 Catch2 还提供了完整的 matcher 集来实现不同的浮点数比较方法，`Approx` 就保持原样，被视为已废弃，新代码中不应再使用。

这些问题包括：
  * 所有内部计算都在 `double` 中完成，因此如果输入是 `float`，结果会有些许不同。
  * `Approx` 的相对 margin 比较不是对称的。这意味着 `Approx( 10 ).epsilon(0.1) != 11.1`，但 `Approx( 11.1 ).epsilon(0.1) == 10`。
  * 默认情况下，`Approx` 只使用相对 margin 比较。这意味着 `Approx(0) == X` 只有在 `X == 0` 时才通过。

### Approx 细节

如果你仍然想/需要了解更多关于 `Approx` 的内容，请继续往下看。

Catch2 为 `Approx` 提供了一个 UDL：`_a`。它位于 `Catch::literals` 命名空间中，可以这样使用：

```cpp
using namespace Catch::literals;
REQUIRE( performComputation() == 2.1_a );
```

`Approx` 有三个比较自定义点：

* **epsilon** - epsilon 设置一个系数，结果在被拒绝之前可以与 `Approx` 的值相差这么多。
_默认值为 `std::numeric_limits<float>::epsilon()*100`。_

```cpp
Approx target = Approx(100).epsilon(0.01);
100.0 == target; // 显然为 true
200.0 == target; // 显然仍然为 false
100.5 == target; // 为 true，因为我们允许最多 1% 的差异
```

* **margin** - margin 设置一个绝对值，结果在被拒绝之前可以与 `Approx` 的值相差这么多。
_默认值为 `0.0`。_

```cpp
Approx target = Approx(100).margin(5);
100.0 == target; // 显然为 true
200.0 == target; // 显然仍然为 false
104.0 == target; // 为 true，因为我们允许绝对差异最多 5
```

* **scale** - scale 用于改变 `Approx` 在相对检查中的量级。
_默认值为 `0.0`。_

Scale 在结果的计算尺度与实际结果使用的尺度不同的时候会很有用。计算允许的相对 margin 时，会把 `Approx` 的 scale 加到 `Approx` 的值上。

---

[Home](Readme_zh.md#top)
