<a id="top"></a>
# 其他宏

本页用于记录那些没有在别处文档中说明的宏。当前这些宏分为两类：“与断言相关的宏”和“与测试用例相关的宏”。

## 与断言相关的宏

* `CHECKED_IF` 和 `CHECKED_ELSE`

`CHECKED_IF( expr )` 是 `if` 的替代品，它还会把 Catch2 的字符串化机制应用到 _expr_ 上并记录结果。和 `if` 一样，只有当表达式求值为 `true` 时，`CHECKED_IF` 后面的代码块才会进入。`CHECKED_ELSE( expr )` 的作用类似，但只有当 _expr_ 求值为 `false` 时，代码块才会进入。

> `CHECKED_X` 宏在 Catch2 3.0.1 中被修改为不再计为失败。

示例：
```cpp
int a = ...;
int b = ...;
CHECKED_IF( a == b ) {
    // 当 a == b 时进入此块
} CHECKED_ELSE ( a == b ) {
    // 当 a != b 时进入此块
}
```

* `CHECK_NOFAIL`

`CHECK_NOFAIL( expr )` 是 `CHECK` 的一个变体，即使 _expr_ 求值为 `false` 也不会让测试用例失败。这对于检查某些假设很有用，即使该假设被违反，测试也不一定必须失败。

示例输出：
```
main.cpp:6:
FAILED - but was ok:
  CHECK_NOFAIL( 1 == 2 )

main.cpp:7:
PASSED:
  CHECK( 2 == 2 )
```

* `SUCCEED`

`SUCCEED( msg )` 大体上等价于 `INFO( msg ); REQUIRE( true );`。换句话说，`SUCCEED` 适用于“只要执行到某一行，就代表测试成功”的场景。

示例用法：
```cpp
TEST_CASE( "SUCCEED showcase" ) {
    int I = 1;
    SUCCEED( "I is " << I );
}
```

* `STATIC_REQUIRE` 和 `STATIC_CHECK`

> `STATIC_REQUIRE` 在 Catch2 2.4.2 中被[引入](https://github.com/catchorg/Catch2/issues/1362)。

`STATIC_REQUIRE( expr )` 的用法和 `static_assert` 类似，但它还会向 Catch2 注册成功结果，因此在运行时也会报告为成功。通过在包含 Catch2 头文件之前定义 `CATCH_CONFIG_RUNTIME_STATIC_REQUIRE`，整个检查还可以推迟到运行时。

示例：
```cpp
TEST_CASE("STATIC_REQUIRE showcase", "[traits]") {
    STATIC_REQUIRE( std::is_void<void>::value );
    STATIC_REQUIRE_FALSE( std::is_void<int>::value );
}
```

> `STATIC_CHECK` 在 Catch2 3.0.1 中被[引入](https://github.com/catchorg/Catch2/pull/2318)。

`STATIC_CHECK( expr )` 与 `STATIC_REQUIRE( expr )` 等价，不同之处在于当定义了 `CATCH_CONFIG_RUNTIME_STATIC_REQUIRE` 时，它会变成 `CHECK`，而不是 `REQUIRE`。

示例：
```cpp
TEST_CASE("STATIC_CHECK showcase", "[traits]") {
    STATIC_CHECK( std::is_void<void>::value );
    STATIC_CHECK_FALSE( std::is_void<int>::value );
}
```

## 与测试用例相关的宏

* `METHOD_AS_TEST_CASE`

`METHOD_AS_TEST_CASE( member-function-pointer, description )` 允许你把类的成员函数注册为一个 Catch2 测试用例。这样注册的每个方法都会由独立实例化的类来执行。

```cpp
class TestClass {
    std::string s;

public:
    TestClass()
        :s( "hello" )
    {}

    void testCase() {
        REQUIRE( s == "hello" );
    }
};


METHOD_AS_TEST_CASE( TestClass::testCase, "Use class's method as a test case", "[class]" )
```

* `REGISTER_TEST_CASE`

`REGISTER_TEST_CASE( function, description )` 允许你把一个 `function` 注册为测试用例。这个函数必须具有 `void()` 签名，description 中可以同时包含名称和标签。

示例：
```cpp
REGISTER_TEST_CASE( someFunction, "ManuallyRegistered", "[tags]" );
```

_注意，注册仍然必须发生在 Catch2 session 启动之前。这意味着它要么需要在全局构造函数中完成，要么需要在用户自己的 main 中、Catch2 session 创建之前完成。_

* `DYNAMIC_SECTION`

> Introduced in Catch2 2.3.0.

`DYNAMIC_SECTION` 是一种 `SECTION`，用户可以使用 `operator<<` 来为该 section 创建最终名称。这在比如 generator 或者在循环中动态创建 `SECTION` 时会很有用。

示例：
```cpp
TEST_CASE( "looped SECTION tests" ) {
    int a = 1;

    for( int b = 0; b < 10; ++b ) {
        DYNAMIC_SECTION( "b is currently: " << b ) {
            CHECK( b > a );
        }
    }
}
```
