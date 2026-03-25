<a id="top"></a>
# Test fixture

## 定义测试 fixture

虽然 Catch 允许你通过[在测试用例中使用 sections](test-cases-and-sections_zh.md)把测试分组，但有时用更传统的 test fixture 来组织它们也会很方便。Catch 同样完整支持这一点。你可以把 test fixture 定义成一个简单的结构：

```c++
class UniqueTestsFixture {
  private:
   static int uniqueID;
  protected:
   DBConnection conn;
  public:
   UniqueTestsFixture() : conn(DBConnection::createConnection("myDB")) {
   }
  protected:
   int getID() {
     return ++uniqueID;
   }
 };

 int UniqueTestsFixture::uniqueID = 0;

 TEST_CASE_METHOD(UniqueTestsFixture, "Create Employee/No Name", "[create]") {
   REQUIRE_THROWS(conn.executeSQL("INSERT INTO employee (id, name) VALUES (?, ?)", getID(), ""));
 }
 TEST_CASE_METHOD(UniqueTestsFixture, "Create Employee/Normal", "[create]") {
   REQUIRE(conn.executeSQL("INSERT INTO employee (id, name) VALUES (?, ?)", getID(), "Joe Bloggs"));
 }
```

这里的两个测试用例会创建 `UniqueTestsFixture` 的独特派生类，因此可以访问 `getID()` 受保护的方法和 `conn` 成员变量。这样可以确保两个测试用例都通过同一种方式创建 `DBConnection`（DRY 原则），并且创建的任何 ID 都是唯一的，因此测试执行顺序不会影响结果。

Catch2 还提供了 `TEMPLATE_TEST_CASE_METHOD` 和 `TEMPLATE_PRODUCT_TEST_CASE_METHOD`，可以和模板 fixture 以及模板模板 fixture 一起使用，从而对多种不同类型执行测试。与 `TEST_CASE_METHOD` 不同，`TEMPLATE_TEST_CASE_METHOD` 和 `TEMPLATE_PRODUCT_TEST_CASE_METHOD` 都要求 tag 规范不能为空，因为后面还会跟着更多宏参数。

另外还要注意，由于 C++ 预处理器的限制，如果你想指定一个带多个模板参数的类型，需要把它括在括号里，例如 `std::map<int, std::string>` 需要写成 `(std::map<int, std::string>)`。对于 `TEMPLATE_PRODUCT_TEST_CASE_METHOD`，如果类型列表中的某一项本身包含多个类型，还需要再加一层括号，例如 `(std::map, std::pair)` 和 `((int, float), (char, double))`。

示例：
```cpp
template< typename T >
struct Template_Fixture {
    Template_Fixture(): m_a(1) {}

    T m_a;
};

TEMPLATE_TEST_CASE_METHOD(Template_Fixture,
                          "A TEMPLATE_TEST_CASE_METHOD based test run that succeeds",
                          "[class][template]",
                          int, float, double) {
    REQUIRE( Template_Fixture<TestType>::m_a == 1 );
}

template<typename T>
struct Template_Template_Fixture {
    Template_Template_Fixture() {}

    T m_a;
};

template<typename T>
struct Foo_class {
    size_t size() {
        return 0;
    }
};

TEMPLATE_PRODUCT_TEST_CASE_METHOD(Template_Template_Fixture,
                                  "A TEMPLATE_PRODUCT_TEST_CASE_METHOD based test succeeds",
                                  "[class][template]",
                                  (Foo_class, std::vector),
                                  int) {
    REQUIRE( Template_Template_Fixture<TestType>::m_a.size() == 0 );
}
```

_虽然在单个 `TEMPLATE_TEST_CASE_METHOD` 或 `TEMPLATE_PRODUCT_TEST_CASE_METHOD` 中可指定的类型数量有上限，但这个上限非常高，实际中一般不会碰到。_

## 基于签名的参数化 test fixture

> [Introduced](https://github.com/catchorg/Catch2/issues/1609) in Catch2 2.8.0.

Catch2 还提供 `TEMPLATE_TEST_CASE_METHOD_SIG` 和 `TEMPLATE_PRODUCT_TEST_CASE_METHOD_SIG`，用于支持带非类型模板参数的 fixture。这些测试用例的工作方式与 `TEMPLATE_TEST_CASE_METHOD` 和 `TEMPLATE_PRODUCT_TEST_CASE_METHOD` 类似，只是额外提供了一个 [signature](test-cases-and-sections_zh.md#signature-based-parametrised-test-cases) 的位置参数。

示例：
```cpp
template <int V>
struct Nttp_Fixture{
    int value = V;
};

TEMPLATE_TEST_CASE_METHOD_SIG(
    Nttp_Fixture,
    "A TEMPLATE_TEST_CASE_METHOD_SIG based test run that succeeds",
    "[class][template][nttp]",
    ((int V), V),
    1, 3, 6) {
    REQUIRE(Nttp_Fixture<V>::value > 0);
}

template<typename T>
struct Template_Fixture_2 {
    Template_Fixture_2() {}

    T m_a;
};

template< typename T, size_t V>
struct Template_Foo_2 {
    size_t size() { return V; }
};

TEMPLATE_PRODUCT_TEST_CASE_METHOD_SIG(
    Template_Fixture_2,
    "A TEMPLATE_PRODUCT_TEST_CASE_METHOD_SIG based test run that succeeds",
    "[class][template][product][nttp]",
    ((typename T, size_t S), T, S),
    (std::array, Template_Foo_2),
    ((int,2), (float,6))) {
    REQUIRE(Template_Fixture_2<TestType>{}.m_a.size() >= 2);
}
```

## 在模板类型列表中指定类型的 template fixture

Catch2 还提供 `TEMPLATE_LIST_TEST_CASE_METHOD`，用于支持在模板类型列表中指定类型的 template fixture，例如 `std::tuple`、`boost::mpl::list` 或 `boost::mp11::mp_list`。这个测试用例和 `TEMPLATE_TEST_CASE_METHOD` 的工作方式相同，唯一的区别是类型来源不同。这让你可以在多个测试用例中复用同一个模板类型列表。

示例：
```cpp
using MyTypes = std::tuple<int, char, double>;
TEMPLATE_LIST_TEST_CASE_METHOD(Template_Fixture,
                               "Template test case method with test types specified inside std::tuple",
                               "[class][template][list]",
                               MyTypes) {
    REQUIRE( Template_Fixture<TestType>::m_a == 1 );
}
```

---

[Home](Readme_zh.md#top)
