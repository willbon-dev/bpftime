# uprobe、uretprobe、map 以及读写操作的微基准测试

一条命令即可运行 uprobe 基准测试：

```sh
cd /path/to/bpftime
python3 benchmark/uprobe/benchmark.py
```

结果会写入 `results.md`。示例见 [example_results_zh.md](example_results_zh.md)。

下面介绍一些基准测试细节以及如何手动运行它。

## 基线

```sh
benchmark/test
```

基线函数的耗时为 0.000243087 秒，对应测试函数如下：

```c
__attribute_noinline__ 
uint64_t __benchmark_test_function3(const char *a, int b,
          uint64_t c)
{
 return a[b] + c;
}
```

## 内核 uprobe

构建 uprobe 和 uretprobe：

```sh
make -C benchmark/uprobe
make -C benchmark/uretprobe
```

运行 uprobe：

```sh
sudo benchmark/uprobe/uprobe
```

在另一个终端中运行基准程序：

```sh
benchmark/test
```

我们使用的 uprobe 或 uretprobe 函数如下：

```c
SEC("uprobe/benchmark/test:__benchmark_test_function3")
int BPF_UPROBE(__benchmark_test_function, const char *a, int b, uint64_t c)
{
 return b + c;
}
```

## 用户态 uprobe

运行 uprobe：

```sh
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so benchmark/uprobe/uprobe
```

在另一个终端中运行基准程序：

```sh
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so benchmark/test
```

如果出现如下错误：

```txt
terminate called after throwing an instance of 'boost::interprocess::interprocess_exception'
  what():  File exists
Aborted (core dumped)
```

请尝试使用 `sudo` 模式，或者通过 [tools/bpftimetool](../../tools/bpftimetool) 清理共享内存。

## 嵌入 runtime

```sh
build/benchmark/simple-benchmark-with-embed-ebpf-calling
```

## 旧版 uprobe 和 uretprobe 基准结果

借助用户态 eBPF runtime，我们可以：

- 将 uprobe 和 uretprobe 加速约 `10x`
- 用户态读写用户内存的速度约比内核快 `10x`（约 5ns 对 50ns）
- 无需任何内核补丁，也无需修改 tracing eBPF 程序
- 运行 eBPF tracing 程序不需要特权

探针：

| Probe/Tracepoint Types | Kernel (ns)  | Userspace (ns) | Insn Count |
|------------------------|-------------:|---------------:|-----------:|
| Uprobe                 | 3224.172760  | 314.569110     | 4    |
| Uretprobe              | 3996.799580  | 381.270270     | 2    |
| Syscall Tracepoint     | 151.82801    | 232.57691      | 4    |
| Embedding runtime      | Not avaliable |  110.008430   | 4    |

读写用户内存：

| Probe/Tracepoint Types  | Kernel (ns)     | Userspace (ns) |
|-------------------------|----------------:|---------------:|
| bpf_probe_read - uprobe  | 46.820830       | 2.200530       |
| bpf_probe_write_user - uprobe | 45.004100  | 8.101980       |

测试环境为 `6.2.0-32-generic` 内核和 `Intel(R) Core(TM) i7-11800H CPU @ 2.30GHz`（2023）。

## 另一台机器上的结果（2024）

测试环境为 `kernel version 6.2` 和 `Intel(R) Xeon(R) Gold 5418Y` CPU，结果如下：

### 使用 `bpf_probe_write_user` 和 `bpf_probe_read_user` 的 Uprobe 与读写

内核态：

```txt
Benchmarking __bench_uprobe_uretprobe in thread 1
Average time usage 3060.196770 ns, iter 100000 times

Benchmarking __bench_uretprobe in thread 1
Average time usage 2958.493390 ns, iter 100000 times

Benchmarking __bench_uprobe in thread 1
Average time usage 1910.731360 ns, iter 100000 times

Benchmarking __bench_read in thread 1
Average time usage 1957.552190 ns, iter 100000 times

Benchmarking __bench_write in thread 1
Average time usage 1955.735460 ns, iter 100000 times
```

用户态：

```txt
Benchmarking __bench_uprobe_uretprobe in thread 1
Average time usage 391.967450 ns, iter 100000 times

Benchmarking __bench_uretprobe in thread 1
Average time usage 383.851670 ns, iter 100000 times

Benchmarking __bench_uprobe in thread 1
Average time usage 380.935190 ns, iter 100000 times

Benchmarking __bench_read in thread 1
Average time usage 383.135720 ns, iter 100000 times

Benchmarking __bench_write in thread 1
Average time usage 389.037170 ns, iter 100000 times
```

需要注意，`bpf_probe_read_user` 和 `bpf_probe_write_user` 的性能会受到 `ENABLE_PROBE_WRITE_USER` 和 `ENABLE_PROBE_READ_USER` 选项的影响。

### map 操作

在一个函数中将 map 操作运行 1000 次。当前版本下，用户态 map 操作也比内核更快。当前版本比早期版本快了 10 倍。

```c
SEC("uprobe/benchmark/test:__bench_hash_map_lookup")
int test_lookup(struct pt_regs *ctx)
{
    for (int i = 0; i < 1000; i++) {
        u32 key = i;
        u64 value = i;
        bpf_map_lookup_elem(&test_hash_map, &key);
    }
    return 0;
}
```

内核 map 操作开销：

```txt

Benchmarking __bench_hash_map_update in thread 1
Average time usage 64738.264680 ns, iter 100000 times

Benchmarking __bench_hash_map_lookup in thread 1
Average time usage 17805.898280 ns, iter 100000 times

Benchmarking __bench_hash_map_delete in thread 1
Average time usage 21795.665340 ns, iter 100000 times

Benchmarking __bench_array_map_update in thread 1
Average time usage 11449.295960 ns, iter 100000 times

Benchmarking __bench_array_map_lookup in thread 1
Average time usage 2093.886500 ns, iter 100000 times

Benchmarking __bench_array_map_delete in thread 1
Average time usage 2126.820310 ns, iter 100000 times

Benchmarking __bench_per_cpu_hash_map_update in thread 1
Average time usage 35050.915650 ns, iter 100000 times

Benchmarking __bench_per_cpu_hash_map_lookup in thread 1
Average time usage 15999.969590 ns, iter 100000 times

Benchmarking __bench_per_cpu_hash_map_delete in thread 1
Average time usage 21664.294940 ns, iter 100000 times

Benchmarking __bench_per_cpu_array_map_update in thread 1
Average time usage 10886.969860 ns, iter 100000 times

Benchmarking __bench_per_cpu_array_map_lookup in thread 1
Average time usage 2749.468760 ns, iter 100000 times

Benchmarking __bench_per_cpu_array_map_delete in thread 1
Average time usage 2778.679460 ns, iter 100000 times
```

用户态 map 操作开销：

```txt
Benchmarking __bench_hash_map_update in thread 1
Average time usage 30676.986820 ns, iter 100000 times

Benchmarking __bench_hash_map_lookup in thread 1
Average time usage 23486.304570 ns, iter 100000 times

Benchmarking __bench_hash_map_delete in thread 1
Average time usage 13435.901160 ns, iter 100000 times

Benchmarking __bench_array_map_update in thread 1
Average time usage 7081.922160 ns, iter 100000 times

Benchmarking __bench_array_map_lookup in thread 1
Average time usage 4685.450360 ns, iter 100000 times

Benchmarking __bench_array_map_delete in thread 1
Average time usage 6367.443010 ns, iter 100000 times

Benchmarking __bench_per_cpu_hash_map_update in thread 1
Average time usage 95918.602090 ns, iter 100000 times

Benchmarking __bench_per_cpu_hash_map_lookup in thread 1
Average time usage 63294.791110 ns, iter 100000 times

Benchmarking __bench_per_cpu_hash_map_delete in thread 1
Average time usage 460207.364100 ns, iter 100000 times

Benchmarking __bench_per_cpu_array_map_update in thread 1
Average time usage 26109.863360 ns, iter 100000 times

Benchmarking __bench_per_cpu_array_map_lookup in thread 1
Average time usage 9139.355980 ns, iter 100000 times

Benchmarking __bench_per_cpu_array_map_delete in thread 1
Average time usage 5203.339320 ns, iter 100000 times
```

未对 map 操作函数进行内联时的基准结果：

| Map Operation                      | Kernel (op - uprobe) (ns) | Userspace (op - uprobe) (ns) |
|------------------------------------|--------------------------:|-----------------------------:|
| __bench_hash_map_update            | 62827.533320              | 30296.051630                 |
| __bench_hash_map_lookup            | 15895.166920              | 23005.369380                 |
| __bench_hash_map_delete            | 19884.933980              | 13054.965970                 |
| __bench_array_map_update           | 9538.564600               | 6701.987970                  |
| __bench_array_map_lookup           |  183.155140               | 4305.515170                  |
| __bench_array_map_delete           |  216.088950               | 5987.507820                  |
| __bench_per_cpu_hash_map_update    | 33140.184290              | 95537.666900                 |
| __bench_per_cpu_hash_map_lookup    | 14089.238230              | 62913.855920                 |
| __bench_per_cpu_hash_map_delete    | 19753.563580              | 459826.428910                |
| __bench_per_cpu_array_map_update   |  8885.238500              | 25728.928170                 |
| __bench_per_cpu_array_map_lookup   |  1838.737400              | 8759.420790                  |
| __bench_per_cpu_array_map_delete   |  1867.948100              | 4802.404130                  |

- 通过将 map 操作函数内联，可以降低一部分开销。
- 还需要修复用户态 runtime 中 per-cpu map 的性能问题。
