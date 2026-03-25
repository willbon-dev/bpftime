# Thread Scheduling 示例

这个示例演示如何使用 bpftime 的 GPU eBPF tracing，把 CUDA 线程映射到它们的硬件执行单元：Streaming Multiprocessor（SM）、warp 和 lane。

## 概览

这个示例由两个主要部分组成：

1. **向量加法 CUDA 应用**（`vec_add`）：一个简单的 CUDA 应用，会在 GPU 上反复执行向量加法。
2. **eBPF CUDA Probe**（`threadscheduling`）：一个挂载到 CUDA kernel 函数上的 eBPF 程序，用于监控其执行和线程调度。

当 CUDA kernel 执行时，GPU scheduler 会把 thread block 分配给 Streaming Multiprocessor（SM）。在每个 SM 内，线程会被分组为 32 个线程的 warp，并以 lockstep 方式执行。

## GPU 硬件概念

| Concept | Description | PTX Register |
|---------|-------------|--------------|
| **SM (Streaming Multiprocessor)** | GPU 上的物理处理单元。多个 SM 会并行运行。 | `%smid` |
| **Warp** | 在某个 SM 上以 lockstep 方式执行的一组 32 个线程。 | `%warpid` |
| **Lane** | 线程在其 warp 内的相对位置（0-31）。 | `%laneid` |

## eBPF Helpers

这个示例使用了三个 GPU eBPF helper：

| Helper ID | Function | Description |
|-----------|----------|-------------|
| 509 | `bpf_get_sm_id()` | 返回当前线程执行所在的 SM ID |
| 510 | `bpf_get_warp_id()` | 返回当前线程在 SM 内的 warp ID |
| 511 | `bpf_get_lane_id()` | 返回当前线程在 warp 内的 lane ID（0-31） |

## 构建示例

```bash
# 从 bpftime 根目录开始，启用 CUDA 支持构建
cmake -Bbuild -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda .
cmake --build build -j$(nproc)

# 构建这个示例
make -C example/gpu/threadscheduling
```

## 运行示例

你需要两个终端：

### 终端 1：启动 eBPF 程序（Server）

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/threadscheduling/threadscheduling
```

### 终端 2：运行 CUDA 应用（Client）

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/threadscheduling/vec_add [num_blocks] [threads_per_block]
```

可选参数：
- `num_blocks`：thread block 数量（默认：4）
- `threads_per_block`：每个 block 的线程数（默认：64）

自定义配置示例：
```bash
# 运行 8 个 block，每个 block 128 个线程
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/threadscheduling/vec_add 8 128
```

## 输出解读

probe 会显示：

### SM 利用率直方图
显示线程如何分布到各个 SM 上：
```
┌─ SM Utilization Histogram ─────────────────────────────────────────┐
│  SM  0: ████████████████████████████████████████     64 threads    │
│  SM  1: ████████████████████████████████████████     64 threads    │
│  SM  2: ████████████████████████████████████████     64 threads    │
│  SM  3: ████████████████████████████████████████     64 threads    │
│                                                                    │
│  Total threads: 256       Active SMs: 4                            │
└────────────────────────────────────────────────────────────────────┘
```

### 每个 SM 的 Warp 分布
显示每个 SM 上哪些 warp 是活跃的：
```
┌─ Warp Distribution per SM ─────────────────────────────────────────┐
│  SM   │ Warp ID │ Thread Count                                     │
├───────┼─────────┼──────────────────────────────────────────────────┤
│    0  │     0   │       32                                         │
│    0  │     1   │       32                                         │
│    1  │     0   │       32                                         │
│    1  │     1   │       32                                         │
└───────┴─────────┴──────────────────────────────────────────────────┘
```

### Thread-to-Hardware Mapping 示例
显示单个线程的分配情况：
```
┌─ Thread-to-Hardware Mapping Samples ───────────────────────────────┐
│  Block(x,y,z)  │ Thread(x,y,z) │  SM  │ Warp │ Lane │              │
├────────────────┼───────────────┼──────┼──────┼──────┼──────────────┤
│  (  0, 0, 0)   │  (  0, 0, 0)  │    2 │    0 │    0 │              │
│  (  0, 0, 0)   │  ( 31, 0, 0)  │    2 │    0 │   31 │              │
│  (  1, 0, 0)   │  (  0, 0, 0)  │    5 │    0 │    0 │              │
└────────────────┴───────────────┴──────┴──────┴──────┴──────────────┘
```

### 负载均衡分数
一个百分比，表示线程在各个 SM 之间分布得有多均匀：
- 100% = 完美分布（所有 SM 负载相同）
- 更低的值表示负载分布不均

## 使用场景

### 1. 验证 block 到 SM 的分布
用不同的 block 数量运行，观察 GPU scheduler 如何分配工作：
```bash
# 少量 block - 可能不会用到所有 SM
./vec_add 2 64

# 大量 block - 应该会分布到所有 SM
./vec_add 16 64
```

### 2. 调试 persistent kernel
对于 persistent kernel 设计（每个 SM 一个 block），可以通过“每个 SM 一个 block”的方式验证每个 block 是否映射到了唯一的 SM：

不同 GPU 的 SM 数量不同，因此你需要相应调整 `block` 大小：
```bash
# 例如 RTX 3090（82 个 SM）
./vec_add 82 64

# 例如 RTX 4090（128 个 SM）
./vec_add 128 64
```

### 3. 分析 warp occupancy
检查 warp 在 block 内的分布：
```bash
# 128 线程 = 每个 block 4 个 warp
./vec_add 4 128

# 256 线程 = 每个 block 8 个 warp
./vec_add 4 256
```

## 实现细节

eBPF probe（`threadscheduling.bpf.c`）挂载到 `vectorAdd` CUDA kernel，并且：

1. 通过 helper 509-511 读取硬件调度寄存器
2. 在 BPF hash map 中记录 thread-to-hardware 映射
3. 维护 SM 和 warp 直方图用于分析
4. 为每个 warp 的第一个线程输出调试信息

userspace loader（`threadscheduling.c`）会周期性地：

1. 读取 BPF map
2. 计算统计数据和直方图
3. 显示映射可视化结果
