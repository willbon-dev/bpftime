# 用户态 uprobe 下的 DeepFlow

TODO：DeepFlow 的情况更复杂。

使用 `wrk`：

```sh
wrk/wrk https://127.0.0.1:446/ -c 500 -t 10 -d 10
```

用 4 种不同类型进行测试：

1. 在 bpftime 中部分使用用户态 uprobe 的 DeepFlow
2. 使用内核 uprobe、完全在内核中运行的 DeepFlow
3. 不启用 uprobe、仅使用 kprobe 或 syscall tracepoint 和 sockets 的 DeepFlow
4. 不使用 DeepFlow

你应该使用两种服务器进行测试：

1. 启用 HTTPS 的 Golang 服务器，使用 goroutine 处理请求
2. 仅启用 HTTP 的 Golang 服务器，使用 goroutine 处理请求

## 用法

- 构建并运行 bpftime_daemon，见 <https://github.com/eunomia-bpf/bpftime>
- 运行 go-server（`./go-server/main`）。如果不能直接运行，使用 `go build main.go` 构建
- 运行 <https://github.com/eunomia-bpf/deepflow/tree/main/build-results> 中的 rust_example。如果无法运行，请参考 <https://github.com/eunomia-bpf/deepflow/blob/main/build.md> 了解如何构建
- 使用 attach 模式运行 bpftime agent：`bpftime attach PID`。PID 可以通过 `ps -aux | grep main` 获取

## 测试示例（https）

在我的机器上：

```console
root@mnfe-pve 
------------- 
OS: Proxmox VE 8.0.4 x86_64 
Host: PowerEdge R720 
Kernel: 6.2.16-19-pve 
Shell: bash 5.2.15 
Terminal: node 
CPU: Intel Xeon E5-2697 v2 (48) @ 3.500GHz 
GPU: NVIDIA Tesla P40 
GPU: AMD ATI Radeon HD 7470/8470 / R5 235/310 OEM 
Memory: 81639MiB / 257870MiB 
```

### HTTPS

这些测试使用 `go-server/main` 执行。

#### 无 trace
| Data Size | Requests/sec | Transfer/sec |
|-----------|--------------|--------------|
|10 B       |259055.53     |31.13MB       |
|1 KB       |255503.06     |278.27MB      |
|2 KB       |240685.38     |497.17MB      |
|4 KB       |172574.61     |696.72MB      |
|16 KB      |123732.81     |1.90GB        |
|128 KB     |32158.82      |3.93GB        |
|256 KB     |18158.14      |4.44GB        |

#### 使用内核 uprobe
| Data Size | Requests/sec | Transfer/sec |
|-----------|--------------|--------------|
|10 B       |95356.66      |11.46MB       |
|1 KB       |96107.28      |104.67MB      |
|2 KB       |94280.83      |194.75MB      |
|4 KB       |71658.19      |289.29MB      |
|16 KB      |56206.68      |0.86GB        |
|128 KB     |26142.56      |3.20GB        |
|256 KB     |15227.34      |3.72GB        |
#### 使用 bpftime 用户态 uprobe（模拟 hashmap，基于 arraymap）

- 共享 hashmap 不使用用户态锁
- 使用 LLVM JIT
- Release 模式
- ThinLTO
| Data Size | Requests/sec | Transfer/sec |
|-----------|--------------|--------------|
|10 B       |113668.80     |13.66MB       |
|1 KB       |113875.62     |124.02MB      |
|2 KB       |107866.63     |222.82MB      |
|4 KB       |86927.05      |350.94MB      |
|16 KB      |69111.42      |1.06GB        |
|128 KB     |26550.50      |3.25GB        |
|256 KB     |14926.84      |3.65GB        |
### HTTP

这些测试使用 `go-server-http/main` 执行。

#### 无 trace

| Data Size | Requests/sec | Transfer/sec |
|-----------|--------------|--------------|
| 10 B      |   48174.22   |  5.79MB      |
| 1 KB      |   43417.58   |  47.29MB     |
| 2 KB      |   41130.66   |  84.96MB     |
| 4 KB      |   35208.03   |  142.13MB    |
| 16 KB     |   32904.51   |  518.43MB    |
| 128 KB    |   20155.85   |  2.46GB      |
| 256 KB    |   15352.78   |  3.75GB      |
#### 使用内核 uprobe

| Data Size | Requests/sec | Transfer/sec |
|-----------|--------------|--------------|
|10 B       |36592.86      |4.40MB        |
|1 KB       |35790.68      |38.98MB       |
|2 KB       |33427.74      |69.05MB       |
|4 KB       |26541.33      |107.15MB      |
|16 KB      |23743.19      |374.09MB      |
|128 KB     |14970.04      |1.83GB        |
|256 KB     |11550.26      |2.82GB        |

#### 使用 bpftime 用户态 uprobe（模拟 hashmap，基于 arraymap）

- 共享 hashmap 不使用用户态锁
- 使用 LLVM JIT
- Release 模式
- ThinLTO
| Data Size | Requests/sec | Transfer/sec |
|-----------|--------------|--------------|
|1 KB       |37977.61      |41.36MB       |
|2 KB       |37424.72      |77.31MB       |
|4 KB       |30036.29      |121.26MB      |
|16 KB      |28305.94      |445.98MB      |
|128 KB     |17180.66      |2.10GB        |
|256 KB     |12339.24      |3.01GB        |
