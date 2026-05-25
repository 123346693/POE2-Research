# Alpha 使用说明

## 启动

```powershell
python run_alpha.py --host 127.0.0.1 --port 8765
```

浏览器打开：

```text
http://127.0.0.1:8765/
```

## 当前可测功能

- Build 推荐：选择升华、玩法、预算 D、交易模式，返回推荐排序。
- 角色诊断：粘贴角色 JSON，输入预算 D，返回升级优先级。
- 数据状态：查看当前升华覆盖和样例角色。

## 可测样例

- `Invoker` + `mapping` + `5D`：会返回预算内的 Budget Invoker Tempest Flurry。
- 示例角色 + `20D`：会优先提示补抗性、换武器、升级胸甲。

## Alpha 限制

当前推荐使用 seed data。它验证的是工具链、数据契约、预算约束和诊断流程；真实版本强度需要接入 POE2DB、官方角色 API、trade2/poe.ninja 价格快照后再下结论。
