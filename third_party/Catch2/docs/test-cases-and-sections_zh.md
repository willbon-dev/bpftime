<a id="top"></a>
# 测试用例和 sections

**目录**<br>
[标签](#tags)<br>
[标签别名](#tag-aliases)<br>
[BDD 风格测试用例](#bdd-style-test-cases)<br>
[类型参数化测试用例](#type-parametrised-test-cases)<br>
[基于签名的参数化测试用例](#signature-based-parametrised-test-cases)<br>

虽然 Catch 完整支持传统的 xUnit 风格、基于类 fixture 并包含测试方法的写法，但这不是推荐风格。

相反，Catch 提供了一种强大的机制，可以在测试用例内部嵌套测试用例 section。想了解更详细的讨论，请看[教程](tutorial_zh.md#test-cases-and-sections)。

测试用例和 section 在实践中非常容易使用：

* **TEST_CASE(** _test name_ \[, _tags_ \] **)**
* **SECTION(** _section name_, \[, _section description_ \] **)**

_test name_ 和 _section name_ 都是自由格式的、带引号的字符串。
可选的 _tags_ 参数是一个带引号的字符串，包含一个或多个用方括号包起来的标签，下面会介绍。
_section description_ 可以用于提供 section 的长描述，同时保留较短的 _section name_ 以便在 [`-c` 命令行参数](docs/docs/command-line_zh.md#specify-the-section-to-run) 中使用。

**测试名称和标签的组合在 Catch2 可执行文件内部必须唯一。**

示例请看 [Tutorial](tutorial_zh.md#top)

## 标签

标签允许为测试用例关联任意数量的附加字符串。测试用例可以按标签选择（用于运行或仅用于列出），也可以通过组合多个标签的表达式来选择。最基本层面上，它们提供了一种把多个相关测试分组的简单方式。

例如，给定如下测试用例：

    TEST_CASE( "A", "[widget]" ) { /* ... */ }
    TEST_CASE( "B", "[widget]" ) { /* ... */ }
    TEST_CASE( "C", "[gadget]" ) { /* ... */ }
    TEST_CASE( "D", "[widget][gadget]" ) { /* ... */ }

标签表达式 ```"[widget]"``` 会选择 A、B 和 D。```"[gadget]"``` 会选择 C 和 D。```"[widget][gadget]"``` 只选择 D，而 ```"[widget],[gadget]"``` 会选择全部四个测试用例。

关于命令行选择的更多细节，请看[命令行文档](docs/docs/command-line_zh.md#specifying-which-tests-to-run)。

标签名不区分大小写，并且可以包含任何 ASCII 字符。
这意味着标签 `[tag with spaces]` 和 `[I said "good day"]`
都可以使用并被过滤。不过，转义并不受支持，因此 `[\]]` 不是合法标签。

同一个标签可以在单个测试用例中出现多次，但相同标签的多个实例只会保留一个。保留哪一个在功能上是随机的。

### 特殊标签

所有以非字母数字字符开头的标签名都保留给 Catch 使用。Catch 定义了一些“特殊”标签，它们对测试运行器本身有意义。这些特殊标签都以符号字符开头。下面是当前定义的特殊标签及其含义。

* `[.]` - 让测试用例从默认列表中被跳过（也就是当没有通过标签表达式或名称通配符显式选择测试用例时）。隐藏标签常常会和另一个用户标签组合使用，例如 `[.][integration]`，这样所有集成测试都会被默认运行排除，但可以通过命令行传入 `[integration]` 来运行。作为快捷方式，你也可以简单地在自己的用户标签前加上 `.`，例如 `[.integration]`。

* `[!throws]` - 让 Catch 知道这个测试即使成功也很可能抛出异常。这会在使用 `-e` 或 `--nothrow` 运行时把该测试排除掉。

* `[!mayfail]` - 如果任意断言失败，不让测试失败（但仍然会报告）。这对于标记一个进行中的工作，或者一个你暂时不想立即修复但又想在测试中跟踪的已知问题很有用。

* `[!shouldfail]` - 类似 `[!mayfail]`，但如果测试 _通过_，它反而会让测试 _失败_。这在你想获知某些意外修复，或者第三方修复时很有用。

* `[!nonportable]` - 表示行为可能会因平台或编译器而异。

* `[#<filename>]` - 当你使用 [`-#` 或 `--filenames-as-tags`](docs/docs/command-line_zh.md#filenames-as-tags) 运行 Catch2 时，这些标签会被添加到测试用例上。

* `[@<alias>]` - 标签别名都以 `@` 开头（见下文）。

* `[!benchmark]` - 这个测试用例其实是一个 benchmark。当前它只用于默认隐藏测试用例，以避免执行时间成本。

## 标签别名

在标签表达式和带通配符的测试名称之间（以及两者的组合）可以构造出相当复杂的模式，用来指定运行哪些测试用例。如果某个复杂模式经常使用，那么创建它的别名会很方便。可以在代码中用下面的形式实现：

    CATCH_REGISTER_TAG_ALIAS( <alias string>, <tag expression> )

别名必须以 `@` 字符开头。一个标签别名的例子是：

    CATCH_REGISTER_TAG_ALIAS( "[@nhf]", "[failing]~[.]" )

这样，当在命令行使用 `[@nhf]` 时，它会匹配所有带有 `[failing]` 标签、但同时又不是隐藏测试的测试。

## BDD 风格测试用例

除了 Catch 对经典风格测试用例的处理之外，Catch 还支持一种替代语法，允许把测试写成“可执行规格说明”（这也是行为驱动开发 [Behaviour Driven Development](http://dannorth.net/introducing-bdd/) 的早期目标之一）。这组宏会映射到 ```TEST_CASE``` 和 ```SECTION```，并附带一些内部支持来让它们更好用。

* **SCENARIO(** _scenario name_ \[, _tags_ \] **)**

这个宏映射到 ```TEST_CASE```，行为也一样，只不过测试用例名称会加上前缀 `"Scenario: "`

* **GIVEN(** _something_ **)**
* **WHEN(** _something_ **)**
* **THEN(** _something_ **)**

这些宏映射到 ```SECTION```，区别在于 section 名称会是加上前缀 `"given: "`、`"when: "` 或 `"then: "` 的 _something_ 文本。这些宏也映射到 AAA 或 A<sup>3</sup> 测试模式（分别代表 [Assemble-Activate-Assert](http://wiki.c2.com/?AssembleActivateAssert) 或 [Arrange-Act-Assert](http://wiki.c2.com/?ArrangeActAssert)），在这种上下文里，这些宏既能作为代码文档，也能在报告中体现测试用例的这些部分，而不需要额外注释或代码。

从语义上讲，一个 `GIVEN` 子句中可以有多个 _独立_ 的 `WHEN` 子句。这允许测试拥有一组“given”对象，并在多个 `WHEN` 子句中以不同方式对这些对象做子测试，而无需重复 `GIVEN` 子句中的初始化。当存在 _依赖_ 子句时，例如一个必须在前一个 `WHEN` 子句执行并验证之后才发生的第二个 `WHEN` 子句，还有额外的 `AND_` 前缀宏：

* **AND_GIVEN(** _something_ **)**
* **AND_WHEN(** _something_ **)**
* **AND_THEN(** _something_ **)**

这些用于把 ```GIVEN```、```WHEN``` 和 ```THEN``` 串联起来。`AND_*` 子句会放在它所依赖的子句 _内部_。可以存在多个彼此独立、但都依赖同一个外层子句的子句。
```cpp
SCENARIO( "vector can be sized and resized" ) {
    GIVEN( "An empty vector" ) {
        auto v = std::vector<std::string>{};

        // 验证 GIVEN 子句的假设
        THEN( "The size and capacity start at 0" ) {
            REQUIRE( v.size() == 0 );
            REQUIRE( v.capacity() == 0 );
        }

        // 验证 GIVEN 对象的一种用法
        WHEN( "push_back() is called" ) {
            v.push_back("hullo");

            THEN( "The size changes" ) {
                REQUIRE( v.size() == 1 );
                REQUIRE( v.capacity() >= 1 );
            }
        }
    }
}
```

这段代码会导致场景运行两次：
```
Scenario : vector can be sized and resized
  Given  : An empty vector
  Then   : The size and capacity start at 0

Scenario : vector can be sized and resized
  Given  : An empty vector
  When   : push_back() is called
  Then   : The size changes
```

另请参阅 [godbolt 上的可运行示例](https://godbolt.org/z/eY5a64r99)，其中还有一个更复杂（而且会失败）的例子。

> `AND_GIVEN` 是在 Catch2 2.4.0 中[引入](https://github.com/catchorg/Catch2/issues/1360)的。

当使用这些宏时，console reporter 能识别它们，并格式化测试用例头部，使 Givens、Whens 和 Thens 对齐，以提升可读性。

除了额外的前缀和 console reporter 的格式化之外，这些宏的行为与 ```TEST_CASE``` 和 ```SECTION``` 完全相同。因此，并没有什么机制会强制这些宏按正确顺序使用，这要靠程序员自己保证！

## 类型参数化测试用例

除了 `TEST_CASE` 之外，Catch2 还支持按类型参数化的测试用例，形式为 `TEMPLATE_TEST_CASE`、`TEMPLATE_PRODUCT_TEST_CASE` 和 `TEMPLATE_LIST_TEST_CASE`。这些宏定义在 `catch_template_test_macros.hpp` 头文件中，因此编译下面的示例代码时还需要
`#include <catch2/catch_template_test_macros.hpp>`。

* **TEMPLATE_TEST_CASE(** _test name_ , _tags_,  _type1_, _type2_, ..., _typen_ **)**

> [Introduced](https://github.com/catchorg/Catch2/issues/1437) in Catch2 2.5.0.

_test name_ 和 _tag_ 与 `TEST_CASE` 中完全相同，区别在于必须提供 tag 字符串（不过它可以是空的）。_type1_ 到 _typen_ 是该测试用例应该运行的类型列表，而在测试代码内部，当前类型可以通过 `TestType` 这个类型名访问。

由于 C++ 预处理器的限制，如果你想指定一个带多个模板参数的类型，需要把它放在括号里，例如 `std::map<int, std::string>` 需要传成 `(std::map<int, std::string>)`。

示例：
```cpp
TEMPLATE_TEST_CASE( "vectors can be sized and resized", "[vector][template]", int, std::string, (std::tuple<int,float>) ) {

    std::vector<TestType> v( 5 );

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

        SECTION( "We can use the 'swap trick' to reset the capacity" ) {
            std::vector<TestType> empty;
            empty.swap( v );

            REQUIRE( v.capacity() == 0 );
        }
    }
```

* **TEMPLATE_PRODUCT_TEST_CASE(** _test name_ , _tags_, (_template-type1_, _template-type2_, ..., _template-typen_), (_template-arg1_, _template-arg2_, ..., _template-argm_) **)**

> [Introduced](https://github.com/catchorg/Catch2/issues/1468) in Catch2 2.6.0.

_template-type1_ 到 _template-typen_ 是模板模板类型列表，它们会和 _template-arg1_ 到 _template-argm_ 中的每一项组合，得到 _n * m_ 个测试用例。在测试用例内部，结果类型通过 `TestType` 这个名字可用。

如果想把多个类型作为单个 _template-type_ 或 _template-arg_，就必须再额外加一层括号，例如 `((int, float), (char, double))` 表示 2 个 template-arg，每个都包含 2 个具体类型（分别是 `int`、`float` 以及 `char`、`double`）。如果你在 _template-types_ 或 _template-args_ 中只指定一个类型，也可以省略外层括号。

示例：
```cpp
template< typename T>
struct Foo {
    size_t size() {
        return 0;
    }
};

TEMPLATE_PRODUCT_TEST_CASE("A Template product test case", "[template][product]", (std::vector, Foo), (int, float)) {
    TestType x;
    REQUIRE(x.size() == 0);
}
```

你也可以在 _template-arg_ 包中使用不同的元数：
```cpp
TEMPLATE_PRODUCT_TEST_CASE("Product with differing arities", "[template][product]", std::tuple, (int, (int, double), (int, double, float))) {
    TestType x;
    REQUIRE(std::tuple_size<TestType>::value >= 1);
}
```

* **TEMPLATE_LIST_TEST_CASE(** _test name_, _tags_, _type list_ **)**

> [Introduced](https://github.com/catchorg/Catch2/issues/1627) in Catch2 2.9.0.

_type list_ 是一个通用类型列表，测试用例会基于它实例化。类型列表可以是 `std::tuple`、`boost::mpl::list`、`boost::mp11::mp_list`，或者任何具有 `template <typename...>` 签名的类型。

这让你可以在多个测试用例中复用同一个 _type list_。

示例：
```cpp
using MyTypes = std::tuple<int, char, float>;
TEMPLATE_LIST_TEST_CASE("Template test case with test types specified inside std::tuple", "[template][list]", MyTypes)
{
    REQUIRE(sizeof(TestType) > 0);
}
```

## 基于签名的参数化测试用例

> [Introduced](https://github.com/catchorg/Catch2/issues/1609) in Catch2 2.8.0.

除了[类型参数化测试用例](#type-parametrised-test-cases)之外，Catch2 还支持基于签名的参数化测试用例，形式为 `TEMPLATE_TEST_CASE_SIG` 和 `TEMPLATE_PRODUCT_TEST_CASE_SIG`。这些测试用例的语法与[类型参数化测试用例](#type-parametrised-test-cases)类似，只是额外增加了一个位置参数来指定 signature。这些宏定义在 `catch_template_test_macros.hpp` 头文件中，因此编译下面的示例代码时也需要 `#include <catch2/catch_template_test_macros.hpp>`。

### Signature

Signature 必须遵守一些严格规则，测试用例才能正常工作：
* 带多个模板参数的 signature，例如 `typename T, size_t S`，在测试用例声明中必须写成 `((typename T, size_t S), T, S)`
* 带可变参数模板参数的 signature，例如 `typename T, size_t S, typename...Ts`，在测试用例声明中必须写成 `((typename T, size_t S, typename...Ts), T, S, Ts...)`
* 带单个非类型模板参数的 signature，例如 `int V`，在测试用例声明中必须写成 `((int V), V)`
* 带单个类型模板参数的 signature，例如 `typename T`，不应这样使用，因为这实际上就是 `TEMPLATE_TEST_CASE`

目前 Catch2 的 signature 最多支持 11 个模板参数

### 示例

* **TEMPLATE_TEST_CASE_SIG(** _test name_ , _tags_,  _signature_, _type1_, _type2_, ..., _typen_ **)**

在 `TEMPLATE_TEST_CASE_SIG` 测试用例内部，你可以使用在 _signature_ 中定义的模板参数名。

```cpp
TEMPLATE_TEST_CASE_SIG("TemplateTestSig: arrays can be created from NTTP arguments", "[vector][template][nttp]",
  ((typename T, int V), T, V), (int,5), (float,4), (std::string,15), ((std::tuple<int, float>), 6)) {

    std::array<T, V> v;
    REQUIRE(v.size() > 1);
}
```

* **TEMPLATE_PRODUCT_TEST_CASE_SIG(** _test name_ , _tags_, _signature_, (_template-type1_, _template-type2_, ..., _template-typen_), (_template-arg1_, _template-arg2_, ..., _template-argm_) **)**

```cpp

template<typename T, size_t S>
struct Bar {
    size_t size() { return S; }
};

TEMPLATE_PRODUCT_TEST_CASE_SIG("A Template product test case with array signature", "[template][product][nttp]", ((typename T, size_t S), T, S), (std::array, Bar), ((int, 9), (float, 42))) {
    TestType x;
    REQUIRE(x.size() > 0);
}
```

---

[Home](Readme_zh.md#top)
