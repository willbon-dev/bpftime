# libbtf
[![CI/CD](https://github.com/Alan-Jowett/libbtf/actions/workflows/CICD.yml/badge.svg)](https://github.com/Alan-Jowett/libbtf/actions/workflows/CICD.yml)
[![Coverage Status](https://coveralls.io/repos/github/Alan-Jowett/libbtf/badge.svg?branch=main)](https://coveralls.io/github/Alan-Jowett/libbtf?branch=main)

用于解析 BPF Type Format 数据的工具库

本项目允许解析 LLVM 和 "pahole" 生成的 BTF 数据，并将其返回为 C++ 类型。

## 构建
运行 ```cmake -S . -B build``` 配置项目，然后运行 ```cmake --build build``` 构建项目。

## 运行测试
Linux
```build/test/tests -d yes```

Windows
```build/test/Debug/tests.exe -d yes```

## 使用库
1. 在你的 cmake 项目中添加引用
```
Include(FetchContent)

FetchContent_Declare(
  libbtf
  GIT_REPOSITORY https://github.com/Alan-Jowett/libbtf.git
  GIT_TAG        0.0.1 # 或更高版本
)

FetchContent_MakeAvailable(libbtf)

include_directories(${libbtf_SOURCE_DIR})

target_link_libraries(<your project> PRIVATE libbtf)
```

2. 获取指向 BTF 数据向量的指针。
```
    auto reader = ELFIO::elfio();
    if (!reader.load(argv[1])) {
        std::cerr << "Failed to load " << argv[1] << "\n";
        return 1;
    }

    auto btf = reader.sections[".BTF"];
```

3. 解析 BTF 数据。
```
    libbtf::btf_type_data btf_data = std::vector<std::byte>(
      {reinterpret_cast<const std::byte *>(btf->get_data()),
       reinterpret_cast<const std::byte *>(btf->get_data() + btf->get_size())});
```

4. 使用 BTF 数据。
```
    std::ostringstream json;
    btf_data.to_json(json);

    std::cout << libbtf::pretty_print_json(json.str()) << "\n";
```
