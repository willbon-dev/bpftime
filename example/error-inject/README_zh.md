# error-inject

bpftime 允许你覆盖用户态函数的执行，并返回你指定的值，也可以对 system call 做错误注入。

这对于测试程序的错误处理非常有用。

## 运行：覆盖用户态函数

server

```sh
LD_PRELOAD=~/.bpftime/libbpftime-syscall-server.so ./error_inject
```

client

```sh
LD_PRELOAD=~/.bpftime/libbpftime-agent.so ./victim
```
