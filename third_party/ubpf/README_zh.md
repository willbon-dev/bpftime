# uBPF

用户态 eBPF VM

[![Main](https://github.com/iovisor/ubpf/actions/workflows/main.yml/badge.svg)](https://github.com/iovisor/ubpf/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/iovisor/ubpf/badge.svg?branch=main&service=github)](https://coveralls.io/github/iovisor/ubpf?branch=main)

## 关于

这个项目的目标是创建一个使用 Apache 许可证的库，用于执行 eBPF 程序。eBPF 的主要实现位于 Linux kernel 中，但由于它采用 GPL 许可证，因此无法在许多项目中使用。

[Linux documentation for the eBPF instruction set](https://www.kernel.org/doc/Documentation/networking/filter.txt)

[Instruction set reference](https://github.com/iovisor/bpf-docs/blob/master/eBPF.md)

[API Documentation](https://iovisor.github.io/ubpf)

这个项目包含 eBPF 汇编器、反汇编器、解释器（适用于所有平台），以及 JIT 编译器（适用于 x86-64 和 Arm64 目标）。

## 检出源码

在执行下面关于 [构建](#building-with-cmake)、[测试](#running-the-tests)、[贡献](#contributing) 等说明之前，请先正确检出源码，并初始化子模块：

```
git submodule update --init --recursive
```

## 准备构建环境

为了让你的系统能够成功使用 CMake 生成构建系统，请按照下面的平台说明进行准备。

### Windows

在 Windows 上构建、编译和测试需要安装 Visual Studio（不是 VS Code，MSVC 编译器是必须的）。

> 注意：Visual Studio 有适合个人开发者的免费版本，即 community 版本。

你可以使用 VS Code，但 [仍然需要 Visual Studio](https://code.visualstudio.com/docs/cpp/config-msvc)。

另一个要求是你的 `PATH` 中必须有 [`nuget.exe`](https://learn.microsoft.com/en-us/nuget/install-nuget-client-tools)。你可以通过直接执行 `nuget.exe` 来检查主机是否满足这个条件：

```console
> nuget.exe
```

如果输出的是关于如何执行该程序的说明，就说明已经安装好了。安装了 `nuget.exe` 之后，`cmake` 配置系统会在生成构建系统时下载所需的开发库。

### macOS
首先，确保你安装了 XCode Command Line Tools：

```console
$ xcode-select --install
```

安装 XCode Command Line Tools 会同时安装 Apple 版的 Clang 编译器和其他开发工具。

uBPF 还要求主机上安装一些支持库。最简单的方式是：

1. 安装 [homebrew](https://brew.sh/)
2. 安装 [boost](https://www.boost.org/)：
```console
$ brew install boost
```
3. 安装 [LLVM](https://llvm.org/)（以及相关工具）：
```console
$ brew install llvm cmake
$ brew install clang-format
```

在 macOS 上开发和使用 uBPF 时，通过 Homebrew 安装 LLVM 是可选的。如果你计划通过编译 LLVM 并把 eBPF 程序存到 ELF 文件中，那么就必须安装。如果你确实安装了 Homebrew 版 LLVM，请在 `cmake` 配置命令里加上 `-DUBPF_ALTERNATE_LLVM_PATH=/opt/homebrew/opt/llvm/bin`：

```console
cmake -S . -B build -DUBPF_ENABLE_TESTS=true -DUBPF_ALTERNATE_LLVM_PATH=/opt/homebrew/opt/llvm/bin
```

### Linux

```bash
./scripts/build-libbpf.sh
```

## 使用 CMake 构建

用于在 Windows、Linux 和 macOS 平台上编译和测试 uBPF 的构建系统，可以通过 [`cmake`](https://cmake.org/) 生成：

```
cmake -S . -B build -DUBPF_ENABLE_TESTS=true
cmake --build build --config Debug
```

## 运行测试

### Linux 和 MacOS
```
cmake --build build --target test --
```

### Windows
```
ctest --test-dir build
```

## 贡献

我们非常欢迎贡献！

### 准备代码贡献

我们希望每次代码变更都能保持代码覆盖率。CI/CD 流水线会在贡献流程中验证这一点。不过，你也可以在本地计算代码覆盖率：

```console
coveralls --gcov-options '\-lp' -i $PWD/vm/ubpf_vm.c -i $PWD/vm/ubpf_jit_x86_64.c -i $PWD/vm/ubpf_loader.c
```

我们也希望保持一致的代码格式。uBPF 仓库配置的 pre-commit git hooks 会确保你的代码改动符合预期格式。为了让这些 hook 正常工作，你需要在系统中安装并可访问 `clang-format`。

## 将 C 编译为 eBPF

你需要 [Clang 3.7](http://llvm.org/releases/download.html#3.7.0)。

    clang-3.7 -O2 -target bpf -c prog.c -o prog.o

然后你可以把 `prog.o` 的内容传给 `ubpf_load_elf`，或者传给 `vm/test` 二进制的 stdin。

## 许可证

Copyright 2015, Big Switch Networks, Inc. Licensed under the Apache License, Version 2.0
<LICENSE.txt or http://www.apache.org/licenses/LICENSE-2.0>.
