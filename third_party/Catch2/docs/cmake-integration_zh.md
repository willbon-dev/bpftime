<a id="top"></a>
# CMake 集成

**目录**<br>
[CMake targets](#cmake-targets)<br>
[自动注册测试](#automatic-test-registration)<br>
[CMake 项目选项](#cmake-project-options)<br>
[`CATCH_CONFIG_*` 在 CMake 中的自定义选项](#catch_config_-customization-options-in-cmake)<br>
[从 git 仓库安装 Catch2](#installing-catch2-from-git-repository)<br>
[从 vcpkg 安装 Catch2](#installing-catch2-from-vcpkg)<br>

由于我们用 CMake 构建 Catch2，也为用户提供了几个集成入口。

1) Catch2 导出一个（带命名空间的）CMake target
2) Catch2 仓库包含用于在 CTest 中自动注册 `TEST_CASE` 的 CMake 脚本

## CMake targets

Catch2 的 CMake 构建会导出两个 target：`Catch2::Catch2` 和 `Catch2::Catch2WithMain`。如果你不需要自定义 `main` 函数，应该使用后者（而且只使用后者）。链接它会自动带上正确的 include 路径，并把实现 Catch2 和默认 main 的两个静态库一起链接进来。如果你需要自定义 `main`，则应该只链接 `Catch2::Catch2`。

这意味着，如果 Catch2 已经安装到系统中，只需要这样：
```cmake
find_package(Catch2 3 REQUIRED)
# 这些测试可以使用 Catch2 提供的 main
add_executable(tests test.cpp)
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)

# 这些测试需要自己的 main
add_executable(custom-main-tests test.cpp test-main.cpp)
target_link_libraries(custom-main-tests PRIVATE Catch2::Catch2)
```

当 Catch2 作为子目录使用时，也同样提供这些 targets。假设 Catch2 已经克隆到 `lib/Catch2`，只需要把上面的 `find_package` 改成 `add_subdirectory(lib/Catch2)`，示例仍然可以正常工作。

另一种方式是使用 [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html)：
```cmake
Include(FetchContent)

FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v3.0.1 # 或更新的 release
)

FetchContent_MakeAvailable(Catch2)

add_executable(tests test.cpp)
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
```

## 自动注册测试

Catch2 的仓库里还包含三个帮助用户自动把 `TEST_CASE` 注册到 CTest 的 CMake 脚本。它们位于 `extras` 文件夹中：

1) `Catch.cmake`（以及它依赖的 `CatchAddTests.cmake`）
2) `ParseAndAddCatchTests.cmake`（已废弃）
3) `CatchShardTests.cmake`（以及它依赖的 `CatchShardTestsImpl.cmake`）

如果 Catch2 已安装到系统中，`find_package(Catch2 REQUIRED)` 之后这两种方式都可以直接使用。否则你需要把它们加入自己的 CMake module path。

<a id="catch_discover_tests"></a>
### `Catch.cmake` 和 `CatchAddTests.cmake`

`Catch.cmake` 提供 `catch_discover_tests` 函数，用来从 target 中获取测试。这个函数会运行生成的可执行文件并加上 `--list-test-names-only` 标志，然后解析输出以查找所有已有测试。

#### 用法
```cmake
cmake_minimum_required(VERSION 3.5)

project(baz LANGUAGES CXX VERSION 0.0.1)

find_package(Catch2 REQUIRED)
add_executable(tests test.cpp)
target_link_libraries(tests PRIVATE Catch2::Catch2)

include(CTest)
include(Catch)
catch_discover_tests(tests)
```

如果使用 `FetchContent`，除非显式把 extras 目录加入 `CMAKE_MODULE_PATH`，否则 `include(Catch)` 会失败。

```cmake
# ... FetchContent ...
#
list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)
include(CTest)
include(Catch)
catch_discover_tests(tests)
```

#### 自定义
`catch_discover_tests` 可以接受一些额外参数：
```cmake
catch_discover_tests(target
                     [TEST_SPEC arg1...]
                     [EXTRA_ARGS arg1...]
                     [WORKING_DIRECTORY dir]
                     [TEST_PREFIX prefix]
                     [TEST_SUFFIX suffix]
                     [PROPERTIES name1 value1...]
                     [TEST_LIST var]
                     [REPORTER reporter]
                     [OUTPUT_DIR dir]
                     [OUTPUT_PREFIX prefix]
                     [OUTPUT_SUFFIX suffix]
                     [DISCOVERY_MODE <POST_BUILD|PRE_TEST>]
)
```

* `TEST_SPEC arg1...`

指定随 `--list-test-names-only` 一起传给 Catch 可执行文件的测试用例、带通配符的测试用例、标签和标签表达式。

* `EXTRA_ARGS arg1...`

要传给每个测试用例的额外命令行参数。

* `WORKING_DIRECTORY dir`

指定运行发现出来的测试用例时所处的目录。如果不提供这个选项，就使用当前 binary directory。

* `TEST_PREFIX prefix`

给每个发现到的测试用例名称加上前缀。这个选项在同一个测试可执行文件被多次 `catch_discover_tests()` 调用、且 `TEST_SPEC` 或 `EXTRA_ARGS` 不同时尤其有用。

* `TEST_SUFFIX suffix`

与 `TEST_PREFIX` 类似，只不过是给测试名称加后缀。`TEST_PREFIX` 和 `TEST_SUFFIX` 可以同时使用。

* `PROPERTIES name1 value1...`

为这次 `catch_discover_tests` 发现到的所有测试设置额外属性。

* `TEST_LIST var`

把测试列表提供给变量 `var`，而不是默认的 `<target>_TESTS`。当同一个测试可执行文件被多次 `catch_discover_tests()` 调用时这会很有用。注意这个变量只在 CTest 中可用。

* `REPORTER reporter`

运行测试用例时使用指定 reporter。reporter 会作为 `--reporter reporter` 传给测试运行器。

* `OUTPUT_DIR dir`

如果指定了这个选项，则会把参数以 `--out dir/<test_name>` 的形式传给测试可执行文件。实际文件名就是测试名本身。这个选项应当替代 `EXTRA_ARGS --out foo`，以避免并行测试执行时写结果输出产生竞争条件。

* `OUTPUT_PREFIX prefix`

可以和 `OUTPUT_DIR` 一起使用。如果指定了，则 `prefix` 会加在每个输出文件名前面，例如 `--out dir/prefix<test_name>`。

* `OUTPUT_SUFFIX suffix`

也可以和 `OUTPUT_DIR` 一起使用。如果指定了，则 `suffix` 会加在每个输出文件名后面，例如 `--out dir/<test_name>suffix`。这可用于给输出文件加扩展名，例如 `.xml`。

* `DISCOVERY_MODE mode`

如果指定，则可以控制测试发现何时执行。`POST_BUILD`（默认）表示在构建时执行发现；`PRE_TEST` 表示把发现延迟到测试执行前一刻（例如在交叉编译环境下很有用）。
如果调用 `catch_discover_tests` 时没有传入这个参数，则 `DISCOVERY_MODE` 会默认使用 `CMAKE_CATCH_DISCOVER_TESTS_DISCOVERY_MODE` 变量的值。这提供了一种全局选择偏好测试发现行为的机制。

### `ParseAndAddCatchTests.cmake`

⚠ 这个脚本在 Catch2 2.13.4 中[废弃](https://github.com/catchorg/Catch2/pull/2120)，并被上面的 `catch_discover_tests` 方式取代。更多细节见 [#2092](https://github.com/catchorg/Catch2/issues/2092)。

`ParseAndAddCatchTests` 的工作方式是解析 target 相关的所有实现文件，然后通过 CTest 的 `add_test` 注册它们。这个方式有一些限制，例如注释掉的测试也会被注册。更严重的是，Catch 当前可用的断言宏里只有一部分能被这个脚本识别，任何无法解析的宏对应的测试都会被 *静默忽略*。

#### 用法

```cmake
cmake_minimum_required(VERSION 3.5)

project(baz LANGUAGES CXX VERSION 0.0.1)

find_package(Catch2 REQUIRED)
add_executable(tests test.cpp)
target_link_libraries(tests PRIVATE Catch2::Catch2)

include(CTest)
include(ParseAndAddCatchTests)
ParseAndAddCatchTests(tests)
```

#### 自定义

`ParseAndAddCatchTests` 提供了一些自定义点：
* `PARSE_CATCH_TESTS_VERBOSE` -- 设为 `ON` 时，脚本会打印调试信息。默认是 `OFF`。
* `PARSE_CATCH_TESTS_NO_HIDDEN_TESTS` -- 设为 `ON` 时，隐藏测试（带 `[.]` 或 `[.foo]` 标签的测试）不会被注册。默认是 `OFF`。
* `PARSE_CATCH_TESTS_ADD_FIXTURE_IN_TEST_NAME` -- 设为 `ON` 时，会把 fixture 类名加到 CTest 的测试名里。默认是 `ON`。
* `PARSE_CATCH_TESTS_ADD_TARGET_IN_TEST_NAME` -- 设为 `ON` 时，会把 target 名加到 CTest 的测试名里。默认是 `ON`。
* `PARSE_CATCH_TESTS_ADD_TO_CONFIGURE_DEPENDS` -- 设为 `ON` 时，会把测试文件加入 `CMAKE_CONFIGURE_DEPENDS`。这意味着当测试文件变化时，CMake 配置步骤会重新运行，从而自动发现新测试。默认是 `OFF`。

还可以在调用 `ParseAndAddCatchTests` 之前设置变量 `OptionalCatchTestLauncher`，为测试指定启动命令。例如，如果想让一些测试通过 MPI 运行，而另一些顺序运行，可以这样写：
```cmake
set(OptionalCatchTestLauncher ${MPIEXEC} ${MPIEXEC_NUMPROC_FLAG} ${NUMPROC})
ParseAndAddCatchTests(mpi_foo)
unset(OptionalCatchTestLauncher)
ParseAndAddCatchTests(bar)
```

### `CatchShardTests.cmake`

> `CatchShardTests.cmake` 在 Catch2 3.1.0 中引入。

`CatchShardTests.cmake` 提供 `catch_add_sharded_tests(TEST_BINARY)` 函数，它会把 `TEST_BINARY` 中的测试拆分成多个 shard。每个 shard 内的测试及其顺序都会被随机化，而且种子会在每次 CTest 调用时变化。

这个脚本当前有 3 个自定义点：

 * SHARD_COUNT - 把 target 的测试拆成多少个 shard
 * REPORTER    - 测试使用的 reporter spec
 * TEST_SPEC   - 用于过滤测试的 test spec

示例：

```
include(CatchShardTests)

catch_add_sharded_tests(foo-tests
  SHARD_COUNT 4
  REPORTER "xml::out=-"
  TEST_SPEC "A"
)

catch_add_sharded_tests(tests
  SHARD_COUNT 8
  REPORTER "xml::out=-"
  TEST_SPEC "B"
)
```

这会总共注册 12 个 CTest 测试（4 + 8 个 shard），用于运行来自 `foo-tests` 测试二进制、并按 test spec 过滤的 shard。

_注意，这个脚本目前只是一个用于在每次 CTest 运行时重新给 shard 设种子的 proof-of-concept，因此它不支持（也暂时不打算支持）[`catch_discover_tests`](#catch_discover_tests) 的所有自定义点。_

## CMake 项目选项

Catch2 的 CMake 项目也为使用它的其他项目提供了一些选项：

* `BUILD_TESTING` -- 当为 `ON` 且项目不是作为子项目使用时，会构建 Catch2 的测试二进制。默认 `ON`。
* `CATCH_INSTALL_DOCS` -- 当为 `ON` 时，Catch2 文档会包含在安装中。默认 `ON`。
* `CATCH_INSTALL_EXTRAS` -- 当为 `ON` 时，Catch2 的 extras 文件夹（上面提到的 CMake 脚本、debugger helper）会包含在安装中。默认 `ON`。
* `CATCH_DEVELOPMENT_BUILD` -- 当为 `ON` 时，会把构建配置为 Catch2 的开发模式，也就是启用测试项目、警告等。默认 `OFF`。

启用 `CATCH_DEVELOPMENT_BUILD` 还会启用更多配置选项：

* `CATCH_BUILD_TESTING` -- 当为 `ON` 时，会构建 Catch2 的 SelfTest 项目。默认 `ON`。注意 Catch2 也会遵守 `BUILD_TESTING` 这个 CMake 变量，因此两个变量都要为 `ON` 才会构建 SelfTest，而任一项设为 `OFF` 都会禁用它。
* `CATCH_BUILD_EXAMPLES` -- 当为 `ON` 时，会构建 Catch2 的使用示例。默认 `OFF`。
* `CATCH_BUILD_EXTRA_TESTS` -- 当为 `ON` 时，会构建 Catch2 的额外测试。默认 `OFF`。
* `CATCH_BUILD_FUZZERS` -- 当为 `ON` 时，会构建 Catch2 的 fuzzing 入口。默认 `OFF`。
* `CATCH_ENABLE_WERROR` -- 当为 `ON` 时，会在编译中加入 `-Werror` 或等效标志。默认 `ON`。
* `CATCH_BUILD_SURROGATES` -- 当为 `ON` 时，Catch2 的每个头文件都会单独编译，以确保它们是自洽的。默认 `OFF`。

## `CATCH_CONFIG_*` 在 CMake 中的自定义选项

> 对 `CATCH_CONFIG_*` 选项的 CMake 支持是在 Catch2 3.0.1 中引入的

由于新的分离编译模型，来自 [编译期配置文档](configuration_zh.md#top) 的所有选项也都可以通过 Catch2 的 CMake 设置。要设置它们，只需把想要的选项设成 `ON`，例如 `-DCATCH_CONFIG_NOSTDOUT=ON`。

注意，把选项设为 `OFF` 并不会禁用它。要强制禁用某个选项，需要把 `_NO_` 形式设成 `ON`，例如 `-DCATCH_CONFIG_NO_COLOUR_WIN32=ON`。

下面用一个例子总结配置选项的行为：

| `-DCATCH_CONFIG_COLOUR_WIN32` | `-DCATCH_CONFIG_NO_COLOUR_WIN32` |      结果 |
|-------------------------------|----------------------------------|-------------|
|                          `ON` |                             `ON` |       error |
|                          `ON` |                            `OFF` |    force-on |
|                         `OFF` |                             `ON` |   force-off |
|                         `OFF` |                            `OFF` | auto-detect |

## 从 git 仓库安装 Catch2

如果你无法从包管理器安装 Catch2（例如 Ubuntu 16.04 提供的 catch 只有 1.2.0 版本），你可能会想直接从仓库安装。假设你有足够权限，可以直接安装到默认位置：
```
$ git clone https://github.com/catchorg/Catch2.git
$ cd Catch2
$ cmake -Bbuild -H. -DBUILD_TESTING=OFF
$ sudo cmake --build build/ --target install
```

如果你没有超级用户权限，还需要在配置构建时指定 [CMAKE_INSTALL_PREFIX](https://cmake.org/cmake/help/latest/variable/CMAKE_INSTALL_PREFIX.html)，并相应修改 [find_package](https://cmake.org/cmake/help/latest/command/find_package.html) 的调用。

## 从 vcpkg 安装 Catch2

或者，你也可以使用 [vcpkg](https://github.com/microsoft/vcpkg/) 依赖管理器来构建和安装 Catch2：
```
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh
./vcpkg integrate install
./vcpkg install catch2
```

vcpkg 里的 catch2 port 由微软团队成员和社区贡献者维护更新。如果版本过旧，请到 vcpkg 仓库 [创建 issue 或 pull request](https://github.com/Microsoft/vcpkg)。

---

[Home](Readme_zh.md#top)
