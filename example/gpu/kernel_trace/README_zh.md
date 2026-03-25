# kernel_trace - CUDA kernel trace 演示

`kernel_trace` 是一个最小的端到端示例，用于展示 bpftime 如何对 CUDA kernel 做 instrumentation。它会把一个 eBPF 程序注入到 `vec_add.cu` 中的 `vectorAdd` kernel，收集每个线程的 block/thread 索引以及 GPU global timer，并通过 CUDA trampoline 将事件发送回 host。

这个 demo 还展示了 **stub-based attach** 模式：CUDA kernel 中包含一个几乎为空的 hook stub `__bpftime_cuda__kernel_trace()`，并且每个线程会调用一次。在 PTX 阶段，bpftime 会重写这次调用，让它指向 eBPF 生成的 probe 函数，而不是那个空 stub。

## 构建

```bash
# 从仓库根目录
cmake -Bbuild -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda .
cmake --build build -j$(nproc)

# 构建这个 demo（BPF、userspace loader、示例 CUDA 程序）
make -C example/gpu/kernel_trace
```

## 运行

这个 demo 需要 syscall server（用于 map polling）和 agent（用于拦截 CUDA fatbin）。请打开两个终端：

### 终端 1 - 启动 tracer

```bash
BPFTIME_MAP_GPU_THREAD_COUNT=8192 \
BPFTIME_SHM_MEMORY_MB=256 \
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
example/gpu/kernel_trace/kernel_trace 
```

### 终端 2 - 启动示例 CUDA 程序

```bash
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
example/gpu/kernel_trace/vec_add
```

你应该会看到类似下面的输出：

```text
[kernel_trace] ts=809635273301344 block=(0,0,0) thread=(0,0,0)
[kernel_trace] ts=809635273301456 block=(0,0,0) thread=(1,0,0)
[kernel_trace] total events: 256
```

每一行都对应一个进入 `vectorAdd` 的 GPU 线程，说明 hook 已经生效。

## 自定义 hook

- 如果要跟踪别的 kernel，请修改 `kernel_trace.bpf.c` 中的 section name：

  ```c
  SEC("kprobe/_Z9vectorAddPKfS0_Pf")
  ```

  可以使用 `cuobjdump -symbols your_app | grep <kernel>` 找到其他 C++ mangled kernel 名。

- 如果要捕获更多字段（参数、计算值等），请扩展 `struct kernel_trace_event`，并保持 `kernel_trace.bpf.c` 和 `kernel_trace.c` 中的结构定义同步。
- 你也可以把 `vectorAdd` 换成自己的 CUDA 程序，只要你预加载 agent，让 fatbin 拦截和 PTX 重写流程处于启用状态即可。

## 工作方式

1. bpftime agent 拦截 `vectorAdd` 的 fatbin 注册，重写 PTX，并注入 trampoline。
2. 在 `vec_add.cu` 中，kernel 会调用一个空的 device 函数：

   ```c++
   __device__ __noinline__ void __bpftime_cuda__kernel_trace() {}

   __global__ void vectorAdd(...) {
       ...
       __bpftime_cuda__kernel_trace(); // hook point
       ...
   }
   ```

   `kprobe` entry 的 PTX pass 会看到 `call __bpftime_cuda__kernel_trace` 指令，并把它重定向到这个 kernel 对应的 eBPF 生成 PTX 函数。如果没有这样的 stub 调用，这个 pass 会退回到在 kernel entry 注入一次调用，因此现有代码也能继续工作。

3. eBPF 程序使用 GPU helper ID（`503`、`505`、`502`）来收集线程坐标和时间戳。
4. 事件会写入 GPU ring buffer map（`BPF_MAP_TYPE_GPU_RINGBUF_MAP`），由 syscall server 暴露给 userspace。
5. userspace loader 轮询该 map，并打印每个事件。

这可以作为一个最小模板，用于 hook CUDA kernel 并在 GPU 上运行自定义 eBPF 逻辑，你可以把它扩展成更高级的 tracepoint 或 profiler。

## 通过 JSON 控制 PTX pass（`kprobe_entry.json`）

CUDA kprobe entry 的 PTX 重写由 `kprobe_entry` pass 驱动。默认情况下，它的配置是编译进 pass binary 的，但也有一个 JSON 配置：

- 本仓库中的路径：`attach/nv_attach_impl/configs/ptxpass/kprobe_entry.json`
- 关键字段：
  - `attach_points.includes = ["^kprobe/.*$"]` – 匹配 CUDA kprobe attach points。
  - `attach_type = 8` – CUDA entry attach type。
  - `parameters.stub_name` – 作为 hook point 使用的 CUDA stub 函数名（默认是 `__bpftime_cuda__kernel_trace`）。

在这个树中，nv_attach_impl 总是使用 pass binary 的 `print_config()` 入口返回的 pass 配置；这个 JSON 文件只是默认配置的文档副本，也是记录自定义设置的方便位置。仅修改 `kprobe_entry.json` 还不会改变运行时行为。

你可以概念上这样定制基于 stub 的 attach：

1. 编辑 `kprobe_entry.json`，把 `"stub_name"` 改成你自己的 device 函数名。
2. 更新你的 CUDA kernel，让它定义并调用那个 stub。

PTX pass 会始终在 PTX 中查找 `call <stub_name>`（使用它参数里的 `stub_name`），并把这些调用重定向到对应的 eBPF probe 函数。未来版本也许会让运行时直接从 JSON 加载 pass 定义。
