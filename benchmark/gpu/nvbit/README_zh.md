# CUDA 基准测试的 NVBit 插桩工具

本目录包含一个基于 NVBit 的插桩工具，用于以较低开销监控 CUDA kernel 执行。

## 概述

NVBit（NVIDIA Binary Instrumentation Tool）是一个研究原型，它允许通过拦截 CUDA driver API 调用，并在需要时把代码注入到 SASS 级别的 kernel 中，对 CUDA 应用进行动态插桩。

这个工具提供：
- kernel 启动计数
- 使用 CUDA event 进行逐个 kernel 的执行计时
- 在应用结束时输出汇总统计

## 文件

- **nvbit_vec_add.cu** - 主要的 NVBit 插桩工具（host 代码）
- **nvbit_timing_funcs.cu** - 用于插桩的 device 函数（当前未使用）
- **Makefile** - NVBit 工具的构建配置

## 前置条件

- **NVBit**：从 [https://github.com/NVlabs/NVBit](https://github.com/NVlabs/NVBit) 下载
  - 期望位置：`~/nvbit_release_x86_64/`
  - 如果安装在其他位置，请在 Makefile 中设置 `NVBIT_PATH`
- **CUDA Toolkit**：11.0 或更高版本
- **GCC**：兼容 C++11 的编译器

## 构建

构建 NVBit 插桩工具：

```bash
cd /path/to/bpftime/benchmark/gpu/nvbit
make
```

这会生成 `nvbit_vec_add.so`，一个可以通过预加载方式插桩 CUDA 应用的共享库。

### 构建选项

- **DEBUG=1**：以调试符号构建且不做优化
- **ARCH=sm_XX**：指定目标 GPU 架构（默认：`all`）
- **NVBIT_PATH**：覆盖 NVBit 安装路径

示例：
```bash
make DEBUG=1 ARCH=sm_75
```

## 用法

### 基本用法

要插桩 CUDA 应用，可使用 `LD_PRELOAD`：

```bash
export LD_PRELOAD=/path/to/nvbit_vec_add.so
./your_cuda_application
```

也可以写成一行：

```bash
LD_PRELOAD=/path/to/nvbit/nvbit_vec_add.so ./your_cuda_application
```

### 使用工作负载基准测试

在 vec_add 基准上测试：

```bash
cd ../workload
export LD_PRELOAD=/home/yunwei37/workspace/bpftime/benchmark/gpu/nvbit/nvbit_vec_add.so
./vec_add
```

在 matrixMul 基准上测试：

```bash
cd ../workload
export LD_PRELOAD=/home/yunwei37/workspace/bpftime/benchmark/gpu/nvbit/nvbit_vec_add.so
./matrixMul
```

### 环境变量

NVBit 支持若干环境变量（见 NVBit 横幅输出）：

- `NOBANNER=1` - 隐藏 NVBit 横幅
- `TOOL_VERBOSE=1` - 启用详细输出（如果工具实现了）
- `NVDISASM=/path/to/nvdisasm` - 覆盖 nvdisasm 位置

## 预期输出

加载工具后，你应该看到：

```
------------- NVBit (NVidia Binary Instrumentation Tool v1.7.6) Loaded --------------
NVBit: Minimal Vector Addition Instrumentation Tool
------------------------------------------------
```

如果插桩正常，每次 kernel 启动都会看到：

```
NVBit: Kernel kernel_name - Time: XXX.XXX us
```

在程序结束时：

```
NVBit Instrumentation Summary:
Total kernel calls: N
Total execution time: XXX.XXX ms
Average kernel time: XXX.XXX us
```

## 当前限制

**注意**：当前实现能够成功加载并让 CUDA 应用正常运行，但在工作负载基准测试所使用的 Runtime API 编译模式下，kernel 启动回调不会被触发。这是当前实现的已知限制。

### 为什么 kernel 计数不起作用

工作负载基准测试（`vec_add`、`matrixMul`）使用 `-cudart shared` 编译，这会使用 CUDA Runtime API。当前 NVBit 工具只拦截 CUDA Driver API 调用（`cuLaunchKernel`）。Runtime API 会包装 Driver API，而在较新的 CUDA 版本中，使用 shared runtime 时，回调可能不会像预期那样触发。

### 可行方案

1. **使用 Driver API 基准测试**：将基准重新编译为直接使用 CUDA Driver API
2. **拦截 Runtime API**：修改工具以拦截 `cudaLaunch*` 调用
3. **使用 NVBit device 插桩**：注入真正的 device 代码来统计 kernel 启动次数（需要正确的 device 代码注入）

## 性能开销

根据原始基准结果（见 `../README_zh.md`）：

| Device | Baseline | NVBit Overhead |
|--------|----------|----------------|
| **NVIDIA P40** | 51.8 μs | 174.4 μs (3.37x) |
| **NVIDIA RTX 5090** | 4.1 μs | 55.8 μs (13.6x) |

开销来源包括：
- kernel 的二进制插桩
- 运行时分析与回调开销
- 基于 event 的计时测量

## 与 BPFtime 的对比

与使用 bpftime 进行 eBPF 插桩相比：

| Approach | P40 Overhead | RTX 5090 Overhead | Notes |
|----------|--------------|-------------------|-------|
| **NVBit** | 3.37x | 13.6x | Binary instrumentation, GPU-level |
| **BPFtime** | 1.56x | 2.0x | System-level hooks, lower overhead |

## 清理

删除构建产物：

```bash
make clean
```

## 故障排查

### 工具加载了，但显示 0 次 kernel 调用

这是当前已知问题。工具加载成功，但不会拦截 Runtime API 的 kernel 启动。详见上面的“当前限制”。

### 段错误

- 确保 NVBit 版本与 CUDA 版本匹配
- 检查 CUDA toolkit 是否正确安装
- 验证 GPU 驱动版本兼容性

### 构建错误

- 确认 `NVBIT_PATH` 指向正确的 NVBit 安装
- 确保 CUDA toolkit 在 `PATH` 中
- 检查 GCC 版本是否与你的 CUDA 版本兼容

## 参考

- [NVBit GitHub Repository](https://github.com/NVlabs/NVBit)
- [NVBit Paper](https://ieeexplore.ieee.org/document/8891668)
- [CUDA Driver API Documentation](https://docs.nvidia.com/cuda/cuda-driver-api/)

## 许可证

该工具遵循 bpftime 项目的许可证。NVBit 本身由 NVIDIA 按照 BSD-3-Clause 许可证提供。
