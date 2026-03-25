开发指南
=================

编码约定
------------------

* **应当** 使用定义在 `stdint.h` 中的固定长度类型，而不是编译器决定的语言关键字（例如使用 `int64_t, uint8_t`，而不是 `long, unsigned char`）。

* **应当** 尽可能使用 `const`、`static` 和可见性修饰符来限制变量和方法的暴露范围。

* **应当** 在所有公共 API 头文件中使用 doxygen 注释，并带上 \[in,out\]
  [方向注释](http://www.doxygen.nl/manual/commands.html#cmdparam)。对于内部 API 头文件，也推荐这样做，虽然不是强制要求。

* **不要** 尽可能使用全局变量。

* **不要** 使用缩写，除非它们已经是用户广为熟知的术语（例如 "app"、"info"），或者开发者必须使用的术语（例如 "min"、"max"、"args"）。不好的例子是用 `num_widgets` 代替 `widget_count`，或者用 `opt_widgets` 代替 `option_widgets` 或 `optional_widgets`。

* **不要** 为在不同文件之间必须保持一致的内容硬编码魔数。应当根据需要使用 `#define`、枚举或 const 值。

* **不要** 在整个项目中对同一个 C 函数名使用两个不同的原型，只要可以避免。

* **不要** 使用被注释掉的代码，或写在 `#if 0` 或等价条件中的代码。确保所有代码都真正参与构建。

头文件
------------

* **应当** 确保任何头文件都可以被直接包含，而无需先包含其他头文件。也就是说，任何依赖都应当包含在该头文件自身内部。

* **应当** 先包含本地头文件（使用 `""`），再包含系统头文件（使用 `<>`）。这有助于确保本地头文件不依赖于其他内容先被包含，也与预编译头使用本地头文件的做法一致。

* **应当** 尽可能按字母顺序列出头文件。这样有助于确保不会重复包含，也有助于头文件可以直接使用。

* **应当** 在所有头文件中使用 `#pragma once`，而不是使用 ifdef 来检测重复包含。

风格指南
-----------

### 使用 `clang-format` 自动格式化

对于所有 C/C++ 文件（`*.c`、`*.cpp` 和 `*.h`），我们使用 `clang-format`（具体版本为 ```11.0.1```）来应用代码格式规则。修改 C/C++ 文件后、合并前，请运行：

```sh
$ ./scripts/format-code
```

### 格式说明：

我们的编码约定遵循 [LLVM coding standards](https://llvm.org/docs/CodingStandards.html)，但做了以下调整：

* 源代码行 **不得** 超过 120 列。
* 单行 if/else/loop 代码块 **必须** 使用花括号包裹。

请在提交中包含这些格式化改动，不要单独再提交一个“Format Code”提交。你的编辑器大概率可以配置为在你编辑文件或代码块时自动运行 `clang-format`。可参考：

- Emacs 的 [clang-format.el](https://github.com/llvm-mirror/clang/blob/master/tools/clang-format/clang-format.el)
- Vim 的 [vim-clang-format](https://github.com/rhysd/vim-clang-format)
- Visual Studio Code 的 [vscode-cpptools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)

[.clang-format](../.clang-format) 文件描述了脚本强制执行的风格，它基于 LLVM 风格，并做了一些更接近默认 Visual Studio 风格的修改。更多细节请参见 [clang-format style options](
http://releases.llvm.org/3.6.0/tools/clang/docs/ClangFormatStyleOptions.html)
。

如果你看到意料之外的格式变化，请确认你使用的是 LLVM 工具链 11 或更高版本。

### 许可证头

以下许可证头 **必须** 放在每个代码文件顶部：

```c
// Copyright (c) Microsoft Corporation
// SPDX-License-Identifier: MIT
```

它应当以文件的注释标记作为前缀。如果有充分理由不包含该头部，可以把文件加入
`.check-license.ignore`。

所有文件都会通过以下脚本检查这个头部：

```sh
$ ./scripts/check-license
```

### 命名约定

我们采用但不自动化检查的命名约定包括：

1. 变量、成员/字段和函数名使用 `lower_snake_case`。
2. 宏名和常量使用 `UPPER_SNAKE_CASE`。
3. 头文件和源文件优先使用 `lower_snake_case` 命名。
4. 名称优先使用完整单词，而不是缩写（例如 `memory_context`，不要 `mem_ctx`）。
5. 用前导 `_` 表示内部和私有字段或方法（例如 `_internal_field, _internal_method()`）。
6. 单下划线（`_`）保留给局部定义（static、文件作用域定义）。
   例如：`static ebpf_result_t _do_something(..)`。
7. `struct` 定义以前导 `_` 开头（这是第 6 条的例外），并且始终创建带 `_t` 后缀的 `typedef`。例如：
```c
typedef struct _ebpf_widget
{
    uint64_t count;
} ebpf_widget_t;
```
8. 全局命名空间中的 eBPF 专有名称应以 `ebpf_` 为前缀（例如 `ebpf_result_t`）。

总之，如果某个文件的风格与这些指南不同（例如私有成员命名为 `m_member` 而不是 `_member`），则该文件中已有的风格优先。
