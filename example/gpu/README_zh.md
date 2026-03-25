# 使用 bpftime 在 GPU 上编写和运行 eBPF

> Yusheng Zheng=, Tong Yu=, Yiwei Yang=

bpftime 通过其 CUDA/ROCm 挂载实现提供 GPU 支持，使得 eBPF 程序可以在 **GPU kernel 内部** 于 NVIDIA 和 AMD GPU 上执行。这把 eBPF 的可编程性、可观测性和可定制能力带到 GPU 计算负载中，让你无需修改源代码，就能对 GPU 应用进行实时 profiling、调试和运行时扩展。

> **注意：** GPU 支持仍处于实验阶段。如果你有问题或建议，请 [提交 issue](https://github.com/eunomia-bpf/bpftime/issues) 或 [联系我们](mailto:team@eunomia.dev)。

## 问题背景：GPU 可观测性挑战

GPU 已经成为机器学习、科学计算和高性能计算工作负载的主力加速器，但它们的 SIMT（Single Instruction, Multiple Thread）执行模型带来了显著的可观测性和可扩展性挑战。现代 GPU 会把成千上万的线程组织成 warp（通常 32 个线程），在 streaming multiprocessor（SM）上以 lockstep 方式执行，而 kernel 又是从 host 异步启动的。这些线程会穿行于复杂的多级内存层次结构中：从快速但容量有限的 per-thread 寄存器，到 thread block 内的 shared memory/LDS，再到 L1/L2 cache，最后到更慢但容量更大的 device memory；与此同时，有限的抢占能力也让 kernel 很难被中断、检查或扩展。这种体系结构复杂性带来了丰富的性能特征，包括 warp divergence、内存合并模式、bank conflict 和 occupancy 变化，这些都会直接影响吞吐量，但对传统可观测性工具来说却几乎是黑箱。要理解并优化 kernel stall、内存瓶颈、低效同步或 SM 利用率不足等问题，需要对执行流、内存访问模式以及 warp 间协调进行细粒度可见性，还需要能够动态注入自定义逻辑。而这正是现有工具很难以灵活、可编程方式提供的能力。

现有 GPU tracing 和 profiling 工具大致分为两类，但都有明显局限。第一类工具只在 CPU-GPU 边界上工作，通过拦截 CUDA/ROCm 用户态库调用（例如通过对 `libcuda.so` 的 `LD_PRELOAD` hook）或在系统调用层对 kernel driver 做埋点。这类方法虽然能捕获 kernel launch、内存传输和 API timing 等 host 侧事件，但本质上把 GPU 当成黑箱：看不到 kernel 执行期间发生了什么，看不到具体 warp 行为或内存 stall 的关联，也无法根据 device 内部运行时条件自适应地修改行为。第二类工具是 GPU 厂商专用 profiler（例如 NVIDIA 的 CUPTI、Nsight Compute、Intel 的 GTPin、AMD 的 ROCProfiler，以及研究工具如 NVBit 或 Neutrino）。它们确实能做 device-side instrumentation，并收集硬件 performance counter、warp-level trace 或 instruction-level metric。但这些工具通常运行在各自隔离的生态中，与 Linux kernel 的可观测性和扩展栈割裂。它们无法把 GPU 事件与 CPU 侧的 eBPF probe（kprobe、uprobe、tracepoint）关联起来，需要单独的数据采集和分析流程，而且往往会带来较高开销（细粒度 instrumentation 时可达 10-100 倍慢化）。更重要的是，它们缺少 eBPF 在生产环境里那种动态可编程性和控制能力，也就是在不重新编译、不打断服务的情况下，自由定制要采集什么数据、如何处理数据。

### 时间线可见性缺口：什么能看见，什么看不见

设想一个常见的调试场景：“我的 CUDA 应用完成一次要 500ms，但我不知道时间都花在哪了。是内存传输、kernel 执行，还是 API 开销？”答案高度依赖应用使用的是同步还是异步 CUDA API，这也揭示了 CPU 侧可观测性的根本局限。

#### 同步执行：CPU 侧工具能看到什么，不能看到什么

在同步模式下，CUDA API 调用会阻塞直到 GPU 完成每个操作，这会让 CPU 和 GPU 时间线高度耦合。考虑一个典型流程：分配 device memory、把数据传到 GPU（host-to-device）、执行 kernel、等待完成。CPU 侧 profiler 可以测量每个阻塞 API 调用的墙钟时间，提供有用的高层洞察。例如，如果 `cudaMemcpy()` 需要 200μs，而 `cudaDeviceSynchronize()`（等待 kernel 完成）只需要 115μs，开发者就能快速判断数据传输比计算更耗时，说明瓶颈可能在 PCIe，可以通过 pinned memory、更大的 batch size 或异步传输来改善。

```
CPU Timeline (traditional tools can see this):
───────────────────────────────────────────────────────────────────────────
cudaMalloc()  cudaMemcpy()       cudaLaunchKernel()  cudaDeviceSync()
──────●─────────●──────────────────●──────────────────●───────────────────
  ~1μs wait     200μs wait        returns           115μs wait
  (blocked)     (H→D transfer)    immediately       (kernel done)

GPU Timeline (actual execution, usually hidden from CPU-side tools):
───────────────────────────────────────────────────────────────────────────
Alloc ─► Transfer ─► Kernel launch queued ─► Actual kernel execution
```

#### 异步执行：CPU 侧时间线为何会失真

在异步模式下，CPU 只会快速发出多个 kernel launch 请求，随后继续执行别的工作，而 GPU 可能在完全不同的时间点开始真正执行这些 kernel。此时，CPU 侧观测到的只是“launch 已经发出”，而不是“kernel 何时真正开始”。如果没有 device 侧 probe，你就无法知道这些 kernel 是否排队、是否被前序操作阻塞、是否因为资源竞争而晚启动。

这就是 bpftime 在 GPU 场景中的价值：它把 eBPF 直接注入到 GPU kernel 中，让你在 kernel 入口、退出和运行过程内部获得观测能力，从而把 CPU 和 GPU 两边的时间线对齐。

## 架构概览

bpftime 的 GPU 支持由三部分组成：

1. **CUDA/ROCm attach 实现**：拦截 GPU 二进制加载与 kernel 调用。
2. **PTX/LLVM 重写**：把 eBPF 转换为 GPU 可执行代码，并在目标 kernel 位置注入。
3. **GPU helper 和 map**：提供线程索引、计时、共享内存通信等能力。

```
┌─────────────────────────────────────────────────────────────────┐
│                        Host (Userspace)                        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  CUDA/ROCm   │     │  bpftime     │     │  Userspace   │    │
│  │   App        │     │   Runtime    │     │  eBPF Loader │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                              │                      │            │
│                              ▼                      ▼            │
│                       ┌──────────────┐      ┌──────────────┐   │
│                       │ Shared Memory│      │  GPU Kernel  │   │
│                       │  (Host-GPU)  │      │  with eBPF   │   │
│                       └──────────────┘      └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 示例

我们通过几个 bcc 风格示例展示 GPU eBPF 能力：

### [kernelretsnoop](kernelretsnoop/README_zh.md) - 每线程退出时间戳跟踪器

挂载到 CUDA kernel 退出点，记录每个 GPU 线程完成执行的精确纳秒时间戳。这可以揭示线程 divergence、内存访问模式和 warp 调度问题，而这些在传统 profiler 里是看不到的。

> 这里的 `kprobe` / `kretprobe` 名称其实不太准确，只是占位符，我觉得后面应该改掉。

**使用场景**：你发现 kernel 比预期慢。`kernelretsnoop` 揭示每个 warp 中的线程 31 比线程 0-30 晚了 750ns 完成，暴露出一个导致 divergence 的边界条件。你重构代码消除这个分支后，所有线程都在纳秒级别同时完成。

```c
// eBPF 程序在 kernel 退出时运行在 GPU 上
SEC("kretprobe/_Z9vectorAddPKfS0_Pf")
int ret__cuda() {
    u64 tid_x, tid_y, tid_z;
    bpf_get_thread_idx(&tid_x, &tid_y, &tid_z);  // 我是哪一个线程？
    u64 ts = bpf_get_globaltimer();               // 我什么时候完成的？

    // 写入 ringbuffer 供 userspace 分析
    bpf_perf_event_output(ctx, &events, 0, &data, sizeof(data));
}
```

### [threadhist](threadhist/README_zh.md) - 线程执行次数直方图

使用 GPU array map 统计每个线程执行了多少次。它能发现工作负载不均衡的问题，即某些线程比其他线程做得多得多，白白浪费 GPU 计算能力。

**使用场景**：你的 grid-stride loop 处理 100 万个元素，但只有 5 个线程。你预期负载均衡，但 `threadhist` 显示线程 4 的执行次数只有线程 0-3 的 75%。边界元素分配不均，导致线程 4 空闲，而其他线程继续工作。你调整分配方式后，执行就变得均衡了。

```c
// eBPF 程序在 kernel 退出时运行在 GPU 上
SEC("kretprobe/_Z9vectorAddPKfS0_Pf")
int ret__cuda() {
    u64 tid_x, tid_y, tid_z;
    bpf_get_thread_idx(&tid_x, &tid_y, &tid_z);

    // GPU array map 中的 per-thread 计数器
    u64 *count = bpf_map_lookup_elem(&thread_counts, &tid_x);
    if (count) {
        __atomic_add_fetch(count, 1, __ATOMIC_SEQ_CST);  // 线程 N 又执行了一次
    }
}
```

### [launchlate](launchlate/README_zh.md) - kernel launch 延迟分析器

测量 CPU 上 `cudaLaunchKernel()` 和 GPU 上真正开始执行 kernel 之间的时间差。它能揭示隐藏的排队延迟、调度开销和同步代价，这些因素会让快速 kernel 在生产环境里变慢。

**使用场景**：你的 kernel 单次只执行 100μs，但用户却反馈 50ms 延迟。`launchlate` 显示每个 kernel 的 launch latency 其实有 200-500μs，因为它们在等待前一个 kernel 和内存传输完成。总时间是 5ms，而不是 1ms。你切换到 CUDA graphs，把所有 launch 打包，延迟降到 1.2ms。

```c
BPF_MAP_DEF(BPF_MAP_TYPE_ARRAY, launch_time);

// CPU 侧 uprobe 捕获 launch 时间
SEC("uprobe/app:cudaLaunchKernel")
int uprobe_launch(struct pt_regs *ctx) {
    u64 ts_cpu = bpf_ktime_get_ns();  // CPU 何时请求 launch？
    bpf_map_update_elem(&launch_time, &key, &ts_cpu, BPF_ANY);
}

// GPU 侧 kprobe 捕获执行开始
SEC("kprobe/_Z9vectorAddPKfS0_Pf")
int kprobe_exec() {
    u64 ts_gpu = bpf_get_globaltimer();  // GPU 何时真正开始？
    u64 *ts_cpu = bpf_map_lookup_elem(&launch_time, &key);

    u64 latency = ts_gpu - *ts_cpu;  // kernel 在队列里等了多久？
    u32 bin = get_hist_bin(latency);
    // 更新直方图...
}
```

### 其他示例

- **[cuda-counter](cuda-counter/README_zh.md)**：基础 probe/retprobe，并带有计时测量
- **[mem_trace](mem_trace/README_zh.md)**：内存访问模式跟踪与分析
- **[directly_run_on_gpu](directly_run_on_gpu/README_zh.md)**：不挂载到 kernel，而是直接在 GPU 上运行 eBPF 程序
- **[rocm-counter](rocm-counter/README_zh.md)**：AMD ROCm GPU instrumentation（实验性）

### 关键组件

1. **CUDA Runtime Hooking**：使用基于 Frida 的动态 instrumentation 拦截 CUDA API 调用
2. **PTX Modification**：将 eBPF 字节码转换为 PTX（Parallel Thread Execution）汇编，并注入到 GPU kernel 中
3. **Helper Trampoline**：提供 GPU 可访问的 helper 函数，用于 map 操作、计时和上下文访问
4. **Host-GPU Communication**：通过 pinned shared memory 让 GPU 与 host 进行同步调用

### 挂载类型

bpftime 支持 GPU kernel 的三种挂载类型（定义于 `attach/nv_attach_impl/nv_attach_impl.hpp:33-34`）：

- **`ATTACH_CUDA_PROBE` (8)** - 在 kernel entry 执行 eBPF 代码
- **`ATTACH_CUDA_RETPROBE` (9)** - 在 kernel exit 执行 eBPF 代码
- **Memory capture probe (`__memcapture`)** - 用于捕获内存访问模式的特殊 probe 类型

所有类型都支持按名称指定目标 kernel 函数，例如 `_Z9vectorAddPKfS0_Pf` 这样的 mangled C++ 名称。

## GPU 专用 BPF Map

**bpftime 支持 CPU 上的所有 map，但直接使用 CPU eBPF map 会显著降低性能。**

bpftime 提供了针对 GPU 操作优化的专用 map 类型，性能影响要小得多：

### `BPF_MAP_TYPE_PERGPUTD_ARRAY_MAP` 和 `BPF_MAP_TYPE_GPU_ARRAY_MAP`

具备 **per-thread storage** 的 GPU 常驻 array map，适合高性能数据采集。

主要特性：
- 数据直接存储在 GPU memory 中（CUDA IPC shared memory）
- 每个线程都有独立存储（`max_entries × max_thread_count × value_size`）
- 从 GPU 侧零拷贝访问，host 侧通过 DMA 传输
- 在 GPU 代码中支持 `bpf_map_lookup_elem()` 和 `bpf_map_update_elem()`

实现位置：`runtime/src/bpf_map/gpu/nv_gpu_array_map.cpp:14-81`

### `BPF_MAP_TYPE_GPU_RINGBUF_MAP` (1527)

用于高效 **per-thread event streaming** 到 host 的 GPU ring buffer map。

主要特性：
- GPU memory 中的 lock-free per-thread ring buffer
- 支持带元数据的可变大小事件记录
- 低开销的异步数据采集
- 与 `bpf_perf_event_output()` helper 兼容

实现位置：`runtime/src/bpf_map/gpu/nv_gpu_ringbuf_map.cpp`

## GPU Helper Functions

bpftime 为 CUDA kernel 提供 GPU 专用 eBPF helper（见 `attach/nv_attach_impl/trampoline/default_trampoline.cu:331-390`）：

### 核心 GPU Helpers

| Helper ID | Function Signature | Description |
|-----------|-------------------|-------------|
| **501** | `ebpf_puts(const char *str)` | 将 GPU kernel 中的字符串打印到 host 控制台 |
| **502** | `bpf_get_globaltimer(void)` | 读取 GPU global timer（纳秒精度） |
| **503** | `bpf_get_block_idx(u64 *x, u64 *y, u64 *z)` | 获取 CUDA block 索引（blockIdx） |
| **504** | `bpf_get_block_dim(u64 *x, u64 *y, u64 *z)` | 获取 CUDA block 维度（blockDim） |
| **505** | `bpf_get_thread_idx(u64 *x, u64 *y, u64 *z)` | 获取 CUDA thread 索引（threadIdx） |
| **506** | `bpf_gpu_membar(void)` | 执行 GPU memory barrier（`membar.sys`） |

### 标准 BPF Helpers（GPU 兼容）

下面这些标准 eBPF helper 在 GPU 上也可以工作，并做了特殊优化：

- **`bpf_map_lookup_elem()`** (1)：GPU array map 的 fast path，其他 map 则回退到 host
- **`bpf_map_update_elem()`** (2)：GPU array map 的 fast path，其他 map 则回退到 host
- **`bpf_map_delete_elem()`** (3)：通过 shared memory 进行 host 调用
- **`bpf_trace_printk()`** (6)：格式化输出到 host 控制台
- **`bpf_get_current_pid_tgid()`** (14)：返回 host 进程的 PID/TID
- **`bpf_perf_event_output()`** (25)：针对 GPU ringbuf map 做了优化

### Host-GPU 通信协议

对于需要 host 交互的 helper，bpftime 使用带 spinlock 和 warp-level serialization 的 shared memory 协议来保证正确性。协议流程如下：

1. GPU thread 获取 spinlock
2. 将请求参数写入 shared memory
3. 设置标志位并等待 host 响应
4. host 处理请求并发出完成信号
5. GPU 读取响应并释放锁

## 构建 GPU 支持

### 前置条件

- **NVIDIA CUDA Toolkit**（推荐 12.x）或 **AMD ROCm**
- **CMake** 3.15+
- **LLVM** 15+（用于 PTX 生成）
- **Frida-gum**（用于运行时 hooking）

### 构建配置

```bash
# 对于 NVIDIA CUDA
cmake -Bbuild \
  -DBPFTIME_ENABLE_CUDA_ATTACH=1 \
  -DBPFTIME_CUDA_ROOT=/usr/local/cuda-12.6 \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
```

## 参考资料

1. [bpftime OSDI '25 Paper](https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng)
2. [CUDA Runtime API](https://docs.nvidia.com/cuda/cuda-runtime-api/)
3. [PTX ISA](https://docs.nvidia.com/cuda/parallel-thread-execution/)
4. [eBPF Documentation](https://ebpf.io/)
5. [eGPU: Extending eBPF Programmability and Observability to GPUs](https://dl.acm.org/doi/10.1145/3723851.3726984)

引用：

```txt
@inproceedings{yang2025egpu,
  title={eGPU: Extending eBPF Programmability and Observability to GPUs},
  author={Yang, Yiwei and Yu, Tong and Zheng, Yusheng and Quinn, Andrew},
  booktitle={Proceedings of the 4th Workshop on Heterogeneous Composable and Disaggregated Systems},
  pages={73--79},
  year={2025}
}
```

如有问题或反馈，请在 [GitHub](https://github.com/eunomia-bpf/bpftime) 提交 issue，或 [联系我们](mailto:team@eunomia.dev)。
