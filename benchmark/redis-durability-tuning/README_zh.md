# 使用 BPFtime 调优 Redis 持久性

这个项目探索如何在尽量减少性能影响的前提下，使用 BPFtime 增强 Redis 的持久性。

## 背景

Redis 是一个键值存储，通过预写日志（Append-Only File，简称 AOF）提供持久性。默认情况下，Redis 提供三种持久性配置，它们在持久性和性能开销之间做权衡：

- **no AOF**：不提供持久性
- **everysec**：确保每秒写入一次持久化
- **alwayson**：确保每次写入都会立即持久化

alwayson 与 everysec 之间的持久性差距很大：在 everysec 模式下发生崩溃，可能会丢失数万次更新。不幸的是，与 everysec 相比，alwayson 也会让吞吐量下降约 6 倍。

## 方法

Redis 可以通过扩展使用 BPFtime 提供可定制的持久性。由于 Redis AOF 目前并不是为扩展而设计的，我们在源代码中添加了新的函数来支持扩展。我们定义了 3 个新函数，并在 Redis 的 write、fsync 和 fdatasync 函数顶部调用它们。

随后，我们使用 BPFtime 注解将这些新函数标识为扩展入口。总共只需要大约 20 行代码。借助更新后的 Redis，系统管理员就可以尝试自定义持久性策略。

## 实现

我们实现了多种不同方法来提升 Redis 持久性：

### 1. 延迟 fsync（delayed-fsync）

这个扩展修改 fdatasync 的行为，使其等待前一次 fdatasync 调用完成，从而确保系统最多只会丢失 2 次更新。

### 2. 快速路径优化（fsync-fast-notify）

这个方案扩展内核，向用户态暴露一个共享变量，用于跟踪进程各个已打开文件上完成的 fdatasync 次数。fdatasync 扩展从这个共享变量中读取数据，并仅在前一次 fdatasync 尚未完成时才执行系统调用。

### 3. BPF Sync Kernel（bpf-sync-kernel）

一种额外的内核级同步优化方案。

## 前置条件

在构建和运行基准测试之前，请确保安装了以下工具：

- GCC/G++ 编译器
- Make
- Git
- Python（用于运行基准脚本）
- Clang（用于 BPF 编译）
- LibELF 开发文件（`libelf-dev` 或等价包）

## 构建与运行

### 构建 Redis

该基准使用了一个支持 BPFtime 扩展的 Redis 修改版。要构建 Redis：

```bash
make redis
```

这会：

1. 从 <https://github.com/eunomia-bpf/redis> 克隆 Redis 仓库
2. 从源码构建 Redis

### 构建 BPF 扩展

每个 BPF 扩展实现都有自己的 Makefile。你可以通过以下命令一次性构建全部实现：

```bash
make build
```

这个命令会构建 `batch_process` 实现。要分别构建各个实现：

#### 单独构建各个实现

**Batch Process 实现：**

```bash
cd batch_process
make
```

**Delayed-Fsync 实现：**

```bash
cd delayed-fsync
make
```

**Fast-Notify 实现：**

```bash
cd fsync-fast-notify
make
```

**IO_uring 实现：**

```bash
cd poc-iouring-minimal
make
```

### 运行基准测试

在构建完所有组件之后，你可以运行基准脚本来比较不同实现：

```bash
python benchmark.py
```

基准测试会比较不同持久性设置和 BPF 扩展下的 Redis 性能。

## 实现细节

每种方法都放在各自目录中：

- `batch_process/`：批处理实现
- `poc-iouring-minimal/`：io_uring 批量 I/O 实现
- `delayed-fsync/`：延迟 fsync 实现
- `fsync-fast-notify/`：快速路径优化实现
- `bpf-sync-kernel/`：内核级同步优化实现

每个实现目录都包含：

- BPF 程序的 C 源文件
- 用于构建的 Makefile
- 介绍该实现细节的 README

## 故障排查

如果你遇到构建问题：

1. 确认所有前置条件都已安装
2. 检查 libbpf 和内核头文件是否可用
3. 查看构建输出中的错误信息
4. 查阅对应实现目录下的 README，确认是否有特殊要求

## 目录结构

```
redis-durability-tuning/
├── batch_process/         # 批处理实现
├── delayed-fsync/         # 延迟 fsync 实现
├── fsync-fast-notify/     # 快速路径优化实现
├── poc-iouring-minimal/   # IO_uring 实现
├── redis/                 # 修改后的 Redis 源码
├── benchmark.py           # 基准脚本
└── Makefile               # 用于构建各组件的主 Makefile
```
