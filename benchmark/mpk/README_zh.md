# 内存保护密钥（MPK）基准测试

这个基准测试比较启用和未启用内存保护密钥（MPK）时 BPFtime 的性能，以评估这一安全特性带来的性能影响。

## 什么是 MPK？

Memory Protection Keys（MPK）是近期 Intel 处理器提供的一项 CPU 特性，它允许用户态进程保护同一进程内某些内存区域不被其他部分访问。在 BPFtime 的场景中，MPK 用于将 eBPF 程序与宿主应用隔离，从而提供额外的安全层。

## 如何运行基准测试

### 前置条件

- 支持 MPK 的 Intel CPU 的 Linux 系统（通常是 Intel Core 第 7 代或更新型号）
- 分别带有和不带有 MPK 支持构建好的 BPFtime

### 构建说明

该基准测试需要两套 BPFtime 构建：

1. 标准构建（不启用 MPK），位于 `build/`
2. 启用 MPK 的构建，位于 `build-mpk/`

你可以使用本目录中的 `build.sh` 脚本自动创建这两套构建。

### 运行基准测试

```bash
cd path/to/bpftime
python benchmark/mpk/benchmark.py
```

脚本会：

1. 为每种配置（MPK 和标准版）启动一个服务进程
2. 使用两种配置运行多个基准测试
3. 在 `benchmark/mpk/results.md` 中生成 Markdown 报告
4. 以 JSON 格式保存详细基准数据到 `benchmark/mpk/benchmark-output.json`

## 示例结果

示例结果见 [example_results_zh.md](example_results_zh.md)。
