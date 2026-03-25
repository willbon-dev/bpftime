# BPF Queue（FIFO）测试指南

本文档介绍 `bpftime` 中 BPF Queue（`BPF_MAP_TYPE_QUEUE`）功能的实现和测试。BPF Queue 遵循先进先出（FIFO）的数据处理方式。

## 组件

- `uprobe_queue.bpf.c`：定义并操作 `BPF_MAP_TYPE_QUEUE` 的 eBPF kernel 程序
- `uprobe_queue.c`：加载 eBPF 并从 queue 中读取事件的用户态程序
- `target.c`：被 eBPF uprobe 监控函数的演示程序
- `run_demo.sh`：演示 FIFO 行为的自动化测试脚本

## 快速开始

### 1. 构建组件
```bash
make clean
make uprobe_queue target
```

### 2. 运行 Queue 演示
```bash
# 推荐：使用脚本
./run_demo.sh -r

# 手动执行（需要两个终端）：
# 终端 1：启动 queue 监控器（bpftime Server）
LD_PRELOAD=../../build/runtime/syscall-server/libbpftime-syscall-server.so ./uprobe_queue

# 终端 2：启动目标程序（bpftime Agent/Client）
LD_PRELOAD=../../build/runtime/agent/libbpftime-agent.so ./target
```

## FIFO 行为验证

### 示例场景
如果 `target.c` 按以下顺序触发事件（由 counter 字段标识）：
1. 事件 A（counter 1）被推入 queue
2. 事件 B（counter 2）被推入 queue
3. 事件 C（counter 3）被推入 queue

当从 queue 中弹出时，顺序会是：
1. 事件 A（counter 1）- 最先推入，最先弹出
2. 事件 B（counter 2）
3. 事件 C（counter 3）- 最后推入，最后弹出

### 预期日志输出
```text
// BPF 程序输出（bpf_printk）
Pushed event to queue: pid=xxx, counter=1, ...
Pushed event to queue: pid=xxx, counter=2, ...
Pushed event to queue: pid=xxx, counter=3, ...

// 用户态程序输出（uprobe_queue）
Queue status: non-empty (head event: function_id=X, counter=1)
[HH:MM:SS.ms] target_function() called - counter:1 ...
[HH:MM:SS.ms] target_function() called - counter:2 ...
[HH:MM:SS.ms] target_function() called - counter:3 ...
Processed 3 events this round
```

## 技术实现

### BPF Map 定义
```c
struct {
    __uint(type, BPF_MAP_TYPE_QUEUE);
    __uint(max_entries, 64);
    __type(value, struct event_data);
} events_queue SEC(".maps");
```

### 核心 BPF 操作
- **Push**：`bpf_map_push_elem(&events_queue, &event, BPF_ANY)`
- **Pop**：用户态使用 `BPF_MAP_LOOKUP_AND_DELETE_ELEM` syscall
- **Peek**：用户态使用 `BPF_MAP_LOOKUP_ELEM` syscall

### 事件数据结构
```c
struct event_data {
    uint64_t timestamp;
    uint32_t pid;
    uint32_t tid;
    uint32_t counter;
    uint32_t function_id;
    int32_t input_value;
    char comm[16];
};
```

## 已验证的 bpftime 特性

- `BPF_MAP_TYPE_QUEUE`：Queue map 的创建和管理
- `bpf_map_push_elem()`：Queue map 的 push 操作
- `BPF_MAP_LOOKUP_AND_DELETE_ELEM`：Queue map 的 pop 操作
- `BPF_MAP_LOOKUP_ELEM`：Queue map 的 peek 操作
- FIFO 数据访问模式
- uprobe 与 queue map 的集成
