# pass > ban > pass-all > ban-all
"""
Todo:
    clear_redundant_banned()
    ...
"""
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, StarTools
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
import json
import time as time_module
import re

class AtNumberError(ValueError):
    """
    At 数量错误（ReNeBan.get_event_at() 获取@用户时，如果 At 用户数量大于 1，会抛出此错误）
    """
    pass

class ReNeBan(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        # 从插件配置中获取是否启用禁用功能，默认为启用
        self.enable = config.get('enable', True)
        # 持久化存储，使用StarTools获取数据目录
        self.banlist_path = StarTools.get_data_dir() / "ban_list.json"
        self.banall_list_path = StarTools.get_data_dir() / "banall_list.json"
        self.passlist_path = StarTools.get_data_dir() / "passlist.json"
        self.passall_list_path = StarTools.get_data_dir() / "passall_list.json"

        for path in [
            self.banlist_path,
            self.passlist_path,
        ]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text('{}', encoding='utf-8')
        for path in [
            self.banall_list_path,
            self.passall_list_path,
        ]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text('[]', encoding='utf-8')

        # 无理由判断list
        self.no_reason = [
            "无理由",
            "None",
            "NULL"
        ]
        # command语法
        self.commands = {
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
            "dec-pass-all": "/dec-pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]"
        }
        # 输出文案
        self.messages = {
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
            "passed_all": "已解除对 {users} 的所有限制，理由：{reason}",
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
            "ban_enabled": "已临时启用禁用功能～重启后失效",
            "ban_disabled": "已临时禁用禁用功能～重启后失效",
            "help_text": f"""黑名单插件使用指南：

🌸 基础命令：
{self.commands['ban-help']} - 查看这份指南

🚫 限制命令：
{self.commands['ban']} - 在会话限制用户（若会话内已存在限制，则叠加）
{self.commands['ban-all']} - 全局限制用户（若全局已存在限制，则叠加）
{self.commands['dec-ban']} - 删除在会话对用户禁用的时限
{self.commands['dec-ban-all']} - 删除全局对用户禁用的时限

🎀 解限命令：
{self.commands['pass']} - 解除当前会话限制（允许临时解限，若已有解除时限，则叠加）
{self.commands['pass-all']} - 解除全局限制（允许临时解限，若已有解除时限，则叠加）
{self.commands['dec-pass']} - 删除在会话对用户临时解限的时限
{self.commands['dec-pass-all']} - 删除全局对用户临时解限的时限

📒 查询命令：
{self.commands['banlist']} - 查看当前限制名单

⚙️ 功能控制：
{self.commands['ban-enable']} - 启用限制功能
{self.commands['ban-disable']} - 停用限制功能

⏰ 时间格式说明：
- 数字+单位：1d(1天)/2h(2小时)/30m(30分钟)/10s(10秒)
- 默认永久限制

💡 注意事项：
- 只有管理员可以操作
- 永久限制/永久解除限制不支持叠加
- 群内设置优先于全局设置
- 过期限制会自动清理"""
        }

    def clear_expired_banned(self):
        """
        清除过期的禁用列表。
        Ver PoC_0.1.0
        """
        # clear_passlist
        passlist_rawdata = self.passlist_path.read_text(encoding="utf-8")
        passlist_data = json.loads(passlist_rawdata)
        # 遍历umo
        for umo, umo_list in passlist_data.items():
            for umo_list_item in umo_list:
                if umo_list_item.get('time') < int(time_module.time()) and umo_list_item.get('time') != 0:
                    passlist_data[umo].remove(umo_list_item)
        # 保存
        self.passlist_path.write_text(json.dumps(passlist_data, indent=4, ensure_ascii=False), encoding="utf-8")
        # clear_banlist
        banlist_rawdata = self.banlist_path.read_text(encoding="utf-8")
        banlist_data = json.loads(banlist_rawdata)
        for umo, umo_list in banlist_data.items():
            for umo_list_item in umo_list:
                if umo_list_item.get('time') < int(time_module.time()) and umo_list_item.get('time') != 0:
                    banlist_data[umo].remove(umo_list_item)
        self.banlist_path.write_text(json.dumps(banlist_data, indent=4, ensure_ascii=False), encoding="utf-8")
        # clear_banall_list
        banall_rawdata = self.banall_list_path.read_text(encoding="utf-8")
        banall_data = json.loads(banall_rawdata)
        for item in banall_data:
            if item.get('time') < int(time_module.time()) and item.get('time') != 0:
                banall_data.remove(item)
        self.banall_list_path.write_text(json.dumps(banall_data, indent=4, ensure_ascii=False), encoding="utf-8")
        # clear_passall_list
        passall_rawdata = self.passall_list_path.read_text(encoding="utf-8")
        passall_data = json.loads(passall_rawdata)
        for item in passall_data:
            if item.get('time') < int(time_module.time()) and item.get('time') != 0:
                passall_data.remove(item)
        self.passall_list_path.write_text(json.dumps(passall_data, indent=4, ensure_ascii=False), encoding="utf-8")
        return

    def clear_redundant_banned(self):
        """
        清除冗余的禁用列表。
        Ver None
        """
        pass
        # # load ban-all
        # banall_rawdata = self.banall_list_path.read_text(encoding="utf-8")
        # banall_data = json.loads(banall_rawdata) # type: list[dict]
        # # load pass-all
        # passall_rawdata = self.passall_list_path.read_text(encoding="utf-8")
        # passall_data = json.loads(passall_rawdata) # type: list[dict]
        # # load ban
        # ban_rawdata = self.banlist_path.read_text(encoding="utf-8")
        # ban_data = json.loads(ban_rawdata) # type: dict
        # # load pass
        # pass_rawdata = self.passlist_path.read_text(encoding="utf-8")
        # pass_data = json.loads(pass_rawdata) # type: dict

    def clear_banned(self):
        """
        清除禁用列表。
        Ver PoC_0.1.0
        """
        self.clear_expired_banned()
        self.clear_redundant_banned()

    def is_banned(self, event: AstrMessageEvent) -> tuple[bool, str | None]:
        """
        判断用户是否被禁用，以及其理由
        """
        # 禁用功能未启用
        if not self.enable:
            return (False, None)
        # pass > ban > pass-all > ban-all
        self.clear_banned()
        # 获取UMO
        umo = event.unified_msg_origin
        # pass
        # 打开self.passlist_path，取umo对应的list
        tmpdata = self.passlist_path.read_text(encoding='utf-8')
        passlist = json.loads(tmpdata)
        # 如果不存在则返回空列表
        umo_pass_list = passlist.get(umo) if isinstance(passlist.get(umo), list) else []
        # 遍历umo_pass_list中字典对象的ban_uid键
        for item in umo_pass_list:
            if item.get('uid') == event.get_sender_id():
                return (False, item.get('reason'))
        # ban
        # 打开self.banlist_path，取umo对应的list
        tmpdata = self.banlist_path.read_text(encoding='utf-8')
        banlist = json.loads(tmpdata)
        # 如果不存在则返回空列表
        umo_ban_list = banlist.get(umo) if isinstance(banlist.get(umo), list) else []
        # 遍历umo_ban_list中字典对象的ban_uid键
        for item in umo_ban_list:
            if item.get('uid') == event.get_sender_id():
                return (True, item.get('reason'))
        # pass-all
        # 打开self.passall_list_path
        tmpdata = self.passall_list_path.read_text(encoding='utf-8')
        passall_list = json.loads(tmpdata)
        # 遍历passall_list中字典对象的ban_uid键
        for item in passall_list:
            if item.get('uid') == event.get_sender_id():
                return (False, item.get('reason'))
        # ban-all
        # 打开self.banall_list_path
        tmpdata = self.banall_list_path.read_text(encoding='utf-8')
        banall_list = json.loads(tmpdata)
        # 遍历banall_list中字典对象的ban_uid键
        for item in banall_list:
            if item.get('uid') == event.get_sender_id():
                return (True, item.get('reason'))
        return (False, None)

    def timelast_format(self, time_last: int) -> str:
        """
        将剩余秒数格式化为易读的时间描述
        """
        if time_last < 0:
            return "已过期"
        if time_last == 0:
            return "永久"
        
        # 按照从大到小的单位进行转换
        days = time_last // 86400
        hours = (time_last % 86400) // 3600
        minutes = (time_last % 3600) // 60
        seconds = time_last % 60
        
        # 构建易读的时间描述
        result = ["剩余"]
        if days > 0:
            result.append(f"{days}天")
        if hours > 0:
            result.append(f"{hours}小时")
        if minutes > 0:
            result.append(f"{minutes}分钟")
        if seconds > 0 or not result:
            result.append(f"{seconds}秒")
            
        return "".join(result)

    def time_format(self, time_str: str) -> str:
        """
        将时间字符串格式化为易读的时间描述
        """
        if time_str == "0":
            return "永久"
        time = self.timestr_to_int(time_str)
        
        # 按照从大到小的单位进行转换
        days = time // 86400
        hours = (time % 86400) // 3600
        minutes = (time % 3600) // 60
        seconds = time % 60
        
        # 构建易读的时间描述
        result = []
        if days > 0:
            result.append(f"{days}天")
        if hours > 0:
            result.append(f"{hours}小时")
        if minutes > 0:
            result.append(f"{minutes}分钟")
        if seconds > 0 or not result:
            result.append(f"{seconds}秒")
            
        return "".join(result)

    def timestr_to_int(self, timestr: str) -> int:
        """
        将时间字符串（如 1d2h3m4）转换为秒数
        """
        # ^(?=.*\d)(?:(?<days>\d+)d)?(?:(?<hours>\d+)h)?(?:(?<minutes>\d+)m)?(?:(?<seconds>\d+)s?)$
        m = re.compile(r'^(?=.*\d)(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s?)?$').fullmatch(timestr)
        if not m:
            raise ValueError(f'非法的时间字符串格式: {timestr!r}')

        # 命名捕获组一次性全取到，None 的转成 0
        parts = {k: int(v or 0) for k, v in m.groupdict().items()}
        return (
            parts['days'] * 86400
            + parts['hours'] * 3600
            + parts['minutes'] * 60
            + parts['seconds']
        )

    def get_event_at(self, event: AstrMessageEvent) -> str | None:
        """
        获取at的用户uid
        """
        # 获取所有非自身的 At 用户
        at_users = [
            str(seg.qq)
            for seg in event.get_messages()
            if isinstance(seg, Comp.At) and str(seg.qq) != event.get_self_id()
        ]

        # 如果 At 用户数量大于 1，则抛出错误
        if len(at_users) > 1:
            raise AtNumberError("消息中包含多个非bot自身的 At 标记")

        # 返回第一个（也是唯一一个）At 用户，如果没有则返回 None
        return at_users[0] if at_users else None
    @filter.command("banlist")
    async def banlist(self, event: AstrMessageEvent):
        """
        显示当前群禁用名单
        """
        # 禁用功能未启用
        if not self.enable:
            group_banned_text = self.messages["group_banned_list"] + self.messages["no_group_banned"]
            global_banned_text = self.messages["global_banned_list"] + self.messages["no_global_banned"]
            group_passed_text = self.messages["group_passed_list"] + self.messages["no_group_passed"]
            global_passed_text = self.messages["global_passed_list"] + self.messages["no_global_passed"]
            result = f"{group_banned_text}\n\n{global_banned_text}\n\n{group_passed_text}\n\n{global_passed_text}"
            yield event.plain_result(result)
            return
        self.clear_banned()
        # 获取UMO
        umo = event.unified_msg_origin
        # get_pass
        tmpdata = self.passlist_path.read_text(encoding='utf-8')
        passlist = json.loads(tmpdata)
        group_passed_list = passlist.get(umo) if isinstance(passlist.get(umo), list) else []
        # get_pass-all
        tmpdata = self.passall_list_path.read_text(encoding='utf-8')
        global_passed_list = json.loads(tmpdata)
        # get_ban-all
        tmpdata = self.banall_list_path.read_text(encoding='utf-8')
        global_banned_list = json.loads(tmpdata)
        # get_ban
        tmpdata = self.banlist_path.read_text(encoding='utf-8')
        banlist = json.loads(tmpdata)
        group_banned_list = banlist.get(umo) if isinstance(banlist.get(umo), list) else []
        group_banned_str_list = [
            self.messages["banlist_strlist_format"].format(
                user=item.get('uid'),
                time=self.timelast_format((item.get('time')-int(time_module.time())) if item.get('time') != 0 else 0),
                reason=item.get('reason') if item.get('reason') else self.messages["no_reason"]
            )
            for item in group_banned_list
        ]
        if not group_banned_str_list:
            group_banned_str_list.append(self.messages["no_group_banned"])
        global_banned_str_list = [
            self.messages["banlist_strlist_format"].format(
                user=item.get('uid'),
                time=self.timelast_format((item.get('time')-int(time_module.time())) if item.get('time') != 0 else 0),
                reason=item.get('reason') if item.get('reason') else self.messages["no_reason"]
            )
            for item in global_banned_list
        ]
        if not global_banned_str_list:
            global_banned_str_list.append(self.messages["no_global_banned"])
        group_passed_str_list = [
            self.messages["banlist_strlist_format"].format(
                user=item.get('uid'),
                time=self.timelast_format((item.get('time')-int(time_module.time())) if item.get('time') != 0 else 0),
                reason=item.get('reason') if item.get('reason') else self.messages["no_reason"]
            )
            for item in group_passed_list
        ]
        if not group_passed_str_list:
            group_passed_str_list.append(self.messages["no_group_passed"])
        global_passed_str_list = [
            self.messages["banlist_strlist_format"].format(
                user=item.get('uid'),
                time=self.timelast_format((item.get('time')-int(time_module.time())) if item.get('time') != 0 else 0),
                reason=item.get('reason') if item.get('reason') else self.messages["no_reason"]
            )
            for item in global_passed_list
        ]
        if not global_passed_str_list:
            global_passed_str_list.append(self.messages["no_global_passed"])

        group_banned_text = self.messages["group_banned_list"] + "".join(group_banned_str_list)
        global_banned_text = self.messages["global_banned_list"] + "".join(global_banned_str_list)
        group_passed_text = self.messages["group_passed_list"] + "".join(group_passed_str_list)
        global_passed_text = self.messages["global_passed_list"] + "".join(global_passed_str_list)

        result = f"{group_banned_text}\n\n{global_banned_text}\n\n{group_passed_text}\n\n{global_passed_text}"
        yield event.plain_result(result)
    # def time_format(self, time_stamp: int) -> str:
    #     """
    #     将时间戳格式化为易读的日期时间字符串
    #     """
    #     if time_stamp == 0:
    #         return "永久"
        
    #     import datetime
    #     dt = datetime.datetime.fromtimestamp(time_stamp)
    #     return dt.strftime("%Y-%m-%d %H:%M:%S")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban-enable")
    async def ban_enable(self, event: AstrMessageEvent):
        """
        启用禁用功能
        """
        self.enable = True
        yield event.plain_result(self.messages["ban_enabled"])
        logger.warning(f"已临时启用禁用功能(In {event.unified_msg_origin} - {event.get_sender_name()}({event.get_sender_id()}))")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban-disable")
    async def ban_disable(self, event: AstrMessageEvent):
        """
        停用禁用功能
        """
        self.enable = False
        yield event.plain_result(self.messages["ban_disabled"])
        logger.warning(f"已临时禁用禁用功能(In {event.unified_msg_origin} - {event.get_sender_name()}({event.get_sender_id()}))")

    @filter.command("ban-help")
    async def ban_help(self, event: AstrMessageEvent):
        """
        显示reneban帮助信息
        """
        yield event.plain_result(self.messages["help_text"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban")
    async def ban_user(self, event: AstrMessageEvent, banuser: str, time: str = "0", reason: str | None = None ,umo: str | None = None, end: str | None = None):
        """
        在会话中禁用指定用户的使用权限。
        格式：/ban <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/ban @张三 7d
        注意：单次仅能禁用一个会话的一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="ban",commands_text=self.commands["ban"]))
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        # 我没法了（（（
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="ban",commands_text=self.commands["ban"]))
            return
        # 准备ban_user
        self.clear_banned()
        tmpdata = self.banlist_path.read_text(encoding='utf-8')
        banlist = json.loads(tmpdata)
        if not isinstance(banlist.get(umo), list):
            banlist[umo] = []
        group_banned_list = banlist.get(umo)
        tempbool = False
        for item in group_banned_list:
            if item.get('uid') == ban_uid:
                if item.get('time') == 0:
                    yield event.plain_result(self.messages["time_zeroset_error"].format(command="ban"))
                    return
                else:
                    item['time'] = (item['time'] + self.timestr_to_int(time)) if time != "0" else 0
                    item['reason'] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            group_banned_list.append({
                'uid': ban_uid,
                'time': (int(time_module.time()) + self.timestr_to_int(time)) if time != "0" else 0,
                'reason': reason
            })
        logger.warning(f"[ban]{json.dumps(banlist, indent=4, ensure_ascii=False)}")
        self.banlist_path.write_text(json.dumps(banlist, indent=4, ensure_ascii=False), encoding='utf-8')
        yield event.plain_result(self.messages["banned_user"].format(umo=umo, user=ban_uid, time=self.time_format(time), reason=reason))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban-all")
    async def ban_all(self, event: AstrMessageEvent, banuser: str, time: str = "0", reason: str | None = None, end: str | None = None):
        """
        在全局禁用指定用户的使用权限。
        格式：/ban-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/ban-all @张三 7d
        注意：单次仅能禁用一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="ban-all",commands_text=self.commands["ban-all"]))
            return
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="ban-all",commands_text=self.commands["ban-all"]))
            return
        self.clear_banned()
        tmpdata = self.banall_list_path.read_text(encoding='utf-8')
        banall_list = json.loads(tmpdata)
        tempbool = False
        for item in banall_list:
            if item.get('uid') == ban_uid:
                if item.get('time') == 0:
                    yield event.plain_result(self.messages["time_zeroset_error"].format(command="ban-all"))
                    return
                else:
                    item['time'] = (item['time'] + self.timestr_to_int(time)) if time != "0" else 0
                    item['reason'] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            banall_list.append({
                'uid': ban_uid,
                'time': (int(time_module.time()) + self.timestr_to_int(time)) if time != "0" else 0,
                'reason': reason
            })
        logger.warning(f"[ban-all]{json.dumps(banall_list, indent=4, ensure_ascii=False)}")
        self.banall_list_path.write_text(json.dumps(banall_list, indent=4, ensure_ascii=False), encoding='utf-8')
        yield event.plain_result(self.messages["banned_user_global"].format(user=ban_uid, time=self.time_format(time), reason=reason))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("pass")
    async def pass_user(self, event: AstrMessageEvent, passuser: str, time: str = "0", reason: str | None = None ,umo: str | None = None, end: str | None = None):
        """
        在会话中解限指定用户。
        格式：/pass <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/pass @张三 7d
        注意：单次仅能解限一个会话的一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="pass",commands_text=self.commands["pass"]))
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="pass",commands_text=self.commands["pass"]))
            return
        self.clear_banned()
        tmpdata = self.passlist_path.read_text(encoding='utf-8')
        passlist = json.loads(tmpdata)
        if not isinstance(passlist.get(umo), list):
            passlist[umo] = []
        group_passed_list = passlist.get(umo)
        tempbool = False
        for item in group_passed_list:
            if item.get('uid') == pass_uid:
                if item.get('time') == 0:
                    yield event.plain_result(self.messages["time_zeroset_error"].format(command="pass"))
                    return
                else:
                    item['time'] = (item['time'] + self.timestr_to_int(time)) if time != "0" else 0
                    item['reason'] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            group_passed_list.append({
                'uid': pass_uid,
                'time': (int(time_module.time()) + self.timestr_to_int(time)) if time != "0" else 0,
                'reason': reason
            })
        self.passlist_path.write_text(json.dumps(passlist, indent=4, ensure_ascii=False), encoding='utf-8')
        yield event.plain_result(self.messages["passed_user"].format(umo=umo, user=pass_uid, time=self.time_format(time), reason=reason))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("pass-all")
    async def pass_all(self, event: AstrMessageEvent, passuser: str, time: str = "0", reason: str | None = None, end: str | None = None):
        """
        在全局中解限指定用户。
        格式：/pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/pass-all @张三 7d
        注意：单次仅能解限一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="pass-all",commands_text=self.commands["pass-all"]))
            return
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="pass-all",commands_text=self.commands["pass-all"]))
            return
        self.clear_banned()
        tmpdata = self.passall_list_path.read_text(encoding='utf-8')
        passall_list = json.loads(tmpdata)
        tempbool = False
        for item in passall_list:
            if item.get('uid') == pass_uid:
                if item.get('time') == 0:
                    yield event.plain_result(self.messages["time_zeroset_error"].format(command="pass-all"))
                    return
                else:
                    item['time'] = (item['time'] + self.timestr_to_int(time)) if time != "0" else 0
                    item['reason'] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            passall_list.append({
                'uid': pass_uid,
                'time': (int(time_module.time()) + self.timestr_to_int(time)) if time != "0" else 0,
                'reason': reason
            })
        self.passall_list_path.write_text(json.dumps(passall_list, indent=4, ensure_ascii=False), encoding='utf-8')
        if time == "0":
            yield event.plain_result(self.messages["passed_all"].format(user=pass_uid, reason=reason))
        else:
            yield event.plain_result(self.messages["passed_user_global"].format(user=pass_uid, time=self.time_format(time), reason=reason))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-pass")
    async def dec_pass(self, event: AstrMessageEvent, passuser: str, time: str = "0", reason: str | None = None ,umo: str | None = None, end: str | None = None):
        """
        删除指定用户的会话解限时间。
        格式：/dec-pass <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除解限记录
        示例：/dec-pass @张三 7d
        注意：单次仅能操作一个会话的一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="dec-pass",commands_text=self.commands["dec-pass"]))
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="dec-pass",commands_text=self.commands["dec-pass"]))
            return
        self.clear_banned()
        tmpdata = self.passlist_path.read_text(encoding='utf-8')
        passlist = json.loads(tmpdata)
        group_passed_list = passlist.get(umo)
        if not isinstance(group_passed_list, list):
            yield event.plain_result(self.messages["dec_no_record"])
            return
        for item in group_passed_list:
            if item.get('uid') == pass_uid:
                if time == "0":
                    group_passed_list.remove(item)
                    self.passlist_path.write_text(json.dumps(passlist, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_passed_user"].format(umo=umo, user=pass_uid, time=self.time_format(time), reason=reason))
                    return
                if item.get('time') == 0:
                    yield event.plain_result(self.messages["dec_zerotime_error"])
                    return
                else:
                    item['time'] = (item['time'] - self.timestr_to_int(time))
                    item['reason'] = reason
                    self.passlist_path.write_text(json.dumps(passlist, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_passed_user"].format(umo=umo, user=pass_uid, time=self.time_format(time), reason=reason))
                    return
        yield event.plain_result(self.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-pass-all")
    async def dec_pass_all(self, event: AstrMessageEvent, passuser: str, time: str = "0", reason: str | None = None, end: str | None = None):
        """
        删除指定用户的全局解限时间。
        格式：/dec-pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除解限记录
        示例：/dec-pass-all @张三 7d
        注意：单次仅能操作一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="dec-pass-all",commands_text=self.commands["dec-pass-all"]))
            return
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="dec-pass-all",commands_text=self.commands["dec-pass-all"]))
            return
        self.clear_banned()
        tmpdata = self.passall_list_path.read_text(encoding='utf-8')
        passall_list = json.loads(tmpdata)
        for item in passall_list:
            if item.get('uid') == pass_uid:
                if time == "0":
                    passall_list.remove(item)
                    self.passall_list_path.write_text(json.dumps(passall_list, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_passed_user_global"].format(user=pass_uid, time=self.time_format(time), reason=reason))
                    return
                else:
                    item['time'] = (item['time'] - self.timestr_to_int(time))
                    item['reason'] = reason
                    self.passall_list_path.write_text(json.dumps(passall_list, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_passed_user_global"].format(user=pass_uid, time=self.time_format(time), reason=reason))
                    return
        yield event.plain_result(self.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-ban")
    async def dec_ban(self, event: AstrMessageEvent, banuser: str, time: str = "0", reason: str | None = None ,umo: str | None = None, end: str | None = None):
        """
        删除指定用户的会话封禁时间。
        格式：/dec-ban <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除封禁记录
        示例：/dec-ban @张三 7d
        注意：单次仅能操作一个会话的一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="dec-ban",commands_text=self.commands["dec-ban"]))
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="dec-ban",commands_text=self.commands["dec-ban"]))
            return
        self.clear_banned()
        tmpdata = self.banlist_path.read_text(encoding='utf-8')
        banlist = json.loads(tmpdata)
        group_banned_list = banlist.get(umo)
        if not isinstance(group_banned_list, list):
            yield event.plain_result(self.messages["ban_no_record"])
            return
        for item in group_banned_list:
            if item.get('uid') == ban_uid:
                if time == "0":
                    group_banned_list.remove(item)
                    self.banlist_path.write_text(json.dumps(banlist, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_banned_user"].format(umo=umo, user=ban_uid, time=self.time_format(time), reason=reason))
                    return
                if item['time'] == 0:
                    yield event.plain_result(self.messages["dec_zerotime_error"])
                    return
                else:
                    item['time'] = (item['time'] - self.timestr_to_int(time))
                    item['reason'] = reason
                    self.banlist_path.write_text(json.dumps(banlist, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_banned_user"].format(umo=umo, user=ban_uid, time=self.time_format(time), reason=reason))
                    return
        yield event.plain_result(self.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-ban-all")
    async def dec_ban_all(self, event: AstrMessageEvent, banuser: str, time: str = "0", reason: str | None = None ,end: str | None = None):
        """
        删除指定用户的全局封禁时间。
        格式：/dec-ban-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除封禁记录
        示例：/dec-ban-all @张三 7d
        注意：单次仅能操作一个用户
        """
        if end != None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(self.messages["command_error"].format(command="dec-ban-all",commands_text=self.commands["dec-ban-all"]))
            return
        if reason in self.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event) # type: ignore
        except AtNumberError:
            yield event.plain_result(self.messages["command_error"].format(command="dec-ban-all",commands_text=self.commands["dec-ban-all"]))
            return
        self.clear_banned()
        tmpdata = self.banall_list_path.read_text(encoding='utf-8')
        banall_list = json.loads(tmpdata)
        for item in banall_list:
            if item.get('uid') == ban_uid:
                if time == "0":
                    banall_list.remove(item)
                    self.banall_list_path.write_text(json.dumps(banall_list, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_banned_user_global"].format(user=ban_uid, time=self.time_format(time), reason=reason))
                    return
                if item['time'] == 0:
                    yield event.plain_result(self.messages["dec_zerotime_error"])
                    return
                else:
                    item['time'] = (item['time'] - self.timestr_to_int(time))
                    item['reason'] = reason
                    self.banall_list_path.write_text(json.dumps(banall_list, indent=4, ensure_ascii=False), encoding='utf-8')
                    yield event.plain_result(self.messages["dec_banned_user_global"].format(user=ban_uid, time=self.time_format(time), reason=reason))
                    return
        yield event.plain_result(self.messages["dec_no_record"])

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def filter_banned_users(self, event: AstrMessageEvent):
        """
        全局事件过滤器：
        如果禁用功能启用且发送者被禁用，则停止事件传播，机器人不再响应该用户的消息。
        """
        if self.enable and self.is_banned(event)[0]:
            event.stop_event()

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
