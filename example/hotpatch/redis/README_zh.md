# redis 示例

预编译的二进制包是适用于 x86 的 tar.gz。

你也可以在 `redis-5.0-rc1` 中自行编译一个版本。

1. 查找函数

     ```console
     $ nm ./redis-server | grep xgroupCommand
     00000000000b7c80 T xgroupCommand
     00000000000280b9 t xgroupCommand.cold
     ```

2. 生成 btf（可选）

     ```sh
     pahole --btf_encode_detached redis-server.btf ./redis-server
     ```

3. 生成头文件

     ```sh
     bpftool btf dump file redis-server.btf format c > redis-server.btf.h
     ```

4. 触发 PoC（打补丁之前）：

     PoC：

     ```console
     $ ./redis-server

     # 在另一个 bash 中
     $ ./redis-cli -p 6379
     127.0.0.1:1234> set a 123
     OK
     127.0.0.1:1234> xgroup create a b $
     Error: Connection reset by peer  <— segfault'ed
     127.0.0.1:1234>

     这个 bug 也可以通过 netcat 触发
     $ nc 127.0.0.1 1234
     set a 123
     +OK
     xgroup create a b $  <— segfault’ed after this line
     ```

5. 准备补丁：

     下面这个 commit 修复了问题：

     ```c
     @@ -1576,7 +1576,7 @@ NULL
          /* Lookup the key now, this is common for all the subcommands but HELP. */
          if (c->argc >= 4) {
     robj *o = lookupKeyWriteOrReply(c,c->argv[2],shared.nokeyerr);
     -         if (o == NULL) return;
     +         if (o == NULL || checkType(c,o,OBJ_STREAM)) return;
          s = o->ptr;
          grpname = c->argv[3]->ptr;
     ```

     参见 `poc.bpf.c` 和 `poc.json`。

6. 打补丁后，运行命令进行安装：

     ```console
     $ sudo build/tools/cli/bpftime-cli workloads/ebpf-patch-dev/poc4-redis/poc.json
     Successfully injected. ID: 1
     ```

     结果如下：

     ```console
     find and load program: xgroupCommand
     load insn cnt: 79
     attach replace 0x562b4fcf7c80
     Successfully attached
     xgroupCommand: 0x562b50b15c98
     c->argc >= 4lookupKeyWriteOrReply: 0x562b50b15c98 0x562b50b23ed8 (nil)
     find func lookupKeyWrite at 545
     ----------------------op code: 0 ret: 0
     xgroupCommand: 0x562b50b15c98
     c->argc >= 4lookupKeyWriteOrReply: 0x562b50b15c98 0x562b50b220d8 (nil)
     find func lookupKeyWrite at 545
     ----------------------op code: 0 ret: 0
     ```
