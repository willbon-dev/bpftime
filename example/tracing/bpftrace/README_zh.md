# bpftrace 示例：在用户态运行 bpftrace

bpftrace 是一种面向 Linux 的高级 tracing 语言，针对增强型 Berkeley Packet Filter（eBPF）而设计，可用于较新的 Linux 内核（4.x）。bpftrace 使用 LLVM 作为后端把脚本编译为 BPF 字节码，并借助 BCC 与 Linux BPF 系统交互，同时利用现有的 Linux tracing 能力：内核动态 tracing（kprobes）、用户态动态 tracing（uprobes）以及 tracepoints。该语言的灵感来自 awk 和 C，也参考了 DTrace 和 SystemTap 等前辈 tracing 工具。

仓库：<https://github.com/iovisor/bpftrace>

不过，运行 bpftrace 需要 root 权限，并且依赖内核中的 eBPF 能力。使用 bpftime 后，你可以在用户态运行 bpftrace，而不需要内核 eBPF 支持。

注意：我们测试仓库实例中的 `.bt` 文件所用操作系统是 Ubuntu 22.04。在该系统版本下，执行 `apt install bpftrace` 可以安装 bpftrace 0.9.4。

## uprobe 示例

下面是一个示例，可以先在用户态通过 uprobe 运行一条 bpftrace 命令：

```console
$ sudo ~/.bpftime/bpftime load bpftrace -e 'uretprobe:/bin/bash:readline { printf("%-6d %s\n", pid, str(retval)); }'
[2023-10-27 19:00:32][info][13368] bpftime-syscall-server started
Attaching 1 probe...
13615  
13615  clear
13615  clear
13615  cat
```

然后启动一个 bash 进程，你就能看到 bpftrace 的输出。

```console
sudo ~/.bpftime/bpftime start /bin/bash
```

我们使用过 [这个 commit](https://github.com/iovisor/bpftrace/commit/75aca47dd8e1d642ff31c9d3ce330e0c616e5b96) 对 bpftrace 进行测试。较旧版本的 bpftrace 可能会引入一些问题。

## syscall tracing 示例

```console
$ sudo SPDLOG_LEVEL=error ~/.bpftime/bpftime load bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'
[2023-10-27 19:17:34.099] [info] manager constructed
[2023-10-27 19:17:34.289] [info] Initialize syscall server
Attaching 1 probe...
cat /usr/lib/locale/locale-archive
cat build/install_manifest.txt
```

然后：

```console
$ sudo SPDLOG_LEVEL=error ~/.bpftime/bpftime start -s cat build/install_manifest.txt
[2023-10-27 19:17:41.677] [info] Entering bpftime agent
[2023-10-27 19:17:41.986] [info] Global shm constructed. shm_open_type 1 for bpftime_maps_shm
/root/.bpftime/bpftime_daemon
/root/.bpftime/bpftimetool
/root/.bpftime/libbpftime-agent.so
/root/.bpftime/libbpftime-agent-transformer.so
/root/.bpftime/libbpftime-syscall-server.so
```

你也可以结合本目录下的工具，在用户态尝试 bpftrace。

## One-Liners

下面是一些可以尝试的 bpftrace 单行命令，它们都可以通过用户态 bpftime 运行。它们展示了不同的能力：

```sh
# 被进程打开的文件
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# 按程序统计 syscall 次数
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'

# 按进程统计读取字节数：
bpftrace -e 'tracepoint:syscalls:sys_exit_read /args->ret/ { @[comm] = sum(args->ret); }'

# 按进程统计读取大小分布：
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @[comm] = hist(args->ret); }'

# 显示每秒 syscall 速率：
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @ = count(); } interval:s:1 { print(@); clear(@); }'
```

更复杂的脚本也很容易构造。可以查看其他工具示例。注意：由于缺少部分 helper，某些脚本可能不会按预期工作，我们正在处理这个问题。
