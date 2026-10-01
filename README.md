<div align="center">

# ReNeBan

_🚫 为 [astrbot](https://github.com/AstrBotDevs/AstrBot) 设计的简易黑名单插件 🚫_

[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
<br>
[![AstrBot](https://img.shields.io/badge/AstrBot-yellow.svg)](https://github.com/AstrBotDevs/AstrBot)
<br>
[![GitHub](https://img.shields.io/badge/NekoiMeiov__Team-orange.svg?style=for-the-badge)](https://github.com/NekoiMeiov)

</div>

## 介绍
ReNeBan 是一个为 [astrbot](https://github.com/AstrBotDevs/AstrBot) 设计的简易黑名单插件，允许bot管理员在**会话**或**全局**范围较为灵活地禁用指定用户。
ReNeBan 允许为**禁用/解禁**设置**时限**和**理由**，并自动整理记录。
ReNeBan 的指令优先级策略为：`局部优先`，`pass > ban`。

## 命令
| 命令 | 语法 | 说明 | 示例 |
|------|------|------|------|
| `/ban` | /ban <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO] | 在**指定会话**范围内禁用**一名指定用户** | /ban @AAA高价收游戏账号 0 打广告 |
| `/pass` | /pass <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO] | 在**指定会话**范围内解除禁用**一名指定用户** | /pass @yfseh218 0 None |
| `/ban-all` | /ban-all <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] | 在**全局**范围内禁用**一名指定用户** | /ban-all 2110453981 1d30m 试图让bot输出敏感内容 |
| `/pass-all` | /pass-all <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] | 在**全局**范围内解除禁用**一名指定用户** | /pass-all @我想不出来啥名了 0 误封 |
| `/ban-enable` | /ban-enable | 启用禁用功能，重启后失效 | /ban-enable |
| `/ban-disable` | /ban-disable | 禁用禁用功能，重启后失效 | /ban-disable |
| `/banlist` | /banlist | 输出在**当前会话**与**全局**范围下的**禁用/解禁**情况（包括**UID/剩余时长/理由**） | /banlist |
| `/ban-help` | /ban-help | 输出简易帮助信息 | /ban-help |
| `/dec-ban` | /dec-ban <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO] | 删除在**指定会话**范围内对**一名指定用户**的禁用时长 | /dec-ban @UserA 0 表现良好 |
| `/dec-pass` | /dec-pass <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO] | 删除在**指定会话**范围内对**一名指定用户**的解禁时长 | /dec-pass @UserB 0 None |
| `/dec-ban-all` | /dec-ban-all <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] | 删除在**全局**范围内对**一名指定用户**的禁用时长 | /dec-ban-all 3869541370 1d30m 表现良好 |
| `/dec-pass-all` | /dec-pass-all <@用户\|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] | 删除在**全局**范围内对**一名指定用户**的解禁时长 | /dec-pass-all @XYZ 0 NULL |
| `/ban-reset` | /ban-reset <@用户\|UID（QQ号）> | 删除**一名指定用户**的**所有**记录 | /ban-reset @NekoiMeiov |
| `/ban-umo` | /ban-umo \<UMO\> [时间（默认无期限）] [理由（默认无理由）] | 禁用**一个指定会话** | /ban-umo napcat:GroupMessage:1145141919 3d |
| `/pass-umo` | /pass-umo \<UMO\> [时间（默认无期限）] [理由（默认无理由）] | 解除禁用**一个指定会话** | /pass-umo napcat:GroupMessage:1145141919 12h |
| `/dec-ban-umo` | /dec-ban-umo \<UMO\> [时间（默认无期限）] [理由（默认无理由）] | 删除对**一个指定会话**的禁用时长 | /dec-ban-umo napcat:GroupMessage:1145141919 1d12h |
| `/dec-pass-umo` | /dec-pass-umo \<UMO\> [时间（默认无期限）] [理由（默认无理由）] | 删除**一个指定会话**的解禁时长 | /dec-pass-umo napcat:GroupMessage:1145141919 3h NULL |
| `/ban-reset-umo` | /ban-reset-umo \<UMO\> | 删除**一个指定会话**的**所有**记录 | /ban-reset-umo napcat:GroupMessage:1145141919 |

时间字段支持如下格式：

```text
- `1d` → 1 天
- `2h` → 2 小时
- `30m` → 30 分钟
- `10s`，`10` → 10 秒
```

输入时需按单位大小填写！不允许如`20m1h`的时间表达式！
若不填写时间字段或时间时长为 0，则为**无期限**。

以下理由将会被判定为无理由：
- `"无理由"`
- `"None"`
- `"NULL"`

## 语言

面板与插件配置界面支持 AstrBot 的全部四种语言：简体中文、English、日本語、Русский。

词表位于 `.astrbot-plugin/i18n/<locale>.json`，按 AstrBot 的约定分四个命名空间：

| 命名空间 | 用途 |
|---|---|
| `metadata` | 插件在插件页显示的名称（`display_name`）、卡片短描述（`short_desc`）与描述（`desc`） |
| `config.<配置项>` | `_conf_schema.json` 中的配置文案（`description` / `hint` / `labels`） |
| `pages.<页面目录>` | Dashboard Page 的标题与描述，以及页面内的自定义文案 |
| `errors.<键>` / `fields.<键>` | 本插件用于后端报错与字段名的文案 |

界面文案与后端报错共用同一份词表，切换语言后二者同时生效。新增语言只需在 `.astrbot-plugin/i18n/` 下增加对应 JSON 文件（嵌套结构，键名不含点号），代码无需改动。

> 说明：配置弹窗顶部的 `astrbot_plugin_reneban 配置` 取自插件模块名，AstrBot 不对其做 i18n 解析，因此无法翻译；插件列表中显示的名称走 `metadata.display_name`，可以翻译。

## 管理面板（Dashboard Page）

ReNeBan 自带一个 WebUI 管理页面，可在 **插件管理 → ReNeBan → Pages** 中打开「黑名单管理面板」。

它能做这些事：

- **指标带**：记录总数 / 禁用 / 解限 / 永久 / 24 小时内到期 / 涉及会话，每项带占比环与数字动画
- **未来 7 天到期热力**：列＝日期、行＝当天时段（每格 3 小时），颜色越深表示该时段到期越集中，点格子可定位到记录
- **到期分布**：按剩余时长分桶的堆叠柱状图（≤1 小时 / 1–6 小时 / 6–24 小时 / 1–3 天 / 3–7 天 / >7 天），永久记录单独标注
- **禁用 / 解限构成**：环形图与占比明细
- **即将到期**：按到期时间排序，超过一天会额外显示具体日期
- **洞察**：最近到期记录、记录最多的用户、限制最多的会话
- **分类视图**：全局记录、会话记录（会话内被禁用的用户）、会话级记录（整个会话被禁用/解限）、会话列表
- **筛选与搜索**：按范围、类型、时限过滤，支持按用户 ID、会话名、UMO、理由搜索，表格/卡片两种视图，点表头排序
- **管理操作**：新增禁用或解限（支持 `1h`/`1d`/`7d`/`30d`/永久 快捷时长）、延长或缩短剩余时长、删除单条记录、清除某用户或某会话的全部记录
- **运行开关**：顶部开关等同于 `/ban-enable` 与 `/ban-disable`（仅本次运行有效，重启后恢复配置值）
- 剩余时长按秒实时倒计时，30 天内以进度条呈现，1 小时内与 24 小时内分别高亮

配色采用「分层用色」：主色为靛蓝，禁用与解限用低饱和度的暗梅与青玉，而暖红只留给「一小时内即将到期」——也就是说，页面上一旦出现红色，就代表需要立刻处理。柱状图、环形图、热力条使用品牌色序列而非状态色填充，避免数据主体把整页染成警告色。亮色与暗色是两套独立调色，跟随 WebUI 主题切换。

剩余时长按秒实时倒计时，越接近到期颜色越暖（>24 小时为中性、≤24 小时为琥珀、≤1 小时为红）。

页面通过 AstrBot 的 Pages bridge 调用插件注册的后端接口，运行在受限 iframe 中，不依赖任何外部字体、图标或 CDN，离线实例也能正常渲染。

> 关于「解限」的一条插件规则：解限记录必须对应一条已存在的禁用记录，否则会在写入时被自动清理。因此如果目标用户/会话当前并未被禁用，面板会直接提示，而不是写一条立刻消失的记录。

## 安装

- 从插件市场安装

在 插件管理 - 插件市场 搜索 ReNeBan

- 从链接安装

在 插件管理 - 安装 - 从链接安装 输入以下链接
``` text
https://github.com/NekoiMeiov/astrbot_plugin_reneban
```

- 从源码安装

在终端中输入以下命令（若为手动安装，请将 /AstrBot 修改为手动安装的路径）
```bash
# 克隆仓库到插件目录
cd /AstrBot/data/plugins
git clone https://github.com/NekoiMeiov/astrbot_plugin_reneban

# 控制台重启AstrBot
```

## 贡献指南

- 给...给这个Repo点个Star（不...不给也可以......）
- 提交 Issue 报告问题/提出建议
- 提交 Pull Request 改进