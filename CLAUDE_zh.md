# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在处理本仓库代码时提供指引。

## 项目概览

bpftime 是一个高性能的用户态 eBPF runtime 和通用扩展框架。它支持在用户态运行 eBPF 程序，用于可观测性、网络、GPU 以及其他场景，在某些操作上可比 kernel eBPF 获得最高 10 倍的性能提升。

## 常用开发命令

### 构建命令

```bash
# 构建包含测试和全部组件的版本（Debug 模式）
make build

# 构建 release 版本
make release

# 构建带 LLVM JIT 支持的版本
make release-with-llvm-jit

# 构建静态库版本
make release-with-static-lib

# 清理构建产物
make clean

# 构建指定组件
cmake --build build --target <target_name>
```

### 测试命令

```bash
# 运行所有单元测试
make unit-test

# 仅运行 runtime 测试
make unit-test-runtime

# 仅运行 daemon 测试
make unit-test-daemon

# 构建 eBPF 测试程序（来自 runtime/test/bpf）
make -C runtime/test/bpf

# 运行指定测试二进制
./build/runtime/unit-test/bpftime_runtime_tests
./build/daemon/test/bpftime_daemon_tests
```

### 运行示例

```bash
# 构建示例程序
make -C example/malloc

# 加载并运行 eBPF 程序
export PATH=$PATH:~/.bpftime/
bpftime load ./example/malloc/malloc
bpftime start ./example/malloc/victim

# 附加到正在运行的进程（需要 sudo）
sudo bpftime attach <pid>
```

### 开发工具

```bash
# 安装到系统（构建完成后）
sudo cmake --install build

# 使用特定特性构建
cmake -Bbuild -DBPFTIME_ENABLE_IOURING_EXT=1  # IO uring support
cmake -Bbuild -DBPFTIME_LLVM_JIT=1           # LLVM JIT backend
cmake -Bbuild -DBPFTIME_ENABLE_MPK=1         # Memory Protection Keys
```

## 架构与代码结构

### 组件组织

代码库由若干通过清晰接口相互协作的组件组成：

1. **`vm/`** - 虚拟机实现
   - `vm-core/`：核心 VM 接口与抽象
   - `llvm-jit/`：基于 LLVM 的 JIT/AOT 编译器（高性能）
   - 支持多个 backend（LLVM JIT、ubpf）

2. **`runtime/`** - 核心 runtime 功能
   - `include/`：公开 API 与接口
   - `src/handler/`：用于管理 eBPF 对象（programs、maps、links）的 handler 模式
   - `src/bpf_map/`：map 实现（hash、array、ringbuf 等）
   - `syscall-server/`：拦截 eBPF syscalls 以提升兼容性
   - `agent/`：注入到目标进程中的库

3. **`attach/`** - 事件挂载机制
   - `base_attach_impl/`：所有 attach 类型的抽象接口
   - `frida_uprobe_attach_impl/`：通过 Frida 进行动态插桩
   - `syscall_trace_attach_impl/`：syscall 拦截
   - `nv_attach_impl/`：CUDA/GPU 事件挂载

4. **`daemon/`** - 系统监控和内核交互
   - 监控 kernel eBPF 操作
   - 可重定向到用户态 runtime

5. **`bpftime-verifier/`** - 安全验证
   - 封装 PREVAIL verifier 作为用户态 verifier
   - 支持可选的 kernel verifier 集成

### 关键架构模式

1. **共享内存架构**：使用 boost::interprocess 在进程间实现零拷贝 IPC
   - 共享内存中的 central `handler_manager` 注册表
   - 用于兼容 kernel 的文件描述符抽象

2. **Handler 模式**：所有 eBPF 对象（programs、maps、links）都通过 handler 管理
   - 提供统一的创建/销毁/访问接口
   - 支持跨进程对象共享

3. **模块化 Attach 系统**：通过实现 `base_attach_impl` 来增加新的事件源
   - 每种 attach 类型提供自己的 helper
   - 支持自定义上下文准备

4. **VM 抽象**：通过统一接口支持多种 VM backend
   - 可透明切换 interpreter / JIT / AOT
   - 可扩展的 helper function 注册机制

### 重要文件和接口

- `runtime/include/bpftime.hpp`：主要 runtime API
- `runtime/include/bpftime_shm.hpp`：共享内存管理
- `vm/vm-core/include/ebpf-vm.h`：VM 接口
- `attach/base_attach_impl/base_attach_impl.hpp`：Attach 接口
- `runtime/src/handler/handler_manager.hpp`：中心对象注册表

### 开发流程

1. **新增功能**：先检查相似组件中的现有模式
2. **测试**：在对应组件的 test 目录中添加单元测试
3. **eBPF 程序**：使用标准 clang/libbpf 工具链，同时在用户态和内核中测试
4. **性能**：考虑共享内存开销，优先批量操作

这个架构优先考虑性能（绕过内核）、兼容性（与 kernel eBPF 保持相同 API）和可扩展性（通过模块化设计支持新特性）。
