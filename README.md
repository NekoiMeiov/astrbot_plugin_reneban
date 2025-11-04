## 注意！
ReNeBan 插件目前仅通过 PoC（概念验证），功能会持续迭代。若您在迭代期间需要取消一个时长被设定为永久的命令，请操作插件数据目录中的相应json文件。

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
ReNeBan 的指令优先级策略为：`pass > ban`，`会话 > 全局`。

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

时间字段支持如下格式：

```text
- `1d` → 1 天
- `2h` → 2 小时
- `30m` → 30 分钟
- `10s` → 10 秒
- `0` → 永久（默认，且不支持与以上单位复用）
```

输入时需按单位大小填写！不允许如`20m1h`的时间表达式！

以下理由将会被判定为无理由：
- `"无理由"`
- `"None"`
- `"NULL"`

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