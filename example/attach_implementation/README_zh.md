# 动态加载的 attach 实现示例

这个示例展示了 bpftime 在 nginx 插件中的用法。它使用 eBPF 程序根据 URL 路径前缀过滤 nginx 处理的请求（例如，只接受以 `/aaa` 开头的路径）。eBPF 程序还会把被过滤的请求发送到 ringbuf，方便 controller 读取。

## 说明

这个示例主要由三部分组成：

- 一个名为 `controller` 的可执行程序。它调用 bpftime_shm 的 API，把程序、maps 和 links 加载到共享内存中，并轮询 eBPF 程序的 ringbuf 输出，再打印到 stdout
- 一个名为 `nginx_plugin_adaptor` 的库。由于 nginx 使用自己的构建系统，我们无法把 nginx 直接集成进 CMake，所以通过这个动态库处理和 bpftime 相关的内容，例如 attach 实现、动态注册、调用 attach 上下文来实例化 handler 等
- 一个名为 `ngx_http_bpftime_module` 的 nginx 模块，位于 `nginx_plugin` 目录。这个模块链接 `nginx_plugin_adaptor`，并调用其中实现的多个函数来完成请求过滤。该模块会使用 nginx 自己的构建系统编译

## 如何使用这个示例

### 检查 nginx 版本

我们假定你使用的 nginx 版本与 `1.22.1` 兼容。如果在链接或启动 nginx 时遇到不兼容问题，请把 `example/attach_implementation` 下 `CMakeLists.txt` 第 34 行的 URL 修改为你实际使用的 nginx 版本。

### 使用 cmake 构建 controller、adapter，并让 CMake 调用 nginx 构建系统

在仓库根目录运行以下命令：

```console
cmake -DBPFTIME_LLVM_JIT=0 -DCMAKE_BUILD_TYPE:STRING=Release -DBUILD_ATTACH_IMPL_EXAMPLE=YES -B build -S .
cmake --build build --config Release --target attach_impl_example_nginx -j$(nproc)
```

### 运行并测试

我们需要两个终端，一个用于 controller，另一个用于运行 curl。

#### 终端 A

在项目根目录运行 `build/example/attach_implementation/controller/attach_impl_example_controller /aaaa`。`/aaaa` 是你希望过滤的路径前缀。只有以这个字符串开头的路径才会被接受，其他路径会返回 403。

#### 终端 B

在 `example/attach_implementation` 目录下运行 `nginx_plugin_output/nginx -p $(pwd) -c ./nginx.conf` 来启动 nginx。nginx 应该会作为守护进程启动。

然后执行 `curl http://127.0.0.1:9023/aaab` 和 `curl http://127.0.0.1:9023/aaaab` 检查响应。你也会看到 controller 打印出被接受或被拒绝的访问。

## benchmark

参见 [benchmark/README.md](benchmark/README_zh.md)

这里包含以下方案的 benchmark：

- 无模块
- 基线 C 模块
- eBPF/bpftime 模块
- Wasm 模块
- Lua 模块
