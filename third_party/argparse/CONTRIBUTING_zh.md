# 贡献
欢迎贡献。可以提交 Pull Request 或 Issue。

## 行为准则
本项目遵循 [Open Code of Conduct][code-of-conduct]。参与项目时，期望你遵守这份准则。

[code-of-conduct]: https://github.com/spotify/code-of-conduct/blob/master/code-of-conduct.md

## 代码风格

本项目偏好某种特定的源代码风格，但并不强制要求严格遵守。该风格定义在 `.clang-format` 和 `.clang-tidy` 中。

生成 clang-tidy 报告：

```bash
clang-tidy --extra-arg=-std=c++17 --config-file=.clang-tidy include/argparse/argparse.hpp
```
