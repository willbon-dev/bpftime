# syscall_server.so

可作为 `LD_PRELOAD` 使用，用于拦截 bpf syscalls，并在用户态中模拟它们，或者对它们进行跟踪，让 kernel eBPF 与用户态 eBPF 协同运行。

## 以用户态 eBPF 运行

默认行为是使用用户态 eBPF。使用用户态 eBPF 意味着使用共享内存中的用户态 eBPF maps、用户态 eBPF verifier，以及用户态 eBPF runtime。

server：

```sh
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so example/malloc/malloc
```

client：

```sh
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so example/malloc/victim
```

## 与 kernel 一起运行

把环境变量 `BPFTIME_RUN_WITH_KERNEL` 设置为 `true`，即可让 kernel eBPF 与用户态 eBPF 协同运行。这意味着会使用 kernel eBPF maps 代替用户态 eBPF maps，并使用 kernel eBPF verifier 代替用户态 eBPF verifier。

```sh
BPFTIME_RUN_WITH_KERNEL=true
```

开始跟踪的示例：

```sh
SPDLOG_LEVEL=Debug BPFTIME_RUN_WITH_KERNEL=true LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so example/malloc/malloc
```

运行目标程序的示例：

```sh
SPDLOG_LEVEL=Debug LD_PRELOAD=build/runtime/agent/libbpftime-agent.so example/malloc/victim
```

## 跳过某些程序的验证

```sh
BPFTIME_NOT_LOAD_PATTERN=.*
```
