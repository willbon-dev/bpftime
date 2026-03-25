# bpftime daemon：与 kernel eBPF 协同运行的 runtime userspace eBPF

bpftime daemon 是一个系统级监控服务，用于拦截并把来自内核空间的 eBPF 操作重定向到用户态，从而为 eBPF 程序提供更高的性能和灵活性。它会跟踪 kernel eBPF syscalls，并将它们无缝接入 bpftime 的用户态 runtime。

## 概览

daemon 通过以下方式连接 kernel 与用户态 eBPF：

- **透明重定向**：拦截 kernel uprobe/uretprobe eBPF 程序，并在用户态运行，最高可获得 10 倍性能提升，而无需修改原始程序
- **共享状态**：让用户态 eBPF 程序与 kernel eBPF 程序共享 maps，实现无缝数据交换
- **零拷贝通信**：通过共享内存架构实现高效的进程间通信
- **Syscall 跟踪**：监控与 BPF 相关的 syscalls（bpf、perf_event_open、ioctl），以跟踪 eBPF 对象生命周期

## 架构与实现

### 组件

daemon 由两部分组成：

1. **内核态组件**（`kernel/bpf_tracer.bpf.c`）：
   - 运行在内核空间的 eBPF 程序
   - 跟踪 syscalls：bpf()、perf_event_open()、ioctl()、open/close
   - 捕获进程生命周期事件（exec/exit）
   - 通过 ring buffer 向用户态发送事件

2. **用户态组件**（`user/`）：
   - 处理内核事件的 event handler
   - 管理 bpftime runtime 集成的 driver
   - 用于跨进程通信的共享内存管理器

### 关键实现细节

- **事件类型**：daemon 跟踪 `bpf_tracer_event.h` 中定义的多种事件：
  - `SYS_BPF`：BPF syscall 操作（map/program 创建）
  - `SYS_PERF_EVENT_OPEN`：Perf event 创建（包括 uprobes）
  - `BPF_PROG_LOAD_EVENT`：eBPF program 加载
  - `SYS_IOCTL`：Perf event enable/disable 操作
  - `EXEC_EXIT`：进程生命周期事件

- **BPF Program 拦截**：当一个 BPF program 被加载时：
  1. kernel tracer 捕获程序指令和元数据
  2. daemon 为用户态执行重定位 map 引用
  3. 程序被注册到 bpftime 的共享内存 runtime 中
  4. 后续的 uprobe 命中由用户态 runtime 处理

- **Map 共享**：内核中创建的 maps 会在用户态镜像出来：
  - map ID 由 `bpf_obj_id_fd_map` 跟踪
  - 文件描述符映射到共享内存句柄
  - kernel 和用户态程序都能访问同一份数据

## 使用

### 基本使用

```console
$ sudo SPDLOG_LEVEL=Debug build/daemon/bpftime_daemon
[2023-10-24 11:07:13.143] [info] Global shm constructed. shm_open_type 0 for bpftime_maps_shm
```

### 命令行选项

```
Usage: bpftime_daemon [OPTION...]
Trace and modify bpf syscalls

  -p, --pid=PID              Process ID to trace
  -u, --uid=UID              User ID to trace  
  -o, --open                 Show open events
  -v, --verbose              Verbose debug output
  -w, --whitelist-uprobe=ADDR
                             Whitelist uprobe function addresses
```

## 运行 malloc 示例

```console
$ sudo example/malloc/malloc
libbpf: loading object 'malloc_bpf' from buffer
11:08:11 
11:08:12 
11:08:13 
```

和不使用 bpftime_daemon 的 kernel malloc 不同，这里的 malloc 不会输出任何消息。这是因为我们修改了 kernel 中 bpf 和 perf event 的加载及 attach 流程。

## 在目标程序中跟踪 malloc 调用

```console
$ sudo SPDLOG_LEVEL=Debug ~/.bpftime/bpftime start example/malloc/victim
malloc called from pid 12314
continue malloc...
malloc called from pid 12314
continue malloc...
malloc called from pid 12314
continue malloc...
malloc called from pid 12314
continue malloc...
malloc called from pid 12314
```

另一个控制台会输出目标进程中的 malloc 调用。

```console
20:43:22 
        pid=113413      malloc calls: 9
20:43:23 
        pid=113413      malloc calls: 10
20:43:24 
        pid=113413      malloc calls: 10
20:43:25 
        pid=113413      malloc calls: 10
```

## 高级使用

### 环境变量

- `SPDLOG_LEVEL`：设置日志级别（Debug、Info、Warn、Error）
- `BPFTIME_DAEMON_CONFIG`：daemon 配置文件路径（可选）

### 过滤与白名单

daemon 支持过滤 eBPF 操作：

```bash
# 只跟踪指定进程
sudo bpftime_daemon -p 12345

# 只把白名单中的 uprobe 地址重定向到用户态
sudo bpftime_daemon -w 0x401234 -w 0x401567

# 跟踪指定用户的进程
sudo bpftime_daemon -u 1000
```

### 与 bpftime 集成

daemon 会自动与 bpftime runtime 集成：

1. **共享内存**：使用 `/dev/shm/bpftime_maps_shm` 上的 boost::interprocess shared memory
2. **文件描述符**：把 kernel FDs 映射到 bpftime handler IDs
3. **Program 加载**：为用户态执行重定位 eBPF 指令
4. **事件挂载**：把 uprobe/uretprobe 重定向到基于 Frida 的用户态 hooks

## 实现说明

### 关键文件

- `user/bpf_tracer.cpp`：daemon 主循环和内核事件处理
- `user/handle_bpf_event.cpp`：不同 syscall 类型的 event handler
- `user/bpftime_driver.cpp`：与 bpftime runtime 的集成
- `kernel/bpf_tracer.bpf.c`：用于 syscall 跟踪的内核 eBPF 程序
- `bpf_tracer_event.h`：内核与用户态共享的事件定义

### 安全考虑

- 加载内核 eBPF 程序需要 root 权限
- 可通过 PID/UID 过滤来限制作用范围
- 白名单模式限制哪些 uprobes 会在用户态运行
- 会避免跟踪 daemon 自身，以防递归

## 调试：使用 bpftimetool 导出状态

导出结果示例在 [daemon/test/asserts/malloc.json](test/asserts/malloc.json)。

有关如何加载并在内核中回放，请参见 [tools/bpftimetool/README_zh.md](../tools/bpftimetool/README_zh.md)。

## 从源码构建

daemon 是 bpftime 项目的一部分：

```bash
# 构建带 daemon 支持的版本
make build

# daemon 二进制文件会位于：
# build/daemon/bpftime_daemon
```

## 故障排查

1. **Permission Denied**：确保使用 sudo/root 权限运行
2. **共享内存问题**：检查 `/dev/shm/bpftime_maps_shm` 的权限
3. **缺少 Uprobe**：使用 verbose 模式（`-v`）查看 uprobe 解析过程
4. **性能问题**：在配置中调整 `duration_ms` 以过滤短生命周期进程
