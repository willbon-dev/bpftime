# 使用 bpftime 的 FUSE 缓存

## 概述

与内核内替代方案相比，用户态文件系统（FUSE）框架在可靠性和安全性方面有优势，但由于每次 I/O 系统调用都要额外进行上下文切换，因此运行时开销也更高。

像 ExtFuse 这类方案可以通过把 FUSE 文件系统的逻辑推入内核，显著降低这类开销，但它们需要自定义内核模块，而这类模块通常很难维护。

这个项目演示了 bpftime 如何在不需要自定义内核模块的情况下提供同样的收益。

构建和运行基准测试的方法请参考 [bpf/README](bpf/README_zh.md)。

## 实现

我们实现了两个扩展，用于加速使用 FUSE 的应用：

### 1. 元数据缓存

这个扩展通过以下方式加速对同一文件系统条目的重复查找：

- 使用 bpftime 自动化的 syscall tracepoint，覆盖 `open`、`close`、`getdents` 和 `stat`
- 基于 bpftime 自动化可定制扩展类别
- 为会与文件路径交互的 bpftime helper 添加函数能力（例如 `realpath`）
- 使用进程与内核共享的 map
- 通过内核中的 `unlink` kprobe 扩展维持缓存一致性

### 2. 权限检查黑名单

这个扩展通过使用 bpftime 自动化可定制扩展类别，加速访问文件系统条目（例如 `open`）时的权限检查。

## 性能评估

我们在 System A 的 FUSE 文件系统上，使用 bpftime 实现缓存并评估了性能提升：

- **Passthrough**：直接将文件系统操作传递给底层文件系统
- **LoggedFS**：在传递给底层文件系统之前，先将所有文件系统操作记录到文件中

### 测试工作负载

1. 对 FUSE 目录中的某个文件执行 100,000 次 `fstatat`
2. 对 FUSE 目录中的某个文件执行 100,000 次 `openat`
3. Linux 工具 `find` 递归遍历目录

## 构建与运行

```sh
make
```

如何运行基准测试请参考 [bpf/README](bpf/README_zh.md)。
