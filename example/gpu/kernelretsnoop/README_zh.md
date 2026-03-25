# kernelretsnoop - CUDA kernel 每线程退出时间戳跟踪器

## 注意

环境变量 `BPFTIME_MAP_GPU_THREAD_COUNT` 应设置为更小的值（例如 10），以避免 `bad_alloc`。

## 概览

假设你在试图理解为什么 CUDA kernel 没有你预期的那么快。传统 profiling 工具会告诉你这个 kernel 运行了 10 毫秒，但这就像只知道一场马拉松花了 3 个小时，却不知道有一半选手在 5 英里处迷路了。你需要看到每个线程到底在做什么，以及它们到底什么时候完成工作。

`kernelretsnoop` 提供的正是这种可见性。它是一个基于 eBPF 的工具，会捕获每个 GPU 线程退出 CUDA kernel 的精确时刻，从而揭示传统 profiler 完全看不到的 timing 模式。

## 理解 GPU 线程

在深入了解 `kernelretsnoop` 之前，先理解我们在测什么。当你 launch 一个 CUDA kernel 时，你不只是运行一段代码，而是在 GPU 上并行启动成千上万甚至数百万个线程。

这些线程被组织成一个 3D grid。每个线程都有一个 (x, y, z) 坐标，用来标识它在 grid 中的位置。线程会被分组成 32 个线程一组的 “warp”，并以 lockstep 方式一起执行。这意味着理想情况下，一个 warp 里的 32 个线程应该同时做同样的事情。当它们没有做到这一点时，比如有些线程走了不同的代码路径，或者在等待慢速内存，warp 的效率就会下降，性能问题也就藏在这里。

问题在于，GPU 硬件和传统 profiler 只会展示聚合统计信息：kernel 总执行时间、平均 occupancy、内存吞吐量。它们无法告诉你线程 0 在 100 纳秒时就完成了，而线程 31 直到 850 纳秒才完成，或者处理数据边缘的线程总是比中间线程更慢。

## 这个工具捕获什么

`kernelretsnoop` 会挂载到 CUDA kernel 的退出点，并在每个完成的线程上记录：
- **线程 3D 坐标**（x, y, z）- 这个线程在 kernel launch grid 中的具体位置
- **GPU global timer 时间戳** - 这个线程完成执行的精确纳秒时间

这些简单的数据可以解锁关于 kernel 行为的强大洞察。

## 为什么这很重要

### 分歧 warp 的案例

你 launch 了一个有 1024 个线程的 kernel 来处理数组。运行 `kernelretsnoop` 时，你发现了意料之外的事情：

```
Thread (0, 0, 0) timestamp: 1749147474550023136
Thread (1, 0, 0) timestamp: 1749147474550023140  // +4ns
Thread (2, 0, 0) timestamp: 1749147474550023145  // +5ns
...
Thread (31, 0, 0) timestamp: 1749147474550023890 // +750ns later!
```

线程 0 到 30 都在几纳秒之内完成，完全符合 lockstep 执行的预期。但线程 31 晚了 750 纳秒才完成。怎么回事？

你检查 kernel 代码后发现，线程 31 遇到了一个边界条件。它在处理 chunk 的最后一个元素时，触发了额外的边界检查，或者在代码里走了不同的分支。由于 32 个线程作为一个 warp 一起执行，当线程 31 走上这条不同路径时，整个 warp 会被强制串行：先执行线程 0-30 的公共路径，再执行线程 31 的特殊路径。这就是 **thread divergence**，它正在杀死你的性能。

有了这个洞察，你可以重构代码，消除这个分歧分支，确保 warp 内所有线程走同一条路径。修改之后，所有线程会在几纳秒内同时完成。

### 内存访问之谜

在另一个 kernel 里，当你分析时间戳时，可能会看到这样的模式：

```
Thread (0, 0, 0) timestamp: 1749147474550023140
Thread (8, 0, 0) timestamp: 1749147474550023890  // Much slower
Thread (16, 0, 0) timestamp: 1749147474550023150
Thread (24, 0, 0) timestamp: 1749147474550023900 // Much slower again
```

每隔 8 个线程就会慢很多。这指向了一个 **memory access pattern problem**。你意识到你的数据结构导致每第 8 个线程访问了不同的 memory bank，从而产生 bank conflict；更糟的情况是，这些线程会触发 cache miss，而其他线程命中了 cache。

通过把线程索引和时间关联起来，你已经精确找到了哪些线程遇到了内存瓶颈。现在你可以重构数据布局，确保 coalesced memory access，也就是让连续线程访问连续的内存地址。这是 GPU 最擅长的访问模式。

### 理解 warp 调度

如果你跨多个 warp 分析时间戳，可能会发现 warp 并不是全部并行执行的：

```
Warp 0 (threads 0-31):   finish around timestamp 1749147474550023000
Warp 1 (threads 32-63):  finish around timestamp 1749147474550025000  // 2μs later
Warp 2 (threads 64-95):  finish around timestamp 1749147474550027000  // 4μs later
```

这表明你的 kernel 受到了资源限制，也许是寄存器使用量或 shared memory 使用量太高，导致 warp 只能串行执行，而不是并行执行。现在你就知道该从哪里优化了：降低寄存器压力或 shared memory 使用量，以提高并行度。

## 构建

```bash
# 从 bpftime 根目录
make -C example/gpu/kernelretsnoop
```

要求：
- 已构建带 CUDA 支持的 bpftime（`-DBPFTIME_ENABLE_CUDA_ATTACH=1`）
- 已安装 CUDA toolkit

## 运行

### 终端 1：启动 tracer
```bash
BPFTIME_SHM_MEMORY_MB=1000 BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/kernelretsnoop/kernelretsnoop
```

### 终端 2：运行你的 CUDA 应用
```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/kernelretsnoop/vec_add
```

或者跟踪任意 CUDA 应用：
```bash
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  ./your_cuda_app
```

## 示例输出

```
Thread (0, 0, 0) timestamp: 1749147474550023136
Thread (1, 0, 0) timestamp: 1749147474550023140
Thread (2, 0, 0) timestamp: 1749147474550023145
Thread (3, 0, 0) timestamp: 1749147474550023150
Thread (4, 0, 0) timestamp: 1749147474550023155
Total events collected: 5
```

## 使用场景

### 1. 诊断性能异常

你发现 kernel 比预期慢。`kernelretsnoop` 揭示有 10% 的线程完成时间是其他线程的 5 倍，这指向了一个具体的线程索引模式，它访问数据的方式不同。

### 2. 验证优化

在重写内存访问模式后，验证线程之间的时间戳差值是否减小，从而确认所有线程现在都能在几纳秒内完成。

### 3. 理解边界条件

发现处理数组边界的线程（例如接近 N 的线程索引）因为额外的边界检查或未对齐访问而更慢。

### 4. 调试竞态条件

时间戳顺序可以揭示你对线程执行顺序的假设是否被破坏，从而帮助识别同步 bug。

## 工作方式

1. 把一个 eBPF kretprobe 挂载到目标 CUDA kernel 函数上（例如 `vectorAdd`）
2. 在 kernel 退出时，每个 GPU 线程执行 eBPF 代码
3. eBPF 程序调用 GPU 专用 helper：
   - `bpf_get_thread_idx()` - 获取当前线程坐标
   - `bpf_get_globaltimer()` - GPU 纳秒精度计时器
4. 数据写入 GPU ringbuffer
5. userspace 轮询并显示结果

## 代码结构

- **`kernelretsnoop.bpf.c`**：在 kernel 退出时运行在 GPU 上的 eBPF 程序
- **`kernelretsnoop.c`**：userspace loader 和输出处理器
- **`vec_add.cu`**：用于测试的示例 CUDA 应用

## 局限性

- 只捕获 kernel **退出** 时间戳（不捕获 entry）
- 不捕获 kernel 参数或返回值
- ringbuffer 开销可能影响绝对时间（但线程间相对时间仍然准确）
- 需要 kernel 函数符号名（mangled C++ name）

## 自定义

要跟踪别的 kernel，请修改 `kernelretsnoop.bpf.c` 中的 SEC 注解：

```c
SEC("kretprobe/_Z9vectorAddPKfS0_Pf")  // 当前：vectorAdd(const float*, const float*, float*)
```

用下面的命令查找 kernel 的 mangled name：
```bash
cuobjdump -symbols your_app | grep your_kernel_name
```

## 高级分析

把时间戳导出到文件里做更深入分析：

```bash
./kernelretsnoop | tee timestamps.txt
```

然后你可以用脚本来：
- 计算每个 warp 的 timing variance
- 找出带离群值的线程索引模式
- 把时间戳和线程坐标关联起来，用于可视化访问模式

## 故障排查

**没有输出**：确认 eBPF 程序已经成功 attach。检查 kernel 名称是否完全匹配（包括 C++ mangling）。

**数据不完整**：对于高频 kernel，ringbuffer 可能太小。请增大 ringbuf map 定义里的 `max_entries`。

**时间戳顺序不对**：如果 warp 是并行执行的，这是正常的。如果需要顺序分析，请按时间戳排序。
