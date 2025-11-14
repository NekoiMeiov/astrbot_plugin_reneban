# pass > ban > pass-all > ban-all
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, StarTools
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
import json
import time as time_module
import re

from . import strings, time_utils
from .datafile_manager import DatafileManager
from .user_manager import UserDataList, UserDataModel


class AtNumberError(ValueError):
    """
    At 数量错误（ReNeBan.get_event_at() 获取@用户时，如果 At 用户数量大于 1，会抛出此错误）
    """

    pass


class ReNeBan(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        # 从插件配置中获取是否启用禁用功能，默认为启用
        self.enable = config.get("enable", True)
        # 初始化数据文件管理器
        self.data_manager = DatafileManager(StarTools.get_data_dir())

       


    def is_banned(self, event: AstrMessageEvent) -> tuple[bool, str | None]:
        """
        判断用户是否被禁用，以及其理由
        """
        # 禁用功能未启用
        if not self.enable:
            return (False, None)
        # pass > ban > pass-all > ban-all
        self.data_manager.clear_banned()
        # 获取UMO
        umo = event.unified_msg_origin
        # pass
        # 使用数据管理器读取数据，现在返回的是 UserDataList | dict[str, UserDataList]
        passlist = self.data_manager.read_file(self.data_manager.passlist_path)  # dict[str, UserDataList]
        # 如果不存在则返回空列表
        umo_pass_list = passlist.get(umo) if isinstance(passlist.get(umo), UserDataList) else UserDataList()
        # 遍历umo_pass_list中用户数据的uid
        for item in umo_pass_list:
            if item.uid == event.get_sender_id():
                return (False, item.reason)
        # ban
        # 使用数据管理器读取数据
        banlist = self.data_manager.read_file(self.data_manager.banlist_path)  # dict[str, UserDataList]
        # 如果不存在则返回空列表
        umo_ban_list = banlist.get(umo) if isinstance(banlist.get(umo), UserDataList) else UserDataList()
        # 遍历umo_ban_list中用户数据的uid
        for item in umo_ban_list:
            if item.uid == event.get_sender_id():
                return (True, item.reason)
        # pass-all
        # 使用数据管理器读取数据
        passall_list = self.data_manager.read_file(self.data_manager.passall_list_path)  # UserDataList
        # 遍历passall_list中用户数据的uid
        for item in passall_list:
            if item.uid == event.get_sender_id():
                return (False, item.reason)
        # ban-all
        # 使用数据管理器读取数据
        banall_list = self.data_manager.read_file(self.data_manager.banall_list_path)  # UserDataList
        # 遍历banall_list中用户数据的uid
        for item in banall_list:
            if item.uid == event.get_sender_id():
                return (True, item.reason)
        return (False, None)

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
            group_banned_text = (
                strings.messages["group_banned_list"] + strings.messages["no_group_banned"]
            )
            global_banned_text = (
                strings.messages["global_banned_list"] + strings.messages["no_global_banned"]
            )
            group_passed_text = (
                strings.messages["group_passed_list"] + strings.messages["no_group_passed"]
            )
            global_passed_text = (
                strings.messages["global_passed_list"] + strings.messages["no_global_passed"]
            )
            result = f"{group_banned_text}\n\n{global_banned_text}\n\n{group_passed_text}\n\n{global_passed_text}"
            yield event.plain_result(result)
            return
        self.data_manager.clear_banned()
        # 获取UMO
        umo = event.unified_msg_origin
        # get_pass
        passlist = self.data_manager.read_file(self.data_manager.passlist_path)  # dict[str, UserDataList]
        group_passed_list = (
            passlist.get(umo) if isinstance(passlist.get(umo), UserDataList) else UserDataList()
        )
        # get_pass-all
        global_passed_list = self.data_manager.read_file(self.data_manager.passall_list_path)  # UserDataList
        # get_ban-all
        global_banned_list = self.data_manager.read_file(self.data_manager.banall_list_path)  # UserDataList
        # get_ban
        banlist = self.data_manager.read_file(self.data_manager.banlist_path)  # dict[str, UserDataList]
        group_banned_list = (
            banlist.get(umo) if isinstance(banlist.get(umo), UserDataList) else UserDataList()
        )
        group_banned_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.uid,
                time=time_utils.timelast_format(
                    (item.time - int(time_module.time()))
                    if item.time != 0
                    else 0
                ),
                reason=item.reason
                if item.reason
                else strings.messages["no_reason"],
            )
            for item in group_banned_list
        ]
        if not group_banned_str_list:
            group_banned_str_list.append(strings.messages["no_group_banned"])
        global_banned_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.uid,
                time=time_utils.timelast_format(
                    (item.time - int(time_module.time()))
                    if item.time != 0
                    else 0
                ),
                reason=item.reason
                if item.reason
                else strings.messages["no_reason"],
            )
            for item in global_banned_list
        ]
        if not global_banned_str_list:
            global_banned_str_list.append(strings.messages["no_global_banned"])
        group_passed_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.uid,
                time=time_utils.timelast_format(
                    (item.time - int(time_module.time()))
                    if item.time != 0
                    else 0
                ),
                reason=item.reason
                if item.reason
                else strings.messages["no_reason"],
            )
            for item in group_passed_list
        ]
        if not group_passed_str_list:
            group_passed_str_list.append(strings.messages["no_group_passed"])
        global_passed_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.uid,
                time=time_utils.timelast_format(
                    (item.time - int(time_module.time()))
                    if item.time != 0
                    else 0
                ),
                reason=item.reason
                if item.reason
                else strings.messages["no_reason"],
            )
            for item in global_passed_list
        ]
        if not global_passed_str_list:
            global_passed_str_list.append(strings.messages["no_global_passed"])

        group_banned_text = strings.messages["group_banned_list"] + "".join(
            group_banned_str_list
        )
        global_banned_text = strings.messages["global_banned_list"] + "".join(
            global_banned_str_list
        )
        group_passed_text = strings.messages["group_passed_list"] + "".join(
            group_passed_str_list
        )
        global_passed_text = strings.messages["global_passed_list"] + "".join(
            global_passed_str_list
        )

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
        yield event.plain_result(strings.messages["ban_enabled"])
        logger.warning(
            f"已临时启用禁用功能(In {event.unified_msg_origin} - {event.get_sender_name()}({event.get_sender_id()}))"
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban-disable")
    async def ban_disable(self, event: AstrMessageEvent):
        """
        停用禁用功能
        """
        self.enable = False
        yield event.plain_result(strings.messages["ban_disabled"])
        logger.warning(
            f"已临时禁用禁用功能(In {event.unified_msg_origin} - {event.get_sender_name()}({event.get_sender_id()}))"
        )

    @filter.command("ban-help")
    async def ban_help(self, event: AstrMessageEvent):
        """
        显示reneban帮助信息
        """
        yield event.plain_result(strings.messages["help_text"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban")
    async def ban_user(
        self,
        event: AstrMessageEvent,
        banuser: str,
        time: str = "0",
        reason: str | None = None,
        umo: str | None = None,
        end: str | None = None,
    ):
        """
        在会话中禁用指定用户的使用权限。
        格式：/ban <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/ban @张三 7d
        注意：单次仅能禁用一个会话的一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="ban", commands_text=strings.commands["ban"]
                )
            )
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        # 我没法了（（（
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="ban", commands_text=strings.commands["ban"]
                )
            )
            return
        # 准备ban_user
        self.data_manager.clear_banned()
        banlist = self.data_manager.read_file(self.data_manager.banlist_path)  # dict[str, UserDataList]
        if not isinstance(banlist.get(umo), UserDataList):
            banlist[umo] = UserDataList()
        group_banned_list = banlist.get(umo)  # UserDataList
        tempbool = False
        for item in group_banned_list:
            if item.uid == ban_uid:
                if item.time == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="ban")
                    )
                    return
                else:
                    # 更新时间
                    new_time = (item.time + time_utils.timestr_to_int(time)) if time != "0" else 0
                    item.update_data(time=new_time, reason=reason)
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            # 添加新的封禁记录
            new_ban_item = UserDataModel(
                uid=ban_uid,
                time=(int(time_module.time()) + time_utils.timestr_to_int(time)) if time != "0" else 0,
                reason=reason
            )
            group_banned_list.append(new_ban_item)
        logger.warning(f"[ban]{json.dumps([{k: [dict(item) for item in v] for k, v in banlist.items()}], indent=4, ensure_ascii=False)}")
        self.data_manager.write_file(self.data_manager.banlist_path, banlist)
        yield event.plain_result(
            strings.messages["banned_user"].format(
                umo=umo, user=ban_uid, time=time_utils.time_format(time), reason=reason
            )
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban-all")
    async def ban_all(
        self,
        event: AstrMessageEvent,
        banuser: str,
        time: str = "0",
        reason: str | None = None,
        end: str | None = None,
    ):
        """
        在全局禁用指定用户的使用权限。
        格式：/ban-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/ban-all @张三 7d
        注意：单次仅能禁用一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="ban-all", commands_text=strings.commands["ban-all"]
                )
            )
            return
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="ban-all", commands_text=strings.commands["ban-all"]
                )
            )
            return
        self.data_manager.clear_banned()
        banall_list = self.data_manager.read_file(self.data_manager.banall_list_path)  # UserDataList
        tempbool = False
        for item in banall_list:
            if item.uid == ban_uid:
                if item.time == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="ban-all")
                    )
                    return
                else:
                    # 更新时间
                    new_time = (item.time + time_utils.timestr_to_int(time)) if time != "0" else 0
                    item.update_data(time=new_time, reason=reason)
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            # 添加新的全局封禁记录
            new_ban_item = UserDataModel(
                uid=ban_uid,
                time=(int(time_module.time()) + time_utils.timestr_to_int(time)) if time != "0" else 0,
                reason=reason
            )
            banall_list.append(new_ban_item)
        logger.warning(
            f"[ban-all]{json.dumps([dict(item) for item in banall_list], indent=4, ensure_ascii=False)}"
        )
        self.data_manager.write_file(self.data_manager.banall_list_path, banall_list)
        yield event.plain_result(
            strings.messages["banned_user_global"].format(
                user=ban_uid, time=time_utils.time_format(time), reason=reason
            )
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("pass")
    async def pass_user(
        self,
        event: AstrMessageEvent,
        passuser: str,
        time: str = "0",
        reason: str | None = None,
        umo: str | None = None,
        end: str | None = None,
    ):
        """
        在会话中解限指定用户。
        格式：/pass <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/pass @张三 7d
        注意：单次仅能解限一个会话的一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="pass", commands_text=strings.commands["pass"]
                )
            )
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="pass", commands_text=strings.commands["pass"]
                )
            )
            return
        self.data_manager.clear_banned()
        passlist = self.data_manager.read_file(self.data_manager.passlist_path)  # dict[str, UserDataList]
        if not isinstance(passlist.get(umo), UserDataList):
            passlist[umo] = UserDataList()
        group_passed_list = passlist.get(umo)  # UserDataList
        tempbool = False
        for item in group_passed_list:
            if item.uid == pass_uid:
                if item.time == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="pass")
                    )
                    return
                else:
                    # 更新时间
                    new_time = (item.time + time_utils.timestr_to_int(time)) if time != "0" else 0
                    item.update_data(time=new_time, reason=reason)
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            # 添加新的解限记录
            new_pass_item = UserDataModel(
                uid=pass_uid,
                time=(int(time_module.time()) + time_utils.timestr_to_int(time)) if time != "0" else 0,
                reason=reason
            )
            group_passed_list.append(new_pass_item)
        self.data_manager.write_file(self.data_manager.passlist_path, passlist)
        yield event.plain_result(
            strings.messages["passed_user"].format(
                umo=umo, user=pass_uid, time=time_utils.time_format(time), reason=reason
            )
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("pass-all")
    async def pass_all(
        self,
        event: AstrMessageEvent,
        passuser: str,
        time: str = "0",
        reason: str | None = None,
        end: str | None = None,
    ):
        """
        在全局中解限指定用户。
        格式：/pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示无期限
        示例：/pass-all @张三 7d
        注意：单次仅能解限一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="pass-all", commands_text=strings.commands["pass-all"]
                )
            )
            return
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="pass-all", commands_text=strings.commands["pass-all"]
                )
            )
            return
        self.data_manager.clear_banned()
        passall_list = self.data_manager.read_file(self.data_manager.passall_list_path)  # UserDataList
        tempbool = False
        for item in passall_list:
            if item.uid == pass_uid:
                if item.time == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="pass-all")
                    )
                    return
                else:
                    # 更新时间
                    new_time = (item.time + time_utils.timestr_to_int(time)) if time != "0" else 0
                    item.update_data(time=new_time, reason=reason)
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            # 添加新的全局解限记录
            new_pass_item = UserDataModel(
                uid=pass_uid,
                time=(int(time_module.time()) + time_utils.timestr_to_int(time)) if time != "0" else 0,
                reason=reason
            )
            passall_list.append(new_pass_item)
        self.data_manager.write_file(self.data_manager.passall_list_path, passall_list)
        yield event.plain_result(
            strings.messages["passed_user_global"].format(
                user=pass_uid, time=time_utils.time_format(time), reason=reason
            )
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-pass")
    async def dec_pass(
        self,
        event: AstrMessageEvent,
        passuser: str,
        time: str = "0",
        reason: str | None = None,
        umo: str | None = None,
        end: str | None = None,
    ):
        """
        删除指定用户的会话解限时间。
        格式：/dec-pass <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除解限记录
        示例：/dec-pass @张三 7d
        注意：单次仅能操作一个会话的一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-pass", commands_text=strings.commands["dec-pass"]
                )
            )
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-pass", commands_text=strings.commands["dec-pass"]
                )
            )
            return
        self.data_manager.clear_banned()
        passlist = self.data_manager.read_file(self.data_manager.passlist_path)  # dict[str, UserDataList]
        group_passed_list = passlist.get(umo)  # UserDataList
        if not isinstance(group_passed_list, UserDataList):
            yield event.plain_result(strings.messages["dec_no_record"])
            return
        for item in group_passed_list:
            if item.uid == pass_uid:
                if time == "0":
                    group_passed_list.remove(item)
                    self.data_manager.write_file(self.data_manager.passlist_path, passlist)
                    yield event.plain_result(
                        strings.messages["dec_passed_user"].format(
                            umo=umo,
                            user=pass_uid,
                            time=time_utils.time_format(time),
                            reason=reason,
                        )
                    )
                    return
                if item.time == 0:
                    yield event.plain_result(strings.messages["dec_zerotime_error"])
                    return
                else:
                    new_time = item.time - time_utils.timestr_to_int(time)
                    item.update_data(time=new_time, reason=reason)
                    self.data_manager.write_file(self.data_manager.passlist_path, passlist)
                    yield event.plain_result(
                        strings.messages["dec_passed_user"].format(
                            umo=umo,
                            user=pass_uid,
                            time=time_utils.time_format(time),
                            reason=reason,
                        )
                    )
                    return
        yield event.plain_result(strings.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-pass-all")
    async def dec_pass_all(
        self,
        event: AstrMessageEvent,
        passuser: str,
        time: str = "0",
        reason: str | None = None,
        end: str | None = None,
    ):
        """
        删除指定用户的全局解限时间。
        格式：/dec-pass-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除解限记录
        示例：/dec-pass-all @张三 7d
        注意：单次仅能操作一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-pass-all", commands_text=strings.commands["dec-pass-all"]
                )
            )
            return
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            pass_uid: str
            if self.get_event_at(event) == None:
                pass_uid = passuser
            else:
                pass_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-pass-all", commands_text=strings.commands["dec-pass-all"]
                )
            )
            return
        self.data_manager.clear_banned()
        passall_list = self.data_manager.read_file(self.data_manager.passall_list_path)  # UserDataList
        for item in passall_list:
            if item.uid == pass_uid:
                if time == "0":
                    passall_list.remove(item)
                    self.data_manager.write_file(self.data_manager.passall_list_path, passall_list)
                    yield event.plain_result(
                        strings.messages["dec_passed_user_global"].format(
                            user=pass_uid, time=time_utils.time_format(time), reason=reason
                        )
                    )
                    return
                else:
                    new_time = item.time - time_utils.timestr_to_int(time)
                    item.update_data(time=new_time, reason=reason)
                    self.data_manager.write_file(self.data_manager.passall_list_path, passall_list)
                    yield event.plain_result(
                        strings.messages["dec_passed_user_global"].format(
                            user=pass_uid, time=time_utils.time_format(time), reason=reason
                        )
                    )
                    return
        yield event.plain_result(strings.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-ban")
    async def dec_ban(
        self,
        event: AstrMessageEvent,
        banuser: str,
        time: str = "0",
        reason: str | None = None,
        umo: str | None = None,
        end: str | None = None,
    ):
        """
        删除指定用户的会话封禁时间。
        格式：/dec-ban <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）] [UMO]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除封禁记录
        示例：/dec-ban @张三 7d
        注意：单次仅能操作一个会话的一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-ban", commands_text=strings.commands["dec-ban"]
                )
            )
            return
        if umo == None:
            # 若umo不存在，则使用event.unified_msg_origin（当前群）
            umo = event.unified_msg_origin
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-ban", commands_text=strings.commands["dec-ban"]
                )
            )
            return
        self.data_manager.clear_banned()
        banlist = self.data_manager.read_file(self.data_manager.banlist_path)  # dict[str, UserDataList]
        group_banned_list = banlist.get(umo)  # UserDataList
        if not isinstance(group_banned_list, UserDataList):
            yield event.plain_result(strings.messages["dec_no_record"])
            return
        for item in group_banned_list:
            if item.uid == ban_uid:
                if time == "0":
                    group_banned_list.remove(item)
                    self.data_manager.write_file(self.data_manager.banlist_path, banlist)
                    yield event.plain_result(
                        strings.messages["dec_banned_user"].format(
                            umo=umo,
                            user=ban_uid,
                            time=time_utils.time_format(time),
                            reason=reason,
                        )
                    )
                    return
                if item.time == 0:
                    yield event.plain_result(strings.messages["dec_zerotime_error"])
                    return
                else:
                    new_time = item.time - time_utils.timestr_to_int(time)
                    item.update_data(time=new_time, reason=reason)
                    self.data_manager.write_file(self.data_manager.banlist_path, banlist)
                    yield event.plain_result(
                        strings.messages["dec_banned_user"].format(
                            umo=umo,
                            user=ban_uid,
                            time=time_utils.time_format(time),
                            reason=reason,
                        )
                    )
                    return
        yield event.plain_result(strings.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("dec-ban-all")
    async def dec_ban_all(
        self,
        event: AstrMessageEvent,
        banuser: str,
        time: str = "0",
        reason: str | None = None,
        end: str | None = None,
    ):
        """
        删除指定用户的全局封禁时间。
        格式：/dec-ban-all <@用户|UID（QQ号）> [时间（默认无期限）] [理由（默认无理由）]
        时间格式：数字+单位（d=天，h=小时，m=分钟，s=秒），如 1d 表示1天，12h 表示12个小时，不带单位默认秒，0表示彻底删除封禁记录
        示例：/dec-ban-all @张三 7d
        注意：单次仅能操作一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-ban-all", commands_text=strings.commands["dec-ban-all"]
                )
            )
            return
        if reason in strings.no_reason:
            # 若reason在no_reason中，则reason为None（无理由）
            reason = None
        try:
            ban_uid: str
            if self.get_event_at(event) == None:
                ban_uid = banuser
            else:
                ban_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="dec-ban-all", commands_text=strings.commands["dec-ban-all"]
                )
            )
            return
        self.data_manager.clear_banned()
        banall_list = self.data_manager.read_file(self.data_manager.banall_list_path)  # UserDataList
        for item in banall_list:
            if item.uid == ban_uid:
                if time == "0":
                    banall_list.remove(item)
                    self.data_manager.write_file(self.data_manager.banall_list_path, banall_list)
                    yield event.plain_result(
                        strings.messages["dec_banned_user_global"].format(
                            user=ban_uid, time=time_utils.time_format(time), reason=reason
                        )
                    )
                    return
                if item.time == 0:
                    yield event.plain_result(strings.messages["dec_zerotime_error"])
                    return
                else:
                    new_time = item.time - time_utils.timestr_to_int(time)
                    item.update_data(time=new_time, reason=reason)
                    self.data_manager.write_file(self.data_manager.banall_list_path, banall_list)
                    yield event.plain_result(
                        strings.messages["dec_banned_user_global"].format(
                            user=ban_uid, time=time_utils.time_format(time), reason=reason
                        )
                    )
                    return
        yield event.plain_result(strings.messages["dec_no_record"])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban-reset")
    async def ban_reset(
        self, event: AstrMessageEvent, resetuser: str, end: str | None = None
    ):
        """
        删除一名指定用户的所有记录
        格式：/ban-reset <@用户|UID（QQ号）>
        示例：/ban-reset @张三
        注意：单次仅能操作一个用户
        """
        if end is not None:
            # 若end存在，说明语法错误，发送错误信息并return
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="ban-reset", commands_text=strings.commands["ban-reset"]
                )
            )
            return
        try:
            reset_uid: str
            if self.get_event_at(event) is None:
                reset_uid = resetuser
            else:
                reset_uid = self.get_event_at(event)  # type: ignore
        except AtNumberError:
            yield event.plain_result(
                strings.messages["command_error"].format(
                    command="ban-reset", commands_text=strings.commands["ban-reset"]
                )
            )
            return
        self.data_manager.clear_banned()

        banall_data = self.data_manager.read_file(self.data_manager.banall_list_path)  # UserDataList
        passall_data = self.data_manager.read_file(self.data_manager.passall_list_path)  # UserDataList
        ban_data = self.data_manager.read_file(self.data_manager.banlist_path)  # dict[str, UserDataList]
        pass_data = self.data_manager.read_file(self.data_manager.passlist_path)  # dict[str, UserDataList]
        # 从全局封禁列表中移除该用户
        banall_data = UserDataList([item for item in banall_data if item.uid != reset_uid])
        # 从全局解封列表中移除该用户
        passall_data = UserDataList([item for item in passall_data if item.uid != reset_uid])
        # 从各UMO的封禁列表中移除该用户
        for umo in list(ban_data.keys()):
            ban_data[umo] = UserDataList([item for item in ban_data[umo] if item.uid != reset_uid])
        # 从各UMO的解封列表中移除该用户
        for umo in list(pass_data.keys()):
            pass_data[umo] = UserDataList([
                item for item in pass_data[umo] if item.uid != reset_uid
            ])
        # 将修改后的数据写回文件
        self.data_manager.write_file(self.data_manager.banall_list_path, banall_data)
        self.data_manager.write_file(self.data_manager.passall_list_path, passall_data)
        self.data_manager.write_file(self.data_manager.banlist_path, ban_data)
        self.data_manager.write_file(self.data_manager.passlist_path, pass_data)

        yield event.plain_result(
            strings.messages["ban_reset_success"].format(user=reset_uid)
        )

    # 设置优先级，可在其他未设置优先级（priority=0）的命令/监听器/钩子前过滤
    @filter.event_message_type(filter.EventMessageType.ALL, priority=1)
    async def filter_banned_users(self, event: AstrMessageEvent):
        """
        全局事件过滤器：
        如果禁用功能启用且发送者被禁用，则停止事件传播，机器人不再响应该用户的消息。
        """
        if self.enable and self.is_banned(event)[0]:
            event.stop_event()

    async def terminate(self):
        """可选择实现 terminate 函数，当插件被卸载/停用时会调用。"""
