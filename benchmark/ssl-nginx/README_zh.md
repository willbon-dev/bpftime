# sslsniff 的 nginx 测试

这个测试用于展示内核态 sslsniff 和用户态 sslsniff 对性能的影响。sslsniff 是一个用于拦截 SSL 握手并打印加密握手报文内容的工具。这类方法在现代可观测性工具和安全工具中非常常见。

## 一键脚本运行

```sh
cd /path/to/bpftime
python3 benchmark/ssl-nginx/draw_figture.py
```

结果会保存在 `size_benchmark_*.txt` 和 `size_benchmark_*.json` 中。你也可以查看生成的图表。

## 测试命令

这个测试说明：

1. 内核态 sslsniff 会显著降低 nginx 的性能，带来约 2 倍的性能下降。

sslsniff 的测试程序来自 bcc 和 [bpftime/example](https://github.com/eunomia-bpf/bpftime/tree/master/example/sslsniff)。用户态部分做了修改，不再打印报文内容。

## 环境

测试环境：

```console
$ uname -a
Linux yunwei37server 6.2.0-35-generic #35-Ubuntu SMP PREEMPT_DYNAMIC Tue Oct  3 13:14:56 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux
$ nginx -v
nginx version /1.22.0 (Ubuntu)
$ ./wrk -v
wrk 4.2.0 [epoll] Copyright (C) 2012 Will Glozer
```

## 准备

启动 nginx 服务：

```sh
nginx -c $(pwd)/nginx.conf -p $(pwd)
```

## 无影响测试

```console
wrk https://127.0.0.1:4043/index.html -c 100 -d 10
```

## 内核态 sslsniff 测试

在一个控制台中：

```console
$ make -C example/sslsniff
$ sudo example/sslsniff/sslsniff 
OpenSSL path: /lib/x86_64-linux-gnu/libssl.so.3
GnuTLS path: /lib/x86_64-linux-gnu/libgnutls.so.30
NSS path: /lib/x86_64-linux-gnu/libnspr4.so
FUNC         TIME(s)            COMM             PID     LEN    
lost 194 events on CPU #2
lost 61 events on CPU #3
^CTotal events: 260335 
```

这个 sslsniff 来自 bpftime/example/sslsniff/sslsniff。用户态部分做了修改，不再打印报文内容。

在另一个 shell 中：

```console
wrk https://127.0.0.1:4043/index.html -c 100 -d 10  
```

## 用户态 sslsniff 测试

注意：你需要将 bpftime 配置为：

1. 不对 hash map 和 array map 使用锁
2. 使用 ubpf JIT
3. 使用 LTO

在一个控制台中启动用户态 sslsniff：

```sh
~/.bpftime/bpftime load example/sslsniff/sslsniff
# 或者 LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so example/sslsniff/sslsniff
```

在另一个控制台中重启 nginx：

```sh
~/.bpftime/bpftime start nginx -- -c nginx.conf -p benchmark/ssl-nginx
# 或者 LD_PRELOAD=build/runtime/agent/libbpftime-agent.so nginx -c nginx.conf -p benchmark/ssl-nginx
```

在另一个控制台中运行 wrk：

```console
$ ./wrk https://127.0.0.1:4043/index.html -c 100 -d 10
```
