# bpftime-verifier

一个围绕 ebpf-verifier 的简单封装，提供更易用的接口。

## 用法

### 设置 cmake
```
add_subdirectory(bpftime-verifier)

add_dependencies(MY_TARGET bpftime-verifier)
target_link_libraries(MY_TARGET bpftime-verifier)
target_include_directories(MY_TARGET PUBLIC ${BPFTIME_VERIFIER_INCLUDES}s)
```
### 调用 verifier

```cpp
#include <bpftime-verifier.hpp>
#include <map>
#include <iostream>
#include <optional>
#include <string>
using namespace bpftime;

int main(){
    // 设置当前 ebpf 程序会使用的 map
    set_map_descriptors(std::map<int, BpftimeMapDescriptor>{
        { 2333, BpftimeMapDescriptor{ .original_fd = 233,
                            .type = BPF_MAP_TYPE_HASH,
                            .key_size = 8,
                            .value_size = 4,
                            .max_entries = 8192,
                            .inner_map_fd = 0 } } });

    // 设置当前 ebpf 程序会使用的 helper
    // 这既可以包含内核提供的 helper，也可以包含自定义 helper
    set_available_helpers(std::vector<int32_t>{ 1, 1000001 });
    // 对于用户自定义 helper，也需要定义原型
    set_non_kernel_helpers(std::map<int, BpftimeHelperProrotype>{
        {1000001, BpftimeHelperProrotype{
            .name = "my_helper",
            .return_type = EBPF_RETURN_TYPE_INTEGER,
            .argument_type = {
                EBPF_ARGUMENT_TYPE_ANYTHING, // 这表示任意 64 位整数
                EBPF_ARGUMENT_TYPE_PTR_TO_MAP, // 这表示一个 map 指针
            }
        }}
    });

    const uint64_t prog_with_map_1[] = { 
        0x00000002000001b7, 
        0x00000000fff81a7b,
        0x000000000000a2bf, 
        0xfffffff800000207,
        0x0000091d00001118, 
        0x0000000000000000,
        0x0000000100000085, 
        0x0000000000000061,
        0x0000000000000095 };

    // 执行验证
    std::optional<std::string> result = auto ret =
            verify_ebpf_program(prog_with_map_1, std::size(prog_with_map_1),
                        "uprobe//proc/self/exe:uprobed_sub");

    // 如果验证成功，verify_ebpf_program 会返回一个空的 optional；否则会返回失败信息
    if(result.has_value()){
        std::cerr << result.value();
    } else {
        std::cout << "Done!";
    }
}
```

## 重要说明

`set_available_helpers`、`set_non_kernel_helpers` 和 `set_map_descriptors` 设置的内容都是线程局部的，这意味着每个线程都有自己的一份。因此，你需要在每个使用到的线程中都设置相应的值。
