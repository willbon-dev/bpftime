# tailcall 示例

这是一个演示如何从用户态发起到内核 tailcall 的示例。

## 用法

```
make -j$(nproc)
```

### 终端 1

```
bpftime load ./tailcall_minimal
```

### 终端 2

```
bpftime start ./victim
```

### 行为

查看 `/sys/kernel/debug/tracing/trace_pipe`，检查其中是否有包含 `Invoked!` 的输出行。

## 关于这个示例

`tailcall_minimal.bpf.c` 本身是一个 uprobe eBPF 程序。当调用 `./victim:add_func` 时，它会被触发，并执行 `bpf_tail_call` 去调用一个内核 eBPF 程序；该内核程序的 fd 存放在 prog array 中。

`tailcall_minimal.c` 是一个 loader 程序。它会执行原始 syscall、将一个 eBPF 程序加载到内核中（该程序会向 `trace_pipe` 打印 `Invoked!`），并把内核 fd 存入用户态 prog array。
