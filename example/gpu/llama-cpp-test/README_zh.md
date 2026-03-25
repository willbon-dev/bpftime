# threadhist - GPU 线程执行直方图

## 概览

当你用多个线程 launch 一个 CUDA kernel 时，你通常希望每个线程都做大致相同的工作。但如果线程 0 执行了 20 万次，而线程 4 只执行了 15 万次呢？这就是 25% 的负载不均衡，它会悄悄拖慢 GPU 性能。

`threadhist` 通过统计每个 GPU 线程真正执行了多少次 kernel，来暴露这些隐藏的负载不均衡。和只看聚合指标的传统 profiler 不同，这个工具直接展示 per-thread 的执行模式，而这些模式会直接影响性能。

## 理解 GPU 线程执行

当你 launch 一个像 `vectorAdd<<<1, 5>>>()` 这样的 CUDA kernel 时，你创建了 5 个线程（`threadIdx.x = 0` 到 `4`），它们应该并行处理数据。在理想情况下，这 5 个线程会以相同次数执行 kernel，并承担相同工作。

不过，下面这些因素都可能导致 **负载不均衡**：

- **Grid-stride loop**：由于数组大小不能整除，最后一个线程可能处理更少的元素
- **条件分支**：某些线程可能因为索引或数据值不同而跳过部分工作
- **提前退出**：线程碰到边界条件时可能提前返回
- **工作分配不均**：算法本身可能给不同线程分配了不同工作量

这些不均衡意味着一些线程很忙，而另一些线程却在空闲，浪费了宝贵的 GPU 计算能力。但由于这些问题发生在 kernel 内部，传统 profiling 工具看不到它们，它们只会告诉你“kernel 花了 X 毫秒”。

## 这个工具捕获什么

`threadhist` 使用 GPU array map 来维护 per-thread 计数器。每当一个线程退出 kernel 时，它就把自己的计数器加 1。userspace 程序会周期性读取这些计数器，并显示直方图，精确展示每个线程执行了多少次。

## 为什么这很重要

### Grid-stride 工作负载不均衡

你正在用 grid-stride loop 处理一个 100 万元素数组。kernel 启动时有 5 个线程，你期望每个线程大约处理 20 万个元素。运行 `threadhist` 几秒后，你会看到：

```
Thread 0: 210432
Thread 1: 210432
Thread 2: 210432
Thread 3: 210432
Thread 4: 158304  (Only 75% of the work!)
```

发生了什么？你的 kernel 在循环里被反复调用，每次调用处理一块数据。由于 grid-stride loop 的写法，线程 4 总是更早完成，因为剩余元素分配得不均匀。线程 0-3 继续工作，而线程 4 在空闲。

**修复方式**：调整 thread block 配置，或者重构 grid-stride loop，让边界工作分配得更均匀。优化后，所有线程的计数会更接近，说明负载已经均衡。

### 条件分支之谜

你正在运行一个包含条件逻辑的 kernel。直方图显示：

```
Thread 0: 195423
Thread 1: 195423
Thread 2: 98156   (50% fewer executions!)
Thread 3: 195423
Thread 4: 195423
```

线程 2 的执行次数明显少于其他线程。查看代码后，你发现某个条件会让线程 2 在某些情况下提前退出：

```cuda
if (threadIdx.x == 2 && someCondition()) {
    return;  // Early exit
}
```

这意味着线程 2 做的工作只有一半，但 warp 中其他线程在它执行时仍然要等它。这就是 **warp divergence** 导致的串行化，而线程 2 的提前退出所造成的空闲时间也浪费了 GPU 周期。

**洞察**：要么去掉这个分支，让所有线程走同一条路径；要么重构数据，让这个条件不要和特定线程索引相关。

### 检测完全空闲的线程

更极端的情况下，你可能会看到：

```
Thread 0: 187234
Thread 1: 187234
Thread 2: 187234
Thread 3: 0       (Never executed!)
Thread 4: 0       (Never executed!)
```

线程 3 和 4 根本没有执行！这说明你的 kernel launch 配置或 grid-stride 逻辑有 bug。也许你的 workload 只需要 3 个线程，但你却启动了 5 个，浪费了 GPU 资源。也可能是某个 bug 导致特定线程索引从未进入主处理循环。

**行动**：调整 kernel launch 参数以匹配真实 workload，或者修复循环逻辑，确保所有线程都参与。

## 构建

```bash
# 从 bpftime 根目录
make -C example/gpu/threadhist
```

要求：
- 已构建带 CUDA 支持的 bpftime（`-DBPFTIME_ENABLE_CUDA_ATTACH=1`）
- 已安装 CUDA toolkit

## 运行

### 终端 1：启动 histogram collector
```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/threadhist/threadhist
```

### 终端 2：运行你的 CUDA 应用
```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/agent/libbpftime-agent.so  example/gpu/threadhist/vec_add
```

或者跟踪任意 CUDA 应用：
```bash
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  ./your_cuda_app
```

## 示例输出

```
12:34:56
Thread 0: 210432
Thread 1: 210432
Thread 2: 210432
Thread 3: 210432
Thread 4: 158304
```

时间戳表示快照拍摄的时间，后面跟着程序启动以来每个线程的总执行次数。

## 使用场景

### 1. 优化 thread block 配置

你正在尝试不同的 block size。通过用不同配置运行 `threadhist`，你可以快速看出哪种配置能产生最均衡的负载分布，从而最大化 GPU 利用率。

### 2. 验证 grid-stride loop 实现

在实现或修改 grid-stride loop 后，验证所有线程是否大致均匀执行。差异过大说明 loop 没有把工作分配均匀。

### 3. 检测算法不均衡

有些算法天然会产生负载不均衡（例如处理稀疏矩阵时，有些线程负责很多元素，有些线程很少）。这个直方图可以量化这种不均衡，帮助你决定是重构算法还是接受这个权衡。

### 4. 调试线程启动问题

如果某些线程的执行次数为零，你就已经在它进入生产之前发现了 launch 配置或 kernel 逻辑中的 bug。

## 工作方式

1. 挂载到目标 CUDA kernel 函数上的 eBPF kretprobe
2. 在 kernel 退出时，每个 GPU 线程把自己的计数器加 1：`*cnt += 1`
3. GPU array map 会自动为每个线程分配存储空间（每个线程一个 `u64`）
4. userspace 周期性读取整个数组并打印直方图
5. 计数会随着时间累积，显示自程序启动以来的总执行次数

## 代码结构

- **`threadhist.bpf.c`**：在 GPU 上运行的 eBPF 程序，在 kernel 退出时递增 per-thread 计数器
- **`threadhist.c`**：读取并显示直方图的 userspace loader
- **`vec_add.cu`**：用于测试的示例 CUDA 应用

## 局限性

- 显示的是自程序启动以来的累计计数（不是每秒速率）
- 固定的线程数（示例里硬编码为 7 个线程，位于 `threadhist.c` 第 87 行）
- 只跟踪 kernel exit（不显示每次执行的时序）
- 需要知道 kernel 函数符号名

## 自定义

要跟踪其他 kernel，请修改 `threadhist.bpf.c` 中的 SEC 注解：

```c
SEC("kretprobe/_Z9vectorAddPKfS0_Pf")  // 当前：vectorAdd(const float*, const float*, float*)
```

使用下面的命令查找 kernel 的 mangled 名称：
```bash
cuobjdump -symbols your_app | grep your_kernel_name
```

要监控更多线程，请修改 `threadhist.c:87` 中的线程数参数：
```c
print_stat(skel, 32);  // 监控 32 个线程，而不是 7 个
```

## 结果解读

**完全均衡**（所有线程 ±5%）：
```
Thread 0: 200000
Thread 1: 199876
Thread 2: 200124
```
✓ 很好 - GPU 资源得到了充分利用

**轻微不均衡**（10-20% 波动）：
```
Thread 0: 200000
Thread 1: 180000
```
⚠ 对复杂算法来说可以接受，但如果可能还是应该检查

**严重不均衡**（>25% 波动）：
```
Thread 0: 200000
Thread 4: 120000
```
❌ 性能问题 - 需要重构 workload 分配

**空闲线程**（计数为零）：
```
Thread 3: 0
```
❌ bug 或配置错误 - 立即修复

## 故障排查

**所有线程都是零**：eBPF 程序没有 attach 成功。检查 kernel 名称是否完全匹配（包括 C++ mangling）。

**计数与预期不符**：确认你测量的是正确的 kernel。使用 `cuobjdump` 验证符号名。

**输出不更新**：应用可能根本没有调用 kernel。检查两个进程是否都在运行，并通过 shared memory 进行通信。
