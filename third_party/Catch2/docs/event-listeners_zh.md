<a id="top"></a>
# Event Listener

Event listener 有点像 reporter，因为它会响应 Catch2 中的各种 reporter 事件，但它不负责输出任何内容。相反，event listener 会在测试进程内部执行动作，例如进行全局初始化（比如 C 库初始化），或者在不需要时清理内存中的日志（例如测试用例通过时）。

与 reporter 不同，每个已注册的 event listener 都总是处于激活状态。Event listener 总是在 reporter 之前收到通知。

要编写自己的 event listener，应该从 `Catch::TestEventListenerBase` 继承，因为它为所有 reporter 事件都提供了空实现，这样你就只需要重写你关心的事件。之后还必须使用 `CATCH_REGISTER_LISTENER` 宏把它注册给 Catch2，这样 Catch2 才会在运行测试前知道并实例化它。

示例 event listener：
```cpp
#include <catch2/reporters/catch_reporter_event_listener.hpp>
#include <catch2/reporters/catch_reporter_registrars.hpp>

class testRunListener : public Catch::EventListenerBase {
public:
    using Catch::EventListenerBase::EventListenerBase;

    void testRunStarting(Catch::TestRunInfo const&) override {
        lib_foo_init();
    }
};

CATCH_REGISTER_LISTENER(testRunListener)
```

_注意，你不应该在 Listener 中使用任何断言宏！_

[你可以在它自己的页面上找到 listener 可以响应的事件列表](reporter-events_zh.md#top)。

---

[Home](Readme_zh.md#top)
