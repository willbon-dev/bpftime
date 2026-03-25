# Host Map 测试 - GPU Host-backed Map 类型

## 概览

这个示例演示并测试两种把数据存放在 **Host memory** 中的 GPU map 类型（与 GPU device memory 相对）：

| Map Type | ID | Description |
|----------|-----|-------------|
| `BPF_MAP_TYPE_PERGPUTD_ARRAY_HOST_MAP` | 1512 | Host memory 中的 per-GPU-thread 存储 |
| `BPF_MAP_TYPE_GPU_ARRAY_HOST_MAP` | 1513 | Host memory 中的共享存储 |

## 为什么要使用 Host-backed Map？

### 和 GPU-memory Map 的对比

| Feature | GPU Memory Maps | Host Memory Maps |
|---------|-----------------|------------------|
| Storage Location | GPU Device Memory | Host (CPU) Memory |
| GPU Access Speed | Fast | Slower (PCIe) |
| Host Access Speed | Slower (DMA) | Fast |
| Memory Size | Limited by GPU VRAM | Limited by Host RAM |
| Use Case | High-frequency GPU updates | Frequent Host reads |

### 什么时候使用 Host-backed Map

1. **频繁 Host 读取**：userspace 需要高频读取 map 数据时
2. **大容量数据存储**：当数据超过 GPU memory 限制时
3. **调试/跟踪**：当低延迟 Host 访问比 GPU 写入速度更重要时
4. **跨设备共享**：当数据需要在多个 GPU 之间共享时

## Map 类型说明

### BPF_MAP_TYPE_GPU_ARRAY_HOST_MAP (1513)

**共享存储** - 所有 GPU 线程看到并修改的是同一组值。

```
Memory Layout:
┌────────────────────────────────────────┐
│ Key 0 │ Key 1 │ Key 2 │ Key 3 │ ...   │  <- Single copy
└────────────────────────────────────────┘
   ↑        ↑        ↑
   │        │        │
   └────────┴────────┴── All threads read/write here
```

**特性**：
- 简单 lookup 会为每个 key 返回单个值
- 最后写入者获胜（非原子写）
- 适合全局计数器、配置值
- 在高并发写入下会产生竞争

### BPF_MAP_TYPE_PERGPUTD_ARRAY_HOST_MAP (1512)

**per-thread 存储** - 每个 GPU 线程都有自己独立的槽位。

```
Memory Layout:
┌──────────────────────────────────────────────────────┐
│ Thread 0 │ Thread 1 │ Thread 2 │ ... │ Thread N-1   │ <- Key 0
├──────────────────────────────────────────────────────┤
│ Thread 0 │ Thread 1 │ Thread 2 │ ... │ Thread N-1   │ <- Key 1
├──────────────────────────────────────────────────────┤
│    ...   │    ...   │    ...   │ ... │    ...       │
└──────────────────────────────────────────────────────┘
```

**特性**：
- lookup 返回 `value_size * thread_count` 字节（数组）
- 线程之间没有竞争
- 适合 per-thread 统计、时间戳、计数器
- 内存占用更高（按线程数成倍增长）

## 构建

```bash
# 从 bpftime 根目录
make -C example/gpu/host_map_test
```

你可以通过定义 `HOST_MAP_MAX_ENTRIES` 来自定义 map 条目数：

```bash
# 使用 20 个条目，而不是默认的 10 个
make -C example/gpu/host_map_test HOST_MAP_MAX_ENTRIES=20
```

要求：
- 已构建带 CUDA 支持的 bpftime（`-DBPFTIME_ENABLE_CUDA_ATTACH=1`）
- 已安装 CUDA toolkit

## 运行

### 终端 1：启动 BPF 程序（Server）

```bash
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/host_map_test/host_map_test [thread_count]
```

可选参数 `thread_count` 指定要监控多少个 GPU 线程（默认：16）。

### 终端 2：运行 CUDA 应用（Agent）

```bash
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/host_map_test/vec_add [threads_per_block] [num_blocks] [sleep_ms]
```

参数：
- `threads_per_block`：每个 CUDA block 的线程数（默认：10）
- `num_blocks`：CUDA block 数量（默认：1）
- `sleep_ms`：每次迭代之间的 sleep 时间，单位 ms（默认：1000）

### 示例

```bash
# 终端 1：监控 20 个线程
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/host_map_test/host_map_test 20

# 终端 2：运行 10 线程/block，2 个 block = 20 个线程
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/host_map_test/vec_add 10 2 500
```

## 示例输出

```
========== 12:34:56 ==========

[shared_counter - GPU_ARRAY_HOST_MAP]
  所有 GPU 线程共享这些计数器（最后写入者获胜）
  Key        Value
  ---        -----
  0          15
  1          12
  2          18
  3          14

[perthread_counter - PERGPUTD_ARRAY_HOST_MAP]
  每个 GPU 线程都有独立存储

  Key 0 (call_count):
    Thread     Value
    ------     -----
    0          5
    1          5
    2          5
    3          5
    ---
    Total: 20 (from 4 active threads)

  Key 1 (exec_time_ns):
    Thread     Value
    ------     -----
    0          1234
    1          1256
    2          1189
    3          1312
    ---
    Total: 4991 (from 4 active threads)

  Key 2 (thread_id):
    Thread     Value
    ------     -----
    0          0
    1          1
    2          2
    3          3
    ---
    Total: 6 (from 4 active threads)
```

## 代码结构

- **`host_map_test.bpf.c`**：带有 map 定义和 probe 的 eBPF 程序
  - 使用 `HOST_MAP_MAX_ENTRIES` 宏（默认：10）设置 map 的 `max_entries`
  - `perthread_counter`：用于 per-thread 统计的 PERGPUTD_ARRAY_HOST_MAP
  - `shared_counter`：用于共享计数器的 GPU_ARRAY_HOST_MAP
  - `thread_timestamp`：用于 entry 时间戳的 PERGPUTD_ARRAY_HOST_MAP

- **`host_map_test.c`**：读取并显示 map 数据的 userspace 程序
  - 同样定义了 `HOST_MAP_MAX_ENTRIES` 宏以保持一致
  - 使用 `bpf_map_get_next_key()` 动态遍历 map key

- **`vec_add.cu`**：用于触发 probe 的 CUDA 向量加法程序

## 输出解读

### shared_counter（GPU_ARRAY_HOST_MAP）

显示所有线程共同递增的全局计数器。由于非原子写和 last-writer-wins 语义，总和可能小于线程总执行次数。

### perthread_counter（PERGPUTD_ARRAY_HOST_MAP）

显示 per-thread 数据：
- **Key 0 (call_count)**：每个线程执行 kernel 的次数
- **Key 1 (exec_time_ns)**：每个线程最近一次执行的时间
- **Key 2 (thread_id)**：每个线程写入的 thread ID（用于验证）

## 使用场景

### 1. 性能分析

跟踪 per-thread 执行时间，找出慢线程或负载不均衡。

### 2. 调用计数

在没有竞争问题的情况下统计每个线程的 kernel 调用次数。

### 3. 调试

存储线程特定的调试数据，供 userspace 低延迟读取。

### 4. 配置分发

使用共享 map 向所有 GPU 线程分发配置。

## 故障排查

**没有数据出现**：
- 检查两个进程是否都在运行
- 验证 CUDA kernel 名称是否与 SEC 注解匹配
- 查看 bpftime 日志，确认是否有 attach 错误

**数据不完整**：
- 确认 `thread_count` 参数与实际 GPU 线程数一致
- 可能有些线程还没有执行

**`shared_counter` 中的计数不正确**：
- 非原子写是预期行为
- 使用 per-thread map 才能精确计数，然后在 userspace 中汇总

## 相关示例

- `gpu_shard_array`：测试 GPU_ARRAY_MAP（GPU memory backed）
- `threadhist`：使用 PERGPUTD_ARRAY_MAP 生成线程直方图
- `cuda-counter`：基础 probe/retprobe 示例
