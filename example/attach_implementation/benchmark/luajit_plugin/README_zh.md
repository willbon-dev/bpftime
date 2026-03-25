# LuaJIT URL 过滤器插件

本目录包含一个基于 LuaJIT 的 URL 过滤器实现，可以被 NGINX 中的 `dynamic_load_plugin` 加载。该实现由两个主要部分组成：

1. **Lua 脚本** (`url_filter.lua`)：其中包含用 Lua 编写的实际 URL 过滤逻辑。
2. **运行时包装器** (`lua_runtime.c`)：一个本地 C 库，用来加载并执行 Lua 脚本，实现与其他过滤器库相同的 API。

## 前置条件

要构建并运行 LuaJIT 过滤器，你需要：

- C/C++ 编译器（GCC 或 Clang）
- Git（如果从源码构建 LuaJIT，用于克隆仓库）
- 以下两者之一：
  - 预先安装好的 LuaJIT 及其开发头文件
  - 或者可以从源码编译 LuaJIT 的构建环境（Makefile 会自动处理）

## 构建 LuaJIT 过滤器

按以下步骤构建 LuaJIT 过滤器：

### 1. 安装或构建 LuaJIT

Makefile 会尝试：
1. 通过 pkg-config 查找现有的 LuaJIT 安装
2. 检查系统中常见的 LuaJIT 头文件和库路径
3. 如果仍未找到，则自动下载并从源码构建 LuaJIT

```bash
# 构建 LuaJIT 过滤器（会按需处理依赖）
cd /path/to/bpftime/example/attach_implementation/benchmark/luajit_plugin
make
```

如果你希望通过包管理器显式安装 LuaJIT：

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y luajit libluajit-5.1-dev

# CentOS/RHEL
sudo yum install -y luajit luajit-devel

# 然后构建过滤器
make
```

## 在 NGINX 中运行 LuaJIT 过滤器

要在 NGINX 中运行 LuaJIT 过滤器：

```bash
cd /path/to/bpftime/example/attach_implementation

# 启动 NGINX，并使用动态加载模块
export DYNAMIC_LOAD_LIB_PATH="$(pwd)/benchmark/luajit_plugin/liblua_filter.so"
export DYNAMIC_LOAD_URL_PREFIX="/aaaa"
export LUA_MODULE_PATH="$(pwd)/benchmark/luajit_plugin/url_filter.lua"
./nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
```

## 测试 LuaJIT 过滤器

当 NGINX 使用 LuaJIT 过滤器运行起来后，可以用 curl 测试：

```bash
# 这里应该成功（HTTP 200）
curl http://localhost:9026/aaaa

# 这里应该失败（HTTP 403 Forbidden）
curl http://localhost:9026/forbidden_path
```

## 工作原理

1. Lua 脚本 (`url_filter.lua`) 包含以下导出函数：
   - `initialize`：设置接受的 URL 前缀并重置计数器
   - `url_filter`：检查 URL 是否以接受的前缀开头
   - `get_counters`：返回接受和拒绝请求的数量
   - `set_buffer`：向缓冲区写入数据
   - `get_buffer`：从缓冲区读取数据

2. 运行时包装器 (`liblua_filter.so`)：
   - 使用 LuaJIT 执行 Lua 脚本
   - 从 `LUA_MODULE_PATH` 环境变量指定的文件加载 Lua 脚本
   - 提供与其他过滤器实现相同的 API
   - 在本地 API 和 Lua 脚本之间转换调用

3. NGINX 中的 `dynamic_load_plugin` 会把运行时包装器作为共享库加载，并调用它的函数来：
   - 用 URL 前缀初始化过滤器
   - 根据 URL 过滤请求
   - 记录已接受和已拒绝的请求

## 纳入 benchmark

LuaJIT 过滤器可以像其他实现一样纳入 benchmark 脚本。运行 benchmark：

```bash
# 先构建 LuaJIT 过滤器
cd /path/to/bpftime/example/attach_implementation/benchmark/luajit_plugin
make

# 运行 benchmark
cd /path/to/bpftime
python3 example/attach_implementation/benchmark/run_benchmark.py
```

benchmark 脚本会在测试时自动构建并使用 LuaJIT 过滤器。

## 性能特征

LuaJIT 以其 Just-In-Time 编译能力而著称，通常具有较高性能：

- **JIT 编译**：LuaJIT 会将热点代码路径编译为原生机器码
- **快速 FFI**：Foreign Function Interface 允许以较低开销调用 C 函数
- **较低开销**：实现重点在于减少 Lua 与 C 代码之间的开销
- **较小内存占用**：与许多其他脚本 runtime 相比，LuaJIT 的内存占用更小

对于 URL 过滤工作负载，LuaJIT 通常能提供接近原生 C 实现的性能，同时保留动态语言的灵活性。

## 故障排查

### 构建时找不到 LuaJIT

如果你看到 LuaJIT 头文件找不到之类的错误，Makefile 会自动尝试在本地下载并构建 LuaJIT。请确保你已安装 git，并且可以访问 GitHub。

如果你更希望手动安装 LuaJIT：

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y luajit libluajit-5.1-dev

# CentOS/RHEL
sudo yum install -y luajit luajit-devel
```

### 运行时找不到 Lua 脚本

如果你看到 Lua 脚本找不到的错误：

```
Failed to load Lua module: cannot open url_filter.lua: No such file or directory
```

请确保把 `LUA_MODULE_PATH` 环境变量设置为 Lua 脚本的绝对路径。

```bash
export LUA_MODULE_PATH="/absolute/path/to/url_filter.lua"
```

### 找不到共享库

如果 NGINX 无法加载共享库：

```
Failed to load shared library: cannot open shared object file: No such file or directory
```

请确保 `DYNAMIC_LOAD_LIB_PATH` 环境变量设置为共享库的绝对路径。

```bash
export DYNAMIC_LOAD_LIB_PATH="/absolute/path/to/liblua_filter.so"
```

### 缺少库依赖

如果运行时提示缺少 LuaJIT 库：

```
liblua_filter.so: cannot open shared object file: No such file or directory
```

请确保 LuaJIT 库在你的 library path 中。如果你是从源码构建的 LuaJIT，可能需要：

```bash
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/path/to/luajit-local/src"
```
