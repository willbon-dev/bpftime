<a id="top"></a>
# 为什么我们还需要另一个 C++ 测试框架？

问得好。C++ 领域已经有不少成熟框架，包括但不限于 [Google Test](http://code.google.com/p/googletest/)、[Boost.Test](http://www.boost.org/doc/libs/1_49_0/libs/test/doc/html/index.html)、[CppUnit](http://sourceforge.net/apps/mediawiki/cppunit/index.php?title=Main_Page)、[Cute](http://www.cute-test.com)，以及[更多、更多的框架](http://en.wikipedia.org/wiki/List_of_unit_testing_frameworks#C.2B.2B)。

那么 Catch2 带来了什么不同之处呢？当然，除了这个朗朗上口的名字之外。

## 核心特性

* 上手非常快也非常简单。只要下载两个文件，把它们加入项目就可以开始了。
* 没有外部依赖。只要你能编译 C++14，并且有 C++ 标准库可用即可。
* 将测试用例写成会自动注册的函数（如果你愿意，也可以写成方法）。
* 将测试用例分成多个 section，每个 section 独立运行（因此不需要 fixture）。
* 同时支持 BDD 风格的 Given-When-Then sections 和传统单元测试用例。
* 比较时只有一个核心断言宏。比较使用标准 C/C++ 运算符，但完整表达式会被拆解并记录 lhs 和 rhs 的值。
* 测试可以使用自由格式字符串命名，不必把名字塞进合法标识符里。

## 其他核心特性

* 测试可以打标签，方便临时运行一组测试。
* 在常见平台上，失败时可以选择性地让调试器中断。
* 输出通过模块化的 reporter 对象完成。内置了基础文本和 XML reporter，也可以很容易添加自定义 reporter。
* 支持 JUnit XML 输出，便于与 CI 服务器等第三方工具集成。
* 提供默认的 main()，但你也可以自己提供一个，从而获得完全控制权（例如集成到自己的测试运行器 GUI 中）。
* 提供命令行解析器，即使你选择自己提供 main()，它仍然可以使用。
* 额外的断言宏可以报告失败，但不会中止测试用例。
* 提供一组不错的浮点数比较工具（`Catch::Approx` 以及完整的 matchers 集）。
* 内部宏和友好宏彼此隔离，因此可以管理命名冲突。
* 数据生成器（数据驱动测试支持）
* 用于测试复杂属性的 Hamcrest 风格 Matchers
* 支持微基准测试

## 还有谁在使用 Catch2？

很多人。根据 2021 年 JetBrains C++ 生态调查，大约 11% 的 C++ 程序员在单元测试中使用 Catch2，使其成为第二受欢迎的单元测试框架。

你也可以看看[使用 Catch2 的开源项目](opensource-users_zh.md#top)或[商业用户列表](commercial-users_zh.md#top)，了解还有谁在使用 Catch2。

---

想进一步体验 Catch2 的实际使用方式，请查看[教程](tutorial_zh.md#top)。

---

[Home](Readme_zh.md#top)
