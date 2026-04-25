# 文案啥的放这
# 无理由判断list
no_reason = ["无理由", "None", "NULL"]
# command语法
commands = {
    "ban": "/ban <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]",
    "ban-all": "/ban-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]",
    "pass": "/pass <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]",
    "pass-all": "/pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]",
    "ban-enable": "/ban-enable",
    "ban-disable": "/ban-disable",
    "banlist": "/banlist",
    "ban-help": "/ban-help",
    "dec-ban": "/dec-ban <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]",
    "dec-pass": "/dec-pass <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]",
    "dec-ban-all": "/dec-ban-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]",
    "dec-pass-all": "/dec-pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]",
    "ban-reset": "/ban-reset",
}
# 输出文案
messages = {
    "command_error": "语法错误，{command} 的语法应为 {commands_text}",
    "time_zeroset_error": "{command} 已被设置永久时限，不支持叠加操作",
    "banned_user": "已在 {umo} 禁用以下用户 {user}，时限：{time}，理由：{reason}",
    "banned_user_global": "已全局禁用 {user}，时限：{time}，理由：{reason}",
    "passed_user": "已在 {umo} 临时解限 {user}，时限：{time}，理由：{reason}",
    "passed_user_global": "已在全局临时解限 {user}，时限：{time}，理由：{reason}",
    "dec_banned_user": "已删除在 {umo} 对 {user} 的禁用（{time}），理由：{reason}",
    "dec_banned_user_global": "已删除全局对 {user} 的禁用（{time}），理由：{reason}",
    "dec_passed_user": "已删除在 {umo} 对 {user} 的临时解限（{time}），理由：{reason}",
    "dec_passed_user_global": "已删除全局对 {user} 的临时解限（{time}），理由：{reason}",
    "dec_no_record": "未找到记录，可能是因为该用户的记录已过期，无需删除",
    "dec_zerotime_error": "无法删除，因为该用户的记录时限被设为永久，请设置删除时间为0以强制删除！",
    "group_banned_list": "本群禁用的用户:",
    "no_group_banned": "\n本群没有禁用用户呢！",
    "global_banned_list": "全局禁用的用户:",
    "no_global_banned": "\n全局没有禁用用户",
    "group_passed_list": "本群临时解限用户：",
    "no_group_passed": "\n本群没有临时解限用户呢！",
    "no_reason": "无理由",
    "global_passed_list": "全局临时解限用户：",
    "no_global_passed": "\n全局没有临时解限用户",
    "banlist_strlist_format": "\n - {user} - {time} - {reason}",
    "ban_reset_success": "已清除用户 {user} 的所有记录。",
    "ban_enabled": "已临时启用禁用功能～重启后失效",
    "ban_disabled": "已临时禁用禁用功能～重启后失效",
    "temp_msg_blocked": "[reneban] 临时会话拦截：{uid} 的临时会话已被屏蔽",
    "help_text": f"""黑名单插件使用指南：

🌸 基础命令：
{commands["ban-help"]} - 查看这份指南

🚫 限制命令：
{commands["ban"]} - 在会话限制用户（若会话内已存在限制，则叠加）
{commands["ban-all"]} - 全局限制用户（若全局已存在限制，则叠加）
{commands["dec-ban"]} - 删除在会话对用户禁用的时限
{commands["dec-ban-all"]} - 删除全局对用户禁用的时限

🎀 解限命令：
{commands["pass"]} - 解除当前会话限制（允许临时解限，若已有解除时限，则叠加）
{commands["pass-all"]} - 解除全局限制（允许临时解限，若已有解除时限，则叠加）
{commands["dec-pass"]} - 删除在会话对用户临时解限的时限
{commands["dec-pass-all"]} - 删除全局对用户临时解限的时限
{commands["ban-reset"]} - 删除一名指定用户的所有记录

📒 查询命令：
{commands["banlist"]} - 查看当前限制名单

⚙️ 功能控制：
{commands["ban-enable"]} - 启用限制功能
{commands["ban-disable"]} - 停用限制功能

⏰ 时间格式说明：
- 数字+单位：1d(1天)/2h(2小时)/30m(30分钟)/10s(10秒)
- 默认永久限制

💡 注意事项：
- 只有管理员可以操作
- 永久限制/永久解除限制不支持叠加
- 群内设置优先于全局设置
- 过期限制会自动清理""",
}
