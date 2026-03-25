# bpftime 中的 XDP

你可以把 XDP 程序加载到用户态 eBPF runtime 中，并通过 DPDK 或 AF_XDP 执行它。这带来以下好处：

- `比 kernel eBPF 更快`：DPDK 在某些场景下可能比 XDP driver mode 更快，bpftime 在某些情况下也可能比 kernel 更快。
- 与 DPDK 中的 ubpf 相比，这样可以实现：
  - `支持控制平面应用`：允许控制库操作 eBPF map，并动态控制 eBPF 程序的加载和卸载。
  - `更多与 kernel 兼容的 maps 和 helpers`：

## 将 XDP 加载到用户态 eBPF runtime

先创建一个虚拟网络设备用于测试：

```sh
sudo ip link add veth0 type veth peer name veth1
```

挂载 netdev：

```sh
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so example/xdp-counter/xdp-counter example/xdp-counter/.output/xdp-counter.bpf.o veth1 example/xdp-counter/base.btf
```

- `example/xdp-counter/base.btf` 用于用户态 XDP 的 relocation。关于用户态 `xdp_md` 的结构，可以参见 [runtime/extension/userspace_xdp.h](../../runtime/extension/userspace_xdp.h)。

## 在用户态运行 XDP 程序

驱动程序参见 <https://github.com/eunomia-bpf/XDP-eBPF-in-DPDK>

## TODO：支持旧的 XDP attach

目前 bpftime 只支持使用 `bpf_link` 挂载 XDP 程序。后续还需要处理旧的 attach 方式。

```sh
newfstatat(1, "", {st_mode=S_IFREG|0644, st_size=0, ...}, AT_EMPTY_PATH) = 0
socket(AF_UNIX, SOCK_DGRAM|SOCK_CLOEXEC, 0) = 7
ioctl(7, SIOCGIFINDEX, {ifr_name="veth1", ifr_ifindex=5}) = 0
close(7)                                = 0
socket(AF_NETLINK, SOCK_RAW|SOCK_CLOEXEC, NETLINK_ROUTE) = 7
setsockopt(7, SOL_NETLINK, NETLINK_EXT_ACK, [1], 4) = 0
bind(7, {sa_family=AF_NETLINK, nl_pid=0, nl_groups=00000000}, 12) = 0
getsockname(7, {sa_family=AF_NETLINK, nl_pid=405177, nl_groups=00000000}, [12]) = 0
sendto(7, [{nlmsg_len=52, nlmsg_type=RTM_SETLINK, nlmsg_flags=NLM_F_REQUEST|NLM_F_ACK, nlmsg_seq=1724212008, nlmsg_pid=0}, {ifi_family=AF_UNSPEC, ifi_type=ARPHRD_NETROM, ifi_index=if_nametoindex("veth1"), ifi_flags=0, ifi_change=0}, [{nla_len=20, nla_type=NLA_F_NESTED|IFLA_XDP}, [[{nla_len=8, nla_type=IFLA_XDP_FD}, 6], [{nla_len=8, nla_type=IFLA_XDP_FLAGS}, XDP_FLAGS_UPDATE_IF_NOEXIST]]]], 52, 0, NULL, 0) = 52
recvmsg(7, {msg_name=NULL, msg_namelen=0, msg_iov=[{iov_base=[{nlmsg_len=36, nlmsg_type=NLMSG_ERROR, nlmsg_flags=NLM_F_CAPPED, nlmsg_seq=1724212008, nlmsg_pid=405177}, {error=0, msg={nlmsg_len=52, nlmsg_type=RTM_SETLINK, nlmsg_flags=NLM_F_REQUEST|NLM_F_ACK, nlmsg_seq=1724212008, nlmsg_pid=0}}], iov_len=4096}], msg_iovlen=1, msg_controllen=0, msg_flags=0}, MSG_PEEK|MSG_TRUNC) = 36
recvmsg(7, {msg_name=NULL, msg_namelen=0, msg_iov=[{iov_base=[{nlmsg_len=36, nlmsg_type=NLMSG_ERROR, nlmsg_flags=NLM_F_CAPPED, nlmsg_seq=1724212008, nlmsg_pid=405177}, {error=0, msg={nlmsg_len=52, nlmsg_type=RTM_SETLINK, nlmsg_flags=NLM_F_REQUEST|NLM_F_ACK, nlmsg_seq=1724212008, nlmsg_pid=0}}], iov_len=4096}], msg_iovlen=1, msg_controllen=0, msg_flags=0}, 0) = 36
close(7)                                = 0
```
