# ptx 程序

这是一个简单的示例程序，演示如何调用 llvmbpf 生成 PTX，并使用 CUDA driver API 执行编译后的 PTX。

请把 `LLVMBPF_CUDA_PATH` 设置为 CUDA 安装目录，例如 `/usr/local/cuda-12.6`。

这个示例演示了如何使用 llvmbpf 从 eBPF 程序生成 NVIDIA PTX code，并在支持 CUDA 的 GPU 上执行。它展示了完整流程：

1. 初始化 LLVM 组件
2. 定义 eBPF 程序
3. 使用 llvmbpf 将 eBPF 程序编译为 PTX
4. 使用 NVIDIA 的 PTX compiler 将 PTX 编译成 CUDA binary
5. 使用 CUDA Driver API 加载并执行 binary
6. 处理 host-device 通信，以支持 helper functions

## 程序概览

### eBPF 到 PTX 的编译流程

程序定义了一个简单的 eBPF 程序，它会与 BPF map 交互，先转换为 PTX，然后运行在 GPU 上。

### Host-Device 通信

程序实现了 host（CPU）和 device（GPU）之间的通信机制，用于处理 BPF helper functions。当 BPF 程序调用类似 `map_lookup_elem` 这样的 helper 时，GPU 代码会通知 host，由 host 处理请求并返回结果。

### 执行模型

1. eBPF 程序被编译成 PTX
2. PTX 被 trampoline code 包裹，以处理 helper function 调用
3. NVIDIA 的 PTX compiler 将 PTX 转换为 CUDA binary
4. binary 被加载到 GPU 并执行
5. host thread 处理来自 GPU 的 helper 请求

## 关键组件

1. **eBPF Program**：定义为 `ebpf_inst` 结构数组
2. **LLVM JIT Context**：用于把 eBPF 编译成 PTX
3. **PTX Compiler Interface**：使用 NVIDIA PTX compiler 生成可执行代码
4. **Shared Memory Structure**：实现 host 与 device 通信
5. **Helper Function Handlers**：在 host 侧处理来自 GPU 的请求

## 使用

构建并运行示例：

```sh
# set the CUDA path, for example, /usr/local/cuda-12.6
cmake -B build -DCMAKE_BUILD_TYPE=Release -DLLVMBPF_ENABLE_PTX=1 -DLLVMBPF_CUDA_PATH=/usr/local/cuda-12.6
cmake --build build --target all -j
```

运行 PTX 示例：

```sh
build/example/ptx/ptx_test
```

## 代码说明

### 1. 初始化与 include

代码首先包含 LLVM、CUDA 和 eBPF 所需的头文件。

### 2. eBPF 程序定义

代码定义了一个测试用的 eBPF 程序，演示 map lookup、结果写回和退出流程。

### 3. PTX 编译函数

`compile()` 函数使用 NVIDIA PTX compiler API 把 PTX 编译为 CUDA binary。

### 4. Host-Device 通信

代码使用共享内存结构实现 host 和 device 之间的通信。

### 5. CUDA Kernel 执行

`elfLoadAndKernelLaunch()` 会初始化 CUDA、加载 binary、设置通信通道并启动 kernel。

### 6. 主函数

`main()` 会串起初始化、编译、加载和执行整个流程。
