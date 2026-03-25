# WebAssembly URL 过滤器插件

本目录包含一个基于 WebAssembly 的 URL 过滤器实现，可以被 NGINX 中的 `dynamic_load_plugin` 加载。该实现由两个主要部分组成：

1. **WebAssembly 模块** (`url_filter.c`)：会被编译成 WebAssembly，其中包含实际的 URL 过滤逻辑。
2. **运行时包装器** (`wasm_runtime.c`)：一个本地 C 库，用于加载并执行 WebAssembly 模块，实现与其他过滤器库相同的 API。

## 前置条件

要构建并运行 WebAssembly 过滤器，你需要：

- C/C++ 编译器（GCC 或 Clang）
- CMake（用于构建 WAMR）
- Git（用于克隆仓库）
- WASI-SDK（用于编译成 WebAssembly）

## 构建 WebAssembly 过滤器

按以下步骤构建 WebAssembly 过滤器：

### 1. 安装 WASI-SDK

如果你没有安装 WASI-SDK，可以使用提供的目标：

```bash
# 将 WASI-SDK 安装到 /opt/wasi-sdk
make install-deps
```

或者手动安装：

```bash
wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-19/wasi-sdk-19.0-linux.tar.gz
tar xf wasi-sdk-19.0-linux.tar.gz
sudo mv wasi-sdk-19.0 /opt/wasi-sdk
```

### 2. 构建 WebAssembly 模块和运行时包装器

```bash
cd /path/to/bpftime/example/attach_implementation/benchmark/wasm_plugin

# 构建 WebAssembly 模块和运行时包装器
make
```

这会：
- 克隆并构建 WebAssembly Micro Runtime（WAMR）
- 将 `url_filter.c` 编译成 WebAssembly（生成 `url_filter.wasm`）
- 将 `wasm_runtime.c` 编译成共享库（生成 `libwasm_filter.so`）

## 在 NGINX 中运行 WebAssembly 过滤器

要在 NGINX 中运行 WebAssembly 过滤器：

```bash
cd /path/to/bpftime/example/attach_implementation

# 启动 NGINX，并使用动态加载模块
export DYNAMIC_LOAD_LIB_PATH="$(pwd)/benchmark/wasm_plugin/libwasm_filter.so"
export DYNAMIC_LOAD_URL_PREFIX="/aaaa"
export WASM_MODULE_PATH="$(pwd)/benchmark/wasm_plugin/url_filter.wasm"
./nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
```

## 测试 WebAssembly 过滤器

当 NGINX 使用 WebAssembly 过滤器运行起来后，可以用 curl 测试：

```bash
# 这里应该成功（HTTP 200）
curl http://localhost:9026/aaaa

# 这里应该失败（HTTP 403 Forbidden）
curl http://localhost:9026/forbidden_path
```

## 工作原理

1. WebAssembly 模块 (`url_filter.wasm`) 包含以下导出函数：
   - `initialize`：设置接受的 URL 前缀并重置计数器
   - `url_filter`：检查 URL 是否以接受的前缀开头
   - `get_counters`：返回接受和拒绝请求的数量
   - `set_buffer`：向缓冲区写入数据
   - `get_buffer`：从缓冲区读取数据

2. 运行时包装器 (`libwasm_filter.so`)：
   - 使用 WebAssembly Micro Runtime（WAMR）执行 WebAssembly 模块
   - 从 `WASM_MODULE_PATH` 环境变量指定的文件加载 WebAssembly 模块
   - 提供与其他过滤器实现相同的 API
   - 在本地 API 和 WebAssembly 模块之间转换调用

3. NGINX 中的 `dynamic_load_plugin` 会把运行时包装器作为共享库加载，并调用它的函数来：
   - 用 URL 前缀初始化过滤器
   - 根据 URL 过滤请求
   - 记录已接受和已拒绝的请求

## 纳入 benchmark

WebAssembly 过滤器会被纳入 benchmark 脚本。运行 benchmark：

```bash
# 先构建 WebAssembly 过滤器
cd /path/to/bpftime/example/attach_implementation/benchmark/wasm_plugin
make

# 运行 benchmark
cd /path/to/bpftime
python3 example/attach_implementation/benchmark/run_benchmark.py
```

benchmark 脚本会在测试时自动构建并使用 WebAssembly 过滤器。

## 故障排查

### 找不到 WASI-SDK

如果你看到 WASI-SDK 找不到的错误：

```
WASI-SDK not found at /opt/wasi-sdk
```

请先安装 WASI-SDK，或者把环境变量设置为它所在的位置：

```bash
export WASI_SDK_PATH=/path/to/your/wasi-sdk
```

### 找不到 WebAssembly 模块

如果你看到 WebAssembly 模块找不到的错误：

```
Failed to open WebAssembly file: url_filter.wasm
```

请确保把 `WASM_MODULE_PATH` 环境变量设置为 WebAssembly 模块的绝对路径。

```bash
export WASM_MODULE_PATH="/absolute/path/to/url_filter.wasm"
```

### 找不到共享库

如果 NGINX 无法加载共享库：

```
Failed to load shared library: cannot open shared object file: No such file or directory
```

请确保 `DYNAMIC_LOAD_LIB_PATH` 环境变量设置为共享库的绝对路径。

```bash
export DYNAMIC_LOAD_LIB_PATH="/absolute/path/to/libwasm_filter.so"
```
