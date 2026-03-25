# bpftime Runtime

bpftime runtime 是核心组件，提供高性能的用户态 eBPF 执行环境。它能够在用户态运行 eBPF 程序，并在某些操作上比 kernel eBPF 提供最高 10 倍的性能提升，同时保持对现有 eBPF 工具链的兼容。

## 架构概览

runtime 使用 Boost.Interprocess 构建了一套复杂的共享内存架构，从而实现进程间的零拷贝 IPC。其核心是 handler 模式，通过统一接口管理所有 eBPF 对象（programs、maps、links）。

### 关键架构组件

1. **共享内存管理**（`bpftime_shm.cpp`、`bpftime_shm_internal.cpp`）
   - 用于跨进程对象共享的共享内存中心注册表
   - 维持 kernel 兼容性的文件描述符抽象
   - 用于持久化和调试的 JSON 导入/导出

2. **Handler 系统**（`src/handler/`）
   - `handler_manager`：管理所有 eBPF 对象的中心注册表
   - 按类型区分的 handlers：`prog_handler`、`map_handler`、`link_handler`、`perf_event_handler`
   - 使用 `std::variant` 做类型安全的多态存储

3. **VM 集成**（`bpftime_prog.cpp`）
   - 抽象多个 VM backend（LLVM JIT、ubpf interpreter）
   - helper function 的注册与管理
   - 跨平台执行支持

## 实现细节

### 核心 API（`include/bpftime.hpp`）

主要 runtime API 提供 C 接口，用于：
- Program 生命周期：`bpftime_progs_create()`、program 执行
- Map 操作：`bpftime_maps_create()`、lookup/update/delete
- 事件挂载：`bpftime_uprobe_create()`、`bpftime_link_create()`
- 共享内存：`bpftime_initialize_global_shm()`、JSON 导入/导出

### BPF Maps 实现（`src/bpf_map/`）

runtime 提供了完整的 BPF map 类型集合，分为三类：

#### 用户态 Maps（`userspace/`）
为性能优化的纯用户态实现：
- **基础 maps**：array、hash（固定和可变大小）
- **Per-CPU maps**：带 CPU 亲和性的 per-cpu array/hash
- **专用结构**：ringbuf、queue、stack、bloom filter
- **高级类型**：LPM trie、LRU hash、prog array、stack trace
- **Map-in-maps**：map 数组

关键特性：
- 通过共享内存实现零拷贝操作
- 自定义优化（固定大小 hash table、per-CPU 结构）
- 扩展操作（queue/stack 的 push/pop/peek）

#### 共享 Maps（`shared/`）
连接 kernel 与用户态 eBPF 程序：
- array、hash、per-CPU array、perf event array
- 通过 BPF syscalls 把操作委派给内核
- 支持 kernel 与用户态之间的数据共享

#### GPU Maps（`gpu/`）
面向 GPU 工作负载的 CUDA 加速 maps：
- GPU array 和 ringbuf 实现
- 通过 `CUipcMemHandle` 进行跨进程 GPU 内存共享
- 支持 per-thread GPU buffer

### Handler 实现模式

所有 handler 都遵循一致的模式：

```cpp
class handler {
    // 核心操作
    int create(args...);
    void destroy();
    
    // 按类型区分的操作
    // 例如 map: lookup, update, delete
    // 例如 prog: load, execute
};
```

Handlers 会存储在共享内存中的全局 `handler_variant_vector` 里，并按文件描述符索引，以兼容 kernel。

### Attach 机制（`src/attach/`）

runtime 支持多种 eBPF 程序挂载类型：
- **Uprobe/uretprobe**：通过 Frida 实现函数入口/出口 hook
- **Syscall tracing**：系统调用拦截
- **自定义事件**：可扩展到新的事件源（例如 CUDA）

### Agent 与 Syscall Server

#### Agent（`agent/agent.cpp`）
- 注入到目标进程中的库
- 拦截与 eBPF 相关的系统调用
- 按配置重定向到用户态 runtime 或内核

#### Syscall Server（`syscall-server/`）
- 独立进程，用于管理 eBPF 操作
- 处理来自 agent 的 syscall 重定向
- 为现有 eBPF 工具提供兼容层

## 内存模型

### 共享内存布局

```text
Global Shared Memory (bpftime_maps_shm)
├── handler_manager (central registry)
│   ├── prog_handlers
│   ├── map_handlers
│   ├── link_handlers
│   └── perf_event_handlers
├── Map data (varies by type)
├── Program bytecode
└── Runtime configuration
```

### 同步
- 使用 Boost interprocess mutex 实现跨进程同步
- 使用 pthread spinlock 提升 map 操作性能
- 尽可能采用无锁设计（例如简单 array maps）

## 扩展点

### 添加新的 Map 类型
1. 在 `src/bpf_map/userspace/` 中实现 map 接口
2. 注册到 `bpf_map_handler::create_map_impl()`
3. 在 `bpf_map_type` 中添加类型枚举

### 添加新的 Attach 类型
1. 在 `attach/` 目录中实现 attach 机制
2. 在 attach context 中注册
3. 如有需要，添加 helper 函数

### 外部 Map 操作
使用 `bpftime_register_map_ops()` 注册自定义 map 实现，而无需修改核心 runtime。

## 构建系统

runtime 使用 CMake，并提供多个构建选项：
- `BPFTIME_LLVM_JIT`：启用 LLVM JIT backend
- `BPFTIME_ENABLE_IOURING_EXT`：启用 IO uring 支持
- `BPFTIME_ENABLE_MPK`：启用 Memory Protection Keys
- `BPFTIME_BUILD_WITH_LIBBPF`：kernel map sharing

## 测试

### 单元测试（`unit-test/`）
- 覆盖 maps、programs、attachments 的全面测试
- 共享内存操作测试
- 跨平台兼容性测试

### 集成测试（`test/`）
- 端到端 eBPF 程序执行
- 多进程共享内存测试
- 性能基准测试

## 维护指南

### 常见问题与解决方案

1. **共享内存损坏**
   - 检查 `BPFTIME_GLOBAL_SHM_NAME` 环境变量
   - 使用 `bpftime_remove_global_shm()` 清理
   - 导出/导入 JSON 以便调试

2. **Map 操作失败**
   - 确认 map 类型兼容性
   - 检查 `should_lock` 标志是否满足线程安全要求
   - 确保初始化顺序正确

3. **Program 加载问题**
   - 使用 verifier 验证 bytecode
   - 检查 helper function 注册
   - 确认 VM backend 可用

### 性能优化

1. **Map 选择**
   - 能用固定大小 map 就尽量使用
   - 高竞争场景优先考虑 per-CPU maps
   - GPU 工作负载可利用 GPU maps

2. **VM backend**
   - 生产环境使用 LLVM JIT 追求性能
   - 调试/开发使用 interpreter

3. **共享内存**
   - 在 `bpftime_shm_internal.hpp` 中调优分配大小
   - 使用内存保护（MPK）提升安全性

### 调试工具

1. **JSON 导出/导入**

   参见工具目录中的 bpftimetool 用法。

2. **日志**
   - 设置 `SPDLOG_LEVEL=debug` 获取详细日志
   - 检查 handler 的分配/释放
   - 监控共享内存使用情况

3. **Tracing**
   - 对 agent library 使用系统 tracing 工具
   - 监控 syscall 拦截
   - 分析 map 操作性能
