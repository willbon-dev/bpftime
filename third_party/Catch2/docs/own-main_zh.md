<a id="top"></a>
# 自己提供 main()

**目录**<br>
[让 Catch2 完全接管参数和配置](#let-catch2-take-full-control-of-args-and-config)<br>
[修改 Catch2 配置](#amending-the-catch2-config)<br>
[添加你自己的命令行选项](#adding-your-own-command-line-options)<br>
[版本检测](#version-detection)<br>

最简单的使用 Catch2 的方式，是使用它自带的 `main` 函数，并让它处理命令行参数。这可以通过链接 Catch2Main 库来实现，例如通过 [CMake target](docs/docs/cmake-integration_zh.md#cmake-targets) 或 pkg-config 文件。

如果你想自己提供 `main`，那就应该只链接静态库（target），不包含 main 部分。然后你需要自己编写 `main`，并手动调用 Catch2 测试运行器。

下面是一些关于自己提供 main 时可以做什么的基本示例。

## 让 Catch2 完全接管参数和配置

如果你只需要在 Catch2 运行测试前后执行一些代码，这个方式就很有用。

```cpp
#include <catch2/catch_session.hpp>

int main( int argc, char* argv[] ) {
  // your setup ...

  int result = Catch::Session().run( argc, argv );

  // your clean-up...

  return result;
}
```

_注意，如果你只是想在测试运行前做一些 setup，那么使用[event listeners](event-listeners_zh.md#top) 可能更简单。_

## 修改 Catch2 配置

如果你希望 Catch2 处理命令行参数，但也想通过程序方式修改 Catch2 运行时最终得到的配置，你有两种方式：

```c++
int main( int argc, char* argv[] ) {
  Catch::Session session; // 必须且只能有一个实例

  // 在这里写 session.configData() 会设置默认值
  // 这是推荐的设置方式

  int returnCode = session.applyCommandLine( argc, argv );
  if( returnCode != 0 ) // 表示命令行错误
        return returnCode;

  // 在这里写 session.configData() 或 session.Config()
  // 会覆盖命令行参数
  // 只有在你确实知道自己需要这样做时才这么做

  int numFailed = session.run();

  // 某些 Unix 只使用低 8 位，因此 numFailed 会被限制到 255
  // 这个限制已经应用过了，所以这里直接返回即可
  // 你也可以在这里做任何运行后的清理
  return numFailed;
}
```

如果你想完全掌控配置，就不要调用 `applyCommandLine`。

## 添加你自己的命令行选项

你可以通过组合预先制作好的 CLI parser（名为 Clara），来向 Catch2 添加新的命令行选项。

```cpp
int main( int argc, char* argv[] ) {
  Catch::Session session; // 必须且只能有一个实例

  int height = 0; // 你希望用户能够设置的变量

  // 在 Catch2 的 parser 上再构建一个新的 parser
  using namespace Catch::Clara;
  auto cli
    = session.cli()           // 获取 Catch2 的命令行 parser
    | Opt( height, "height" ) // 将变量绑定到一个新选项，并带提示字符串
        ["-g"]["--height"]    // 该选项响应的名字
        ("how high?");        // 帮助输出中的描述字符串

  // 现在把新的组合 parser 交回 Catch2，让它使用
  session.cli( cli );

  // 让 Catch2（通过 Clara）解析命令行
  int returnCode = session.applyCommandLine( argc, argv );
  if( returnCode != 0 ) // 表示命令行错误
      return returnCode;

  // 如果在命令行中设置了参数，那么此时 height 已经被设置
  if( height > 0 )
      std::cout << "height: " << height << std::endl;

  return session.run();
}
```

更多关于如何使用 Clara parser 的细节，请参阅 [Clara 文档](https://github.com/catchorg/Clara/blob/master/README.md)。

## 版本检测

Catch2 提供了三个宏来表示头文件版本：

* `CATCH_VERSION_MAJOR`
* `CATCH_VERSION_MINOR`
* `CATCH_VERSION_PATCH`

这些宏会展开为一个单独的数字，对应版本号的相应部分。比如，给定单头文件版本 v2.3.4，这些宏分别会展开成 `2`、`3` 和 `4`。

---

[Home](Readme_zh.md#top)
