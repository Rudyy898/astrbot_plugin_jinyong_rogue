# 项目索引：金庸武侠DND肉鸽踢门团

本索引用于后续快速定位修改目标。当前仓库是 AstrBot 插件，核心逻辑集中在 `engine.py`，QQ/AstrBot 适配在 `main.py`，本地 Web 调试入口在 `web_runtime.py` 与 `web/`。

## 文件职责

| 文件 | 行数 | 职责 |
| --- | ---: | --- |
| `main.py` | 736 | AstrBot 插件类、QQ 指令映射、玩家存档读写、图片/文本回复封装 |
| `engine.py` | 3383 | 游戏状态机、战斗、踢门、事件、背包、装备、钓鱼、局外成长、文本输出 |
| `game_data.py` | 569 | 表驱动配置：门派、武学、装备、敌人、Boss、背囊、钓鱼、文案 |
| `ui.py` | 809 | Pillow 场景卡片渲染、场景识别、玩家状态栏绘制 |
| `storage.py` | 40 | JSON 存档读写 |
| `web_runtime.py` | 新增 | 本地 Web 调试适配层，复用 `engine.py` 的同一套逻辑 |
| `web/server.py` | 新增 | 标准库 HTTP 服务，提供静态页面与 `/api/command` |
| `web/static/*` | 新增 | 本地测试 HTML/CSS/JS |

## 运行时边界

- QQ 正式游玩路径：`main.py` -> `engine.py` / `ui.py` / `storage.py`。
- 本地 Web 测试路径：`web/server.py` -> `web_runtime.py` -> `engine.py` / `ui.py` / `storage.py`。
- 两条路径共用规则层，不共用存档：QQ 存档由 AstrBot 数据目录决定；Web 存档固定在仓库忽略目录 `data/web/`。
- 改游戏规则优先改 `engine.py`；改门派/装备/敌人/钓鱼数值优先改 `game_data.py`；改 QQ 命令兼容性改 `main.py`；改本地调试体验改 `web_runtime.py` 或 `web/static/`。

## 指令入口索引

`main.py` 的 `JinyongRoguePlugin` 是 QQ/AstrBot 入口：

| 方法 | 行 | 作用 |
| --- | ---: | --- |
| `__init__` | 53 | 初始化插件 ID、玩家存档、局外存档、卡片缓存目录 |
| `initialize` | 62 | 创建卡片缓存目录并记录加载日志 |
| `_user_id` | 66 | 从事件取用户 ID |
| `_nickname` | 69 | 从事件取昵称 |
| `_get_player_or_message` | 72 | 读取玩家；无角色时返回提示 |
| `_save` | 78 | 保存玩家 |
| `_current_meta` | 81 | 合并持久局外成长和角色内局外成长 |
| `_with_commands` | 89 | 给正文追加下一步命令提示 |
| `_result` | 92 | 渲染图片卡片，失败时退回纯文本 |
| `_jy_command_key` | 99 | 兼容 `/jy`、`/金庸`、`/踢门` 和战斗短命令 |
| `jy_fallback_route` | 201 | QQ 官方平台中文命令兜底路由 |
| `cmd_help` | 302 | 帮助 |
| `cmd_sects` | 306 | 门派列表/门派详情 |
| `cmd_new` | 321 | 开局创建角色 |
| `cmd_status` | 344 | 状态 |
| `cmd_kick` / `cmd_decline_true_wushen` | 352 | 踢门/进入 Boss；炼狱击败武神镜像后可选择不挑战真·武神并结算 |
| `cmd_next_floor` | 374 | 下一层 |
| `cmd_fish` | 384 | 钓鱼 |
| `cmd_use` | 404 | 使用药品/鱼获 |
| `cmd_inventory` | 418 | 背包 |
| `cmd_buy_bag` | 428 | 买背囊 |
| `cmd_buy_equipment` | 439 | 买装备 |
| `cmd_sell_equipment` | 453 | 卖装备 |
| `cmd_equip` | 468 | 装备物品 |
| `cmd_skill` | 506 | 查看/设置主动武学 |
| `cmd_martial` / `cmd_learn_martial` / `cmd_compose_fragments` / `cmd_unlock_ultimate` / `cmd_ultimate` | 554 | 查看武学领悟页、消耗残页和素材领悟武学、合成顶级残页、手动解锁局外绝学、查看局外绝学库 |
| `cmd_meta` | 574 | 局外强化面板 |
| `cmd_upgrade` | 595 | 局外升级 |
| `cmd_discard` | 611 | 丢弃 |
| `cmd_pickup` | 626 | 拾取待拾取物品 |
| `cmd_attack` | 641 | 战斗攻击 |
| `cmd_flee` | 664 | 战斗逃跑 |
| `cmd_trap_dodge` | 682 | 陷阱躲避 |
| `cmd_trap_block` | 695 | 陷阱格挡 |
| `cmd_trap_counter` | 708 | 陷阱反击 |
| `cmd_defend` | 721 | 战斗防御 |
| `cmd_explore` | 742 | 探索已通关门 |
| `cmd_view_item` | 760 | 查看物品详情 |
| `cmd_reset` | 773 | 删除当前角色 |
| `cmd_surrender` | 783 | 放弃本局并结算 |

`web_runtime.py` 的 `LocalWebGameRuntime` 是本地 Web 入口：

| 对象/方法 | 作用 |
| --- | --- |
| `COMMAND_ALIASES` | Web 复刻 QQ 命令别名到内部动作 key 的映射 |
| `LocalWebGameRuntime.__init__` | 绑定本地 Web 存档和卡片目录 |
| `dispatch` | Web API 主入口：解析用户、命令、调用处理器并返回 JSON |
| `_handle_command` | 将动作 key 分派到 `engine.py` 函数 |
| `_new_game` / `_reset` | Web 本地开局与重置 |
| `_kick` / `_attack` / `_trap_action` / `_finish_sensitive` | 需要保存或结算局外奖励的动作封装 |
| `_skill` | Web 复刻 QQ 的技能列表/切换 |
| `_current_meta` | Web 合并局外成长 |
| `_response` | 追加命令提示、渲染同款卡片、返回文本/图片 URL/角色摘要 |
| `_command_key` | Web 命令识别 |
| `_player_summary` | 给前端侧栏用的轻量状态 |

## 引擎方法索引

`engine.py` 方法按职责分组：

| 方法 | 行 | 修改目标 |
| --- | ---: | --- |
| `new_player` | 91 | 开局字段、初始资源、初始装备、初始药品 |
| `roll_die` / `roll_percent` / `roll_d20` / `roll_dice` / `roll_dice_results` | 145 | 骰子随机 |
| `choose_one` / `weighted_choice` / `weighted_event` | 174 | 随机选择与事件权重 |
| `attr_bonus` / `check` / `_trait_value` | 197 | 属性加值、d20 检定、门派特质取值 |
| `get_current_level` / `get_xp_for_next_level` / `get_xp_progress` / `_apply_level_up` / `add_xp` | 222 | 经验和升级 |
| `_room_completion_xp` / `_award_room_completion_xp` | 315 | 房间完成经验 |
| `normalize_meta_progression` / `merge_meta_progression` / `difficulty_gate_text` / `meta_text` / `ultimate_text` / `unlock_meta_ultimate` / `upgrade_meta_progression` / `apply_pending_meta_rewards` | 329 | 局外成长、炼狱门派解锁门槛、局外强化页、独立绝学库、手动解锁绝学、奖励入账 |
| `_apply_damage` / `_calculate_rogue_points` / `_game_over_text` / `surrender_game` | 401 | 伤害、死亡/放弃结算 |
| `_event_check_bonus` / `_status_dc_delta` / `_apply_status_damage` / `_apply_status` | 486 | 状态与事件检定修正 |
| `status_text` / `_rpg_status_panel` / `_core_state_line` | 536 | 角色状态文本 |
| `_ensure_inventory` 到 `_inventory_free_slots` | 673 | 背包结构、容量、占格 |
| `_add_inventory_item` / `_resolve_inventory_item` / `_inventory_item_text` / `_pending_item_text` | 747 | 入包、物品解析、待拾取文案 |
| `_equipment_bonus` / `_player_ac` / `_player_attack_bonus` / `_compact_equipment_text` | 837 | 装备属性结算 |
| `set_active_skill` / `equip_item` / `inventory_text` / `item_detail_text` | 876 | 技能切换、装备、背包和详情 |
| `_ensure_martial_fragments` / `compose_martial_fragments` / `_settle_martial_fragments_to_meta` / `martial_text` / `learn_martial_skill` | 2692 | 武学残页计数、中阶残页向顶级残页合成、结算入局外并解锁绝学、武学领悟面板 |
| `sect_list_text` / `sect_detail_text` / `_trait_description` / `opening_text` | 1078 | 门派和开局展示 |
| `_floor_atmosphere` / `_door_hints` / `_door_numbers_text` / `floor_square_text` / `command_hint_text` | 1303 | 楼层广场与命令提示 |
| `open_door` / `explore_door` | 1551 | 踢门和探索入口；第 7 层进入武神镜像或真·武神 |
| `_battle` / `combat_attack` / `combat_flee` / `combat_defend` / `_enemy_turn` / `_end_combat` / `decline_true_wushen` | 1754 | 回合制战斗主流程、MP 0 行动限制、逃跑结算、真·武神抉择 |
| `_selected_combat_skill` / `_run_turn_combat` / `_martial_damage_result` / `_damage_with_trait_bonus` | 2307 | 武学选择与伤害计算 |
| `_post_combat_recovery` / `_maybe_equipment_drop` / `_return_to_floor_square` | 2396 | 战后恢复、掉落、回广场 |
| `_chest` / `_encounter` / `_sect_encounter_skill_reward` | 2446 | 宝箱、奇遇、门派进阶武学 |
| `_trap_start` / `trap_dodge` / `trap_block` / `trap_counter` | 2625 | 陷阱状态机 |
| `_merchant` / `_create_merchant_backpack_offer` / `_create_merchant_equipment_offer` | 2818 | 商人门报价 |
| `next_floor` / `boss_fight` | 2895 | 楼层推进与 Boss |
| `fish` / `_select_fishing_pool` / `_select_fishing_loot` | 3022 | 钓鱼 |
| `use_consumable` / `discard_item` / `pickup_item` | 3153 | 使用、丢弃、拾取 |
| `buy_merchant_equipment` / `sell_equipment` / `buy_backpack` | 3269 | 商店交易 |
| `help_text` / `format_attrs` | 3353 | 帮助与属性格式 |

## 数据对象索引

`game_data.py` 主要对象：

| 对象 | 行 | 用途 |
| --- | ---: | --- |
| `Sect` | 19 | 门派数据类；`main_attr` 返回最高属性 |
| `ABILITY_ROWS` / `ATTR_LABELS` | 6 | 六维属性标签 |
| `SECT_ROWS` / `SECTS` | 32 | 16 门派基础数据 |
| `SECT_TRAIT_ROWS` / `SECT_TRAITS_BY_SECT` | 52 | 门派特质 |
| `SECT_FLOOR_RECOVERY_ROWS` / `SECT_FLOOR_RECOVERY_RULES` | 72 | 楼层恢复文案与数值 |
| `PLAYER_START_ROWS` / `PLAYER_START` | 111 | 开局 HP/MP/碎银/药品 |
| `DIFFICULTY_ROWS` / `DIFFICULTIES` | 122 | 普通/困难/炼狱；敌人增幅、战斗/非战斗 MP 恢复、残页掉落；炼狱需本门困难通关解锁 |
| `ENCOUNTER_TYPE_ROWS` / `EVENT_WEIGHTS` | 129 | 事件类型权重 |
| `ENCOUNTER_RULE_ROWS` / `ENCOUNTER_RULES` | 141 | 事件收益/损失规则 |
| `MARTIAL_ART_SKILL_ROWS` / `ULTIMATE_MARTIAL_ART_SKILL_ROWS` / `LEGENDARY_MARTIAL_ART_SKILL_ROWS` / `MARTIAL_ART_SKILLS` | 174 | 进阶武学、门派局外顶级绝学、通用传说绝学 |
| `SKILL_COMBAT_ROWS` / `SKILL_COMBAT_BY_NAME` | 212 | 战斗武学 |
| `STATUS_ROWS` / `STATUS_EFFECTS` | 251 | 状态效果 |
| `EQUIPMENT_ROWS` / `EQUIPMENT_BY_ID` / `EQUIPMENT_BY_NAME` | 260 | 装备 |
| `ENEMY_ROWS` / `ENEMIES_BY_FLOOR` | 293 | 普通敌人 |
| `BOSS_ROWS` / `BOSSES` / `BOSS_CLEAR_REWARDS` | 306 | 武神镜像、真·武神与通关奖励 |
| `LEVEL_UP_XP` / `LEVEL_UP_BONUS` | 321 | 经验升级 |
| `BACKPACK_ROWS` / `BACKPACKS` | 370 | 背囊 |
| `META_UPGRADE_ROWS` / `META_UPGRADES` / `META_UPGRADE_ALIASES` | 380 | 局外强化 |
| `FISHING_POOL_ROWS` / `FISHING_POOLS` / `BAITS` / `FISHING_LOOT_ROWS` | 427 | 钓鱼 |
| `DOOR_TYPE_HINTS` / `FLOOR_FLAVOR` / `COMBAT_FLAVOR` / `EVENT_FLAVOR` | 470 | 场景文案 |
| `ITEM_DESC` / `EQUIPMENT_DESC` | 530 | 详情描述 |

## UI 与存储索引

`ui.py`：

| 方法/对象 | 行 | 作用 |
| --- | ---: | --- |
| `SECT_BASIC_SKILLS` / `SKILL_MP_COST` | 14 | UI 状态栏技能显示辅助 |
| `SCENE_META` | 146 | 场景标题、背景图、强调色 |
| `infer_scene` | 164 | 由文本推断卡片场景 |
| `render_card_image` | 189 | 生成卡片图片主函数 |
| `_draw_status_bar` / `_draw_decor_corner` / `_get_line_style` | 489 | 绘图辅助 |
| `_parse_player_status` / `_build_player_info_from_object` / `_filter_content_lines` | 518 | 玩家状态提取与正文过滤 |
| `_player_skill_names` | 701 | UI 展示技能名 |
| `_load_background` / `_load_font` / `_wrap_text` | 716 | 背景、字体、换行 |
| `_split_hint` / `_plain_body_lines` | 798 | 正文和命令提示拆分 |

`storage.py`：

| 方法 | 行 | 作用 |
| --- | ---: | --- |
| `JsonStore.__init__` | 9 | 绑定 JSON 路径并创建父目录 |
| `load_all` | 13 | 读取所有用户档案 |
| `save_all` | 22 | 写回 JSON |
| `get_player` | 25 | 读取单用户 |
| `put_player` | 30 | 保存单用户 |
| `delete_player` | 35 | 删除单用户 |

## 常见修改定位

| 需求 | 优先文件/方法 |
| --- | --- |
| 新增命令 | `main.py` 增加 `cmd_*`，`web_runtime.py` 增加命令 key 与处理分支 |
| 改踢门概率 | `game_data.py` 的 `ENCOUNTER_TYPE_ROWS` / `EVENT_WEIGHTS` |
| 改战斗平衡 | `engine.py` 战斗方法 + `game_data.py` 敌人/武学/装备表 |
| 改门派 | `game_data.py` 的 `SECT_ROWS`、`SECT_TRAIT_ROWS`、相关武学表 |
| 改背包 | `engine.py` 背包方法 + `game_data.py` `BACKPACK_ROWS` / `INVENTORY_POLICY_ROWS` |
| 改钓鱼 | `engine.py` `fish` 相关 + `game_data.py` 钓鱼表 |
| 改卡片 UI | `ui.py` |
| 改本地测试页面 | `web/static/index.html`、`web/static/app.js`、`web/static/styles.css` |
