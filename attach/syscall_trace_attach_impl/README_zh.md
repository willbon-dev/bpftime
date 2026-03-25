# Syscall Trace Attach 实现

这个组件提供了一个机制，让 bpftime 可以在用户态把 eBPF 程序挂载到系统调用上。

## 概览

syscall trace attach 实现允许通过把 eBPF 程序挂载到以下位置来拦截和监控系统调用：
- 特定 syscall 的入口点（例如进入 `read`、`write`）
- 特定 syscall 的出口点（例如退出 `read`、`write`）
- 所有 syscall 的入口（全局 enter hook）
- 所有 syscall 的出口（全局 exit hook）

## 核心组件

- **Syscall Table**：提供 syscall ID、名称和 tracepoint 之间的映射
- **Syscall Trace Attach 实现**：将 eBPF 回调挂载到 syscall 的核心实现
- **Private Data**：用于 attach 操作的配置结构

## 工作方式

1. **Syscall 映射**：通过 `/sys/kernel/tracing/events/syscalls/*` 将系统调用从 ID 映射到名称和 tracepoint
2. **挂载**：可以通过 `syscall_trace_attach_impl` 类把 eBPF 程序挂载到特定 syscall 的入口/出口点
3. **分发**：当 syscall 被拦截时，实现在适当的已注册回调之间分发调用
4. **回调**：已注册回调会收到包括 syscall 参数在内的上下文信息，并且可以选择覆盖返回值

## 使用示例

下面示例展示了如何把一个 eBPF 程序挂载到 `read` syscall 的入口：

```cpp
// 创建 attach 实现
syscall_trace_attach_impl attacher;

// 为 "read" syscall 入口创建 private data
syscall_trace_private_data data;
data.initialize_from_string("..."); // sys_enter_read 的 tracepoint ID 字符串

// 挂载一个 eBPF 回调
int attach_id = attacher.create_attach_with_ebpf_callback(
    [](const void *ctx, size_t size, uint64_t *ret) -> int {
        // 访问 syscall 上下文
        auto &enter_ctx = *(trace_event_raw_sys_enter *)ctx;
        // 处理 syscall 参数
        // enter_ctx.args[0]、enter_ctx.args[1] 等
        return 0;
    },
    data,
    ATTACH_SYSCALL_TRACE
);

// 之后可以按 ID 解除挂载
attacher.detach_by_id(attach_id);
```

## 与 Text Segment Transformer 集成

该实现旨在与 Text Segment Transformer 配合工作，后者会修改进程的可执行代码，以便在运行时拦截 syscall。

syscall tracing 实现接收来自 transformer 的 syscall 事件，并把它们分发给已注册的 eBPF 程序。
