# POE2 Build Lab

POE2 Build Lab 是一个给 Path of Exile 2 做版本研究、数据归档和 Build 推荐的本地项目。

目标很直接：把 POE2DB、Wiki、天梯、价格、玩家实测和你的个人要求统一成一套可解释的评分系统，然后自动给出“这个版本、这个预算、这个玩法目标下最强/最合适的 Build”。

## 当前能力

- 从本地 JSON 数据库读取 Build 候选。
- 按职业、升华、玩法、预算、Divine 数量、SSF/交易、HC、生存阈值、是否依赖暗金等条件打分。
- 输出推荐排名、总分、推荐理由、扣分点和关键装备/防御层。
- 读取角色快照，按预算输出装备/防御/伤害升级优先级。
- 提供 POE2DB 导出适配器骨架，后续可接自动抓取或手动导入。

示例数据是 seed data，只用于验证流程，不代表真实版本强度。

## 快速运行

启动 Alpha Web：

```powershell
python run_alpha.py --host 127.0.0.1 --port 8765
```

然后打开：

```text
http://127.0.0.1:8765/
```

在项目根目录执行：

```powershell
python -m poe2_build_lab.cli recommend --data data/sample/builds.json --playstyle bossing --budget medium --top 3
```

如果没有安装成包，可以设置源码路径后运行：

```powershell
$env:PYTHONPATH="src"
python -m poe2_build_lab.cli recommend --data data/sample/builds.json --playstyle bossing --budget medium --top 3
```

更具体的需求：

```powershell
$env:PYTHONPATH="src"
python -m poe2_build_lab.cli recommend --data data/sample/builds.json --class Mercenary --playstyle mapping --budget low --ssf --avoid-uniques --top 5
```

5D 预算示例：

```powershell
$env:PYTHONPATH="src"
python -m poe2_build_lab.cli recommend --data data/sample/builds.json --ascendancy Invoker --playstyle mapping --budget-divines 5 --top 3
```

角色诊断示例：

```powershell
$env:PYTHONPATH="src"
python -m poe2_build_lab.cli diagnose --character data/sample/character.json --prices data/sample/prices.json --budget-divines 20
```

## 推荐逻辑

评分分成两层：

1. 版本强度：伤害、刷图速度、生存、成本效率、版本稳定性、SSF 可行性、操作难度、数据可信度。
2. 个人适配：你的职业/升华偏好、玩法目标、预算、交易环境、HC、是否讨厌绑定暗金、手柄友好等。

项目不会把“最强”写死，因为 POE2 的最强 Build 永远取决于版本、资源、玩法目标和数据可信度。

## 计划

- 接 POE2DB / Wiki 数据归档。
- 接官方 OAuth 角色导入。
- 接官方 trade2 / poe.ninja / 价格快照，区分 5D、20D、100D 等预算。
- 加入技能/辅助宝石/装备词缀的约束检查。
- 加 Web UI，让你用中文直接输入需求并得到 Build 方案。

## 重要来源

- POE2DB: https://poe2db.tw/
- POE2 Wiki: https://www.poe2wiki.net/

这些来源会作为数据库层输入；推荐结论仍需要用版本号、数据时间和样本来源标注。
