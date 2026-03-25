开发指南
=================

编码规范
------------------

* **DO** 使用 `stdint.h` 中定义的固定宽度类型，而不是编译器决定的语言关键字（例如 `int64_t`、`uint8_t`，而不是 `long`、`unsigned char`）。

* **DO** 尽可能使用 `const`、`static` 和可见性修饰符来限制变量和方法的可见范围。

* **DO** 在所有公共 API 头文件中使用 doxygen 注释，并为 \[in,out\]
  [方向注解](http://www.doxygen.nl/manual/commands.html#cmdparam)。内部 API 头文件也建议这样做，但不是强制要求。

* **DON'T** 尽量不要使用全局变量。

* **DON'T** 不要使用缩写，除非它们已经是用户广泛熟知的术语（例如 "app"、"info"），或者是开发者必须使用的缩写（例如 "min"、"max"、"args"）。反例包括用 `num_widgets` 代替 `widget_count`，以及用 `opt_widgets` 代替 `option_widgets` 或 `optional_widgets`。

* **DON'T** 不要为那些必须在不同文件之间保持一致的内容硬编码 magic number。应根据情况使用 `#define`、枚举或 `const` 值。

* **DON'T** 尽量不要在整个项目中为同一个 C 函数名使用不同的原型。

* **DON'T** 不要使用被注释掉的代码，也不要使用 `#if 0` 或等价写法。确保所有代码都真的会被构建。

头文件
------------

* **DO** 确保任何头文件都可以直接包含，而不需要先包含其他头文件。也就是说，任何依赖都应当在头文件内部自行包含。

* **DO** 先包含本地头文件（使用 `""`），再包含系统头文件（使用 `<>`）。这有助于确保本地头文件不依赖别的内容先被包含，同时也与使用本地头文件作为预编译头的做法保持一致。

* **DO** 尽量按字母顺序列出头文件。这样可以避免重复包含，也能确保头文件可直接使用。

* **DO** 在所有头文件中使用 `#pragma once`，而不要用 ifdef 来检测重复包含。

风格指南
-----------

### 使用 `clang-format` 的自动格式化

对于所有 C/C++ 文件（`*.c`、`*.cpp` 和 `*.h`），我们使用 `clang-format`（具体版本 `11.0.1`）来应用代码格式规则。修改 C/C++ 文件后、合并前，请运行：

```sh
$ ./scripts/format-code
```

### 格式说明：

我们的编码约定遵循 [LLVM coding standards](https://llvm.org/docs/CodingStandards.html)，并做了如下覆盖性调整：

* 源码行 **MUST NOT** 超过 120 列。
* 单行 if/else/loop 代码块 **MUST** 使用花括号包裹。

请把格式化带来的改动和你的提交一起暂存，不要额外再提交一个“Format Code”提交。你的编辑器通常也可以配置为在编辑文件或区域时自动运行 `clang-format`。可参考：

- Emacs 的 [clang-format.el](https://github.com/llvm-mirror/clang/blob/master/tools/clang-format/clang-format.el)
- Vim 的 [vim-clang-format](https://github.com/rhysd/vim-clang-format)
- Visual Studio Code 的 [vscode-cpptools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)

[.clang-format](../.clang-format) 文件描述了脚本强制执行的风格，它基于 LLVM 风格，并做了一些更接近默认 Visual Studio 风格的修改。更多细节可参考 [clang-format style options](http://releases.llvm.org/3.6.0/tools/clang/docs/ClangFormatStyleOptions.html)。

如果你看到意外的格式变化，请确认你使用的是 LLVM 工具链 11 或更高版本。

### 许可证头

下面的许可证头 **必须** 放在每个代码文件的开头：

```c
// Copyright (c) Microsoft Corporation
// SPDX-License-Identifier: MIT
```

它应该带上对应文件的注释前缀。如果有充分理由不能包含这个头部，可以把文件加入 `.check-license.ignore`。

所有文件都会通过下面的脚本检查是否包含该头部：

```sh
$ ./scripts/check-license
```

### 命名约定

我们使用、但不由工具自动检查的命名约定包括：

1. 变量、成员/字段和函数名使用 `lower_snake_case`。
2. 宏名和常量使用 `UPPER_SNAKE_CASE`。
3. 头文件和源文件名尽量使用 `lower_snake_case`。
4. 名称尽量使用完整单词，不要使用缩写（例如用 `memory_context`，不要用 `mem_ctx`）。
5. 以 `_` 开头表示内部和私有字段或方法（例如 `_internal_field`、`_internal_method()`）。
6. 单个下划线（`_`）保留给局部定义（静态、文件作用域定义）。
   例如：`static ebpf_result_t _do_something(..)`。
7. `struct` 定义以 `_` 开头（这是对第 6 条的例外），并且总是创建一个带 `_t` 后缀的 `typedef`。例如：
```c
typedef struct _ebpf_widget
{
    uint64_t count;
} ebpf_widget_t;
```
8. 在全局命名空间中，eBPF 相关名称以 `ebpf_` 为前缀（例如 `ebpf_result_t`）。

总之，如果某个文件本身的风格与这些指南不同（例如私有成员用的是 `m_member` 而不是 `_member`），那么该文件里已有的风格优先。
