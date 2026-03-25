# Nginx 模块基准测试

本目录包含用于对比四种不同 Nginx 配置性能的 benchmark 工具：

1. **带 bpftime 模块的 Nginx** - 使用基于 eBPF 的 URL 过滤
2. **带基线 C 模块的 Nginx** - 使用传统的 C 实现和共享内存
3. **带动态加载模块的 Nginx** - 运行时动态加载库实现
4. **不带任何模块的 Nginx** - 不做过滤的基线性能

## 目录结构

- `ebpf_controller/` - eBPF controller 实现
- `baseline_nginx_plugin/` - 传统 C 模块实现
- `dynamic_load_plugin/` - 动态库加载实现
- `wasm_plugin/` - 基于 WebAssembly 的过滤实现
- `run_benchmark.py` - 运行 benchmark 的 Python 脚本
- `baseline_c_module.conf` - 基线 C 模块的 Nginx 配置
- `dynamic_load_module.conf` - 动态加载模块的 Nginx 配置
- `no_module.conf` - 不使用模块的 Nginx 配置

## 前置条件

- CMake（3.10+）
- 支持 C++17 的 C++ 编译器
- Nginx
- wrk HTTP benchmark 工具
- Python 3.6+

## 构建项目

### 1. 构建主 bpftime 项目

先构建主 bpftime 项目，并包含 Nginx 插件。（详细信息见父级 [README](../README_zh.md)）

## 运行自动化 benchmark

`run_benchmark.py` 脚本会自动完成以下步骤：

1. 启动 controller（在 Nginx 之前）
2. 用每种配置启动 Nginx
3. 对每种配置运行 wrk benchmark
4. 收集并展示结果
5. 将所有输出记录到 `benchlog.txt`

运行 benchmark：

```bash
cd /path/to/bpftime
python3 example/attach_implementation/benchmark/run_benchmark.py
```

你可以通过以下选项自定义 benchmark：

- `--duration`：每轮 benchmark 持续时间（默认：30 秒）
- `--connections`：使用的连接数（默认：400）
- `--threads`：使用的线程数（默认：12）
- `--url-path`：测试用 URL 路径（默认：`/aaaa`）

例如，运行一个更短、连接数更少的 benchmark：

```bash
python3 example/attach_implementation/benchmark/run_benchmark.py --duration 10 --connections 100 --url-path /aaaa
```

### Benchmark 日志

benchmark 的所有输出都会记录到 benchmark 目录下的 `benchlog.txt`，包括：

- controller 的 stdout/stderr
- Nginx 的 stdout/stderr
- 详细的 wrk benchmark 结果
- 错误信息

这会提供一份完整的 benchmark 执行记录，在排查问题时很有帮助。

日志条目带有时间戳，便于跟踪 benchmark 期间事件的顺序。

## 结果解读

benchmark 脚本会输出类似下面的结果：

```text
=== Benchmark Results Summary ===

Nginx without module:
  Requests/sec: 4536.86 ± 1027.29
  Latency (avg): 16.54ms
  Successful iterations: 20

Nginx with baseline C module:
  Requests/sec: 4559.84 ± 1000.22
  Latency (avg): 16.39ms
  Successful iterations: 20

Nginx with WebAssembly module:
  Requests/sec: 4008.00 ± 797.06
  Latency (avg): 18.11ms
  Successful iterations: 20

Nginx with LuaJIT module:
  Requests/sec: 3982.76 ± 644.57
  Latency (avg): 17.94ms
  Successful iterations: 20

Nginx with bpftime module:
  Requests/sec: 4461.00 ± 1031.08
  Latency (avg): 16.68ms
  Successful iterations: 20

Nginx with RLBox NoOp module:
  Requests/sec: 4148.58 ± 687.99
  Latency (avg): 17.25ms
  Successful iterations: 20

Nginx with ERIM-protected module:
  Requests/sec: 4024.11 ± 784.07
  Latency (avg): 18.80ms
  Successful iterations: 20

Overhead Comparisons:
  Compared to no module:
    Baseline C: -0.51%
    WebAssembly: 11.66%
    LuaJIT: 12.21%
    BPFtime: 1.67%
    RLBox NoOp: 8.56%
    ERIM: 11.30%
JSON results saved to: /home/yunwei37/bpftime/example/attach_implementation/benchmark/benchmark_results_20250512_173550.json
```

更多细节请查看 [example_benchmark_results.json](example_benchmark_results.json)。

需要重点关注的指标：

- **Requests/sec**：越高越好
- **Latency**：越低越好
- **Overhead percentages**：每种过滤方式带来的性能开销

## 手动测试

若要手动验证每种实现的正确性，请按以下步骤进行：

### 测试基线 C 模块

> **重要**：对于基线 C 模块，controller 必须先于 Nginx 实例启动。这是因为 controller 会创建 Nginx 连接的共享内存。

1. 先启动基线 controller：

   ```bash
   cd /path/to/bpftime
   build/example/attach_implementation/benchmark/baseline_nginx_plugin/nginx_baseline_controller /aaaa
   ```

   这会把过滤器配置为接受以 `/aaaa` 开头的 URL，并拒绝其他 URL。

2. 在新终端中启动带基线模块的 Nginx：

   ```bash
   cd /path/to/bpftime/example/attach_implementation/
   nginx_plugin_output/nginx -p $(pwd) -c benchmark/baseline_c_module.conf
   ```

3. 使用 curl 测试：

   ```bash
   # 这里应该成功（HTTP 200）
   curl http://localhost:9025/aaaa

   # 这里应该失败（HTTP 403 Forbidden）
   curl http://localhost:9025/forbidden_path
   ```

4. 查看 controller 输出，确认被接受和被拒绝的计数。

### 测试 eBPF/bpftime 模块

1. 启动 eBPF controller：

   ```bash
   cd /path/to/bpftime/build
   ./example/attach_implementation/benchmark/ebpf_controller/nginx_benchmark_ebpf_controller /aaaa
   ```

2. 在新终端中启动带 bpftime 模块的 Nginx：

   ```bash
   cd /path/to/bpftime/example/attach_implementation
   ./nginx_plugin_output/nginx -p $(pwd) -c nginx.conf
   ```

3. 使用 curl 测试：

   ```bash
   # 这里应该成功（HTTP 200）
   curl http://localhost:9023/aaaa

   # 这里应该失败（HTTP 403 Forbidden）
   curl http://localhost:9023/forbidden_path
   ```

4. 查看 controller 输出，确认已处理的请求。

### 测试动态加载模块

动态加载模块不需要单独的 controller，因为它会直接从共享库加载过滤器实现。

这套方式也会用于 wasm 模块和 lua 模块。

它通过环境变量进行配置：

1. 先构建过滤器实现库：

   ```bash
   cd /path/to/bpftime/example/attach_implementation/benchmark/dynamic_load_plugin/dynamic_tests
   make
   ```

2. 启动带动态加载模块的 Nginx：

   ```bash
   cd /path/to/bpftime/example/attach_implementation
   DYNAMIC_LOAD_LIB_PATH="/home/yunwei37/bpftime/example/attach_implementation/benchmark/dynamic_load_plugin/dynamic_tests/libfilter_impl.so"  DYNAMIC_LOAD_URL_PREFIX="/aaaa" nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
   ```

3. 使用 curl 测试：

   ```bash
   # 这里应该成功（HTTP 200）
   curl http://localhost:9026/aaaa

   # 这里应该失败（HTTP 403 Forbidden）
   curl http://localhost:9026/forbidden_path
   ```

5. 过滤器库会在内部记录接受/拒绝的请求，这些日志可以从 nginx 日志中取回。

### 测试 WebAssembly 过滤器

WebAssembly 过滤器沿用动态加载模块的基础设施，但使用 WebAssembly runtime 执行过滤逻辑。

1. 构建 WebAssembly 模块和 runtime wrapper：

   ```bash
   cd /path/to/bpftime/example/attach_implementation/benchmark/wasm_plugin
   make
   ```

   更多细节请见 [WebAssembly Plugin README](wasm_plugin/README_zh.md)。

2. 启动带 WebAssembly 过滤器的 Nginx：

   ```bash
   cd /path/to/bpftime/example/attach_implementation
   
   # 设置必要的环境变量
   export DYNAMIC_LOAD_LIB_PATH="$(pwd)/benchmark/wasm_plugin/libwasm_filter.so"
   export DYNAMIC_LOAD_URL_PREFIX="/aaaa"
   export WASM_MODULE_PATH="$(pwd)/benchmark/wasm_plugin/url_filter.wasm"
   
   # 使用动态加载模块启动 Nginx
   ./nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
   ```

## 备注

- 性能对比关注的是每种模块实现带来的额外开销
- 所有实现都使用相同的字符串比较逻辑来做 URL 过滤
- 基线 C 模块通过共享内存与 controller 共享数据
- bpftime 模块使用 eBPF 实现过滤逻辑
- 动态加载模块在运行时加载过滤器实现的共享库
- WebAssembly 过滤器会把过滤逻辑编译成 WebAssembly，并在 WebAssembly runtime 中执行

## 故障排查

### Nginx 启动时报 "Failed to open shared memory" 错误

- 确保在启动 Nginx 之前 controller 已经运行
- controller 会创建 Nginx 连接的共享内存
- 如果先启动 Nginx，它将找不到共享内存

### "Failed to open shared memory" 错误

- 确认没有残留的 controller 或 Nginx 实例在运行
- 如果上一次运行崩溃，可能需要手动清理共享内存：

  ```bash
  rm /dev/shm/baseline_nginx_filter_shm
  ```

### controller 或 Nginx 无法启动

- 检查端口冲突（9023、9024、9025）
- 确保你有绑定这些端口的权限
- 查看 nginx error log 或 `benchlog.txt` 中的错误信息
