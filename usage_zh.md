<a id="manual"></a>
# 手册

🚧 目前仍处于早期阶段，可能在更多平台或更多 eBPF 程序上存在 bug。我们正在持续提升稳定性和兼容性，因此现在还不适合生产环境使用。

如果你发现任何 bug 或有建议，欢迎提 issue，谢谢！

## 目录

<a id="table-of-contents"></a>
- [手册](#manual)
  - [目录](#table-of-contents)
  - [Uprobe 和 uretprobe](#uprobe-and-uretprobe)
  - [Syscall 跟踪](#syscall-tracing)
  - [直接使用 LD_PRELOAD 运行](#run-with-ld_preload-directly)
  - [runtime 配置](#configurations-for-runtime)
    - [启用或禁用 JIT 运行](#run-with-jit-enabled-or-disabled)
    - [与 kernel eBPF 和 kernel verifier 一起运行](#run-with-kernel-ebpf-and-kernel-verifier)
    - [控制日志级别](#control-log-level)
    - [控制日志路径](#controlling-the-log-path)
    - [允许外部 maps](#allow-external-maps)
    - [设置共享内存 maps 的内存大小](#set-memory-size-for-shared-memory-maps)
  - [Verifier](#verifier)

<a id="uprobe-and-uretprobe"></a>
## Uprobe 和 uretprobe

使用 `bpftime`，你可以用 clang 和 libbpf 等熟悉的工具构建 eBPF 应用，并在用户态执行。例如，`malloc` 这个 eBPF 程序会通过 uprobe 跟踪 malloc 调用，并使用 hash map 聚合计数。

你可以参考 [documents/build-and-test.md](build-and-test.md) 来了解如何构建项目。

要开始使用，你可以构建并运行一个基于 libbpf 的 eBPF 程序，使用 `bpftime` cli：

```console
make -C example/malloc # 构建 eBPF 示例程序
bpftime load ./example/malloc/malloc
```

在另一个 shell 中，运行带有 eBPF 的目标程序：

```console
$ bpftime start ./example/malloc/victim
Hello malloc!
malloc called from pid 250215
continue malloc...
malloc called from pid 250215
```

你也可以把 eBPF 程序动态挂载到一个正在运行的进程上：

```console
$ ./example/malloc/victim & echo $! # pid 是 101771
[1] 101771
101771
continue malloc...
continue malloc...
```

然后把它 attach 上去：

```console
$ sudo bpftime attach 101771 # 你可能需要在 root 下运行 make install
Inject: "/root/.bpftime/libbpftime-agent.so"
Successfully injected. ID: 1
```

你可以看到原始程序的输出：

```console
$ bpftime load ./example/malloc/malloc
...
12:44:35 
        pid=247299      malloc calls: 10
        pid=247322      malloc calls: 10
```

另外，你也可以直接在 kernel eBPF 中运行我们的示例 eBPF 程序，以观察相似的输出：

```console
$ sudo example/malloc/malloc
15:38:05
        pid=30415       malloc calls: 1079
        pid=30393       malloc calls: 203
        pid=29882       malloc calls: 1076
        pid=34809       malloc calls: 8
```

<a id="syscall-tracing"></a>
## Syscall 跟踪

示例可以在 [examples/opensnoop](https://github.com/eunomia-bpf/bpftime/tree/master/example/opensnoop) 找到。

```console
$ sudo ~/.bpftime/bpftime load ./example/opensnoop/opensnoop
[2023-10-09 04:36:33.891] [info] manager constructed
[2023-10-09 04:36:33.892] [info] global_shm_open_type 0 for bpftime_maps_shm
[2023-10-09 04:36:33][info][23999] Enabling helper groups ffi, kernel, shm_map by default
PID    COMM              FD ERR PATH
72101  victim             3   0 test.txt
72101  victim             3   0 test.txt
72101  victim             3   0 test.txt
72101  victim             3   0 test.txt
```

在另一个终端中，运行 victim 程序：

```console
$ sudo ~/.bpftime/bpftime start -s example/opensnoop/victim
[2023-10-09 04:38:16.196] [info] Entering new main..
[2023-10-09 04:38:16.197] [info] Using agent /root/.bpftime/libbpftime-agent.so
[2023-10-09 04:38:16.198] [info] Page zero setted up..
[2023-10-09 04:38:16.198] [info] Rewriting executable segments..
[2023-10-09 04:38:19.260] [info] Loading dynamic library..
...
test.txt closed
Opening test.txt
test.txt opened, fd=3
Closing test.txt...
```

<a id="run-with-ld_preload-directly"></a>
## 直接使用 LD_PRELOAD 运行

如果命令行接口不够用，你也可以直接通过 `LD_PRELOAD` 运行 eBPF 程序。

命令行工具本质上是 `LD_PRELOAD` 的一个封装，并且可以配合 `ptrace` 把 runtime shared library 注入到正在运行的目标进程中。

使用 libbpf 运行 eBPF 工具：

```sh
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so example/malloc/malloc
```

启动要跟踪的目标程序：

```sh
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so example/malloc/victim
```

<a id="configurations-for-runtime"></a>
## runtime 配置

可以通过环境变量来控制 runtime 行为。环境变量的完整定义见 [https://github.com/eunomia-bpf/bpftime/blob/master/runtime/include/bpftime_config.hpp](https://github.com/eunomia-bpf/bpftime/blob/master/runtime/include/bpftime_config.hpp)。

<a id="run-with-jit-enabled-or-disabled"></a>
### 启用或禁用 JIT 运行

如果性能还不够好，你可以尝试启用 JIT。新版本默认已启用 JIT。

例如，在运行 server 时设置 `BPFTIME_DISABLE_JIT=true` 来禁用 JIT：

```sh
LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so BPFTIME_DISABLE_JIT=true example/malloc/malloc
```

旧版本里 JIT 可能是关闭的。此时可通过设置 `BPFTIME_USE_JIT=true` 来启用 JIT，例如：

```sh
LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so BPFTIME_USE_JIT=true example/malloc/malloc
```

默认行为是使用 LLVM JIT，你也可以在启用 LLVM JIT 构建的情况下使用 ubpf JIT。更多细节请参见 [documents/build-and-test.md](build-and-test.md)。

<a id="run-with-kernel-ebpf-and-kernel-verifier"></a>
### 与 kernel eBPF 和 kernel verifier 一起运行

你可以通过两种方式把用户态中的 eBPF 程序与 kernel eBPF 一起运行。内核必须启用 eBPF 支持，并且内核版本要足够新，以支持 mmap eBPF map。

- 使用 `BPFTIME_RUN_WITH_KERNEL` 让 eBPF 应用通过 kernel eBPF loader 和 kernel verifier 加载。程序会先进入内核进行验证，但仍然可以通过 bpftime agent 在用户态运行。
- 使用 `BPFTIME_NOT_LOAD_PATTERN` 在设置了 `BPFTIME_RUN_WITH_KERNEL` 时跳过将 eBPF 程序加载进内核。这个 pattern 是用于匹配程序名称的正则表达式。它可以帮助跳过一些仅支持用户态、而 kernel verifier 不支持的 eBPF 程序。

1. 使用共享库 `libbpftime-syscall-server.so`，例如：

```sh
BPFTIME_NOT_LOAD_PATTERN=start_.* BPFTIME_RUN_WITH_KERNEL=true LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so example/malloc/malloc
```

2. 使用 daemon 模式，参见 <https://github.com/eunomia-bpf/bpftime/tree/master/daemon>

<a id="control-log-level"></a>
### 控制日志级别

设置 `SPDLOG_LEVEL` 可以动态控制日志级别，例如在运行 server 时：

```sh
SPDLOG_LEVEL=debug LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so example/malloc/malloc
```

可用的日志级别包括：

- trace
- debug
- info
- warn
- err
- critical
- off

更多细节请参见 <https://github.com/gabime/spdlog/blob/v1.x/include/spdlog/cfg/env.h>。

也可以在编译时通过指定 `-DSPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_INFO` 来控制日志级别。

<a id="controlling-the-log-path"></a>
### 控制日志路径

你可以通过设置 `BPFTIME_LOG_OUTPUT` 环境变量来控制日志输出路径。默认情况下，日志会发送到 `~/.bpftime/runtime.log`，以避免污染目标进程。你可以通过环境变量覆盖这个默认行为。

要把日志发送到 `stderr`：

```sh
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so example/malloc/malloc
```

要把日志发送到指定文件：

```sh
BPFTIME_LOG_OUTPUT=./mylog.txt LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so example/malloc/malloc
```

<a id="allow-external-maps"></a>
### 允许外部 maps

有时你可能想使用 bpftime 不支持的外部 maps，例如加载一个带有自定义共享内存 map 的 XDP 程序，并使用自己的工具来运行它。

- 设置 `BPFTIME_ALLOW_EXTERNAL_MAPS`，允许外部（不支持的）maps 通过 bpftime syscall-server library 加载，例如：

```sh
BPFTIME_ALLOW_EXTERNAL_MAPS=true LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so userspace-xdp/xdp_loader
```

<a id="set-memory-size-for-shared-memory-maps"></a>
### 设置共享内存 maps 的内存大小

有时更大的 map 需要更多内存。你可以通过在 server 中设置 `BPFTIME_SHM_MEMORY_MB` 来指定共享内存 maps 的内存大小。该值以 MB 为单位，例如在运行 server 时：

```sh
BPFTIME_SHM_MEMORY_MB=1024 LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so example/malloc/malloc
```

<a id="verifier"></a>
## Verifier

由于 bpftime 的主要目标是尽量与 kernel eBPF 保持一致，因此建议使用内核的 eBPF verifier 来保证程序安全。

你可以设置 `BPFTIME_RUN_WITH_KERNEL` 环境变量，让程序加载进内核并由 kernel verifier 验证：

```sh
BPFTIME_RUN_WITH_KERNEL=true LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so example/malloc/malloc
```

如果 kernel verifier 不可用，你可以在 bpftime 构建过程中启用 `ENABLE_EBPF_VERIFIER` 选项，使用 `PREVAIL` 用户态 eBPF verifier：

```sh
cmake -DENABLE_EBPF_VERIFIER=YES -DCMAKE_BUILD_TYPE=Release -S . -B build
```
