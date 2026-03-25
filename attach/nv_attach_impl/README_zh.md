
# CUDA eBPF Attach 实现（bpftime-nv-attach）

这个模块为 bpftime 提供 CUDA attach 支持，使 eBPF 程序可以被注入并在 CUDA kernels 内执行。它支持动态插桩、跟踪和修改 GPU 代码执行，而无需重新编译应用或重启进程。

## 工作方式

CUDA attach 的实现主要依赖以下机制：

1. **CUDA API 拦截**：
   - 使用 Frida-gum hook 关键 CUDA runtime 函数，包括 `__cudaRegisterFatBinary`、`__cudaRegisterFunction`、`__cudaRegisterFatBinaryEnd` 和 `cudaLaunchKernel`
   - 在 binary 数据被传给 CUDA driver 之前进行拦截

2. **PTX 代码转换**：
   - 从 CUDA fat binary 中提取 PTX 代码
   - 在特定位置插入 instrumentation 代码来 patch PTX
   - 通过基于 LLVM 的转换把 eBPF 程序转成 PTX
   - 使用 NVCC 将修改后的 PTX 重新编译回 binary 格式

3. **寄存器保护**：
   - 实现复杂的寄存器保存/恢复机制
   - 确保原始 kernel 行为保持不变
   - 处理各种 PTX 寄存器类型和模式

4. **内存与数据共享**：
   - 在 host 和 device 之间建立共享内存
   - 为 eBPF 与 CUDA 之间的数据传输创建通信通道
   - 处理 eBPF maps 的 map 信息

5. **Attach 类型**：
   - **Memory Capture**：拦截内存操作（load/store）
   - **Function Probes**：在 CUDA kernel function 开始时执行
   - **Return Probes**：在 kernel function 返回前执行

## 构建

### 前置条件

- CUDA Toolkit（已在 12.6 上测试，其他版本也可能可用）
- Frida-gum library
- 用于 eBPF 编译的 LLVM
- 支持 C++20 的编译器
- CMake 3.10+
- spdlog

### 构建步骤

```bash
# 如果还没有克隆仓库
git clone https://github.com/eunomia-bpf/bpftime.git
cd bpftime

# 创建并进入 build 目录
mkdir -p build && cd build

# 使用 CMake 配置
cmake -B build \
  -DBPFTIME_ENABLE_CUDA_ATTACH=1 \
  -DBPFTIME_CUDA_ROOT=/usr/local/cuda-12.6  # 指定 CUDA 安装路径

# 构建
make -j$(nproc) -C build
```

### CMake 选项

- `BPFTIME_ENABLE_CUDA_ATTACH`：启用 CUDA attachment 支持（默认：OFF）
- `BPFTIME_CUDA_ROOT`：CUDA 安装路径（如果没有设置 `CUDA_PATH` 环境变量，则必须提供）
- `BPFTIME_ENABLE_GDRCOPY`：启用可选的 GDRCopy 支持，以更快读取 host 侧 GPU map。需要 GDRCopy 用户态库（`libgdrapi.so`）和 `gdrdrv` 内核模块

## 实现细节

### PTX 转换

模块通过以下方式把 eBPF 指令转换为 PTX code：

1. 使用 LLVM 生成初始 PTX 表示
2. 添加寄存器保护，保留寄存器状态
3. 过滤不必要的 header 和 section
4. 使用 trampoline code 包裹以确保正确执行

### 通信通道

CPU 和 GPU 之间的通信通过以下方式实现：

1. 一个共享内存指针（`constData`）
2. 常量内存中的 map 信息结构
3. 用于安全访问的同步机制

### Memory Capture

内存操作拦截的方式如下：

1. 使用正则模式在 PTX 中查找 load/store 操作
2. 在这些操作之前注入自定义函数调用
3. 把内存地址和数据传递给 eBPF 程序

## 调试

为便于调试，代码可以：

- 把 PTX code dump 到 `/tmp` 目录
- 打印 patch 过程的详细日志
- 展示寄存器使用与状态信息

## 限制

- 目前只支持特定的 CUDA 版本格式
- 重新编译需要兼容的 NVCC 版本
- 对于复杂 kernel 可能有性能开销
- 仅限于 eBPF 和 PTX 都支持的特性

## 后续开发

计划中的改进包括：

- 支持更多 CUDA 版本和功能
- 优化性能，降低开销
- 增加更多 attach 点和能力
- 与 bpftime 生态进行更好的集成

## 配置参考

本节集中列出所有 GPU 相关的宏定义、CMake 选项、编译期宏以及运行时环境变量。

### CMake 构建选项

### 编译期预处理宏

### 运行时环境变量

#### GPU Map 与线程数

#### CUDA 编译与架构

#### PTX Pass 流水线

#### 内部变量（仅供参考）

#### GDRCopy 调优（host 侧 GPU map 读取）

### 快速参考
