# launchlate - CUDA kernel launch 延迟分析器

## 概览

你的 GPU kernel 可能只执行几微秒，但应用却莫名其妙地很慢。传统 profiler 能看到 kernel 执行时间，却看不到 kernel 从 CPU 发出到真正开始在 GPU 上执行之间要等多久。这个“launch latency”可能由 stream 依赖、资源竞争或 driver 开销造成，尤其对于短生命周期 kernel，它带来的延迟可能比 kernel 自身执行时间大 10-100 倍。

`launchlate` 会测量 CPU 上 `cudaLaunchKernel()` 调用与 GPU 上 kernel 真正开始执行之间的时间差。它能揭示隐藏的排队延迟、调度开销和同步成本，这些东西会让本来很快的 kernel 在生产环境里变慢。

## 理解 kernel launch 延迟

当你从 CPU 代码里调用 `cudaLaunchKernel()` 时，你并不是直接让 GPU 开始执行，而是在排队工作。实际发生的是：

1. **CPU 把 kernel 入队**到 CUDA stream 中（微秒级）
2. **Driver 处理命令**并准备 kernel 参数
3. **调度器等待**资源和前序操作完成
4. **GPU 最终接收到** kernel 并开始执行
5. **Streaming multiprocessor** 开始运行你的代码

步骤 1 和步骤 5 之间的时间就是 launch latency。在理想情况下，它可能只有 5-20 微秒。但在有多个 stream、复杂依赖、内存压力或 GPU 忙碌的生产环境里，这个时间可能膨胀到毫秒级，甚至比 kernel 本身执行时间还长。

## 这个工具测量什么

`launchlate` 使用双 probe 方法来捕获 launch latency 缺口的两侧：

1. **CPU 侧 uprobe** 挂在 `cudaLaunchKernel()` 上 - 捕获 kernel 从 host 代码发出的时刻
2. **GPU 侧 kprobe** 挂在真实的 kernel 函数上 - 捕获 device 侧开始执行的时刻
3. **时间关联** - 计算 launch 与执行之间的差值，并做时钟校准
4. **直方图分析** - 将延迟分类到从纳秒到秒的不同区间

结果是一个实时直方图，展示 launch latency 的分布模式，揭示传统 profiler 看不到的现象。

## 为什么这很重要

### Stream 依赖开销

你的推理流水线会按顺序运行多个 kernel。每个 kernel 只执行 100μs，所以你预期 10 个 kernel 总共只要 1ms。但 `launchlate` 显示大多数 kernel 的 launch latency 有 200-500μs，因为每个 kernel 都要等前一个执行完、等内存传输完成、等 GPU scheduler 处理队列。总时间其实是 3-5ms，而不是 1ms。解决方法：使用 CUDA graphs 批量 launch，或者用 persistent kernel 消除每次 launch 的开销。

### 小 kernel 的 launch 开销

你写了整洁、模块化的代码，里面有很多小而专门的 kernel。每个 kernel 只跑 10-20μs，但 `launchlate` 揭示每个 kernel 的 launch latency 有 30-80μs，也就是说你花在 launch 上的时间比执行还多 3-5 倍。这就是典型的小 kernel 陷阱：当 kernel 太小时，固定的 launch 成本（driver 处理、队列管理、资源分配）会占主导。把多个 kernel 融合，或者批量工作来摊销 launch 成本。

### 上下文切换带来的尾延迟

你的 GPU 推理服务运行得很顺，P50 launch latency 是 25μs，但 P99 却飙到 2ms，引发超时错误。`launchlate` 的直方图显示 1-10ms 档有一个小但稳定的尖峰。原因是 GPU 被多个进程共享（监控程序、其他服务），偶尔的 CUDA context switch 会额外增加毫秒级开销。解决方案：给每个服务独占 GPU，使用 MPS（Multi-Process Service），或者通过增加 timeout 来容纳尾延迟。

### PCIe 争用

你的应用在做 GPU 推理的同时，还在通过一个 100Gb NIC 传输数据，而且这块 NIC 和 GPU 共享同一个 PCIe root complex。大多数 kernel launch 都很快，但 `launchlate` 显示会周期性地出现 500μs-2ms 的尖峰，并且与网络突发流量相关。GPU 和 NIC 正在争抢 PCIe 带宽，当 NIC 把总线打满时，GPU 命令就会排队等待 PCIe 访问。解决方案：把设备分布到多个 PCIe root complex 上，或者调度网络 I/O 和 GPU 工作，避免重叠。

## 构建示例

```bash
# 进入 bpftime 根目录
cd bpftime

# 先构建 bpftime 主工程
cmake -Bbuild -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda .
cmake --build build -j$(nproc)

# 构建示例
make -C example/gpu/launchlate-kernel-gpu-shared-map
```

## 运行示例

你需要启动两个进程：

### 1. 启动 eBPF 程序（Server）

```bash
BPFTIME_LOG_OUTPUT=console BPFTIME_NOT_LOAD_PATTERN=cuda.*  BPFTIME_RUN_WITH_KERNEL=true bpftime load ./launchlate
```

该进程会加载 eBPF 程序并等待 CUDA 事件。

### 2. 运行 CUDA 应用（Client）

在另一个终端中：

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/agent/libbpftime-agent.so  example/gpu/launchlate/vec_add
```

这会在 bpftime agent 的配合下运行向量加法程序，并连接到第一个进程执行 eBPF。

## 示例输出

运行成功后，你会看到：

```
Clock calibration: REALTIME - MONOTONIC = 1625284901234 ns
  MONOTONIC: 3842.123456789
  REALTIME:  1625288743.357890890

Monitoring CUDA kernel launch latency... Hit Ctrl-C to end.

12:34:56 Launch Latency Distribution:
latency         : count    distribution
100ns-1us       : 45       |********
1-10us          : 234      |****************************************
10-100us        : 167      |*****************************
100us-1ms       : 89       |***************
1-10ms          : 12       |**
Total samples: 547
```

这表示：
- CPU monotonic clock 和 GPU timer 之间的时钟校准
- 实时 launch latency 直方图
- 展示大多数延迟落在哪个区间的分布图

## 使用场景

- **诊断尾延迟**：通过识别 launch latency 何时飙升，理解为什么 P99 请求延迟是 P50 的 10 倍
- **优化 kernel 粒度**：看自己花在 launch 上的时间是不是比执行还多
- **调试异步性能缺口**：测量 kernel 等待前序操作时真实的队列延迟
- **多租户 GPU 故障排查**：多个进程共享 GPU 时识别 context switch 开销
- **系统级瓶颈**：检测 PCIe 争用、driver CPU 开销或资源分配延迟
- **验证优化**：量化 CUDA graphs、kernel fusion 或 persistent kernel 带来的改进

## 工作方式

1. **CPU 侧 uprobe** 挂在 `cudaLaunchKernel()` 上，捕获 kernel 何时被 launch，并记录时间戳
2. **GPU 侧 kprobe** 挂在 kernel 函数上，捕获真正开始执行的时刻
3. **时钟校准** 同步 CPU 和 GPU 计时器，以便精确比较
4. **延迟计算** 计算时间差并更新直方图
5. **实时显示** 每隔几秒显示一次直方图，揭示 launch latency 模式

## 代码结构

- **`launchlate.bpf.c`**：在 CPU（uprobe）和 GPU（kprobe）上运行的 eBPF 程序，用于捕获时间戳并计算延迟直方图
- **`launchlate.c`**：加载 eBPF 代码、校准时钟并显示直方图的 userspace 程序
- **`vec_add.cu`**：用于测试的示例 CUDA 应用，会反复 launch kernel

## 局限性

- 需要 kernel 函数符号名（使用 `cuobjdump -symbols your_app | grep kernel_name`）
- 长时间运行时时钟漂移可能影响精度（必要时请定期重新校准）
- 一次只能跟踪一个 kernel 函数（如需多个 kernel，请挂载多个 probe）

## 自定义

要跟踪你自己的 kernel，请修改 `launchlate.bpf.c` 中的 kprobe 目标：

```c
SEC("kprobe/_Z15yourKernelNamePfS_")  // 替换为你 kernel 的 mangled 名称
```

查找 kernel 的符号名：
```bash
cuobjdump -symbols your_app | grep your_kernel_name
```

## 结果解读

**很好**：大多数 launch 都低于 100μs
```
1-10us    : 450  |****************************************
10-100us  : 89   |********
```

**警告**：1ms 以上出现明显尾延迟
```
100us-1ms : 234  |********************
1-10ms    : 367  |********************************
```
检查 stream 依赖或多租户问题

**问题**：大量 launch 超过 10ms
```
10-100ms  : 245  |****************************************
100ms-1s  : 123  |********************
```
这是严重瓶颈——检查 context switch、PCIe 争用或 driver 问题

## 故障排查

**没有输出**：kprobe 中的 kernel 名称必须完全匹配（包括 C++ mangling）

**基线延迟过高**：检查 GPU 是否处于省电模式，或者是否被其他进程共享

**周期性尖峰**：可能意味着 context switch、PCIe 争用或 driver CPU 开销
