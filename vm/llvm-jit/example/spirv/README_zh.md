# OpenCL/Vulkan 的 SPIR-V 生成

这个示例演示如何把 eBPF 程序编译为 SPIR-V，并通过 OpenCL 在 GPU 上执行。

## 概览

SPIR-V（Standard Portable Intermediate Representation - V）是一种面向并行计算和图形的跨厂商中间语言。与 NVIDIA 专有的 PTX 不同，SPIR-V 可以运行在：

- Intel GPUs
- AMD GPUs
- NVIDIA GPUs
- ARM Mali GPUs
- Qualcomm Adreno GPUs
- CPU 实现（pocl、Intel OpenCL CPU runtime）

## 需求

### 构建需求

- **LLVM 18+**（LLVM 20+ 具有原生 SPIR-V backend，LLVM 18-19 需要 `llvm-spirv` translator）
- **OpenCL development files**

### 运行需求

- OpenCL ICD loader
- 对应硬件的 OpenCL driver

## 构建

```bash
# Install LLVM 20 (recommended for native SPIR-V support)
sudo apt install llvm-20-dev

# Configure with SPIR-V support
cmake -B build -DCMAKE_BUILD_TYPE=Release \
    -DLLVMBPF_ENABLE_SPIRV=1 \
    -DLLVM_DIR=/usr/lib/llvm-20/cmake

# Build
cmake --build build --target spirv_opencl_test -j

# Run the example
./build/example/spirv/spirv_opencl_test
```

## 示例程序

测试程序演示：

1. eBPF Program 定义
2. SPIR-V 生成
3. OpenCL 执行
4. 结果验证

### eBPF Program

### 预期输出

## 验证 SPIR-V 输出

你可以使用 SPIR-V tools 验证生成的二进制：

```bash
# Install SPIR-V tools
sudo apt install spirv-tools

# Validate the binary
spirv-val bpf_program.spv

# Disassemble to human-readable format
spirv-dis bpf_program.spv -o bpf_program.spvasm
```

## 架构细节

### 编译流水线

### SPIR-V 与 PTX 对比

### 相比 PTX 的关键差异

## 故障排查

### `"SPIR-V target not found"`

### `"OpenCL implementation may not support SPIR-V IL"`

### OpenCL 构建错误

### 找不到 OpenCL 设备

## 高级用法

### 与 Vulkan Compute 配合使用

### Helper Functions

## 实现历史与技术深入

### 为什么加入 SPIR-V 支持

### 实现阶段

## 测试与验证

### 测试硬件配置

### 验证流程

## 性能特征

### 编译时间

### 运行时性能

## 已知限制与未来工作

### 当前限制

### 可能的改进

## 调试技巧

### 启用详细日志

### 检查生成的 LLVM IR

### 验证 SPIR-V 结构

### 常见 OpenCL 错误与解决方案

### 调试 OpenCL 执行

## 参考
