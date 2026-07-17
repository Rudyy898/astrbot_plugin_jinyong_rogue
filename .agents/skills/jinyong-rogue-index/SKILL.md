---
name: jinyong-rogue-index
description: Use when modifying or analyzing this astrbot_plugin_jinyong_rogue project, including gameplay rules, QQ/AstrBot commands, local Web HTML test shell, engine logic, data tables, battle, inventory, fishing, equipment, meta progression, card UI, storage, README, or project structure. Always use PROJECT_INDEX.md first to quickly locate the exact file, method, object, and data table before editing.
triggers:
  - 金庸踢门团
  - astrbot_plugin_jinyong_rogue
  - PROJECT_INDEX.md
  - 修改游戏
  - 修改玩法
  - 修改命令
  - 本地 Web 调试
  - QQ 游戏插件
---

# 金庸踢门团项目索引优先工作流

## 必做流程

1. 先读取仓库根目录的 `PROJECT_INDEX.md`。
2. 根据索引判断修改目标：
   - QQ/AstrBot 命令入口：`main.py`
   - 本地 Web/HTML 调试：`web_runtime.py`、`web/server.py`、`web/static/*`
   - 游戏规则与状态机：`engine.py`
   - 门派、敌人、装备、背囊、钓鱼、文案等配置：`game_data.py`
   - 图片卡片 UI：`ui.py`
   - JSON 存档：`storage.py`
3. 再读取目标文件的相关方法或对象，不要从头盲扫全仓库。
4. 修改后同步考虑 QQ 与 Web 两条入口是否都需要补映射：
   - 新增玩家命令时，通常同时改 `main.py` 和 `web_runtime.py`。
   - 只改规则或数值时，优先改 `engine.py` / `game_data.py`，避免复制逻辑到入口层。
5. 保持 QQ 正式入口和 Web 测试入口解耦；Web 本地存档在 `data/web/`，不得影响 AstrBot 正式数据目录。

## 输出要求

- 修改完成后列出文件路径、变更说明、最小 diff 片段。
- 不主动运行 build、test、server 或验证命令；如需运行，先询问用户。
- 不添加 AI 署名、生成标记或 Co-Authored-By。

## 快速定位规则

- 改“按钮/点击测试/本地浏览器”：先看 `PROJECT_INDEX.md` 的 Web 入口，再看 `web/static/index.html` 与 `web_runtime.py`。
- 改“/金庸xxx 指令”：先看 `main.py` 指令入口索引，再看对应 `engine.py` 函数。
- 改“伤害、骰子、战斗回合”：先看 `engine.py` 战斗方法索引。
- 改“门派、武学、装备、敌人、钓鱼掉落”：先看 `game_data.py` 数据对象索引。
- 改“图片卡片不对、状态栏不对、场景背景不对”：先看 `ui.py` UI 索引。
