# malloc 跟踪

这段代码是一个用 C 编写的 BPF（Berkeley Packet Filter）程序，常用于在 Linux kernel 中进行跟踪和监控。BPF 允许你在不修改 kernel 源码的情况下，在内核中运行自定义程序。这里的代码会创建一个 BPF 程序，使用 BPF map 统计在指定 cgroup 中 `malloc` 函数被调用的次数。

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include "bits.bpf.h"
#include "maps.bpf.h"

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u64);
    __type(value, u64);
} libc_malloc_calls_total SEC(".maps");

SEC("uprobe/libc.so.6:malloc")
int do_count(struct pt_regs *ctx)
{
    u64 cgroup_id = bpf_get_current_cgroup_id();

    increment_map(&libc_malloc_calls_total, &cgroup_id, 1);

    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

来源：<https://github.com/cloudflare/ebpf_exporter/blob/master/examples/uprobe.bpf.c>

下面是对这段代码的分解说明：

1. **包含头文件**：
   - `<vmlinux.h>`：提供对 kernel 数据结构和定义的访问。
   - `<bpf/bpf_helpers.h>`：包含 BPF 程序使用的 helper 函数和宏。
   - `"bits.bpf.h"`：自定义头文件（假定包含额外定义）。
   - `"maps.bpf.h"`：自定义头文件（假定包含与 BPF map 相关的定义）。

2. **BPF Map 定义**：
   这段代码使用 `struct` 语法定义了一个名为 `libc_malloc_calls_total` 的 BPF map。这个 map 的类型是 `BPF_MAP_TYPE_HASH`（hash map），最大条目数是 1024。key 和 value 的类型都是 `u64`（无符号 64 位整数）。

3. **Map 定义属性**：
   map 定义中的属性（`__uint`、`__type`）用于设置 map 的类型、最大条目数以及 key/value 的类型。

4. **BPF 程序**：
   - 这个程序挂载在 `libc.so.6` 库里的 `malloc` 函数上。
   - 当调用 `malloc` 时，`do_count` 函数会被执行。
   - 它通过 `bpf_get_current_cgroup_id()` 获取当前 cgroup ID。
   - 然后使用 cgroup ID 作为 key，把 `libc_malloc_calls_total` map 中对应的计数加 1。

5. **许可信息**：
   `LICENSE[]` 数组包含这个 BPF 程序的许可证信息。这里使用的是 GPL（GNU General Public License）。

这个 BPF 程序的目的是跟踪并统计 Linux kernel 中某个特定 cgroup 里 `malloc` 调用的次数。它使用 BPF hash map 存储并更新计数，这对于监控不同 cgroup 的内存分配模式和资源使用情况非常有用。

## 如何运行

server

```sh
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so example/malloc/malloc
```

client

```sh
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so example/malloc/victim
```
