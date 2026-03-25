# 使用 uprobe 跟踪 goroutine

**警告**：`goid` 字段的偏移量是硬编码的。当前只在随仓库附带的 `go-server-http` 上测试过。它**可能无法**在其他 Go 程序上工作。

随仓库附带的 Go 程序是用 Go 1.17.0 编译的。可执行文件和源码位于 `go-server-http` 文件夹中。

这个示例会跟踪 goroutine 的状态切换，并打印对应的状态、goid、pid 和 tgid。

## 运行示例

运行 tracing 程序：

```console
example/goroutine# LD_PRELOAD=../../build/runtime/syscall-server/libbpftime-syscall-server.so ./goroutine
TIME     EVENT COMM             PID     PPID    FILENAME/EXIT CODE
```

运行 Go 程序：

```console
example/goroutine# LD_PRELOAD=../../build/runtime/agent/libbpftime-agent.so go-server-http/main
Server started!
```

触发 Go 程序：

```console
# curl 127.0.0.1:447
Hello,World!
```

## 使用 bpftime 跟踪 Go 程序

## 动态链接

需要注意的是，由于 bpftime 依赖动态库，某些 Go 程序可能无法工作。这是因为 Go runtime 默认是静态链接的，而 bpftime 无法跟踪静态链接程序。在这个用例里，Go 程序使用了 `net/http` 包，因此会进行动态链接。

> Go1.1 支持所谓的“external” linking，也就是在 Go 自带的链接器（6l、8l 或 5l）之后再调用系统链接器来完成最终链接，因此支持静态链接大多数代码所需的完整特性。举例来说，位于 <http://code.google.com/p/go-sqlite> 的 SQLite 包提供了 SQLite 的源码，并把生成的库静态链接进二进制文件，这在 Go 1.0 的“internal”链接器下是做不到的。如果使用 CGO，“external” linking 通常会自动启用，不过 Go 1.1.1 的二进制发行版在 darwin 上发现了一个较新的 bug（<https://code.google.com/p/go/issues/detail?id=5726>）。注意：“external” linking 并不强制静态链接，它只是受支持得更好；如果 cgo 参数里指定了动态库，Go 仍然会链接动态库，在上面的案例里，它所使用的库可能并没有静态链接版本。
>
> 对于 net 包，名字解析（net.Lookup*）通常由 cgo 代码处理，因为这样会使用系统中其他程序也会使用的同一套 C 代码，从而得到相同的结果。如果禁用了 cgo，就会改用 Go 编写的机制，而这很可能会产生不同且更少的结果。对于 os/user，非 cgo 代码总是返回错误。

参考：

- <https://github.com/eunomia-bpf/bpftime/issues/221>
- <https://groups.google.com/g/golang-nuts/c/H-NTwhQVp-8>

## LD_PRELOAD 和 attach

Go 对 ELF 可执行文件的初始化比较特殊，它不会在 glibc 中调用 `__libc_start_main`，因此通过 `LD_PRELOAD` 注入不会生效。不过远程 attach 的 `bpftime attach` 可以工作。

Console1：
```console
root@mnfe-pve:~/bpftime/example/goroutine# bpftime load ./goroutine
[2024-02-24 19:12:12.559] [info] [syscall_context.hpp:86] manager constructed
[2024-02-24 19:12:12.563] [info] [syscall_server_utils.cpp:24] Initialize syscall server
[2024-02-24 19:12:12][error][3343178] pkey_alloc failed
[2024-02-24 19:12:12][info][3343178] Global shm constructed. shm_open_type 0 for bpftime_maps_shm
[2024-02-24 19:12:12][info][3343178] Enabling helper groups ufunc, kernel, shm_map by default
[2024-02-24 19:12:12][info][3343178] bpftime-syscall-server started
[2024-02-24 19:12:12][info][3343178] Created uprobe/uretprobe perf event handler, module name ./go-server-http/main, offset 38e40
TIME     EVENT COMM             PID     PPID    FILENAME/EXIT CODE
```

Console2：
```console
root@mnfe-pve:~/bpftime/example/goroutine# bpftime attach 3343374
[2024-02-24 19:12:50.606] [info] Injecting to 3343374
[2024-02-24 19:12:50.649] [info] Successfully injected. ID: 1
root@mnfe-pve:~/bpftime/example/goroutine# 
```

Console3：
```console
root@mnfe-pve:~/bpftime/example/goroutine# ./go-server-http/main 
Server started!
[2024-02-24 19:12:50.649] [error] [bpftime_shm_internal.cpp:600] pkey_alloc failed
[2024-02-24 19:12:50.649] [info] [bpftime_shm_internal.cpp:618] Global shm constructed. shm_open_type 1 for bpftime_maps_shm
[2024-02-24 19:12:50.650] [info] [agent.cpp:88] Initializing agent..
[2024-02-24 19:12:50][info][3343464] Initializing llvm
[2024-02-24 19:12:50][info][3343464] Executable path: /root/bpftime/example/goroutine/go-server-http/main
[2024-02-24 19:12:50][info][3343464] Attach successfully
```

效果：
```console
TIME     EVENT COMM             PID     PPID    FILENAME/EXIT CODE
19:16:35  RUNNABLE  Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  SYSCALL   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  SYSCALL   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  SYSCALL   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  SYSCALL   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  SYSCALL   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  DEAD      Goid           0    3344462 3344462
19:16:35  RUNNABLE  Goid           0    3344462 3344462
19:16:35  SYSCALL   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           1    3344462 3344462
19:16:35  WAITING   Goid           1    3344462 3344462
19:16:35  RUNNING   Goid           21   3344466 3344462
19:16:35  SYSCALL   Goid           21   3344466 3344462
19:16:35  RUNNING   Goid           21   3344466 3344462
19:16:35  DEAD      Goid           0    3344466 3344462
19:16:35  RUNNABLE  Goid           0    3344466 3344462
19:16:35  SYSCALL   Goid           21   3344466 3344462
19:16:35  RUNNING   Goid           21   3344466 3344462
19:16:35  WAITING   Goid           21   3344466 3344462
19:16:35  RUNNING   Goid           34   3344464 3344462
19:16:35  RUNNABLE  Goid           21   3344464 3344462
19:16:35  DEAD      Goid           34   3344464 3344462
19:16:35  RUNNING   Goid           21   3344464 3344462
19:16:35  SYSCALL   Goid           21   3344464 3344462
19:16:35  RUNNING   Goid           21   3344464 3344462
19:16:35  WAITING   Goid           21   3344464 3344462
19:16:35  RUNNABLE  Goid           21   3344462 3344462
19:16:35  RUNNING   Goid           21   3344462 3344462
19:16:35  SYSCALL   Goid           21   3344462 3344462
19:16:35  RUNNING   Goid           21   3344462 3344462
19:16:35  SYSCALL   Goid           21   3344462 3344462
19:16:35  RUNNING   Goid           21   3344462 3344462
19:16:35  DEAD      Goid           21   3344462 3344462
```
