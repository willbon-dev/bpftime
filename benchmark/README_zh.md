# bpftime 的基准测试与性能评估

[`benchmark`](https://github.com/eunomia-bpf/bpftime/tree/master/benchmark) 目录包含 bpftime 项目的基准测试和实验内容，包括：

- 运行实验并生成图表的脚本
- 面向不同使用场景的基准测试环境
- 用于性能评估的测试代码

每个提交都会在 CI 中执行这些基准测试：[https://github.com/eunomia-bpf/bpftime/tree/master/.github/workflows/benchmarks.yml](https://github.com/eunomia-bpf/bpftime/tree/master/.github/workflows/benchmarks.yml)

结果会发布在：[https://eunomia-bpf.github.io/bpftime/benchmark/uprobe/results.html](https://eunomia-bpf.github.io/bpftime/benchmark/uprobe/results.html)

你可以阅读我们的 OSDI 论文 [Extending Applications Safely and Efficiently](https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng) 了解更多基准测试细节。

## 入门

### 安装依赖

请参考 [bpftime 构建与测试文档](https://eunomia.dev/bpftime/documents/build-and-test/) 了解如何安装依赖或使用 Docker 镜像。

基准测试脚本可能会自动安装依赖并从 GitHub 克隆仓库，请确保你的机器具备网络访问能力。

运行这些实验需要 Linux 内核支持 eBPF，至少 4 个 CPU 核心，16GB 内存，并且运行在 x86_64 架构上。

### 基本用法

基础用法请参考 [bpftime 使用文档](https://eunomia.dev/bpftime/documents/usage/)。更详细的用法请查看各个实验目录。

### 运行全部实验

在运行实验之前，你还需要为 Python 脚本安装一些额外依赖：

```sh
cd /path/to/bpftime
pip install -r benchmark/requirements.txt
```

随后可以通过以下命令构建并运行实验：

```sh
make benchmark # 构建基准测试
make run-all-benchmark # 运行全部基准测试
```

（构建时间：10 分钟到 20 分钟）

具体命令请参考 Makefile。

你也可以在 [.github/workflows/build-benchmarks.yml](https://github.com/eunomia-bpf/bpftime/tree/master/.github/workflows/benchmarks.yml) 中查看 CI 是如何构建并运行这些实验的。

## 实验概览

### 实验 1：微基准测试

这个实验用于衡量 bpftime 与传统内核 eBPF 在不同操作和使用场景下的性能开销与延迟差异。

示例结果如下：

> *生成于 2025-04-30 03:01:13*。环境信息

- **操作系统：** Linux 6.11.0-24-generic
- **CPU：** Intel(R) Core(TM) Ultra 7 258V（4 核，4 线程）
- **内存：** 15.07 GB
- **Python：** 3.12.7

核心 Uprobe 性能汇总

| Operation | Kernel Uprobe | Userspace Uprobe | Speedup |
|-----------|---------------|------------------|---------|
| __bench_uprobe | 2561.57 | 190.02 | 13.48x |
| __bench_uretprobe | 3019.45 | 187.10 | 16.14x |
| __bench_uprobe_uretprobe | 3119.28 | 191.63 | 16.28x |

内核与用户态 eBPF 的详细对比

| Operation | Environment | Min (ns) | Max (ns) | Avg (ns) | Std Dev |
|-----------|-------------|----------|----------|----------|---------|
| __bench_array_map_delete | Kernel | 2725.99 | 3935.98 | 3237.62 | 359.11 |
| __bench_array_map_delete | Userspace | 2909.07 | 3285.52 | 3096.46 | 114.99 |
| __bench_array_map_lookup | Kernel | 2641.18 | 4155.25 | 2992.88 | 402.00 |
| __bench_array_map_lookup | Userspace | 3354.17 | 3724.05 | 3486.81 | 108.63 |
| __bench_array_map_update | Kernel | 9945.97 | 14917.03 | 12225.93 | 1508.60 |
| __bench_array_map_update | Userspace | 4398.82 | 4841.92 | 4629.57 | 152.57 |
| __bench_hash_map_delete | Kernel | 18560.92 | 27069.99 | 22082.68 | 2295.90 |
| __bench_hash_map_delete | Userspace | 9557.35 | 11240.72 | 10253.54 | 473.67 |
| __bench_hash_map_lookup | Kernel | 10181.58 | 13742.86 | 12375.69 | 1142.61 |
| __bench_hash_map_lookup | Userspace | 20580.46 | 23586.77 | 22152.81 | 969.63 |
| __bench_hash_map_update | Kernel | 43969.13 | 61331.16 | 53376.22 | 5497.51 |
| __bench_hash_map_update | Userspace | 21172.05 | 25878.44 | 23992.67 | 1264.81 |
| __bench_per_cpu_array_map_delete | Kernel | 2782.47 | 3716.44 | 3183.09 | 287.23 |
| __bench_per_cpu_array_map_delete | Userspace | 2865.53 | 3409.70 | 3114.67 | 140.65 |
| __bench_per_cpu_array_map_lookup | Kernel | 2773.47 | 4176.10 | 3170.42 | 416.42 |
| __bench_per_cpu_array_map_lookup | Userspace | 6269.58 | 7395.49 | 7018.47 | 345.91 |
| __bench_per_cpu_array_map_update | Kernel | 10662.37 | 15923.08 | 12326.39 | 1522.21 |
| __bench_per_cpu_array_map_update | Userspace | 15592.15 | 17505.63 | 16528.99 | 553.50 |
| __bench_per_cpu_hash_map_delete | Kernel | 19709.29 | 26844.96 | 21994.95 | 2243.80 |
| __bench_per_cpu_hash_map_delete | Userspace | 55954.89 | 76124.07 | 65603.07 | 5986.58 |
| __bench_per_cpu_hash_map_lookup | Kernel | 10783.48 | 15208.46 | 12315.21 | 1525.86 |
| __bench_per_cpu_hash_map_lookup | Userspace | 48033.46 | 57481.09 | 50651.83 | 2503.34 |
| __bench_per_cpu_hash_map_update | Kernel | 31072.46 | 43163.81 | 35580.60 | 3748.51 |
| __bench_per_cpu_hash_map_update | Userspace | 73661.69 | 79157.12 | 76526.24 | 1868.13 |
| __bench_read | Kernel | 22506.85 | 30934.20 | 25865.43 | 3018.32 |
| __bench_read | Userspace | 1491.75 | 1862.13 | 1653.45 | 101.66 |
| __bench_uprobe | Kernel | 2130.54 | 4389.26 | 2561.57 | 628.77 |
| __bench_uprobe | Userspace | 166.54 | 232.13 | 190.02 | 16.11 |
| __bench_uprobe_uretprobe | Kernel | 2658.28 | 3859.19 | 3119.28 | 311.45 |
| __bench_uprobe_uretprobe | Userspace | 179.61 | 202.69 | 191.63 | 9.64 |
| __bench_uretprobe | Kernel | 2581.48 | 3916.19 | 3019.45 | 359.75 |
| __bench_uretprobe | Userspace | 175.54 | 196.49 | 187.10 | 7.66 |
| __bench_write | Kernel | 22783.52 | 31415.49 | 26478.92 | 2787.90 |
| __bench_write | Userspace | 1406.01 | 1802.50 | 1542.49 | 106.23 |

#### 第 1 部分：bpftime 与 eBPF 对比

性能对比包括：

- Uprobe/uretprobe（见 [./uprobe/](uprobe/README_zh.md)）
- 内存读写操作（见 [./uprobe/](uprobe/README_zh.md)）
- Map 操作（见 [./uprobe/](uprobe/README_zh.md)）
- 在程序中嵌入 VM 而不进行挂载（见 [./uprobe/](uprobe/README_zh.md) 以及 [test_embed.c](https://github.com/eunomia-bpf/bpftime/tree/master/benchmark/test_embed.c)）
- Syscall tracepoint（见 [./syscall/](syscall/README_zh.md)）
- MPK 启用/禁用（见 [./mpk/](mpk/README_zh.md)）

你可以查看各个目录中的实验详情、运行方式和结果。

（计算时间：20 分钟到 30 分钟）

#### 第 2 部分：执行引擎效率

这一部分评估不同 eBPF 虚拟机和 JIT 编译器的执行性能，用来比较它们运行 eBPF 程序的效率。

相关代码见我们的 [bpf-benchmark 仓库](https://github.com/eunomia-bpf/bpf-benchmark)。

#### 第 3 部分：加载延迟

这一部分测量加载并挂载 eBPF 程序所需的时间。

测量工具位于 [../tools/cli/main.cpp](https://github.com/eunomia-bpf/bpftime/tree/master/tools/cli/main.cpp)。

### 实验 2：SSL/TLS 流量检测（sslsniff）

这个实验展示了 bpftime 通过挂载 OpenSSL 函数，实时截获并检查 nginx 中 SSL/TLS 流量的能力，同时衡量性能影响和功能效果。

- 环境与结果：见 [./ssl-nginx/](ssl-nginx/README_zh.md)
- 示例代码：见 [../example/tracing/sslsniff](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/sslsniff)

### 实验 3：系统调用计数（syscount）

这个实验评估 bpftime 跟踪并统计 nginx 等应用发起的系统调用的能力，并将其开销和准确性与内核级跟踪进行比较。

- 环境与结果：见 [./syscount-nginx/](syscount-nginx/README_zh.md)
- 示例代码：见 [../example/tracing/syscount](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/syscount)

### 实验 4：Nginx 插件/模块

这个实验展示了 bpftime 如何作为 nginx 的插件或模块集成进去。

- 实现代码：见 [../example/attach_implementation](https://github.com/eunomia-bpf/bpftime/tree/master/example/attach_implementation)
- 基准脚本包含在实现目录中

### 实验 5：DeepFlow

这个实验衡量将 bpftime 集成到可观测平台 DeepFlow 后带来的性能影响，用于评估用户态 eBPF 对网络监控和跟踪工作负载的影响。

DeepFlow 集成的性能评估见 [./deepflow/](deepflow/README_zh.md) 目录。

### 实验 6：FUSE（用户态文件系统）

这个实验评估 bpftime 在为基于 FUSE 的文件系统做插桩并缓存系统调用结果时的性能。

FUSE 相关基准见 [./fuse/](fuse/README_zh.md) 目录。

### 实验 7：Redis 持久性调优

这个实验展示了如何利用 bpftime 在运行时动态调节 Redis 的持久化配置，并衡量用户态扩展对数据库优化的性能收益。

Redis 持久性调优基准见 [./redis-durability-tuning/](redis-durability-tuning/README_zh.md) 目录。

### 实验 8：兼容性

这个实验验证现有 eBPF 程序能否在内核 eBPF 和 bpftime 上无需修改地顺利运行，从而展示用户态 eBPF runtime 的兼容性和可移植性。

可在内核 eBPF 和 bpftime 上运行的兼容性示例见 [../example](https://github.com/eunomia-bpf/bpftime/tree/master/example) 目录。
