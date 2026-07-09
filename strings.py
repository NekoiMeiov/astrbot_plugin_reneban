# 无理由判断list
_no_reason = ["无理由", "None", "NULL"]


def noreason_to_none(reason: str | None) -> str | None:
    if reason in _no_reason:
        return None
    return reason


def command_error(command: str) -> str:
    return messages["command_error"].format(
        command=command, commands_text=commands[command]
    )


def reason_format(reason: str | None) -> str:
    if noreason_to_none(reason):
        return reason
    else:
        return messages["no_reason"]


# command语法，通常不会修改
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
    "ban-reset": "/ban-reset <@用户|UID（QQ号）>",
    "ban-umo": "/ban-umo <UMO> [时间（默认无期限）] [理由（默认无理由）]",
    "pass-umo": "/pass-umo <UMO> [时间（默认无期限）] [理由（默认无理由）]",
    "dec-ban-umo": "/dec-ban-umo <UMO> [时间（默认无期限）] [理由（默认无理由）]",
    "dec-pass-umo": "/dec-pass-umo <UMO> [时间（默认无期限）] [理由（默认无理由）]",
    "ban-reset-umo": "/ban-reset-umo <UMO>",
}
# 默认输出文案
messages = {
    "command_error": "语法错误，{command} 的语法应为 {commands_text}",
    "invalid_timestr_error": "时间字符串 {timestr} 格式错误，请使用数字+单位，如：1d3m51s",
    "time_zeroset_error": "相应的 {command} 记录已被设置为永久时限，不支持叠加操作",
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
    "banned_umo": "已禁用会话 {umo}，时限：{time}，理由：{reason}",
    "passed_umo": "已临时解限会话 {umo}，时限：{time}，理由：{reason}",
    "dec_banned_umo": "已删除对会话 {umo} 的禁用（{time}），理由：{reason}",
    "dec_passed_umo": "已删除对会话 {umo} 的临时解限（{time}），理由：{reason}",
    "group_banned_list": "本群禁用的用户:",
    "no_group_banned": "\n本群没有禁用用户呢！",
    "group_passed_list": "本群临时解限用户：",
    "no_group_passed": "\n本群没有临时解限用户呢！",
    "global_banned_list": "全局禁用的用户:",
    "no_global_banned": "\n全局没有禁用用户",
    "global_passed_list": "全局临时解限用户：",
    "no_global_passed": "\n全局没有临时解限用户",
    "umo_banned_list": "禁用的会话：",
    "no_umo_banned": "\n没有禁用的会话呢！",
    "umo_passed_list": "临时解限的会话：",
    "no_umo_passed": "\n没有临时解限会话呢！",
    "no_reason": "无理由",
    "banlist_strlist_format": "\n - {id} - {time} - {reason}",
    "ban_reset_success": "已清除用户 {user} 的所有记录。",
    "ban_reset_umo_success": "已清除会话 {umo} 的所有记录。",
    "ban_enabled": "已临时启用禁用功能～重启后失效",
    "ban_disabled": "已临时禁用禁用功能～重启后失效",
    "help_text": f"""黑名单插件使用指南：

🌸 基础命令：
{commands["ban-help"]} - 查看这份指南

🚫 限制命令：
{commands["ban"]} - 在会话限制用户（若会话内已存在限制，则叠加）
{commands["ban-all"]} - 全局限制用户（若全局已存在限制，则叠加）
{commands["ban-umo"]} - 限制指定会话（若会话已存在限制，则叠加）
{commands["dec-ban"]} - 删除在会话对用户禁用的时限
{commands["dec-ban-all"]} - 删除全局对用户禁用的时限
{commands["dec-ban-umo"]} - 删除对指定会话的禁用的时限

🎀 解限命令：
{commands["pass"]} - 解除当前会话限制（允许临时解限，若已有解除时限，则叠加）
{commands["pass-all"]} - 解除全局限制（允许临时解限，若已有解除时限，则叠加）
{commands["pass-umo"]} - 解除指定会话限制（允许临时解限，若已有解除时限，则叠加）
{commands["dec-pass"]} - 删除在会话对用户临时解限的时限
{commands["dec-pass-all"]} - 删除全局对用户临时解限的时限
{commands["dec-pass-umo"]} - 删除对指定会话的临时解限的时限
{commands["ban-reset"]} - 删除一名指定用户的所有记录
{commands["ban-reset-umo"]} - 删除指定会话的所有记录

📒 查询命令：
{commands["banlist"]} - 查看当前限制名单

⚙️ 功能控制：
{commands["ban-enable"]} - 启用限制功能
{commands["ban-disable"]} - 停用限制功能

⏰ 时间格式说明：
- 数字+单位：1d(1天)/2h(2小时)/30m(30分钟)/10s(10秒)
- 若不填写或时长为 0，则为永久。

💡 注意事项：
- 只有管理员可以操作
- 永久限制/永久解除限制不支持叠加
- 群内设置优先于全局设置
- 过期限制会自动清理""",
}
