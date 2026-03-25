# opensnoop

跟踪进程中的文件打开或关闭 syscall。

由于程序并没有挂载到所有 syscall 事件上，因此程序内没有必要按 pid 和 uid 过滤事件。这样还可以提升程序速度并降低开销。

## 用法

```console
$ sudo ~/.bpftime/bpftime load ./example/opensnoop/opensnoop
[2023-10-09 04:36:33.891] [info] manager constructed
[2023-10-09 04:36:33.892] [info] global_shm_open_type 0 for bpftime_maps_shm
[2023-10-09 04:36:33][info][23999] Enabling helper groups ffi, kernel, shm_map by default
PID    COMM              FD ERR PATH
72101  victim             3   0 test.txt
72101  victim             3   0 test.txt
72101  victim             3   0 test.txt
72101  victim             3   0 test.txt
```

在另一个终端中运行 victim 程序：

```console
$ sudo ~/.bpftime/bpftime start -s example/opensnoop/victim
[2023-10-09 04:38:16.196] [info] Entering new main..
[2023-10-09 04:38:16.197] [info] Using agent /root/.bpftime/libbpftime-agent.so
[2023-10-09 04:38:16.198] [info] Page zero setted up..
[2023-10-09 04:38:16.198] [info] Rewriting executable segments..
[2023-10-09 04:38:19.260] [info] Loading dynamic library..
...
test.txt closed
Opening test.txt
test.txt opened, fd=3
Closing test.txt...
```
