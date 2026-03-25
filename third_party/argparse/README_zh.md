<p align="center">
  <img height="100" src="https://i.imgur.com/oDXeMUQ.png" alt="argparse"/>
</p>

<p align="center">
  <a href="https://github.com/p-ranav/argparse/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="license"/>
  </a>
  <img src="https://img.shields.io/badge/version-3.0-blue.svg?cacheSeconds=2592000" alt="version"/>
</p>

## Highlights

* 单头文件
* 需要 C++17
* MIT License

## Table of Contents

*    [Quick Start](#quick-start)
     *    [Positional Arguments](#positional-arguments)
     *    [Optional Arguments](#optional-arguments)
          *    [Requiring optional arguments](#requiring-optional-arguments)
          *    [Accessing optional arguments without default values](#accessing-optional-arguments-without-default-values)
          *    [Deciding if the value was given by the user](#deciding-if-the-value-was-given-by-the-user)
          *    [Joining values of repeated optional arguments](#joining-values-of-repeated-optional-arguments)
          *    [Repeating an argument to increase a value](#repeating-an-argument-to-increase-a-value)
          *    [Mutually Exclusive Group](#mutually-exclusive-group)
     *    [Negative Numbers](#negative-numbers)
     *    [Combining Positional and Optional Arguments](#combining-positional-and-optional-arguments)
     *    [Printing Help](#printing-help)
     *    [Adding a description and an epilog to help](#adding-a-description-and-an-epilog-to-help)
     *    [List of Arguments](#list-of-arguments)
     *    [Compound Arguments](#compound-arguments)
     *    [Converting to Numeric Types](#converting-to-numeric-types)
     *    [Default Arguments](#default-arguments)
     *    [Gathering Remaining Arguments](#gathering-remaining-arguments)
     *    [Parent Parsers](#parent-parsers)
     *    [Subcommands](#subcommands)
     *    [Parse Known Args](#parse-known-args)
     *    [ArgumentParser in bool Context](#argumentparser-in-bool-context)
     *    [Custom Prefix Characters](#custom-prefix-characters)
     *    [Custom Assignment Characters](#custom-assignment-characters)
*    [Further Examples](#further-examples)
     *    [Construct a JSON object from a filename argument](#construct-a-json-object-from-a-filename-argument)
     *    [Positional Arguments with Compound Toggle Arguments](#positional-arguments-with-compound-toggle-arguments)
     *    [Restricting the set of values for an argument](#restricting-the-set-of-values-for-an-argument)
     *    [Using `option=value` syntax](#using-optionvalue-syntax)
*    [Developer Notes](#developer-notes)
     *    [Copying and Moving](#copying-and-moving)
*    [CMake Integration](#cmake-integration)
*    [Building, Installing, and Testing](#building-installing-and-testing)
*    [Supported Toolchains](#supported-toolchains)
*    [Contributing](#contributing)
*    [License](#license)

## Quick Start

只需要包含 `argparse.hpp` 就可以开始使用。

```cpp
#include <argparse/argparse.hpp>
```

开始解析命令行参数时，先创建一个 `ArgumentParser`。

```cpp
argparse::ArgumentParser program("program_name");
```

**NOTE:** `ArgumentParser` 的第二个可选参数是程序版本号。例如：`argparse::ArgumentParser program("libfoo", "1.9.0");`

**NOTE:** `ArgumentParser` 的第三和第四个可选参数用于控制默认参数。例如：`argparse::ArgumentParser program("libfoo", "1.9.0", default_arguments::help, false);` 详情见下面的 [Default Arguments](#default-arguments)。

新增参数时，直接调用 ```.add_argument(...)``` 即可。你可以一次传入多个参数名，把它们视为同一个参数组，比如 ```-v``` 和 ```--verbose```。

```cpp
program.add_argument("foo");
program.add_argument("-v", "--verbose"); // parameter packing
```

argparse 支持多种参数类型，包括位置参数、可选参数和复合参数。下面分别介绍它们的配置方式。

### Positional Arguments

下面是一个***位置参数***示例：

```cpp
#include <argparse/argparse.hpp>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("program_name");

  program.add_argument("square")
    .help("display the square of a given integer")
    .scan<'i', int>();

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::exception& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  auto input = program.get<int>("square");
  std::cout << (input * input) << std::endl;

  return 0;
}
```

运行结果如下：

```console
foo@bar:/home/dev/$ ./main 15
225
```

这里发生了什么：

* `add_argument()` 用来指定程序愿意接收哪些命令行参数。这里我们把它命名为 `square`，让它和功能一致。
* 命令行参数本质上是字符串。要把它平方并打印结果，我们需要先把它转成数字，所以这里使用 `.scan` 方法把用户输入转换为整数。
* 可以通过 `parser.get<T>(key)` 获取解析器里保存的某个参数值。

### Optional Arguments

现在来看***可选参数***。可选参数以 `-` 或 `--` 开头，例如 `--verbose` 或 `-a`。可选参数可以放在输入序列的任何位置。

```cpp
argparse::ArgumentParser program("test");

program.add_argument("--verbose")
  .help("increase output verbosity")
  .default_value(false)
  .implicit_value(true);

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

if (program["--verbose"] == true) {
  std::cout << "Verbosity enabled" << std::endl;
}
```

```console
foo@bar:/home/dev/$ ./main --verbose
Verbosity enabled
```

这里的逻辑是：

* 程序被写成：指定 `--verbose` 时输出一些内容，不指定时什么都不输出。
* 由于这个参数是可选的，所以即使不传 `--verbose` 也不会报错。通过 `.default_value(false)`，如果没有使用这个参数，它会自动被设置为 `false`。
* 通过 `.implicit_value(true)`，你可以把这个选项当作一个标志位，而不是必须带值的参数。当用户提供 `--verbose` 时，它的值会变成 `true`。

#### Flag

定义 flag 参数时，可以使用 `flag()` 这个简写，它等价于 `default_value(false).implicit_value(true)`。

```cpp
argparse::ArgumentParser program("test");

program.add_argument("--verbose")
  .help("increase output verbosity")
  .flag();

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

if (program["--verbose"] == true) {
  std::cout << "Verbosity enabled" << std::endl;
}
```

#### Requiring optional arguments

有些场景下，你希望把一个可选参数变成***必需***参数。正如前面所说，可选参数通常以 `-` 或 `--` 开头。你可以这样把它们设为必需：

```cpp
program.add_argument("-o", "--output")
  .required()
  .help("specify the output file.");
```

如果用户没有提供这个参数的值，就会抛出异常。

你也可以给它提供一个默认值：

```cpp
program.add_argument("-o", "--output")
  .default_value(std::string("-"))
  .required()
  .help("specify the output file.");
```

#### Accessing optional arguments without default values

如果你需要一个可选参数必须存在，但又没有合适的默认值，可以这样判断并访问：

```cpp
if (auto fn = program.present("-o")) {
    do_something_with(*fn);
}
```

和 `get` 类似，`present` 也支持模板参数。但它返回的不是 `T`，而是 `std::optional<T>`。因此当用户没有提供这个参数时，返回值会等于 `std::nullopt`。

#### Deciding if the value was given by the user

如果你想知道用户是否为一个带 `.default_value` 的参数显式提供了值，可以检查该参数的 `.is_used()`。

```cpp
program.add_argument("--color")
  .default_value(std::string{"orange"})   // 否则可能会被推导成 const char*，导致 program.get<std::string> 时出错
  .help("specify the cat's fur color");

try {
  program.parse_args(argc, argv);    // 例如：./main --color orange
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto color = program.get<std::string>("--color");  // "orange"
auto explicit_color = program.is_used("--color");  // true，用户显式传入了 orange
```

#### Joining values of repeated optional arguments

如果你希望一个可选参数可以重复出现，并把所有值收集到一起，可以这样做：

```cpp
program.add_argument("--color")
  .default_value<std::vector<std::string>>({ "orange" })
  .append()
  .help("specify the cat's fur color");

try {
  program.parse_args(argc, argv);    // 例如：./main --color red --color green --color blue
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto colors = program.get<std::vector<std::string>>("--color");  // {"red", "green", "blue"}
```

注意，`.default_value` 显式指定了模板参数，以匹配你希望 `.get` 返回的类型。

#### Repeating an argument to increase a value

一个常见模式是重复同一个参数来表示更高的强度或数值。

```cpp
int verbosity = 0;
program.add_argument("-V", "--verbose")
  .action([&](const auto &) { ++verbosity; })
  .append()
  .default_value(false)
  .implicit_value(true)
  .nargs(0);

program.parse_args(argc, argv);    // 例如：./main -VVVV

std::cout << "verbose level: " << verbosity << std::endl;    // verbose level: 4
```

#### Mutually Exclusive Group

可以用 `program.add_mutually_exclusive_group(required = false)` 创建互斥组。`argparse` 会保证互斥组中的参数在命令行里最多只出现一个：

```cpp
auto &group = program.add_mutually_exclusive_group();
group.add_argument("--first");
group.add_argument("--second");
```

如果像下面这样使用，就会报错：

```console
foo@bar:/home/dev/$ ./main --first 1 --second 2
Argument '--second VAR' not allowed with '--first VAR'
```

`add_mutually_exclusive_group()` 也支持 `required` 参数，表示互斥组中至少要有一个参数出现：

```cpp
auto &group = program.add_mutually_exclusive_group(true);
group.add_argument("--first");
group.add_argument("--second");
```

如果像下面这样使用，也会报错：

```console
foo@bar:/home/dev/$ ./main
One of the arguments '--first VAR' or '--second VAR' is required
```

### Negative Numbers

可选参数以 `-` 开头。那么 `argparse` 能处理负数吗？答案是可以！

```cpp
argparse::ArgumentParser program;

program.add_argument("integer")
  .help("Input number")
  .scan<'i', int>();

program.add_argument("floats")
  .help("Vector of floats")
  .nargs(4)
  .scan<'g', float>();

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

// 输出参数的代码
```

```console
foo@bar:/home/dev/$ ./main -5 -1.1 -3.1415 -3.1e2 -4.51329E3
integer : -5
floats  : -1.1 -3.1415 -310 -4513.29
```

可以看到，`argparse` 支持负整数、负浮点数以及科学计数法。

### Combining Positional and Optional Arguments

```cpp
argparse::ArgumentParser program("main");

program.add_argument("square")
  .help("display the square of a given number")
  .scan<'i', int>();

program.add_argument("--verbose")
  .default_value(false)
  .implicit_value(true);

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

int input = program.get<int>("square");

if (program["--verbose"] == true) {
  std::cout << "The square of " << input << " is " << (input * input) << std::endl;
}
else {
  std::cout << (input * input) << std::endl;
}
```

```console
foo@bar:/home/dev/$ ./main 4
16

foo@bar:/home/dev/$ ./main 4 --verbose
The square of 4 is 16

foo@bar:/home/dev/$ ./main --verbose 4
The square of 4 is 16
```

### Printing Help

`std::cout << program` 会打印帮助信息，包括程序用法以及 `ArgumentParser` 已注册参数的信息。前面这个例子中，默认帮助信息如下：

```
foo@bar:/home/dev/$ ./main --help
Usage: main [-h] [--verbose] square

Positional arguments:
  square       	display the square of a given number

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits
  --verbose
```

你也可以通过 `program.help().str()` 以字符串形式获取帮助信息。

#### Adding a description and an epilog to help

`ArgumentParser::add_description` 会在详细参数信息之前添加文本。`ArgumentParser::add_epilog` 则会在所有帮助输出之后添加文本。

```cpp
#include <argparse/argparse.hpp>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("main");
  program.add_argument("thing").help("Thing to use.").metavar("THING");
  program.add_argument("--member").help("The alias for the member to pass to.").metavar("ALIAS");
  program.add_argument("--verbose").default_value(false).implicit_value(true);

  program.add_description("Forward a thing to the next member.");
  program.add_epilog("Possible things include betingalw, chiz, and res.");

  program.parse_args(argc, argv);

  std::cout << program << std::endl;
}
```

```console
Usage: main [-h] [--member ALIAS] [--verbose] THING

Forward a thing to the next member.

Positional arguments:
  THING         	Thing to use.

Optional arguments:
  -h, --help    	shows help message and exits
  -v, --version 	prints version information and exits
  --member ALIAS	The alias for the member to pass to.
  --verbose

Possible things include betingalw, chiz, and res.
```

### List of Arguments

`ArgumentParser` 通常把一个命令行参数映射到一个动作。`.nargs` 则允许一个动作接收多个命令行参数。当使用 `nargs(N)` 时，会把命令行中的 N 个参数收集成一个列表。

```cpp
argparse::ArgumentParser program("main");

program.add_argument("--input_files")
  .help("The list of input files")
  .nargs(2);

try {
  program.parse_args(argc, argv);   // 例如：./main --input_files config.yml System.xml
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto files = program.get<std::vector<std::string>>("--input_files");  // {"config.yml", "System.xml"}
```

`ArgumentParser.get<T>()` 对 `std::vector` 和 `std::list` 有专门支持。所以下面这种形式也可以工作：

```cpp
auto files = program.get<std::list<std::string>>("--input_files");  // {"config.yml", "System.xml"}
```

使用 `.scan`，你可以快速把命令行参数转换成想要的值类型列表。比如：

```cpp
argparse::ArgumentParser program("main");

program.add_argument("--query_point")
  .help("3D query point")
  .nargs(3)
  .default_value(std::vector<double>{0.0, 0.0, 0.0})
  .scan<'g', double>();

try {
  program.parse_args(argc, argv); // 例如：./main --query_point 3.5 4.7 9.2
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto query_point = program.get<std::vector<double>>("--query_point");  // {3.5, 4.7, 9.2}
```

你也可以用 `.nargs` 定义长度可变的参数列表，下面是几个例子。

```cpp
program.add_argument("--input_files")
  .nargs(1, 3);  // 接受 1 到 3 个参数。
```

argparse 还支持像 Python 中一样的 `"?"`、`"*"`、`"+"` 模式：

```cpp
program.add_argument("--input_files")
  .nargs(argparse::nargs_pattern::any);  // Python 里的 "*"。接受任意数量的参数，包括 0 个。
```
```cpp
program.add_argument("--input_files")
  .nargs(argparse::nargs_pattern::at_least_one);  // Python 里的 "+"。接受一个或多个参数。
```
```cpp
program.add_argument("--input_files")
  .nargs(argparse::nargs_pattern::optional);  // Python 里的 "?"。表示参数可选。
```

### Compound Arguments

复合参数是把多个可选参数组合后，以一个参数形式提供的情况。例如 `ps -aux`。

```cpp
argparse::ArgumentParser program("test");

program.add_argument("-a")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-b")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-c")
  .nargs(2)
  .default_value(std::vector<float>{0.0f, 0.0f})
  .scan<'g', float>();

try {
  program.parse_args(argc, argv);                  // 例如：./main -abc 1.95 2.47
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto a = program.get<bool>("-a");                  // true
auto b = program.get<bool>("-b");                  // true
auto c = program.get<std::vector<float>>("-c");    // {1.95, 2.47}

/// 输出解析后的参数
```

```console
foo@bar:/home/dev/$ ./main -ac 3.14 2.718
a = true
b = false
c = {3.14, 2.718}

foo@bar:/home/dev/$ ./main -cb
a = false
b = true
c = {0.0, 0.0}
```

这里的逻辑是：
* 有三个可选参数 `-a`、`-b` 和 `-c`。
* `-a` 和 `-b` 是切换型参数。
* `-c` 需要从命令行接收 2 个浮点数。
* argparse 能处理复合参数，例如 `-abc`、`-bac` 或 `-cab`。这只适用于短的单字符参数名。
  - `-a` 和 `-b` 会变成 `true`。
  - 会继续解析 `argv`，找出映射到 `-c` 的输入。
  - 如果 argparse 找不到任何可映射到 `c` 的参数，那么 `c` 会按照 `.default_value` 的定义，默认成 `{0.0, 0.0}`。

### Converting to Numeric Types

对于输入，用户可以把原始值表示为某种基本类型。

`.scan<Shape, T>` 方法会根据 `Shape` 转换说明，把传入的 `std::string` 尝试转换成 `T`。如果出错，会抛出 `std::invalid_argument` 或 `std::range_error`。

```cpp
program.add_argument("-x")
       .scan<'d', int>();

program.add_argument("scale")
       .scan<'g', double>();
```

`Shape` 指定输入“长什么样”，类型模板参数指定预定义动作的返回值。可接受的类型包括浮点型（`float`、`double`、`long double`）和整型（`signed char`、`short`、`int`、`long`、`long long`）。

这个语法规则参考 `std::from_chars`，但并不完全相同。例如，十六进制数字可以以 `0x` 或 `0X` 开头，带前导零的数字可能会按八进制处理。

| Shape      | interpretation                            |
| :--------: | ----------------------------------------- |
| 'a' or 'A' | hexadecimal floating point                |
| 'e' or 'E' | scientific notation (floating point)      |
| 'f' or 'F' | fixed notation (floating point)           |
| 'g' or 'G' | general form (either fixed or scientific) |
|            |                                           |
| 'd'        | decimal                                   |
| 'i'        | `std::from_chars` grammar with base == 10 |
| 'o'        | octal (unsigned)                          |
| 'u'        | decimal (unsigned)                        |
| 'x' or 'X' | hexadecimal (unsigned)                    |

### Default Arguments

`argparse` 为 `-h`/`--help` 和 `-v`/`--version` 提供了预定义参数和动作。默认情况下，这些动作会在显示帮助或版本信息后**退出**程序。这个退出过程不会调用析构函数，因此不会执行资源清理。

你可以在创建 `ArgumentParser` 时禁用这些默认参数，这样就能自己处理它们。（注意：当你选择默认参数时，程序名和版本号必须一起提供。）

```cpp
argparse::ArgumentParser program("test", "1.0", default_arguments::none);

program.add_argument("-h", "--help")
  .action([=](const std::string& s) {
    std::cout << help().str();
  })
  .default_value(false)
  .help("shows help message")
  .implicit_value(true)
  .nargs(0);
```

上面的代码会输出帮助信息并继续运行。它不支持 `--version` 参数。

默认值 `default_arguments::all` 会为包含的参数添加全部默认参数。`default_arguments::none` 不会添加任何默认参数。`default_arguments::help` 和 `default_arguments::version` 会分别只添加 `--help` 和 `--version`。

你也可以在保留默认参数的同时，禁用这些参数触发默认退出的行为。`ArgumentParser` 的第四个参数（`exit_on_default_arguments`）是一个布尔值，默认是 `true`。下面的调用会保留 `--help` 和 `--version`，但使用这些参数时不会退出。

```cpp
argparse::ArgumentParser program("test", "1.0", default_arguments::all, false)
```

### Gathering Remaining Arguments

`argparse` 支持收集命令末尾的“剩余”参数，例如编译器场景：

```console
foo@bar:/home/dev/$ compiler file1 file2 file3
```

要启用这个功能，只需创建一个参数并把它标记为 `remaining`。传给 argparse 的所有剩余参数都会收集到这里。

```cpp
argparse::ArgumentParser program("compiler");

program.add_argument("files")
  .remaining();

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

try {
  auto files = program.get<std::vector<std::string>>("files");
  std::cout << files.size() << " files provided" << std::endl;
  for (auto& file : files)
    std::cout << file << std::endl;
} catch (std::logic_error& e) {
  std::cout << "No files provided" << std::endl;
}
```

没有参数时：

```console
foo@bar:/home/dev/$ ./compiler
No files provided
```

多个参数时：

```console
foo@bar:/home/dev/$ ./compiler foo.txt bar.txt baz.txt
3 files provided
foo.txt
bar.txt
baz.txt
```

收集剩余参数的过程也可以和可选参数很好地配合：

```cpp
argparse::ArgumentParser program("compiler");

program.add_arguments("-o")
  .default_value(std::string("a.out"));

program.add_argument("files")
  .remaining();

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto output_filename = program.get<std::string>("-o");
std::cout << "Output filename: " << output_filename << std::endl;

try {
  auto files = program.get<std::vector<std::string>>("files");
  std::cout << files.size() << " files provided" << std::endl;
  for (auto& file : files)
    std::cout << file << std::endl;
} catch (std::logic_error& e) {
  std::cout << "No files provided" << std::endl;
}

```

```console
foo@bar:/home/dev/$ ./compiler -o main foo.cpp bar.cpp baz.cpp
Output filename: main
3 files provided
foo.cpp
bar.cpp
baz.cpp
```

***NOTE***：记得把所有可选参数放在 remaining 参数之前。如果把可选参数放在 remaining 参数之后，它也会被当作 remaining 参数：

```console
foo@bar:/home/dev/$ ./compiler foo.cpp bar.cpp baz.cpp -o main
5 arguments provided
foo.cpp
bar.cpp
baz.cpp
-o
main
```

### Parent Parsers

一个解析器可以复用其它解析器也会用到的参数。

这些共享参数可以先加入一个解析器，然后把它作为“父解析器”给其它需要这些参数的解析器使用。你可以通过 `.add_parents` 给一个解析器添加一个或多个父解析器。每个父解析器里的位置参数和可选参数都会被加入到子解析器中。

```cpp
argparse::ArgumentParser surface_parser("surface", 1.0, argparse::default_arguments::none);
parent_parser.add_argument("--area")
  .default_value(0)
  .scan<'i', int>();

argparse::ArgumentParser floor_parser("floor");
floor_parser.add_argument("tile_size").scan<'i', int>();
floor_parser.add_parents(surface_parser);
floor_parser.parse_args({ "./main", "--area", "200", "12" });  // --area = 200, tile_size = 12

argparse::ArgumentParser ceiling_parser("ceiling");
ceiling_parser.add_argument("--color");
ceiling_parser.add_parents(surface_parser);
ceiling_parser.parse_args({ "./main", "--color", "gray" });  // --area = 0, --color = "gray"
```

在父解析器被加入子解析器之后，对父解析器做的修改不会反映到子解析器里。所以在把父解析器加进去之前，要先把它完整初始化好。

每个解析器都会带有标准的默认参数。为了避免帮助信息重复，建议在父解析器中禁用默认参数。

### Subcommands

很多程序会把功能拆成多个子命令，例如 `git` 可以调用 `git checkout`、`git add` 和 `git commit`。当一个程序包含多个彼此不同、且需要不同命令行参数的功能时，这种拆分方式特别合适。`ArgumentParser` 通过 `add_subparser()` 成员函数支持创建这样的子命令。

```cpp
#include <argparse/argparse.hpp>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("git");

  // git add subparser
  argparse::ArgumentParser add_command("add");
  add_command.add_description("Add file contents to the index");
  add_command.add_argument("files")
    .help("Files to add content from. Fileglobs (e.g.  *.c) can be given to add all matching files.")
    .remaining();

  // git commit subparser
  argparse::ArgumentParser commit_command("commit");
  commit_command.add_description("Record changes to the repository");
  commit_command.add_argument("-a", "--all")
    .help("Tell the command to automatically stage files that have been modified and deleted.")
    .default_value(false)
    .implicit_value(true);

  commit_command.add_argument("-m", "--message")
    .help("Use the given <msg> as the commit message.");

  // git cat-file subparser
  argparse::ArgumentParser catfile_command("cat-file");
  catfile_command.add_description("Provide content or type and size information for repository objects");
  catfile_command.add_argument("-t")
    .help("Instead of the content, show the object type identified by <object>.");

  catfile_command.add_argument("-p")
    .help("Pretty-print the contents of <object> based on its type.");

  // git submodule subparser
  argparse::ArgumentParser submodule_command("submodule");
  submodule_command.add_description("Initialize, update or inspect submodules");
  argparse::ArgumentParser submodule_update_command("update");
  submodule_update_command.add_description("Update the registered submodules to match what the superproject expects");
  submodule_update_command.add_argument("--init")
    .default_value(false)
    .implicit_value(true);
  submodule_update_command.add_argument("--recursive")
    .default_value(false)
    .implicit_value(true);
  submodule_command.add_subparser(submodule_update_command);

  program.add_subparser(add_command);
  program.add_subparser(commit_command);
  program.add_subparser(catfile_command);
  program.add_subparser(submodule_command);

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::exception& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  // 使用参数
}
```

```console
foo@bar:/home/dev/$ ./git --help
Usage: git [-h] {add,cat-file,commit,submodule}

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits

Subcommands:
  add           Add file contents to the index
  cat-file      Provide content or type and size information for repository objects
  commit        Record changes to the repository
  submodule     Initialize, update or inspect submodules

foo@bar:/home/dev/$ ./git add --help
Usage: add [-h] files

Add file contents to the index

Positional arguments:
  files        	Files to add content from. Fileglobs (e.g.  *.c) can be given to add all matching files.

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits

foo@bar:/home/dev/$ ./git commit --help
Usage: commit [-h] [--all] [--message VAR]

Record changes to the repository

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits
  -a, --all    	Tell the command to automatically stage files that have been modified and deleted.
  -m, --message	Use the given <msg> as the commit message.

foo@bar:/home/dev/$ ./git submodule --help
Usage: submodule [-h] {update}

Initialize, update or inspect submodules

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits

Subcommands:
  update        Update the registered submodules to match what the superproject expects
```

当从子解析器请求帮助信息时，只会打印该特定解析器的帮助内容，不会包含父解析器或兄弟解析器的帮助信息。

此外，每个解析器都有 `.is_subcommand_used("<command_name>")` 和 `.is_subcommand_used(subparser)` 成员函数，用来检查某个子命令是否被使用过。

有时你可能希望在帮助信息中隐藏一部分子命令。为此，`ArgumentParser` 提供了 `.set_suppress(bool suppress)` 方法：

```cpp
argparse::ArgumentParser program("test");

argparse::ArgumentParser hidden_cmd("hidden");
hidden_cmd.add_argument("files").remaining();
hidden_cmd.set_suppress(true);

program.add_subparser(hidden_cmd);
```

```console
foo@bar:/home/dev/$ ./main -h
Usage: test [--help] [--version] {}

Optional arguments:
  -h, --help    shows help message and exits
  -v, --version prints version information and exits

foo@bar:/home/dev/$ ./main hidden -h
Usage: hidden [--help] [--version] files

Positional arguments:
  files         [nargs: 0 or more]

Optional arguments:
  -h, --help    shows help message and exits
  -v, --version prints version information and exits
```

### Getting Argument and Subparser Instances

加入到 `ArgumentParser` 的 `Argument` 和 `ArgumentParser` 实例，可以通过 `.at<T>()` 取回。默认返回类型是 `Argument`。

```cpp
argparse::ArgumentParser program("test");

program.add_argument("--dir");
program.at("--dir").default_value(std::string("/home/user"));

program.add_subparser(argparse::ArgumentParser{"walk"});
program.at<argparse::ArgumentParser>("walk").add_argument("depth");
```

### Parse Known Args

有时程序只会解析部分命令行参数，把剩余参数传给另一个脚本或程序。这个时候，`parse_known_args()` 会很有用。它的行为和 `parse_args()` 类似，只是当存在额外参数时不会报错，而是返回剩余参数字符串列表。

```cpp
#include <argparse/argparse.hpp>
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.add_argument("--foo").implicit_value(true).default_value(false);
  program.add_argument("bar");

  auto unknown_args =
    program.parse_known_args({"test", "--foo", "--badger", "BAR", "spam"});

  assert(program.get<bool>("--foo") == true);
  assert(program.get<std::string>("bar") == std::string{"BAR"});
  assert((unknown_args == std::vector<std::string>{"--badger", "spam"}));
}
```

### ArgumentParser in bool Context

在调用 `.parse_args` 或 `.parse_known_args` 之前，`ArgumentParser` 的布尔值为 `false`。一旦它（或它的某个子解析器）成功提取了已知值，就会变成 `true`。使用 `.parse_known_args` 时，未知参数不会让解析器变成 `true`。

### Custom Prefix Characters

大多数命令行选项都会用 `-` 作为前缀，例如 `-f/--foo`。如果解析器需要支持不同或额外的前缀字符，比如 `+f` 或 `/foo`，可以通过 `set_prefix_chars()` 来指定。

默认前缀字符是 `-`。

```cpp
#include <argparse/argparse.hpp>
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.set_prefix_chars("-+/");

  program.add_argument("+f");
  program.add_argument("--bar");
  program.add_argument("/foo");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::exception& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  if (program.is_used("+f")) {
    std::cout << "+f    : " << program.get("+f") << "\n";
  }

  if (program.is_used("--bar")) {
    std::cout << "--bar : " << program.get("--bar") << "\n";
  }

  if (program.is_used("/foo")) {
    std::cout << "/foo  : " << program.get("/foo") << "\n";
  }  
}
```

```console
foo@bar:/home/dev/$ ./main +f 5 --bar 3.14f /foo "Hello"
+f    : 5
--bar : 3.14f
/foo  : Hello
```

### Custom Assignment Characters

除了前缀字符，还可以设置自定义的赋值字符。这个设置允许你写出像 `./test --foo=Foo /B:Bar` 这样的调用。

默认赋值字符是 `=`.

```cpp
#include <argparse/argparse.hpp>
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.set_prefix_chars("-+/");
  program.set_assign_chars("=:");

  program.add_argument("--foo");
  program.add_argument("/B");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::exception& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  if (program.is_used("--foo")) {
    std::cout << "--foo : " << program.get("--foo") << "\n";
  }

  if (program.is_used("/B")) {
    std::cout << "/B    : " << program.get("/B") << "\n";
  }
}
```

```console
foo@bar:/home/dev/$ ./main --foo=Foo /B:Bar
--foo : Foo
/B    : Bar
```

## Further Examples

### Construct a JSON object from a filename argument

```cpp
argparse::ArgumentParser program("json_test");

program.add_argument("config")
  .action([](const std::string& value) {
    // 读取 JSON 文件
    std::ifstream stream(value);
    nlohmann::json config_json;
    stream >> config_json;
    return config_json;
  });

try {
  program.parse_args({"./test", "config.json"});
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

nlohmann::json config = program.get<nlohmann::json>("config");
```

### Positional Arguments with Compound Toggle Arguments

```cpp
argparse::ArgumentParser program("test");

program.add_argument("numbers")
  .nargs(3)
  .scan<'i', int>();

program.add_argument("-a")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-b")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-c")
  .nargs(2)
  .scan<'g', float>();

program.add_argument("--files")
  .nargs(3);

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto numbers = program.get<std::vector<int>>("numbers");        // {1, 2, 3}
auto a = program.get<bool>("-a");                               // true
auto b = program.get<bool>("-b");                               // true
auto c = program.get<std::vector<float>>("-c");                 // {3.14f, 2.718f}
auto files = program.get<std::vector<std::string>>("--files");  // {"a.txt", "b.txt", "c.txt"}

/// 输出解析后的参数
```

```console
foo@bar:/home/dev/$ ./main 1 2 3 -abc 3.14 2.718 --files a.txt b.txt c.txt
numbers = {1, 2, 3}
a = true
b = true
c = {3.14, 2.718}
files = {"a.txt", "b.txt", "c.txt"}
```

### Restricting the set of values for an argument

```cpp
argparse::ArgumentParser program("test");

program.add_argument("input")
  .default_value(std::string{"baz"})
  .choices("foo", "bar", "baz");

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto input = program.get("input");
std::cout << input << std::endl;
```

```console
foo@bar:/home/dev/$ ./main fex
Invalid argument "fex" - allowed options: {foo, bar, baz}
```

`choices` 也可以用于整数类型，例如：

```cpp
argparse::ArgumentParser program("test");

program.add_argument("input")
  .default_value(0)
  .choices(0, 1, 2, 3, 4, 5);

try {
  program.parse_args(argc, argv);
}
catch (const std::exception& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto input = program.get("input");
std::cout << input << std::endl;
```

```console
foo@bar:/home/dev/$ ./main 6
Invalid argument "6" - allowed options: {0, 1, 2, 3, 4, 5}
```

### Using `option=value` syntax

```cpp
#include "argparse.hpp"
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.add_argument("--foo").implicit_value(true).default_value(false);
  program.add_argument("--bar");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::exception& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  if (program.is_used("--foo")) {
    std::cout << "--foo: " << std::boolalpha << program.get<bool>("--foo") << "\n";
  }

  if (program.is_used("--bar")) {
    std::cout << "--bar: " << program.get("--bar") << "\n";
  }  
}
```

```console
foo@bar:/home/dev/$ ./test --bar=BAR --foo
--foo: true
--bar: BAR
```

## Developer Notes

### Copying and Moving

`argparse::ArgumentParser` 的设计目标是只在一个函数里使用：把设置和解析都放在同一处完成。尝试移动或拷贝会使内部引用失效（issue #260）。因此从 v3.0 开始，`argparse::ArgumentParser` 的拷贝和移动构造函数都被标记为 `delete`。

## CMake Integration

可以在 CMake 项目里直接使用最新的 argparse，而无需复制任何内容。

```cmake
cmake_minimum_required(VERSION 3.14)

PROJECT(myproject)

# fetch latest argparse
include(FetchContent)
FetchContent_Declare(
    argparse
    GIT_REPOSITORY https://github.com/p-ranav/argparse.git
)
FetchContent_MakeAvailable(argparse)

add_executable(myproject main.cpp)
target_link_libraries(myproject argparse)
```

## Building, Installing, and Testing

```bash
# Clone the repository
git clone https://github.com/p-ranav/argparse
cd argparse

# Build the tests
mkdir build
cd build
cmake -DARGPARSE_BUILD_SAMPLES=on -DARGPARSE_BUILD_TESTS=on ..
make

# Run tests
./test/tests

# Install the library
sudo make install
```

## Supported Toolchains

| Compiler             | Standard Library | Test Environment   |
| :------------------- | :--------------- | :----------------- |
| GCC >= 8.3.0         | libstdc++        | Ubuntu 18.04       |
| Clang >= 7.0.0       | libc++           | Xcode 10.2         |
| MSVC >= 16.8         | Microsoft STL    | Visual Studio 2019 |

## Contributing

欢迎贡献。更多信息请查看 [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md) 文档。

## License

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。
