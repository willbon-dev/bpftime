# bpftime LPM Trie 演示

这个演示展示了 bpftime 的 LPM（Longest Prefix Matching）Trie 功能，用于文件访问控制。

## 概览

该演示实现了一个文件访问监控系统，使用：
- **BPF_MAP_TYPE_LPM_TRIE**：用于前缀匹配的真实 LPM Trie map
- **Client/Server 架构**：bpftime syscall-server 和 agent
- **实时监控**：基于 uprobe 的文件访问拦截

## 文件

- `file_access_filter.bpf.c`：包含 LPM Trie 逻辑的 BPF 程序
- `file_access_monitor.c`：监控程序（bpftime server）
- `file_access_target.c`：测试目标程序（bpftime client）
- `run_lmp_trie_demo.sh`：演示执行脚本
- `Makefile`：构建配置

## 快速开始

```bash
# 运行完整演示
./run_lpm_trie_demo.sh

# 仅构建
./run_lpm_trie_demo.sh --build

# 仅测试
./run_lpm_trie_demo.sh --test

# 清理
./run_lpm_trie_demo.sh --clean
```

## 工作原理

1. **Monitor**（Server）：加载 BPF 程序，并用允许的前缀初始化 LPM Trie
2. **Target**（Client）：执行会触发 uprobe 事件的文件操作
3. **LPM Trie**：自动查找最长匹配前缀，用于访问控制
4. **Event Queue**：实时处理文件访问事件

## 允许的前缀

- `/tmp/`
- `/var/tmp/`
- `/usr/share/`
- `/home/user/documents/`

## 架构

```text
Monitor (Server) → bpftime Server → BPF Maps (LPM Trie, Queue, Counter)
Target (Client)  → bpftime Agent  → Shared Memory
BPF Program      → LPM Trie       → Access Control
```

## 要求

- 已构建的 bpftime runtime
- 支持 BPF 的 Linux
- Make 和 GCC
