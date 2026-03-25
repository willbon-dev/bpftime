# BPF Bloom Filter 测试指南

本文档介绍 `bpftime` 中 BPF Bloom Filter（`BPF_MAP_TYPE_BLOOM_FILTER`）功能的实现和测试。Bloom filter 是一种概率型数据结构，用于集合成员测试，具有“没有假阴性，但可能有假阳性”的特点。

## 组件

- `uprobe_bloom_filter.bpf.c`：定义并操作 `BPF_MAP_TYPE_BLOOM_FILTER` 的 eBPF kernel 程序
- `uprobe_bloom_filter.c`：加载 eBPF 并监控用户访问模式的用户态程序（通过 skeleton 嵌入 BPF 程序）
- `target.c`：被 eBPF uprobe 监控函数的演示程序
- `test_correct_bloom_filter.sh`：演示 bloom filter 行为的自动化测试脚本

## 快速开始

### 1. 构建组件
```bash
make clean
make uprobe_bloom_filter target
```

### 2. 运行 Bloom Filter 演示
```bash
# 推荐：使用脚本（会自动设置 VM 类型）
./test_correct_bloom_filter.sh

# 手动执行（需要两个终端）：
# 终端 1：启动 bloom filter 监控器（bpftime Server）
BPFTIME_VM_NAME=ubpf LD_PRELOAD=../../build/runtime/syscall-server/libbpftime-syscall-server.so ./uprobe_bloom_filter

# 终端 2：启动目标程序（bpftime Agent/Client）
BPFTIME_VM_NAME=ubpf LD_PRELOAD=../../build/runtime/agent/libbpftime-agent.so ./target
```

**注意**：这个演示需要设置 `BPFTIME_VM_NAME=ubpf`，以使用 ubpf VM 而不是默认的 llvm VM，保证兼容性。

## Bloom Filter 行为验证

### 测试原理

这个演示使用 bloom filter 监控用户访问模式：
1. 当 `user_access()` 函数带着某个用户 ID 被调用时
2. eBPF 程序检查该用户 ID 是否存在于 bloom filter 中
3. 如果未找到（miss）：标记为新用户并加入 bloom filter
4. 如果找到（hit）：标记为重复用户（可能存在假阳性）

### 预期统计
```text
=== Bloom Filter Real-time Monitoring Statistics ===
Total user accesses:      10
New users (first access): 8
Repeat users (re-access): 2
Admin operations:         4
System events:            6

--- Bloom Filter Performance Analysis ---
Bloom Filter hits:        2 (detected as possibly existing)
Bloom Filter misses:      8 (definitely not existing)
Hit rate:                 20.00%
New user ratio:           80.00%
Repeat user ratio:        20.00%
```

### BPF 程序输出示例
```text
Bloom filter MISS for user_id=1003 (new user, added to filter)
Bloom filter HIT for user_id=1003 (repeat user)
Admin operation by admin_id=2002
System event triggered
```

### 验证要点
- **没有假阴性**：所有新用户都能被正确识别为新用户 ✅
- **可能有假阳性**：某些新用户可能会被误判为重复用户
- **统计一致性**：新用户 + 重复用户 = 总访问次数
- **假阳性率**：根据 bloom filter hits 与实际重复用户之间的差异估算

## 技术实现

### BPF Map 定义
嵌入的 BPF 程序将 bloom filter map 定义为：
```c
struct {
    __uint(type, BPF_MAP_TYPE_BLOOM_FILTER);
    __uint(max_entries, 1000);
    __uint(value_size, sizeof(u32));
    __uint(map_extra, 3); // Number of hash functions
} user_bloom_filter SEC(".maps");
```

### 核心 BPF 操作
- **Lookup**：`bpf_map_lookup_elem(&user_bloom_filter, &user_id)`
- **Update**：`bpf_map_update_elem(&user_bloom_filter, &user_id, &value, BPF_ANY)`
- **Peek**：`bpf_map_peek_elem(&user_bloom_filter, &user_id)`（userspace）

### 统计跟踪
```c
// Statistics index definitions
#define STAT_TOTAL_ACCESSES 0
#define STAT_UNIQUE_USERS 1
#define STAT_REPEAT_USERS 2
#define STAT_BLOOM_HITS 5
#define STAT_BLOOM_MISSES 6
```

### 用户访问模式
目标程序会模拟不同的用户访问模式：
- **高频**：轮换用户 ID（1001-1010）的用户访问
- **中频**：管理员操作
- **低频**：系统事件

## Bloom Filter 的关键特性

### 1. 没有假阴性
- 如果 bloom filter 返回“未找到”，则该元素**一定不在**集合中
- 所有新用户都能被正确识别为新用户

### 2. 可能有假阳性
- 如果 bloom filter 返回“找到”，则该元素**可能在**集合中
- 某些新用户可能会被错误识别为重复用户
- 假阳性率取决于：
  - 已添加元素数量
  - Bloom filter 的大小
  - hash 函数的数量

### 3. 内存效率高
- 不管元素数量多少，都使用固定大小的 bit array
- 相比 hash table，更适合大规模数据集，内存效率更高
- 代价：准确率与内存占用之间的权衡

## 性能分析

这个演示会实时分析 bloom filter 的性能：

### 跟踪指标
- **Total Accesses**：`user_access()` 调用次数
- **New Users**：第一次被看到的用户（bloom filter miss → add）
- **Repeat Users**：之前见过的用户（bloom filter hit）
- **Hit Rate**：bloom filter hits 的百分比
- **False Positive Estimate**：估算的假阳性次数

### 分析输出
```text
=== Bloom Filter Test Analysis ===
Test result verification:
  Theory: new users + repeat users = total accesses
  Actual: 8 + 2 = 10 (total accesses: 10)
  ✅ Consistency check passed

  Bloom Filter characteristics verification:
  - No false negatives: all new users correctly identified ✅
  - Possible false positives: some new users may be misjudged as repeat users
  - False positive detection: possible 0 false positives
```

## 故障排查

### VM 兼容性问题
如果你看到类似 `"No VM factory registered for name: llvm"` 的错误，请设置：
```bash
export BPFTIME_VM_NAME=ubpf
```

### 没有捕获到事件
如果统计一直是 0，请检查：
1. VM 类型是否设置正确（`BPFTIME_VM_NAME=ubpf`）
2. 目标程序是否使用了正确的 `LD_PRELOAD`
3. uprobe 是否挂载成功（查看控制台输出）

## 已验证的 bpftime 特性

- `BPF_MAP_TYPE_BLOOM_FILTER`：Bloom filter map 的创建和管理
- `bpf_map_lookup_elem()`：在 bloom filter 中做成员测试
- `bpf_map_update_elem()`：向 bloom filter 添加元素
- `bpf_map_peek_elem()`：在 userspace 查询 bloom filter
- uprobe 与 bloom filter map 的集成
- 实时 bloom filter 性能监控
- 假阳性率分析与估算
- ubpf VM 集成与兼容性
