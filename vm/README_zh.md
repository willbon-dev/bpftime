# bpftime Virtual Machine（VM）架构

bpftime VM 子系统提供了一个高性能、模块化的框架，用于在用户态执行 eBPF 程序。它具有多种执行 backend、高级优化能力，并能与 bpftime runtime 系统无缝集成。

## 架构概览

VM 子系统采用分层架构和清晰的抽象：

```
┌─────────────────────────────────────────────────────────────┐
│                    外部使用者                                │
├─────────────────────────────────────────────────────────────┤
│                 VM Core API（C 接口）                       │
│                    (vm-core/ebpf-vm.h)                      │
├─────────────────────────────────────────────────────────────┤
│              Compatibility Layer（C++ 接口）                │
│                 (compat/bpftime_vm_compat.hpp)              │
├─────────────┬─────────────────┬─────────────────────────────┤
│  LLVM JIT   │   uBPF Backend  │   Future Backends...        │
│  Backend    │                 │                              │
└─────────────┴─────────────────┴─────────────────────────────┘
```

示例请见 [example/main.cpp](example/main.cpp)。

## 构建

只构建 vm：

```sh
make build-llvm # 构建 llvm backend
make build-ubpf # 构建 ubpf backend
```

有关 LLVM JIT backend 的使用方式，请参见 [llvm-jit/README_zh.md](llvm-jit/README_zh.md)。

你也可以把 eBPF 的 llvm JIT/AOT 当作一个独立库在自己的目录中构建：

```sh
sudo apt install llvm-15-dev
cd llvm-jit
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target all -j
```

关于如何使用 [AOT compile](cli/README.md)，请查看 cli。

也请参见 [ubpf-vm/README.md](ubpf-vm/README.md)。

## 仅用于 VM 的 cli

这是一个仅在 VM 中加载和运行 eBPF 程序的工具。

```console
$ bpftime-cli
Usage: build/vm/cli/bpftime-cli <path to ebpf instructions> [path to memory for the ebpf program]
```

详情请见 [cli](cli/README.md)。由于 cli 依赖 libbpf 来加载 eBPF 程序，你需要在项目根目录下编译它：

```sh
make release-with-llvm-jit
```

更多信息请参见 [.github/workflows/test-aot-cli.yml](../.github/workflows/test-aot-cli.yml)。

## 组件

### 1. VM Core（`vm-core/`）

VM core 为外部使用者提供主要的 C API 接口。它只是一个薄封装，委托给兼容层处理，同时保持稳定的 C ABI。

### 2. Compatibility Layer（`compat/`）

兼容层为不同 VM backend 提供统一的 C++ 抽象。它采用 factory 模式来进行动态 backend 注册与选择。

### 3. LLVM JIT Backend（`llvm-jit/`）

这是基于 LLVM 基础设施的高性能 JIT/AOT 编译器，是生产环境的主要 backend。

### 4. uBPF Backend（`compat/ubpf-vm/`）

这是基于 uBPF 项目的轻量级解释器和基础 JIT backend。

## 设计模式

### Factory 注册模式

### 抽象 VM 接口

### LDDW Helper 系统

## VM Backends

### Backend 对比

### 选择 backend

## API 参考

### 核心 VM 操作

### Helper 函数管理

### 高级操作

## 高级特性

### GPU 执行支持

### Ahead-of-Time（AOT）编译

### Inline Map 操作

## 性能优化

### LLVM 优化流水线

### 内存管理

### 性能提示

## 集成指南

### 基本使用示例

### 与 bpftime Runtime 集成

## 开发指南

### 添加新的 VM backend

### 测试

### 调试
