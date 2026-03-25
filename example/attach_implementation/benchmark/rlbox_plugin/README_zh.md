# RLBox 沙箱化 URL 过滤器插件

本目录包含一个使用 RLBox sandboxing 框架实现的 URL 过滤器。RLBox 提供了一种以较低性能开销安全地隔离第三方库的方法。

## 实现变体

这个实现提供两种沙箱选项：

1. **NoOp 沙箱**：一种轻量级沙箱，用于开发和初始测试。它并不真正强制隔离，但提供与生产沙箱相同的 API，因此更容易把代码迁移到 RLBox。

2. **Wasm2c 沙箱**：一种生产级沙箱，会把过滤器库先编译成 WebAssembly，再转换成 C，从而在保持较好性能的同时提供较强隔离。

## 前置条件

要构建并运行这个 RLBox 沙箱化过滤器，你需要：

- 支持 C++17 的 C/C++ 编译器（GCC 或 Clang）
- RLBox framework
- 对于 wasm2c 沙箱：用于 WebAssembly 编译的 WASI-SDK
- CMake（用于构建依赖）

## 构建插件

### 1. 安装依赖

先安装 RLBox 和其他依赖：

```bash
cd /path/to/bpftime/example/attach_implementation/benchmark/rlbox_plugin

# 安装 RLBox 及其依赖
make install-deps
```

### 2. 构建 NoOp 沙箱版本（默认）

用于开发和测试时，构建 NoOp 沙箱版本（默认就是它）：

```bash
cd /path/to/bpftime/example/attach_implementation/benchmark/rlbox_plugin

# 构建 NoOp 沙箱版本
make
```

这会生成 `libfilter_rlbox.so`，可与动态加载模块一起使用。

### 3. 构建 Wasm2c 沙箱版本（生产环境）

如果要在生产环境中使用真实隔离，构建 wasm2c 沙箱版本：

```bash
cd /path/to/bpftime/example/attach_implementation/benchmark/rlbox_plugin

# 构建 wasm2c 沙箱版本
make wasm2c
```

这会生成 `libfilter_rlbox_wasm2c.so`，通过 WebAssembly 提供较强隔离。

## 与 Nginx 一起运行

要在 Nginx 中运行这个 RLBox 沙箱化过滤器：

### 使用 RLBox 沙箱

```bash
cd /path/to/bpftime/example/attach_implementation

# 设置环境变量
DYNAMIC_LOAD_LIB_PATH="$(pwd)/benchmark/rlbox_plugin/libfilter_rlbox.so"  DYNAMIC_LOAD_URL_PREFIX="/aaaa" ./nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
```

### 使用 Wasm2c 沙箱

```bash
cd /path/to/bpftime/example/attach_implementation

# 设置环境变量
export DYNAMIC_LOAD_LIB_PATH="$(pwd)/benchmark/rlbox_plugin/libfilter_rlbox_wasm2c.so"
export DYNAMIC_LOAD_URL_PREFIX="/aaaa"

# 使用动态加载模块启动 Nginx
./nginx_plugin_output/nginx -p $(pwd) -c benchmark/dynamic_load_module.conf
```

## 测试过滤器

当 Nginx 使用 RLBox 过滤器运行起来后，可以用 curl 测试：

```bash
# 这里应该成功（HTTP 200）
curl http://localhost:9026/aaaa

# 这里应该失败（HTTP 403 Forbidden）
curl http://localhost:9026/forbidden_path
```

## 工作原理

1. RLBox framework 提供了一种安全与非受信任代码交互的方式，通过：
   - 将库代码放入沙箱
   - 确保穿越沙箱边界的所有数据都经过正确校验
   - 防止内存安全问题泄漏出沙箱

2. 我们的实现：
   - 由一个包含过滤逻辑的过滤器库（`mylib.c`）组成
   - 用 RLBox 沙箱（`rlbox_filter.cpp`）封装这个库
   - 提供与其他过滤器实现相同的 `module_*` API

3. NoOp 沙箱：
   - 不真正强制隔离
   - 用于开发和测试
   - 有助于把代码迁移到 RLBox

4. Wasm2c 沙箱：
   - 将过滤器库编译成 WebAssembly
   - 使用 wasm2c 把 WebAssembly 转成 C
   - 提供较强隔离和良好性能

## 纳入 benchmark

RLBox 过滤器可以像其他实现一样纳入 benchmark 脚本。运行 benchmark：

```bash
# 先构建 RLBox 过滤器
cd /path/to/bpftime/example/attach_implementation/benchmark/rlbox_plugin
make

# 运行 benchmark
cd /path/to/bpftime
python3 example/attach_implementation/benchmark/run_benchmark.py
```

## 故障排查

### 找不到 RLBox

如果你看到 RLBox 找不到的错误：

```
fatal error: rlbox/rlbox.hpp: No such file or directory
```

请确保运行过 `make install-deps`，或者手动克隆 RLBox 仓库：

```bash
git clone https://github.com/PLSysSec/rlbox
git clone https://github.com/PLSysSec/rlbox_wasm2c_sandbox
```

### 找不到 WASI-SDK

如果你在构建 wasm2c 版本时看到 WASI-SDK 找不到的错误：

```
WASI-SDK not found at /opt/wasi-sdk
```

运行 `make install-wasi-sdk`，或者手动安装 WASI-SDK。

### 找不到共享库

如果 Nginx 无法加载共享库：

```
Failed to load shared library: cannot open shared object file: No such file or directory
```

请确保 `DYNAMIC_LOAD_LIB_PATH` 环境变量设置为共享库的绝对路径。

## 参考资料

- [RLBox Documentation](https://rlbox.dev/)
- [RLBox GitHub Repository](https://github.com/PLSysSec/rlbox)
- [RLBox Wasm2c Sandbox](https://github.com/PLSysSec/rlbox_wasm2c_sandbox)
