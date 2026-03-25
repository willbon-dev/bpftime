<a id="top"></a>
# 如何发布

当积累了足够多的变更后，就该发布 Catch 的新版本了。本文档描述了发布流程，以免遗漏步骤。注意，所有引用到的脚本都可以在 `tools/scripts/` 目录中找到。

## 必要步骤

这些步骤在每次新版本发布前都必须执行。它们用于确保新发布版本是正确的，并且能够从标准位置正确链接到。

### 测试

目前所有测试都在基于 TravisCI 和 AppVeyor 的 CI 环境中运行。只要最后一次提交测试通过，发布就可以继续。

### 递增版本号

Catch 使用一种 [语义化版本](http://semver.org/) 的变体，API 的破坏性变更（因此也意味着主版本号递增）非常少见。因此，发布时通常只会在包含少量 bug 修复时增加 patch 版本，或在包含新功能或现有功能实现的较大改动时增加 minor 版本。

在确定应该递增版本号的哪一部分之后，你可以使用某个 `*Release.py` 脚本来对 Catch 执行必要改动。

这会负责生成单头文件、更新各处版本号，并把新版本推送到 Wandbox。

### 发布说明

一旦准备发布，就需要编写发布说明。它们应该总结自上次发布以来的变更。至于预期格式，可以参考以前的发布说明。写好之后，应该把发布说明添加到 `docs/release-notes.md`。

### 提交并推送更新到 GitHub

在递增版本号、重新生成单头文件并更新发布说明之后，就应该把改动提交并推送到 GitHub。

### 在 GitHub 上发布

把改动推送到 GitHub 之后，还需要创建 GitHub release。标签版本和 release 标题应与新版本相同，描述中应包含当前发布的发布说明。我们还会把两个 amalgamated 文件作为“二进制”附件上传。

自 2.5.0 起，release tag 和“二进制”（amalgamated 文件）都应该进行 PGP 签名。

#### 为 tag 签名

要创建签名 tag，请使用 `git tag -s <VERSION>`，其中 `<VERSION>` 是要发布的版本，例如 `git tag -s v2.6.0`。

短消息使用版本名，长消息使用发布说明正文。

#### 为 amalgamated 文件签名

这会为上传到 GitHub release 的两个 amalgamated 文件创建 ASCII-armored 签名：

```bash
gpg --armor --output extras/catch_amalgamated.hpp.asc --detach-sig extras/catch_amalgamated.hpp
gpg --armor --output extras/catch_amalgamated.cpp.asc --detach-sig extras/catch_amalgamated.cpp
```

_注意，GPG 不支持在一次调用中对多个文件签名。_
