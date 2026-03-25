<a id="top"></a>
# 字符串转换

**目录**<br>
[std::ostream 的 `operator <<` 重载](#operator--overload-for-stdostream)<br>
[Catch::StringMaker 特化](#catchstringmaker-specialisation)<br>
[Catch::is_range 特化](#catchis_range-specialisation)<br>
[异常](#exceptions)<br>
[枚举](#enums)<br>
[浮点精度](#floating-point-precision)<br>

Catch 需要能够把你在断言和日志表达式中使用的类型转换成字符串，以便用于日志和报告。大多数内置类型或 std 类型都开箱即用，但你可以通过两种方式告诉 Catch 如何把你自己的类型（或其他第三方类型）转换成字符串。

## std::ostream 的 `operator <<` 重载

这是 C++ 中提供字符串转换的标准方式，而且你很可能已经为了其他用途这样做过了。如果你不熟悉这种惯用法，它的形式就是写一个自由函数：

```cpp
std::ostream& operator << ( std::ostream& os, T const& value ) {
    os << convertMyTypeToString( value );
    return os;
}
```

（其中 ```T``` 是你的类型，```convertMyTypeToString``` 是你写入把类型转成可打印形式所需逻辑的地方，它不一定非要是另一个函数。）

你应该把这个函数放在与你的类型相同的命名空间里，或者放在全局命名空间，并且要在包含 Catch 头文件之前声明它。

## Catch::StringMaker 特化
如果你不想提供 `operator <<` 重载，或者你希望为了测试目的以不同方式转换类型，可以为 `Catch::StringMaker<T>` 提供特化：

```cpp
namespace Catch {
    template<>
    struct StringMaker<T> {
        static std::string convert( T const& value ) {
            return convertMyTypeToString( value );
        }
    };
}
```

## Catch::is_range 特化
作为后备方案，Catch 会尝试检测类型是否可以迭代（即 `begin(T)` 和 `end(T)` 是否有效）。如果可以，它就会把它当作一个范围来字符串化。对于某些类型，这可能会导致无限递归，因此可以像这样通过特化 `Catch::is_range` 来禁用：

```cpp
namespace Catch {
    template<>
    struct is_range<T> {
        static const bool value = false;
    };
}
```

## 异常

默认情况下，所有继承自 `std::exception` 的异常都会通过调用 `what()` 方法转换为字符串。对于不继承自 `std::exception` 的异常类型，或者 `what()` 没有返回合适字符串的情况，可以使用 `CATCH_TRANSLATE_EXCEPTION`。这会定义一个接受你的异常类型引用并返回字符串的函数。它可以出现在代码中的任意位置，不必和异常类型在同一个 translation unit 中。例如：

```cpp
CATCH_TRANSLATE_EXCEPTION( MyType const& ex ) {
    return ex.message();
}
```

## 枚举

> Introduced in Catch2 2.8.0.

已经有 `std::ostream` 的 `<<` 重载的枚举，会像预期一样被转换成字符串。
如果你只需要把枚举转换成字符串用于测试报告，那么你也可以像其他类型一样提供 `StringMaker` 特化。
不过，为了方便，Catch 提供了 `REGISTER_ENUM` 辅助宏，它会替你生成 `StringMaker` 特化，代码量很少。
只要提供限定名的枚举名，再跟上所有枚举值即可。

例如：

```cpp
enum class Fruits { Banana, Apple, Mango };

CATCH_REGISTER_ENUM( Fruits, Fruits::Banana, Fruits::Apple, Fruits::Mango )

TEST_CASE() {
    REQUIRE( Fruits::Mango == Fruits::Apple );
}
```

... 或者枚举在命名空间里：
```cpp
namespace Bikeshed {
    enum class Colours { Red, Green, Blue };
}

// 重要！这个宏必须出现在顶层作用域，不能放进命名空间里
// 你可以完全限定名称，或者如果你愿意也可以使用 using
CATCH_REGISTER_ENUM( Bikeshed::Colours,
    Bikeshed::Colours::Red,
    Bikeshed::Colours::Green,
    Bikeshed::Colours::Blue )

TEST_CASE() {
    REQUIRE( Bikeshed::Colours::Red == Bikeshed::Colours::Blue );
}
```

## 浮点精度

> [Introduced](https://github.com/catchorg/Catch2/issues/1614) in Catch2 2.8.0.

Catch 为 `float` 和 `double` 都提供了内建的 `StringMaker` 特化。默认情况下，它会使用我们认为比较合理的精度，但你可以通过修改 `StringMaker` 特化中的 `precision` 静态变量来自定义，例如：

```cpp
        Catch::StringMaker<float>::precision = 15;
        const float testFloat1 = 1.12345678901234567899f;
        const float testFloat2 = 1.12345678991234567899f;
        REQUIRE(testFloat1 == testFloat2);
```

这个断言会失败，并把 `testFloat1` 和 `testFloat2` 以 15 位小数打印出来。

---

[Home](Readme_zh.md#top)
