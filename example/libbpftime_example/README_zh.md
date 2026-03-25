# 示例程序

这是一个展示如何使用 libbpftime 的示例程序。

我使用的是 runtime 中的头文件，并且链接的是安装在 `~/.bpftime` 里的 `libbpftime.a`。

## 前置条件

下面的命令应该已经执行过，这样 `~/.bpftime` 目录下才会有 `libbpftime.a`：

```shell
cmake -Bbuild  -DCMAKE_BUILD_TYPE:STRING=Release \
           -DSPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_INFO -DBPFTIME_BUILD_STATIC_LIB=ON
cmake --build build --config Release --target install
```

## 构建

- Makefile

你可以使用 makefile 来构建示例：

> 推荐使用 make 来运行示例

运行 `make` 后，你会看到如下输出：

```shell
Available targets:
 shm_example          build shared memory example
 clean                clean the build
```

执行代码的命令：
在不使用 llvm-jit 的情况下：

```shell
g++ -o example main.cpp -I../../runtime/include -I../../vm/compat/include/ -I../../third_party/spdlog/include -I../../vm/vm-core/include -L~/.bpftime -lbpftime -lboost_system -lrt -lbpf
```
