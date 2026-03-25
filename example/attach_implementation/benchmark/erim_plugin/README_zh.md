# ERIM 保护的 URL 过滤器插件

本目录包含一个使用 ERIM（Efficient Remote Isolation with Memory Protection Keys）保护的 URL 过滤器实现，它通过硬件强制的隔离机制将宿主应用（例如 Nginx）和插件隔离开来。

## ERIM 保护如何工作

ERIM 使用 Intel 的 Memory Protection Keys（MPK）创建隔离的内存域，具备以下特性：

1. **硬件强制隔离**：
   - 使用 Intel MPK 保护特定内存区域
   - 防止未授权访问受保护内存

2. **域切换**：
   - 在受信任域和非受信任域之间进行受控切换
   - 只有特定、经过验证的代码才能切换域

3. **内存保护**：
   - 全局变量被隔离在受保护内存中
   - 字符串操作在受信任域中进行

## 前置条件

要构建并运行这个 ERIM 保护的过滤器，你需要：

- C 编译器（GCC 或 Clang）
- 支持 Intel MPK 的 CPU（Skylake 及之后的 Intel x86 处理器）
- 支持 MPK 的 Linux 内核（4.9+）
- Make

你可以通过下面的命令检查 CPU 是否支持 MPK：

```bash
grep -q pku /proc/cpuinfo && echo "MPK supported" || echo "MPK not supported"
```

## 构建 ERIM 保护的过滤器

按下面的步骤构建 ERIM 保护的过滤器：

```bash
cd /path/to/bpftime/example/attach_implementation/benchmark/erim_plugin

# 构建 ERIM 库和过滤器实现
make
```

这会完成以下工作：
1. 构建 ERIM 库（使用位置无关代码）
2. 编译带 ERIM 保护的过滤器实现
3. 生成共享库 `liberim_filter.so`

## 与 Nginx 一起运行

要在 Nginx 中使用这个 ERIM 保护的过滤器：

```bash
cd /path/to/bpftime/example/attach_implementation

# 为动态加载器设置环境变量
DYNAMIC_LOAD_LIB_PATH="$(pwd)/benchmark/erim_plugin/liberim_filter.so"  DYNAMIC_LOAD_URL_PREFIX="/aaaa" ./nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
```

## 测试 ERIM 保护的过滤器

### 基本功能测试

当 Nginx 使用 ERIM 保护的过滤器运行起来后，可以用 curl 测试：

```bash
# 这里应该成功（HTTP 200）
curl http://localhost:9026/aaaa

# 这里应该失败（HTTP 403 Forbidden）
curl http://localhost:9026/forbidden_path
```

### 独立测试

你也可以运行附带的测试程序来验证 ERIM 保护：

```bash
cd /path/to/bpftime/example/attach_implementation/benchmark/erim_plugin
make test
```

这个测试会演示：
- 基本的 URL 过滤功能
- 访问统计信息
- 通过 ERIM 进行内存保护（尝试修改受保护内存会触发 segmentation fault）

## 实现细节

插件使用 ERIM 保护其内部状态：

- **全局变量**：`accept_url_prefix` 和 `counter` 受保护在受信任内存中
- **API 函数**：每个导出的函数都会切换到受信任域，执行操作，然后再切换回来
- **内存访问**：从外部直接访问受保护变量会导致 segmentation fault

## 纳入 benchmark

这个 ERIM 保护的过滤器已经包含在 benchmark 脚本中。运行 benchmark：

```bash
# 先构建 ERIM 过滤器
cd /path/to/bpftime/example/attach_implementation/benchmark/erim_plugin
make

# 运行 benchmark
cd /path/to/bpftime
python3 example/attach_implementation/benchmark/run_benchmark.py
```

benchmark 脚本会在测试时自动构建并使用 ERIM 保护的过滤器。

## 故障排查

### 不支持 MPK

如果你看到类似下面的错误：

```
WRPKRU instruction not supported on this CPU
```

你需要一颗支持 Intel MPK 的 CPU（通常是 Skylake 及之后的 Intel 处理器）。

### Permission Denied

如果你看到权限错误：

```
Failed to set protection key for memory region
```

请确保你有使用 protection keys 的必要权限。你可能需要以 root 身份运行，或者调整内核参数。

### 找不到共享库

如果 Nginx 无法加载共享库：

```
Failed to load shared library: cannot open shared object file: No such file or directory
```

请确保 `DYNAMIC_LOAD_LIB_PATH` 环境变量设置为共享库的绝对路径。

```bash
export DYNAMIC_LOAD_LIB_PATH="/absolute/path/to/liberim_filter.so"
```

## 安全收益

这个实现提供了若干安全收益：

1. **隔离**：插件状态与宿主应用隔离
2. **完整性**：受保护变量不能被直接修改
3. **访问控制**：只有显式的 API 函数可以访问受保护状态
4. **硬件强制执行**：保护由 CPU 强制执行，而不是软件

## 性能考虑

ERIM 通过较低的额外开销提供高效隔离：
- 域切换是轻量级操作
- 性能影响主要来自 WRPKRU 指令
- 相比基于进程的隔离，开销要低得多
