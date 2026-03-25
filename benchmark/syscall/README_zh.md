# syscall 微基准测试

运行脚本即可查看结果：

```sh
sudo python benchmark/syscall/benchmark.py
```

结果会写入 `results.md` 和 JSON 文件。示例结果见 [example_results_zh.md](example_results_zh.md)。

## 用户态 syscall

### 运行

```sh
sudo ~/.bpftime/bpftime load benchmark/syscall/syscall
# 或者
sudo LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so benchmark/syscall/syscall
```

在另一个 shell 中，运行内部包含 eBPF 的目标程序：

```sh
sudo ~/.bpftime/bpftime start -s benchmark/syscall/victim
# 或者
sudo AGENT_SO=build/runtime/agent/libbpftime-agent.so LD_PRELOAD=build/attach/text_segment_transformer/libbpftime-agent-transformer.so benchmark/syscall/victim
```

## 结果（2023）

测试环境为 `6.2.0-32-generic` 内核和 `Intel(R) Core(TM) i7-11800H CPU @ 2.30GHz`。

### 基线

平均耗时 213.62178ns，计数 1000000

### 用户态 syscall

平均耗时 446.19869ns，计数 1000000

### 内核 tracepoint

平均耗时 365.44980ns，计数 1000000
