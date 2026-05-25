# POE2 数据源地图

目标不是把网络上的说法无差别吞进数据库，而是给每条结论保留来源、时间和可信度。

## 一线来源

- 官方开发文档：用于 OAuth、角色、联盟、货币交易历史等 API 能力。
- 官方 trade2 网站：用于人工复核与交易搜索入口；自动化访问必须遵守站点策略和限速。
- POE2DB：用于技能、物品、词缀、升华、机制文本和 datamined 变更快照。
- POE2 Wiki：用于职业、升华、机制说明和版本历史的交叉验证。

## 二线来源

- poe.ninja POE2 economy：用于唯一物品和经济趋势的聚合价格信号。
- Build guide、视频、Reddit、Discord：只作为候选证据，不能单独决定推荐。
- 用户实测：死亡原因、Boss 时间、刷图速度、预算记录，权重很高但必须记录版本和装备。

## 当前技术判断

- 官方 API 文档显示，多数开发 API 需要 OAuth；角色读取需要 `account:characters`。
- `realm=poe2` 可用于官方 league 和 currency exchange history。
- 官方 public stash 文档当前标注为 PoE1 only；POE2 装备价格应优先走 trade2 查询、poe.ninja 聚合、人工缓存三层。
- 价格永远要带 `captured_at`、`source`、`sample_size`、`confidence`，否则不能用于高置信推荐。

## 结论门槛

真实 Build 推荐至少需要：

1. 当前版本号和 league。
2. 主技能、升华、预算、目标内容。
3. 至少一个价格来源或明确 SSF 模式。
4. 防御阈值检查，不允许只堆伤害。
5. 升级建议要给出预估收益和置信度。
