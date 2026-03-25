# 用法

终端 1
```
BPFTIME_NOT_LOAD_PATTERN=cuda.*  BPFTIME_RUN_WITH_KERNEL=true bpftime load ./threadhist
```

终端 2

```
bpftime start ./vec_add
```

来自 syscall server 的示例输出

```
21:34:17 
value(0)=10
value(1)=1
21:34:18 
value(0)=20
value(1)=2
21:34:19 
value(0)=30
value(1)=3
```

如果 agent 退出，必须重启 syscall-server，否则下一次启动 agent 时会无法调用 `cuMemHostRegister`。
