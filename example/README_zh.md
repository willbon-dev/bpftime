# 示例与用例

## 目录

- [示例与用例](#示例与用例)
  - [目录](#目录)
  - [最小示例](#最小示例)
  - [系统跟踪](#系统跟踪)
    - [使用 uprobe 跟踪用户态函数](#使用-uprobe-跟踪用户态函数)
    - [使用 tracepoint 跟踪所有 syscall](#使用-tracepoint-跟踪所有-syscall)
    - [bpftrace](#bpftrace)
    - [使用 bpftime 跟踪 SPDK](#使用-bpftime-跟踪-spdk)
  - [BPF 特性演示](#bpf-特性演示)
  - [GPU/CUDA/ROCm 跟踪](#gpucudarocm-跟踪)
  - [应用热补丁](#应用热补丁)
  - [错误注入](#错误注入)
  - [用户态 XDP](#用户态-xdp)
  - [高级示例](#高级示例)
    - [Attach 实现](#attach-实现)
    - [将 bpftime 作为库使用](#将-bpftime-作为库使用)
  - [Nginx eBPF 模块](#nginx-ebpf-模块)
  - [结合 DPDK 和用户态 eBPF 无缝运行 XDP](#结合-dpdk-和用户态-ebpf-无缝运行-xdp)
  - [仅将 vm 作为库使用（不含 runtime，不含 uprobe）](#仅将-vm-作为库使用不含-runtime不含-uprobe)

## 最小示例

参见 [example/minimal](https://github.com/eunomia-bpf/bpftime/tree/master/example/minimal) 了解展示 bpftime 核心特性的基础示例：

- [`uprobe`](https://github.com/eunomia-bpf/bpftime/tree/master/example/minimal)：基础 uprobe 示例
- [`syscall`](https://github.com/eunomia-bpf/bpftime/tree/master/example/minimal)：syscall 跟踪示例
- [`uprobe-override`](https://github.com/eunomia-bpf/bpftime/tree/master/example/minimal)：演示如何使用 `bpf_override_return` 修改函数返回值
- [`usdt_minimal`](https://github.com/eunomia-bpf/bpftime/tree/master/example/minimal/usdt_minimal)：用户静态定义跟踪（USDT）示例

bpftime 支持以下类型的 eBPF 程序：

- `uprobe/uretprobe`：在函数开始或结束时跟踪用户态函数。
- `syscall tracepoints`：跟踪特定类型的 syscall。
- `USDT`：通过 USDT 跟踪用户态函数。

你可以使用 `bpf_override_return` 改变程序的控制流。

更多细节请参见 [documents/available-features.md](https://github.com/eunomia-bpf/bpftime/tree/master/documents/avaliable-features.md)。

## 系统跟踪

### 使用 uprobe 跟踪用户态函数

将 uprobe、uretprobe 或全部 syscall tracepoint（当前仅 x86）eBPF 程序挂载到某个进程或进程组上。

- [`malloc`](https://github.com/eunomia-bpf/bpftime/tree/master/example/malloc)：按 pid 统计 libc 中的 malloc 调用次数，演示如何使用用户态 `uprobe` 和基础 `hashmap`。
- [`bashreadline`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/bashreadline)：打印正在运行的 shell 中输入的 bash 命令。
- [`sslsniff`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/sslsniff)：跟踪并打印所有 SSL/TLS 连接和原始流量数据。
- [`funclatency`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/funclatency)：测量函数延迟分布。
- [`goroutine`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/goroutine)：跟踪 Go runtime 的 goroutine 操作。

### 使用 tracepoint 跟踪所有 syscall

- [`opensnoop`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/opensnoop)：跟踪进程中的文件 open 或 close syscall，演示如何使用用户态 `syscall tracepoint` 和 `ring buffer` 输出。
- [`opensnoop_ring_buf`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/opensnoop_ring_buf)：使用 ring buffer 输出的替代实现。
- [`statsnoop`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/statsnoop)：全局跟踪 stat() syscall。
- [`syscount`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/syscount)：按类型和进程统计 syscall。
- [`mountsnoop`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/mountsnoop)：跟踪 mount 和 umount syscall。
- [`sigsnoop`](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/sigsnoop)：跟踪发送给进程的信号。

更多 bcc/libbpf-tools 风格的示例可以在 [example/tracing](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing) 中找到。

### bpftrace

你也可以让 bpftime 与 `bpftrace` 一起运行，我们已经在 [这个提交](https://github.com/iovisor/bpftrace/commit/75aca47dd8e1d642ff31c9d3ce330e0c616e5b96) 上测试过。

它应该可以直接配合你发行版的软件包管理器中的 bpftrace 使用，例如：

```bash
sudo apt install bpftrace
```

你也可以从源码构建最新的 bpftrace。

更多关于如何在用户态运行 bpftrace 的细节，可以在 [example/tracing/bpftrace](https://github.com/eunomia-bpf/bpftime/tree/master/example/tracing/bpftrace) 中查看。

### 使用 bpftime 跟踪 SPDK

参见 <https://github.com/eunomia-bpf/bpftime/wiki/Benchmark-of-SPDK>，了解如何使用 bpftime 跟踪 SPDK。

## BPF 特性演示

[example/bpf_features](https://github.com/eunomia-bpf/bpftime/tree/master/example/bpf_features) 目录包含多种 BPF map 类型和特性的演示：

- [`bloom_filter_demo`](https://github.com/eunomia-bpf/bpftime/tree/master/example/bpf_features/bloom_filter_demo)：演示如何使用 BPF bloom filter map 做高效的集合成员测试。
- [`get_stack_id_example`](https://github.com/eunomia-bpf/bpftime/tree/master/example/bpf_features/get_stack_id_example)：展示如何使用 `bpf_get_stackid` 捕获并使用堆栈回溯。
- [`lpm_trie_demo`](https://github.com/eunomia-bpf/bpftime/tree/master/example/bpf_features/lpm_trie_demo)：演示用于 IP 地址匹配的最长前缀匹配（LPM）trie map。
- [`queue_demo`](https://github.com/eunomia-bpf/bpftime/tree/master/example/bpf_features/queue_demo)：演示如何使用 BPF queue 和 stack map 实现 FIFO/LIFO 数据结构。
- [`tailcall_minimal`](https://github.com/eunomia-bpf/bpftime/tree/master/example/bpf_features/tailcall_minimal)：BPF tail call 的最小示例，用于程序串联。

## GPU/CUDA/ROCm 跟踪

[example/gpu](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu) 目录包含用于跟踪 GPU kernel 的示例：

- [`cuda-counter`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/cuda-counter)：基础 CUDA kernel 跟踪示例
- [`kernelretsnoop`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/kernelretsnoop)：按线程统计 CUDA kernel 退出时间戳的跟踪器
- [`threadhist`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/threadhist)：线程执行次数直方图
- [`launchlate`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/launchlate)：kernel 启动延迟分析器
- [`mem_trace`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/mem_trace)：内存访问模式跟踪
- [`directly_run_on_gpu`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/directly_run_on_gpu)：直接在 GPU 上运行 eBPF 程序
- [`rocm-counter`](https://github.com/eunomia-bpf/bpftime/tree/master/example/gpu/rocm-counter)：AMD ROCm GPU kernel 跟踪

## 应用热补丁

[example/hotpatch](https://github.com/eunomia-bpf/bpftime/tree/master/example/hotpatch) 目录展示了如何动态修改应用行为：

- [`redis`](https://github.com/eunomia-bpf/bpftime/tree/master/example/hotpatch/redis)：无需修改源代码即可对 Redis 服务端行为打热补丁
- [`vim`](https://github.com/eunomia-bpf/bpftime/tree/master/example/hotpatch/vim)：Vim 编辑器热补丁示例

## 错误注入

- [`error-injection`](https://github.com/eunomia-bpf/bpftime/tree/master/example/error-inject)：向用户态函数或 syscall 注入错误，以测试错误处理能力。

## 用户态 XDP

- [`xdp-counter`](https://github.com/eunomia-bpf/bpftime/tree/master/example/xdp-counter)：在用户态运行 XDP 程序进行数据包处理的示例

## 高级示例

### Attach 实现

[example/attach_implementation](https://github.com/eunomia-bpf/bpftime/tree/master/example/attach_implementation) 目录包含一个完整示例，展示如何使用 bpftime 实现高性能的 nginx 请求过滤器，并附带对比不同过滤方式（eBPF、WASM、LuaJIT、RLBox 等）的 benchmark。

### 将 bpftime 作为库使用

- [`libbpftime_example`](https://github.com/eunomia-bpf/bpftime/tree/master/example/libbpftime_example)：演示如何将 bpftime 的 shared memory 和 runtime 特性作为库使用

## Nginx eBPF 模块

bpftime 实现了一个 Nginx eBPF 模块，可用于用 eBPF 程序扩展 Nginx。

参见 <https://github.com/eunomia-bpf/Nginx-eBPF-module>

## 结合 DPDK 和用户态 eBPF 无缝运行 XDP

参见 <https://github.com/eunomia-bpf/XDP-eBPF-in-DPDK>

我们可以在内核和用户态中运行同一个 eBPF XDP 程序，用户态 eBPF 程序可用于无缝运行 XDP。与 DPDK 中的 ubpf 不同，我们不需要修改 eBPF 程序，并且可以支持 eBPF maps。

## 仅将 vm 作为库使用（不含 runtime，不含 uprobe）

LLVM JIT 或 AOT 可以作为库使用，而不需要 runtime 和 uprobe。

示例：

1. Cli: <https://github.com/eunomia-bpf/bpftime/tree/master/vm/cli>
2. Simple example: <https://github.com/eunomia-bpf/bpftime/tree/master/vm/example>
