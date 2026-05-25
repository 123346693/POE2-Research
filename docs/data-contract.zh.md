# 数据契约

项目先使用本地 JSON，后续所有爬取器、导入器和数据库同步器都要归一成同一套结构。

## Build 候选

```json
{
  "id": "unique-build-id",
  "name": "Build 名称",
  "game_version": "0.x.x",
  "source": "数据来源",
  "player_class": "Mercenary",
  "ascendancy": "Gemling Legionnaire",
  "main_skill": "主技能",
  "damage_type": "physical/fire/cold/lightning/chaos/mixed",
  "tags": ["mapping", "bossing", "starter"],
  "budget": "low",
  "trade_mode": "trade|ssf|either",
  "required_uniques": ["核心暗金"],
  "defensive_layers": ["armour", "block"],
  "metrics": {
    "damage": 84,
    "clear_speed": 77,
    "survivability": 70,
    "cost_efficiency": 90,
    "patch_stability": 75,
    "ssf_viability": 64,
    "ease_of_play": 80,
    "data_confidence": 55
  },
  "nerf_risk": "low|medium|high",
  "pros": ["优点"],
  "cons": ["缺点"],
  "evidence": ["来源链接或测试记录"],
  "notes": "补充说明"
}
```

所有 metric 都用 0-100。分数不是绝对真理，它代表当前数据快照下的相对排序。

## 用户需求

CLI 当前支持：

- `--class`
- `--ascendancy`
- `--playstyle`
- `--budget`
- `--trade-mode`
- `--ssf`
- `--hardcore`
- `--avoid-uniques`
- `--controller-friendly`
- `--min-survivability`

后续可以把这些字段接到聊天输入解析器，让你直接说“我想低预算开荒、能打 Boss、不想绑定贵暗金”，系统自动转换成约束。
