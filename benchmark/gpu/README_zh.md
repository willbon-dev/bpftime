# 使用 BPF 和 NVBit 探针的 CUDA 向量加法基准测试

这个基准测试演示了一个简单的 CUDA 向量加法操作，并附加 eBPF 与 NVBit 探针来监控其执行过程。

**重要：** 除非另有说明，所有命令都应在 bpftime 项目根目录下运行。

## 性能结果（10,000 次迭代）

| Device | Baseline | BPF (bpftime) | NVBit |
|--------|----------|---------------|-------|
| **NVIDIA P40** | 51.8 μs | 81.1 μs (1.56x) | 174.4 μs (3.37x) |
| **NVIDIA RTX 5090** | 4.1 μs | 8.2 μs (2.0x) | 55.8 μs (13.6x) |

## 概述

这个基准测试包含以下组件：

1. **vec_add.cu**：执行向量加法的 CUDA kernel，可配置迭代次数。
2. **cuda_probe.bpf.c**：挂载到 CUDA kernel 并进行监控的 eBPF 程序：
   - kernel 调用次数
   - 总执行时间
   - 每次调用的平均执行时间
3. **cuda_probe.c**：用于加载并挂载 eBPF 程序的用户态程序。
4. **nvbit_vec_add.cu** 和 **nvbit_timing_funcs.cu**：使用 NVBit 框架提供类似监控能力的插桩工具。

## 前置条件

- CUDA Toolkit（已在 CUDA 11.x 及以上版本测试）
- 支持 BPF 目标的 LLVM/Clang
- libbpf
- NVBit（用于 NVBit 插桩方案）

## 构建

构建所有组件：

```bash
make
```

这会构建：
- `vec_add` CUDA 基准程序
- `cuda_probe.bpf.o` BPF 目标文件
- `cuda_probe` 用户态加载器
- `nvbit_vec_add.so` NVBit 插桩工具

## 运行基准测试

### 使用 BPF 探针运行

1. 运行附加了 BPF 探针的基准测试：

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  benchmark/gpu/micro/cuda_probe
# 在另一个终端中
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  benchmark/gpu/workload/vec_add
```

这会：
- 在后台启动 BPF 探针
- 运行 100 次迭代的 CUDA 基准测试
- 显示探针统计信息
- 终止探针进程

2. 分开运行各个组件：

先启动 BPF 探针：
```bash
./cuda_probe
```

在另一个终端中运行基准测试：
```bash
./vec_add [iterations]
```

其中 `iterations` 是可选参数（默认值：10），表示 kernel 启动次数。

### 使用 NVBit 插桩运行

1. 运行 NVBit 插桩版本：

```bash
make run_nvbit
```

这会：
- 加载 NVBit 插桩工具
- 运行 100 次迭代的 CUDA 基准测试
- 输出每次 kernel 调用的时间信息
- 在末尾显示 kernel 统计汇总

2. 查看更详细输出：

```bash
make run_nvbit_verbose
```

这会在执行过程中显示更多信息。

## 预期输出

### CUDA 基准测试输出

CUDA 基准测试会输出如下时间信息：
```
Running benchmark with N iterations...
Benchmark results:
Total time: XXX ms
Average kernel time: XXX ms
Validation check: C[0] = 0, C[1] = 3
```

### BPF 探针输出

BPF 探针会持续输出：
```
PID XXX: kernel calls = N, total time = XXX ns, avg = XXX ns
```

### NVBit 插桩输出

NVBit 工具会显示每个 kernel 的耗时：
```
NVBit: Minimal Vector Addition Instrumentation Tool
------------------------------------------------
NVBit: Kernel _Z9vectorAddPKfS0_Pf - Time: XXX.XXX us
...

NVBit Instrumentation Summary:
Total kernel calls: XXX
Total execution time: XXX.XXX ms
Average kernel time: XXX.XXX us
```

## 对比

这个基准测试用于比较 BPF 与 NVBit 两种 CUDA 插桩方式：

1. **BPF**：使用 Linux 的 eBPF 基础设施挂载到 kernel 函数，提供系统级监控，并尽量降低开销。

2. **NVBit**：使用 NVIDIA 的二进制插桩工具在运行时修改 CUDA kernel 的 SASS 代码，从而提供更细粒度的 GPU 信息，但开销通常更高。

## 清理

清理所有构建产物：

```bash
make clean
``` 

## only results

Device: NVIDIA P40

baseline:

```console
# benchmark/gpu/workload/vec_add
Running benchmark with 10000 iterations...
Benchmark results:
Total time: 518076 us
Average kernel time: 51.8076 us
Validation check: C[0] = 0, C[1] = 3
```

NVbit:

```console
Running benchmark with 10000 iterations...
Benchmark results:
Total time: 1.74412e+06 us
Average kernel time: 174.412 us
Validation check: C[0] = 0, C[1] = 3
```

BPF:

```console
Running benchmark with 10000 iterations...
Benchmark results:
Total time: 810824 us
Average kernel time: 81.0824 us
Validation check: C[0] = 0, C[1] = 3
```

Device: NVIDIA RTX 5090

No trace:

```
$ benchmark/gpu/workload/vec_add
Running benchmark with 10000 iterations...
Benchmark results:
Total time: 40981.7 us
Average kernel time: 4.09817 us
Validation check: C[0] = 0, C[1] = 3
```

With bpftime:

```console  
Running benchmark with 10000 iterations...
Benchmark results:
Total time: 81883.6 us
Average kernel time: 8.18836 us
Validation check: C[0] = 0, C[1] = 3
```


with NVbit:

```console
$ make run_nvbit_verbose
CUDA_VISIBLE_DEVICES=0 LD_PRELOAD=./nvbit_vec_add.so TOOL_VERBOSE=1 ./vec_add
------------- NVBit (NVidia Binary Instrumentation Tool v1.7.6) Loaded --------------
Running benchmark with 10000 iterations...
Benchmark results:
Total time: 557560 us
Average kernel time: 55.756 us
Validation check: C[0] = 0, C[1] = 3
```
