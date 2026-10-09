# 案例：AI 坏毛病整改 — 用 pragmatic-guard 门禁抓住并修复

> 演示 AI 写代码时常见的 5 类坏毛病如何被 `pragmatic-guard` **强制拦截**，以及正确的整改方式。本案例提供"坏代码 → 门禁报错 → 好代码"的完整对照，可直接套用到你的项目。

## 背景

某次开发任务中，AI 自动产出了一批代码。完工时运行 `enforce_active.py`（内含 pragmatic-guard 第 7 项门禁）**失败**，报出 5 类坏毛病。以下逐条展示"坏"与"改"。

## 整改三步法

```
1. 运行门禁定位问题   → python3 framework/lib/scripts/quality/pragmatic-guard.py --project . --json
2. 逐条整改           → 复用现有库 / 删冗余 / 补实现 / 去过度设计 / 命名常量 + 异常处理
3. 重跑直到 PASS      → exit 0 才允许提交 / 完工
```

---

## 问题 1：重复造轮子

**AI 写的坏代码**（手写一个已有的 HTTP 客户端，重复造轮）：
```python
# bad_service.py
import socket

def http_get(url: str) -> str:
    host, path = url.split("://")[1].split("/", 1)
    sock = socket.create_connection((host, 80))
    sock.send(f"GET /{path} HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
    return sock.recv(1024).decode()   # 手动解析 HTTP，极易出错
```

**整改**：复用现有库（`requests`/`httpx`），不重复造轮：
```python
# service.py
import httpx

def http_get(url: str) -> str:
    return httpx.get(url, timeout=5).text
```

---

## 问题 2：冗余文件

**AI 写的坏代码**（生成了一堆没用的空壳文件）：
```
src/
  utils_helper.py        # 空文件（0 字节）
  placeholder_api.py     # 只有占位符
  dummy_service.py       # 从未被 import
```

**门禁报**：
```
✗ [redundant] 空文件: src/utils.py
✗ [redundant] 疑似无用命名: src/placeholder_api.py
✗ [redundant] 可能未被引用: src/dummy_service.py
```

**整改**：删除无用文件，保留真实被引用的代码。新增文件必须被 `import`/`require` 引用。

---

## 问题 3：虚假实现

**AI 写的坏代码**（用占位符冒充完成）：
```python
def process_payment(card: str) -> str:
    pass                        # 空函数体 —— 假装实现了
    # TODO: 接支付网关          # 未完成标记

def refund(order_id: int):
    raise NotImplementedError    # 抛未实现

def get_user(user_id: int):
    return None                  # 占位返回
```

**门禁报**：
```
✗ [fake] src/payment.py 空函数体/仅占位: process_payment
✗ [fake] src/payment.py:1 占位/未实现: raise NotImplementedError
✗ [fake] src/payment.py:2 占位/未实现: TODO 接支付网关
```

**整改**：要么真实现，要么明确不做并说明，不留占位：
```python
# payment.py —— 真实现（或显式声明未纳入本期范围）
def process_payment(payload: dict) -> dict:
    return gateway.charge(payload)

def upload(order_id: str) -> bool:
    # 本期未实现，返回 False 并记录（比 raise NotImplemented 诚实）
    logger.info("upload 不在本期范围, order=%s", order_id)
    return False
```

---

## 问题 4：过度设计

**AI 写的坏代码**（为简单功能造了一堆抽象）：
```python
# 一个"读取配置文件"的需求，造了工厂 + 接口 + 两个子类
class ConfigAbstractFactory:
    def create_reader(self): ...

class JsonConfigReader(ConfigAbstractFactory): ...
class YamlConfigReader(ConfigAbstractFactory): ...

def get_setting(name: str):
    reader = JsonConfigReader()   # 永远只用这一个
    return reader.read(name)
```

**门禁报**：
```
✗ [overengine] src/config.py:1 过度设计: class ConfigAbstractFactory
✗ [overengine] src/config.py:2 过度设计: class JsonConfigReader
```

**整改**：YAGNI + KISS，去掉用不到的抽象：
```python
# config.py —— 只需要一个函数
import json

def get_setting(name: str, path: str = "config.json"):
    with open(path) as f:
        return json.load(f)[name]
```

---

## 问题 5：业务不合现实

**AI 写的坏代码**（魔法数字 + 演示字符串 + 吞异常）：
```python
def checkout(items):
    total = 0
    for item in items:
        total += item.price
    tax = total * 0.0925   # 0.0925 是税率但无命名，业务不可读
    if total > 1000:
        discount = 0        # 魔法数，无业务语义
    try:
        return {"greeting": "hello", "total": tax + total}   # greeting 演示字符串
    except:                # 吞掉所有异常
        pass
```

**门禁报**：
```
✗ [business] src/cart.py:3 魔法数字(>4位)需命名常量: tax = total * 0.0925
✗ [business] src/cart.py:1 疑似演示字符串'hello'
✗ [business] src/cart.py:8 try 无 except/catch（异常被吞）
```

**整改**（命名常量 + 真实业务 + 处理异常）：
```python
# cart.py
TAX_RATE = 0.0925           # 税率，命名常量

def checkout(items: list) -> dict:
    total = sum(i.price for i in items)
    tax = round(total * TAX_RATE, 2)
    try:
        return {"subtotal": total, "tax": tax, "total": total + tax}
    except ValueError as e:
        raise ValueError(f"invalid cart: {e}")   # 结构化异常，不吞
```

---

## 整改后门禁通过

```
$ python3 framework/lib/scripts/quality/pragmatic-guard.py --project .
Pragmatic Guard — /workspace/myapp
  ✅ PASS: 0 个问题
exit=0
```

此时才能进入 `enforce_active.py` 完工门禁 → 提交。

## 复盘

- **机制强于提示**：pragmatic-guard 用退出码阻断，比"让 AI 自觉"可靠得多
- **5 类坏毛病有明确检测规则**：不靠感觉，脚本逐条扫
- **整改是"做减法"**：删冗余、去抽象、补真实实现，代码反而更短更清晰
- **误报可控**：框架层/测试/文档/`except:pass`/字符串内魔法值已排除，不会误伤

## 可复现

```bash
# 1. 用坏代码建项目（上面任意一段）→ 运行门禁看报错
python3 framework/lib/scripts/quality/pragmatic-guard.py --project .

# 2. 逐条整改（参照上文对照）→ 重跑直到 exit 0
# 3. 完工门禁
python3 hooks/scripts/enforce_active.py
```

> AI生成
