# GPU 微基准框架

这是一个灵活的基准测试框架，用于测量 GPU eBPF 插桩的开销。

## 快速开始

**重要：** 所有命令必须在 bpftime 项目根目录下运行，而不是在 `benchmark/gpu/micro/` 目录下。

### 运行内置微基准
```bash
cd /path/to/bpftime
python3 benchmark/gpu/run_cuda_bench.py benchmark/gpu/micro/micro_vec_add_config.json
```
测试多种 eBPF 探针类型：empty、entry、exit、both、ringbuf、timer 等。

### 运行示例程序
```bash
cd /path/to/bpftime
python3 benchmark/gpu/run_cuda_bench.py benchmark/gpu/micro/examples_vec_add_config.json
```
测试真实世界的 eBPF 示例：cuda-counter、mem_trace、threadhist 等。

## 配置文件

### `micro_vec_add_config.json` / `micro_gemm_config.json`
内置微基准测试内容：
- **Baseline**：不启用 eBPF（原生 CUDA 性能）
- **Empty probe**：最小 eBPF 开销
- **Entry/Exit probes**：内核入口/出口插桩
- **GPU Ringbuf**：GPU 侧事件记录
- **Global timer**：GPU 定时测量
- **Per-GPU-thread array**：按线程的数据结构
- **Memtrace**：内存访问跟踪
- **CPU map operations**：GPU 侧的 Array/Hash map 操作

### `examples_vec_add_config.json` / `examples_gemm_config.json`
来自 `example/gpu/` 的真实示例：
- **cuda-counter**：统计 kernel 调用次数
- **mem_trace**：跟踪内存访问模式
- **threadhist**：线程执行直方图
- **launchlate**：kernel 启动延迟
- **kernelretsnoop**：kernel 返回值探测

## 工作负载预设

| Workload | Elements | Iterations | Threads | Blocks |
|----------|----------|------------|---------|--------|
| tiny     | 32       | 10000      | 32      | 1      |
| small    | 1000     | 10000      | 256     | 4      |
| medium   | 10000    | 10000      | 256     | 40     |
| large    | 100000   | 1000       | 512     | 196    |
| xlarge   | 1000000  | 1000       | 512     | 1954   |

## 输出文件

运行基准测试后，输出会根据配置文件中的 `output_prefix` 保存。

**对于微基准（例如前缀为 `benchmark/gpu/micro/micro_vec_add` 的 `micro_vec_add_config.json`）：**
- **`micro_vec_add_result.md`**：Markdown 格式结果
- **`micro_vec_add_result.json`**：原始 JSON 数据
- **`micro_vec_add_bench.log`**：详细执行日志

**对于示例程序（例如前缀为 `benchmark/gpu/micro/examples_vec_add` 的 `examples_vec_add_config.json`）：**
- **`examples_vec_add_result.md`**：Markdown 格式结果
- **`examples_vec_add_result.json`**：原始 JSON 数据
- **`examples_vec_add_bench.log`**：详细执行日志

## 配置结构

两个配置文件使用相同结构：

```json
{
  "output_prefix": "benchmark/gpu/micro/micro_vec_add",
  "workload_presets": {
    "minimal": "benchmark/gpu/workload/vec_add 32 3 32 1"
  },
  "test_cases": [
    {
      "name": "Test Name",
      "probe_binary_cmd": "path/to/probe [args]",
      "workload": "minimal",
      "baseline": "Baseline (minimal)"
    }
  ]
}
```

- **`output_prefix`**：输出文件的基础路径（相对于项目根目录）
- **`workload_presets`**：每个预设指定工作负载二进制文件的完整路径及其参数
- **空的 `probe_binary_cmd`**：运行基线（无 eBPF）
- **带有 probe 路径**：运行 eBPF 插桩
- **所有路径都相对于 bpftime 项目根目录**：例如 `benchmark/gpu/micro/cuda_probe entry` 或 `example/gpu/mem_trace/mem_trace`

**重要：** 所有测试都使用 `benchmark/gpu/workload/vec_add`（或 `matrixMul`、`simpleCUBLAS`）作为工作负载二进制，以保证基准测试的一致性。

## 架构

```
┌─────────────────────────────────────────────┐
│         run_cuda_bench.py                   │
│  - Load config                              │
│  - Run baselines (no eBPF)                  │
│  - Run eBPF tests                           │
│  - Collect metrics                          │
│  - Generate reports                         │
└─────────────────────────────────────────────┘
              │
              ├──► micro_vec_add_config.json
              │    (built-in micro-benchmarks)
              │
              ├──► examples_vec_add_config.json
              │    (example programs)
              │
              └──► Custom configs
```

## 测试执行流程

1. **Baseline**：直接运行 vec_add（不启用 eBPF）
2. **eBPF Tests**：
   - 在后台启动 eBPF probe（带 syscall-server）
   - 预加载 agent 后运行 vec_add
   - 收集时间数据
   - 终止 probe
3. **Calculate Overhead**：与对应基线比较
4. **Generate Reports**：输出 MD/JSON/LOG

## 依赖

- Python 3.x
- CUDA toolkit
- 启用 GPU 支持构建的 bpftime
- 已编译的 eBPF 示例（如果运行 examples 配置）

## 故障排查

**“Custom probe not found”**：确保示例已构建（从项目根目录执行）
```bash
cd /path/to/bpftime
make -C example/gpu
```

**“No vec_add_args specified”**：每个测试用例都需要一个 workload 预设

**开销数值过高**：检查基线是否在没有 eBPF 的情况下正常运行

## 贡献

添加新测试用例时：
1. 添加到合适的配置文件
2. 复用现有基线
3. 指定 workload 预设
4. 对于自定义程序，添加到 `example_programs` 部分

## 许可证

与 bpftime 项目相同
