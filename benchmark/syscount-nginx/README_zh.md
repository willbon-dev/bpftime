# nginx 的 syscount 测试

我们将使用 5 种配置来测试 syscount eBPF 程序对 nginx 的跟踪影响：

1. 不进行 tracing
2. 内核 syscount
3. 内核 syscount，但不针对 nginx pid
4. 用户态 syscount
5. 用户态 syscount，但不针对 nginx pid

## 一键脚本运行

```sh
cd /path/to/bpftime
python3 benchmark/syscount-nginx/benchmark.py
```
