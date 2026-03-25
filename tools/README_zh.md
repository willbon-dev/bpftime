# Tools

这个目录包含 bpftime 的附加工具，用于改善使用体验，提供 eBPF program 管理、编译和 runtime 控制的高级接口。

## 安装

安装所有 CLI 工具和库：

```bash
make install
export PATH=$PATH:~/.bpftime
```

安装完成后，`~/.bpftime/` 下会提供以下工具：

- `bpftime` - 用于运行和管理 eBPF 程序的主 CLI
- `bpftimetool` - 用于检查和管理共享内存状态的工具
- `bpftime-aot` - 将 eBPF 编译为 native code 的 AOT（Ahead-of-Time）工具

## 工具概览

### 1. bpftime CLI（`bpftime`）

**用途**：通过 `LD_PRELOAD` 把 bpftime runtime 注入到目标进程中的高级接口。这是用户在用户态运行 eBPF 程序时最主要的工具。

**用法**：
```bash
bpftime [OPTIONS] COMMAND
```

**命令**：

#### `load` - 使用 syscall server 启动应用
将 bpftime syscall server 注入到目标应用中，以拦截与 eBPF 相关的系统调用。

```bash
bpftime load <COMMAND> [ARGS...]
```

**示例**：
```bash
# 使用 eBPF syscall interception 运行应用
bpftime load ./my_ebpf_program
```

#### `start` - 使用 bpftime agent 启动应用
将 bpftime agent 注入到目标应用中以执行 eBPF 程序。

```bash
bpftime start [OPTIONS] <COMMAND> [ARGS...]
```

**选项**：
- `-s, --enable-syscall-trace`：启用 syscall tracing 功能

**示例**：
```bash
# 基本的 agent 注入
bpftime start ./target_application

# 启用 syscall tracing
bpftime start -s ./target_application
```

#### `attach` - 把 bpftime agent 注入到正在运行的进程
使用 Frida 注入机制，把 bpftime agent 动态 attach 到已经运行的进程。

```bash
bpftime attach [OPTIONS] <PID>
```

**选项**：
- `-s, --enable-syscall-trace`：启用 syscall tracing 功能

**示例**：
```bash
# attach 到 PID 1234 的进程
bpftime attach 1234

# attach 时开启 syscall tracing
bpftime attach -s 1234
```

#### `detach` - 解除所有已 attach 的 agent
向所有已 attach bpftime agent 的进程发送 SIGUSR1 信号，以触发解除 attach。

```bash
bpftime detach
```

**全局选项**：
- `-i, --install-location <PATH>`：指定 bpftime 安装目录（默认：`~/.bpftime`）
- `-d, --dry-run`：不提交任何修改地运行

### 2. bpftime Tool（`bpftimetool`）

**用途**：检查和管理包含 eBPF 对象（programs、maps、links）的共享内存状态，并提供持久化和传输所需的序列化能力。

**用法**：
```bash
bpftimetool COMMAND [OPTIONS]
```

**命令**：

#### `export` - 将共享内存导出为 JSON
把当前 bpftime 共享内存状态序列化为 JSON 文件，以便备份或分析。

```bash
bpftimetool export <filename.json>
```

#### `import` - 将 JSON 导入共享内存
从 JSON 文件加载 eBPF 对象到 bpftime 共享内存系统。

```bash
bpftimetool import <filename.json>
```

#### `load` - 使用特定 fd 映射加载 JSON

```bash
bpftimetool load <fd> <JSON>
```

#### `remove` - 删除全局共享内存

```bash
bpftimetool remove
```

#### `run` - 执行共享内存中的 eBPF 程序

```bash
bpftimetool run <id> <data_file> [repeat <N>] [type <RUN_TYPE>]
```

**运行类型**：
- `JIT`
- `AOT`
- `INTERPRET`

### 3. bpftime AOT 工具（`bpftime-aot`）

**用途**：Ahead-of-Time（AOT）编译工具，把 eBPF bytecode 编译为 native machine code，以获得最高性能。它支持基于 ELF 的编译，也支持共享内存编译。

**用法**：
```bash
bpftime-aot COMMAND [OPTIONS]
```

**命令**：

#### `build` - 将 eBPF ELF 编译为 native ELF
#### `compile` - 编译共享内存中的程序
#### `load` - 将已编译对象加载到共享内存
#### `run` - 直接执行 native eBPF 程序

### AOT 工作流

1. 直接编译 ELF
1. 从共享内存中编译

### 开发与测试工具

### ARM64 构建测试

### Docker 支持

## 集成示例

### 完整工作流示例

### 性能测试

## 环境变量

### 通用变量

### bpftime CLI 变量

### 平台相关库
