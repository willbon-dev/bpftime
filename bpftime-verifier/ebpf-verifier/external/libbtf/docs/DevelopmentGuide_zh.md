开发指南
=================

编码约定
------------------

* **应当** 使用 `stdint.h` 中定义的固定长度类型，而不是由编译器决定的语言关键字（例如使用 `int64_t, uint8_t`，而不是 `long, unsigned char`）。

* **应当** 尽可能使用 `const`、`static` 和可见性修饰符来限制变量和方法的暴露范围。

* **应当** 在所有公共 API 头文件中使用 doxygen 注释，并带上 \[in,out\]
  [方向注释](http://www.doxygen.nl/manual/commands.html#cmdparam)。内部 API 头文件也推荐这样做，但不是强制要求。

* **不要** 在可以避免的情况下使用全局变量。

* **不要** 使用缩写，除非它们已经是用户熟知的术语（例如 "app"、"info"），或者开发者必须使用的术语（例如 "min"、"max"、"args"）。错误示例包括：用 `num_widgets` 代替 `widget_count`，用 `opt_widgets` 代替 `option_widgets` 或 `optional_widgets`。

* **不要** 为在不同文件之间必须保持一致的内容硬编码魔数。应根据需要使用 `#define`、枚举或 const 值。

* **不要** 在整个项目中对同一个 C 函数名使用两个不同的原型。

* **不要** 使用被注释掉的代码，或 `#if 0` 以及等价形式中的代码。确保所有代码都真正参与构建。

头文件
------------

* **应当** 确保任何头文件都可以被直接包含，而不需要先包含其他头文件。也就是说，任何依赖都应包含在该头文件内部。

* **应当** 先包含本地头文件（使用 `""`），再包含系统头文件（使用 `<>`）。这有助于确保本地头文件不依赖于其他内容先被包含，也与预编译头使用本地头文件的方式一致。

* **应当** 尽可能按字母顺序排列头文件。这样可以确保没有重复包含，也有助于头文件可以直接使用。

* **应当** 在所有头文件中使用 `#pragma once`，而不是使用 ifdef 来测试重复包含。

风格指南
-----------

### 使用 `clang-format` 自动格式化

对于所有 C/C++ 文件（`*.c`、`*.cpp` 和 `*.h`），我们使用 `clang-format`（具体是版本 ```11.0.1```）来应用代码格式规则。修改 C/C++ 文件之后、合并之前，请运行：

```sh
$ ./scripts/format-code
```

### 格式化说明：

我们的编码约定遵循 [LLVM coding standards](https://llvm.org/docs/CodingStandards.html)，但做了以下调整：

* 源代码行 **不得** 超过 120 列。
* 单行 if/else/loop 代码块 **必须** 用花括号包裹。

请在提交中一并提交格式化改动，不要单独提交一个“Format Code”提交。你的编辑器大概率可以配置为在编辑文件或代码块时自动运行 `clang-format`。可参考：

- Emacs 的 [clang-format.el](https://github.com/llvm-mirror/clang/blob/master/tools/clang-format/clang-format.el)
- Vim 的 [vim-clang-format](https://github.com/rhysd/vim-clang-format)
- Visual Studio Code 的 [vscode-cpptools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)

[.clang-format](../.clang-format) 文件描述了脚本强制执行的样式，它基于 LLVM 风格，并做了一些更接近默认 Visual Studio 风格的修改。更多细节请参见 [clang-format style options](
http://releases.llvm.org/3.6.0/tools/clang/docs/ClangFormatStyleOptions.html)
。

如果你看到意料之外的格式化变化，请确认你使用的是 LLVM 工具链 11 或更高版本。

### 许可证头

每个代码文件顶部 **必须** 包含以下许可证头：

```c
// Copyright (c) Microsoft Corporation
// SPDX-License-Identifier: MIT
```

它应当以文件的注释标记作为前缀。如果确实有充分理由不包含该头部，可以把文件加入 `.check-license.ignore`。

所有文件都会通过以下脚本检查此头部：

```sh
$ ./scripts/check-license
```

### 命名约定

我们采用但不自动检查的命名约定包括：

1. 变量、成员/字段和函数名使用 `lower_snake_case`。
2. 宏名和常量使用 `UPPER_SNAKE_CASE`。
3. 头文件和源文件名优先使用 `lower_snake_case`。
4. 名称优先使用完整单词，而不是缩写（例如 `memory_context`，而不是 `mem_ctx`）。
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
8. 全局命名空间中的 eBPF 专有名称以 `ebpf_` 为前缀（例如 `ebpf_result_t`）。

总之，如果某个文件的风格与这些指南不同（例如私有成员命名为 `m_member` 而不是 `_member`），则以该文件中已有风格为准。
