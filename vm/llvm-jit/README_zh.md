# 具备 LLVM JIT/AOT 编译器的用户态 eBPF VM

[![Build and Test VM](https://github.com/eunomia-bpf/llvmbpf/actions/workflows/test-vm.yml/badge.svg)](https://github.com/eunomia-bpf/llvmbpf/actions/workflows/test-vm.yml)
[![codecov](https://codecov.io/gh/eunomia-bpf/llvmbpf/graph/badge.svg?token=ZQXHpOwDa1)](https://codecov.io/gh/eunomia-bpf/llvmbpf)

这是一个基于 LLVM 的高性能、多架构 JIT/AOT 编译器和虚拟机（VM）。

这个组件属于 [bpftime](https://github.com/eunomia-bpf/bpftime) 项目，但只专注于核心 VM。它提供以下能力：

- 可作为 `独立的 eBPF VM 库` 或编译工具运行
- 将 eBPF bytecode 编译为 LLVM IR 文件
- 将 eBPF ELF 文件编译为 AOT 后的 native code ELF object 文件，可像 C 编译出来的对象文件一样链接，或加载进 llvmbpf
- 在 eBPF runtime 中加载并执行 AOT 编译后的 ELF object 文件
- 支持 eBPF helpers 和 maps 的 lddw 函数
- **GPU 执行支持**：
  - **为 NVIDIA CUDA GPU 生成 PTX**，并自动检测 compute capability
  - **为跨厂商 GPU 生成 SPIR-V**（Intel、AMD、NVIDIA、ARM），通过 OpenCL/Vulkan 运行

这个 library 针对性能、灵活性和最小依赖进行了优化。它不包含 eBPF 应用所需的 maps、helpers、verifiers 或 loaders，因此适合作为轻量级、高性能库使用。

如果你需要一个完整的用户态 eBPF runtime，支持 maps、helpers，并且能够像内核一样在用户态无缝执行 Uprobe、syscall trace、XDP 等 eBPF 程序，请参考 [bpftime](https://github.com/eunomia-bpf/bpftime) 项目。

- [Userspace eBPF VM with LLVM JIT/AOT Compiler](#userspace-ebpf-vm-with-llvm-jitaot-compiler)
  - [构建项目](#build-project)
  - [用法](#usage)
    - [将 llvmbpf 作为库使用](#use-llvmbpf-as-a-library)
    - [将 llvmbpf 作为 AOT 编译器使用](#use-llvmbpf-as-a-aot-compiler)
    - [从 ELF 文件加载 eBPF bytecode](#load-ebpf-bytecode-from-elf-file)
    - [maps 和 data relocation 支持](#maps-and-data-relocation-support)
    - [构建为可部署的独立二进制](#build-into-standalone-binary-for-deployment)
    - [GPU 执行](#gpu-execution)
      - [NVIDIA CUDA GPU 的 PTX](#ptx-for-nvidia-cuda-gpus)
      - [跨厂商 GPU 的 SPIR-V](#spir-v-for-cross-vendor-gpus)
  - [优化](#optimizaion)
    - [内联 maps 和 helper function](#inline-the-maps-and-helper-function)
    - [直接使用 C 代码生成的 LLVM IR](#use-original-llvm-ir-from-c-code)
  - [测试](#test)
    - [单元测试](#unit-test)
    - [bpf-conformance 测试](#test-with-bpf-conformance)
  - [许可证](#license)

## 构建项目

```sh
sudo apt install llvm-15-dev libzstd-dev
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target all -j
```

## 用法

### 将 llvmbpf 作为库使用

请参考 [example](example/main.cpp) 查看如何把这个库作为 VM 使用。

### 将 llvmbpf 作为 AOT 编译器使用

先构建 cli：

```sh
sudo apt-get install libelf1 libelf-dev
cmake -B build  -DBUILD_LLVM_AOT_CLI=1 
```

你可以使用 cli 从 eBPF bytecode 生成 LLVM IR：

```console
# ./build/cli/bpftime-vm build .github/assets/sum.bpf.o -emit-llvm > test.bpf.ll
...
```

也可以把 AOT 后的 eBPF 程序直接运行起来。

### 从 ELF 文件加载 eBPF bytecode

你可以把 llvmbpf 和 libbpf 一起使用，直接从 `bpf.o` ELF 文件加载 eBPF bytecode。

不过 `bpf.o` ELF 文件本身没有 map 和 data relocation 支持。我们建议使用 bpftime 来从 ELF 文件加载并完成 relocation。

### maps 和 data relocation 支持

bpftime 已经支持 maps 和 data relocation。最简单的用法是像 kernel eBPF 一样编写 loader 和 eBPF program。

eBPF 可以通过两种方式与 maps 交互：

- 使用 helper function 访问 maps，例如 `bpf_map_lookup_elem`、`bpf_map_update_elem` 等
- 把 maps 当作 eBPF 程序里的全局变量直接访问

### 构建为可部署的独立二进制

### GPU 执行

#### NVIDIA CUDA GPU 的 PTX

#### 跨厂商 GPU 的 SPIR-V

## 优化

### 将 maps 和 helper function 内联

### 使用来自 C 代码的原始 LLVM IR

## 测试

### 单元测试

### 使用 bpf-conformance 测试

## 许可证
