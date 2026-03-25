# mem_trace

一个使用 eBPF 跟踪 CUDA kernel 调用的简单示例。

这个示例演示了如何使用 bpftime 将 eBPF probe 挂载到运行在用户态的 CUDA kernel 上，并跟踪其执行。

## 构建

```bash
# 先构建 bpftime（从 bpftime 根目录）
cd bpftime
make release

# 再构建示例
make -C example/gpu/mem_trace
```

这会构建：
- `mem_trace` - eBPF tracing 程序
- `vec_add` - CUDA 向量加法 victim 程序（需要 nvcc）

## 运行

你需要启动两个进程：

### 1. 启动 eBPF 程序（Server）

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/mem_trace/mem_trace
```

该进程会加载 eBPF 程序并等待 CUDA 事件。

### 2. 运行 CUDA 应用（Client）

在另一个终端中：

```bash
BPFTIME_LOG_OUTPUT=console  LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/mem_trace/vec_add
```

这会在 bpftime agent 的配合下运行向量加法程序，并连接到第一个进程执行 eBPF。

## 输出说明

mem_trace 程序会打印统计信息，显示每个进程的 CUDA kernel 调用次数：

```
16:30:45
	pid=12345 	mem_traces: 120
```

这表示进程 12345 已经执行了 120 次 CUDA kernel。
