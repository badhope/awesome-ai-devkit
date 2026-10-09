---
name: calculator-math
description: 精确数学与金融计算。避免大模型算术错误，高精度小数、汇率、税率、利息计算。对齐 OpenClaw 内置 calculator 工具。
layer: utilities
tags: [math, calculation, finance, precision]
---

# Calculator -- 精确数学计算

## 触发条件

涉及金额、税率、统计、科学计算、日期运算时。

## 规则

金额计算必须使用精确计算工具（不依赖模型口算）:

```python
# 使用 Python decimal 避免浮点误差
from decimal import Decimal, ROUND_HALF_UP

a = Decimal("19.99")
b = Decimal("0.0825")  # 8.25% tax
total = (a * (1 + b)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

## 常用场景

| 场景 | 精确方法 |
|------|---------|
| 金额分/元转换 | Decimal * 100 |
| 税率计算 | Decimal + quantize |
| 利率复利 | Decimal(rate) ** periods |
| 分页总数 | math.ceil(total/per_page) |
| 日期运算 | datetime + timedelta |
| 百分比 | (part/total)*100 + ROUND_HALF_UP |

## Checklist

- [ ] 金额类计算不使用 float
- [ ] 中间结果保留精度，最后一步才 quantize
- [ ] 边界条件测试（0、负数、极大值）
