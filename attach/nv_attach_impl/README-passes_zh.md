## NV PTX Passes - 如何端到端运行

本指南演示如何在一个现有 CUDA 示例上触发 `nv_attach_impl` 的 fatbin 处理流程。这个过程包括提取 PTX、按顺序执行外部 passes、添加 trampoline，并使用 `nvcc` 重新打包 fatbin。

### 前置条件
- 已安装 CUDA（例如位于 `/usr/local/cuda-12.6`）。
- `nvcc` 和 `cuobjdump` 在你的 PATH 中可用。

### 构建并运行（自动化脚本）

```bash
# 可选：指定 CUDA 安装路径
export BPFTIME_CUDA_ROOT=/usr/local/cuda-12.6

# 运行脚本（它会自动构建并运行 server/client）
bash example/gpu/cuda-counter/run_nv_ptx_passes.sh
```

**脚本步骤：**
- 使用 `-DBPFTIME_ENABLE_CUDA_ATTACH=ON` 和 `-DBPFTIME_CUDA_ROOT` 构建 bpftime。
- 构建位于 `example/gpu/cuda-counter` 的 `cuda_probe` 和 `vec_add` 示例。
- 启动 server（预加载 syscall-server）。
- 以预加载 agent 的方式运行 `vec_add`，从而触发 CUDA fatbin 注册。
- 在 `/tmp/bpftime-recompile-nvcc` 目录中检查 `main.ptx`（外部 passes 串行执行后的结果）和 `out.fatbin`（重新打包后的结果）。

### 预期结果
- `vec_add` 程序应正常运行并输出原本的结果；在 server 侧日志中应能观察到 CUDA 事件。
- 文件 `/tmp/bpftime-recompile-nvcc/main.ptx` 应存在，并包含以下内容：
  - 一个 `.func __probe_func__<kernel>` 定义。
  - 目标 kernel 函数体内的一条 `call __probe_func__<kernel>;` 指令。
  - 如果启用了 memory capture attach，还会出现 `.func __memcapture__N` 定义以及对应的 `call __memcapture__N;` 指令。
  - 该文件不应包含任何临时寄存器，如 `%ptxpass_*`、`mov.u64 %..., %globaltimer;` 指令，或任何注入的 marker 注释（因为这些内容都应该已被移除）。
- 文件 `/tmp/bpftime-recompile-nvcc/out.fatbin` 应存在且非空（表示已由 `nvcc` 重新打包）。

### 故障排查
- 如果没有生成 `/tmp/bpftime-recompile-nvcc/main.ptx`：
  - 确认以下三个可执行文件存在：
    - `build/attach/nv_attach_impl/pass/ptxpass_kprobe_entry/ptxpass_kprobe_entry`
    - `build/attach/nv_attach_impl/pass/ptxpass_kretprobe/ptxpass_kretprobe`
    - `build/attach/nv_attach_impl/pass/ptxpass_kprobe_memcapture/ptxpass_kprobe_memcapture`
  - 若要通过 JSON 配置驱动 pass 顺序和子集，请设置 `BPFTIME_PTXPASS_DIR` 环境变量，指向一个包含 `*.json` 配置文件的目录。日志应打印 `"Discovered <N> pass definitions from <dir>"`。
  - 如果日志显示 `"Discovered 0 pass definitions..."`，系统会走 fallback 流程（仍然可以完成 injection 和 repackaging）。检查运行日志，确认 `hack_fatbin` 已执行。

### 独立 Pass 可执行文件与配置（仅 JSON 输入/输出）
- **路径：** `attach/nv_attach_impl/pass/ptxpass_*`
  - 所有 passes 通过 stdin/stdout 传递 JSON 结构化数据（不再接受纯文本 PTX）：
    - **输入（stdin）：**
      - `full_ptx`：字符串，待处理的完整 PTX。
      - `to_patch_kernel`：字符串，目标 kernel 名称（可选）。
      - `global_ebpf_map_info_symbol`：字符串，默认是 `map_info`。
      - `ebpf_communication_data_symbol`：字符串，默认是 `constData`。
      - 其他 pass 特定字段（例如 memcapture 的 `source_symbol`、`copy_bytes`、`align_bytes`）。
    - **输出（stdout）：**
      - `output_ptx`：字符串，转换后的 PTX（空字符串或缺省字段表示没有修改）。
  - `PTX_ATTACH_POINT` 环境变量用于标识当前正在处理的 attachment point。
  - **注意：** stdin 只接受 JSON。非 JSON 输入会导致程序报错并立即退出。
- **默认 JSON 配置**位于：`attach/nv_attach_impl/configs/ptxpass/*.json`（可复制到自定义目录，并通过 `BPFTIME_PTXPASS_DIR` 指定）。
