# CUDA eBPF 早退示例

这个示例演示如何使用 `bpftime` 在甚至还没真正进入 CUDA kernel 之前就让其退出，这和网络包场景中的 XDP 作用类似，你可以：

- 实现 [LithOS](https://dl.acm.org/doi/10.1145/3731569.3764818) 中提出的 kernel atomizer
- 从 host 侧配置 CUDA thread block 的划分

## 概览

这个示例由两个主要部分组成：

1. **向量加法 CUDA 应用**（`vec_add`）：一个简单的 CUDA 应用，会在 GPU 上反复执行向量加法。
2. **eBPF CUDA Atomizer**（`cuda_probe`）：一个挂载到 CUDA kernel 函数上的 eBPF 程序，用于决定是否在真正启动 kernel 之前提前退出。

## 工作方式

这个示例利用 bpftime 的 CUDA 挂载实现来完成以下事情：

1. 通过 CUDA runtime API 拦截 CUDA 二进制加载
2. 在 `vectorAdd` kernel 的入口点插入 eBPF 代码（转换为 PTX）
3. 每当 kernel 被调用时执行 eBPF 程序
4. 如果预测条件满足，就直接让 thread block 退出

## 构建示例

```bash
# 进入 bpftime 根目录
cd bpftime

# 先构建 bpftime 主工程
cmake -Bbuild -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda .
cmake --build build -j$(nproc)

# 构建示例
make -C example/gpu/atomizer
```

## 运行示例

你需要启动两个进程：

### 1. 启动 eBPF 程序（Server）

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/atomizer/atomizer
```

该进程会加载 eBPF 程序并等待 CUDA 事件。

### 2. 运行 CUDA 应用（Client）

在另一个终端中：

```bash
BPFTIME_LOG_OUTPUT=console LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/atomizer/vec_add
```

这会运行向量加法程序，并通过 bpftime agent 连接到第一个进程执行 eBPF。

## 输出解读

运行成功后，你会看到类似下面的输出（来自应用本身）：

```
Exited _Z9vectorAddPKfS0_Pf block_id=1, L=5, H=10
Enter _Z9vectorAddPKfS0_Pf block_id=7, L=5, H=10
C[1] = 0 (expected 0)
C[7] = 21 (expected 21)
```

这表示：
- kernel 的进入/退出日志
- 向量加法结果，其中只有上半部分被计算（总共 10 个 block）

## 代码组件

### CUDA 向量加法（`vec_add.cu`）

一个简单的 CUDA 应用，它会：
- 在 GPU 和 CPU 上分配内存
- 循环执行基础向量加法 kernel
- 使用常量内存保存向量大小

### eBPF 程序（`atomizer.bpf.c`）

包含一个 eBPF 程序：
- `probe__cuda`：在进入 CUDA kernel 时执行
  - 从 bpf map 中加载配置
  - 检查是否满足提前退出条件

### Userspace Loader（`atomizer.c`）

负责管理 eBPF 程序生命周期：
- 加载编译后的 eBPF 代码
- 挂载到 CUDA kernel 函数
- 处理正确的信号退出

## 高级特性

这个示例展示了 bpftime 的几个高级能力：

1. **自定义 CUDA Helpers**：用于 CUDA 的特殊 eBPF helper：
   - `bpf_cuda_exit()` - 退出 thread block
   - `bpf_get_block_idx()` - 获取当前 block 索引
   - `bpf_get_grid_dim()` - 获取当前 grid 尺寸

2. **进程间通信**：eBPF 程序与 CUDA 应用运行在不同进程中，通过 shared memory 进行通信。

3. **动态二进制修改**：CUDA 二进制会在运行时被拦截、修改并重新编译。

## 故障排查

如果遇到问题：

- 确认 CUDA 已正确安装并加入 PATH
- 检查两个进程都在运行并且可以通信
- 查看日志，确认 PTX 修改是否成功
- 如果出现 CUDA 错误，尝试简化向量加法 kernel

## 进一步探索

可以尝试修改这个示例来：
- 跟踪 CUDA kernel 的内存访问模式
- 测量 kernel 内部的特定操作
- 将 eBPF 程序应用到更复杂的 CUDA 应用
- 基于 eBPF 洞察实现性能优化
