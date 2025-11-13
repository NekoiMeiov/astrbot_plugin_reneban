# pass > ban > pass-all > ban-all
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, StarTools
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
import json
import time as time_module
import re

from . import strings, time_utils


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
                path.write_text("{}", encoding="utf-8")
        for path in [
            self.banall_list_path,
            self.passall_list_path,
        ]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text("[]", encoding="utf-8")

       

    def _clear_expired_banned(self):
        """
        清除过期的禁用列表。
        Ver 0.1.1_MVP_AI
        我操AI太好用了你们知道吗
        """
        current_time = int(time_module.time())

        # 处理所有列表的公共函数
        def clear_expired_items(data, is_dict=False):
            if is_dict:
                # 字典结构：{umo: [items]}
                for key in list(data.keys()):
                    data[key] = [
                        item
                        for item in data[key]
                        if not (
                            item.get("time", 0) < current_time
                            and item.get("time", 0) != 0
                        )
                    ]
                    # 如果该umo下没有项目了，删除空键
                    if not data[key]:
                        del data[key]
            else:
                # 列表结构：[items]
                data[:] = [
                    item
                    for item in data
                    if not (
                        item.get("time", 0) < current_time and item.get("time", 0) != 0
                    )
                ]
            return data

        # 统一处理所有列表
        lists_to_clear = [
            (self.passlist_path, True),  # passlist是字典结构
            (self.banlist_path, True),  # banlist是字典结构
            (self.banall_list_path, False),  # banall_list是列表结构
            (self.passall_list_path, False),  # passall_list是列表结构
        ]

        for file_path, is_dict in lists_to_clear:
            try:
                raw_data = file_path.read_text(encoding="utf-8")
                data = json.loads(raw_data)
                cleared_data = clear_expired_items(data, is_dict)
                file_path.write_text(
                    json.dumps(cleared_data, indent=4, ensure_ascii=False),
                    encoding="utf-8",
                )
            except Exception as e:
                # 添加错误处理，避免一个文件出错影响其他文件
                logger.error(f"清理文件 {file_path} 时出错: {e}")

    def _clear_redundant_banned(self):
        """
        清除冗余的禁用列表。
        Ver 0.1.0_MVP_AI
        我操AI太好用了你们知道吗
        """
        # 加载所有数据
        banall_data = json.loads(self.banall_list_path.read_text(encoding="utf-8"))
        passall_data = json.loads(self.passall_list_path.read_text(encoding="utf-8"))
        ban_data = json.loads(self.banlist_path.read_text(encoding="utf-8"))
        pass_data = json.loads(self.passlist_path.read_text(encoding="utf-8"))

        # 处理ban_data中的冗余
        for umo in list(ban_data.keys()):
            if umo in pass_data:
                pass_list = pass_data[umo]
                ban_list = ban_data[umo]

                # 创建pass项的uid到time的映射
                pass_time_map = {item["uid"]: item.get("time", 0) for item in pass_list}

                # 过滤ban_list，保留那些没有对应pass项，或者pass项时间不更新的项
                ban_data[umo] = [
                    ban_item
                    for ban_item in ban_list
                    if ban_item["uid"] not in pass_time_map
                    or pass_time_map[ban_item["uid"]] <= ban_item.get("time", 0)
                ]

                # 如果该umo下没有ban项了，删除空键
                if not ban_data[umo]:
                    del ban_data[umo]

        # 处理banall_data中的冗余
        passall_time_map = {item["uid"]: item.get("time", 0) for item in passall_data}

        banall_data = [
            ban_item
            for ban_item in banall_data
            if ban_item["uid"] not in passall_time_map
            or passall_time_map[ban_item["uid"]] <= ban_item.get("time", 0)
        ]

        # 处理passall_data，只保留在banall_data中存在的uid
        banall_uids = {item["uid"] for item in banall_data}
        passall_data = [item for item in passall_data if item["uid"] in banall_uids]

        # 处理pass_data，只保留在ban_data或banall_data中存在的uid
        combine_ban_uids = set()
        # 收集所有ban_data中的uid
        for umo_ban_list in ban_data.values():
            combine_ban_uids.update(item["uid"] for item in umo_ban_list)
        # 添加banall_data中的uid
        combine_ban_uids.update(banall_uids)

        # 过滤pass_data
        for umo in list(pass_data.keys()):
            pass_data[umo] = [
                item for item in pass_data[umo] if item["uid"] in combine_ban_uids
            ]
            # 如果该umo下没有pass项了，删除空键
            if not pass_data[umo]:
                del pass_data[umo]

        # 保存所有数据
        self.banlist_path.write_text(
            json.dumps(ban_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        self.passlist_path.write_text(
            json.dumps(pass_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        self.banall_list_path.write_text(
            json.dumps(banall_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        self.passall_list_path.write_text(
            json.dumps(passall_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )

    def clear_banned(self):
        """
        清除禁用列表。
        Ver 0.1.0_MVP
        """
        self._clear_expired_banned()
        self._clear_redundant_banned()

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
        tmpdata = self.passlist_path.read_text(encoding="utf-8")
        passlist = json.loads(tmpdata)
        # 如果不存在则返回空列表
        umo_pass_list = passlist.get(umo) if isinstance(passlist.get(umo), list) else []
        # 遍历umo_pass_list中字典对象的ban_uid键
        for item in umo_pass_list:
            if item.get("uid") == event.get_sender_id():
                return (False, item.get("reason"))
        # ban
        # 打开self.banlist_path，取umo对应的list
        tmpdata = self.banlist_path.read_text(encoding="utf-8")
        banlist = json.loads(tmpdata)
        # 如果不存在则返回空列表
        umo_ban_list = banlist.get(umo) if isinstance(banlist.get(umo), list) else []
        # 遍历umo_ban_list中字典对象的ban_uid键
        for item in umo_ban_list:
            if item.get("uid") == event.get_sender_id():
                return (True, item.get("reason"))
        # pass-all
        # 打开self.passall_list_path
        tmpdata = self.passall_list_path.read_text(encoding="utf-8")
        passall_list = json.loads(tmpdata)
        # 遍历passall_list中字典对象的ban_uid键
        for item in passall_list:
            if item.get("uid") == event.get_sender_id():
                return (False, item.get("reason"))
        # ban-all
        # 打开self.banall_list_path
        tmpdata = self.banall_list_path.read_text(encoding="utf-8")
        banall_list = json.loads(tmpdata)
        # 遍历banall_list中字典对象的ban_uid键
        for item in banall_list:
            if item.get("uid") == event.get_sender_id():
                return (True, item.get("reason"))
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
        self.clear_banned()
        # 获取UMO
        umo = event.unified_msg_origin
        # get_pass
        tmpdata = self.passlist_path.read_text(encoding="utf-8")
        passlist = json.loads(tmpdata)
        group_passed_list = (
            passlist.get(umo) if isinstance(passlist.get(umo), list) else []
        )
        # get_pass-all
        tmpdata = self.passall_list_path.read_text(encoding="utf-8")
        global_passed_list = json.loads(tmpdata)
        # get_ban-all
        tmpdata = self.banall_list_path.read_text(encoding="utf-8")
        global_banned_list = json.loads(tmpdata)
        # get_ban
        tmpdata = self.banlist_path.read_text(encoding="utf-8")
        banlist = json.loads(tmpdata)
        group_banned_list = (
            banlist.get(umo) if isinstance(banlist.get(umo), list) else []
        )
        group_banned_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.get("uid"),
                time=time_utils.timelast_format(
                    (item.get("time") - int(time_module.time()))
                    if item.get("time") != 0
                    else 0
                ),
                reason=item.get("reason")
                if item.get("reason")
                else strings.messages["no_reason"],
            )
            for item in group_banned_list
        ]
        if not group_banned_str_list:
            group_banned_str_list.append(strings.messages["no_group_banned"])
        global_banned_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.get("uid"),
                time=time_utils.timelast_format(
                    (item.get("time") - int(time_module.time()))
                    if item.get("time") != 0
                    else 0
                ),
                reason=item.get("reason")
                if item.get("reason")
                else strings.messages["no_reason"],
            )
            for item in global_banned_list
        ]
        if not global_banned_str_list:
            global_banned_str_list.append(strings.messages["no_global_banned"])
        group_passed_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.get("uid"),
                time=time_utils.timelast_format(
                    (item.get("time") - int(time_module.time()))
                    if item.get("time") != 0
                    else 0
                ),
                reason=item.get("reason")
                if item.get("reason")
                else strings.messages["no_reason"],
            )
            for item in group_passed_list
        ]
        if not group_passed_str_list:
            group_passed_str_list.append(strings.messages["no_group_passed"])
        global_passed_str_list = [
            strings.messages["banlist_strlist_format"].format(
                user=item.get("uid"),
                time=time_utils.timelast_format(
                    (item.get("time") - int(time_module.time()))
                    if item.get("time") != 0
                    else 0
                ),
                reason=item.get("reason")
                if item.get("reason")
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
        self.clear_banned()
        tmpdata = self.banlist_path.read_text(encoding="utf-8")
        banlist = json.loads(tmpdata)
        if not isinstance(banlist.get(umo), list):
            banlist[umo] = []
        group_banned_list = banlist.get(umo)
        tempbool = False
        for item in group_banned_list:
            if item.get("uid") == ban_uid:
                if item.get("time") == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="ban")
                    )
                    return
                else:
                    item["time"] = (
                        (item["time"] + time_utils.timestr_to_int(time)) if time != "0" else 0
                    )
                    item["reason"] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            group_banned_list.append(
                {
                    "uid": ban_uid,
                    "time": (int(time_module.time()) + time_utils.timestr_to_int(time))
                    if time != "0"
                    else 0,
                    "reason": reason,
                }
            )
        logger.warning(f"[ban]{json.dumps(banlist, indent=4, ensure_ascii=False)}")
        self.banlist_path.write_text(
            json.dumps(banlist, indent=4, ensure_ascii=False), encoding="utf-8"
        )
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
        self.clear_banned()
        tmpdata = self.banall_list_path.read_text(encoding="utf-8")
        banall_list = json.loads(tmpdata)
        tempbool = False
        for item in banall_list:
            if item.get("uid") == ban_uid:
                if item.get("time") == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="ban-all")
                    )
                    return
                else:
                    item["time"] = (
                        (item["time"] + time_utils.timestr_to_int(time)) if time != "0" else 0
                    )
                    item["reason"] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            banall_list.append(
                {
                    "uid": ban_uid,
                    "time": (int(time_module.time()) + time_utils.timestr_to_int(time))
                    if time != "0"
                    else 0,
                    "reason": reason,
                }
            )
        logger.warning(
            f"[ban-all]{json.dumps(banall_list, indent=4, ensure_ascii=False)}"
        )
        self.banall_list_path.write_text(
            json.dumps(banall_list, indent=4, ensure_ascii=False), encoding="utf-8"
        )
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
        self.clear_banned()
        tmpdata = self.passlist_path.read_text(encoding="utf-8")
        passlist = json.loads(tmpdata)
        if not isinstance(passlist.get(umo), list):
            passlist[umo] = []
        group_passed_list = passlist.get(umo)
        tempbool = False
        for item in group_passed_list:
            if item.get("uid") == pass_uid:
                if item.get("time") == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="pass")
                    )
                    return
                else:
                    item["time"] = (
                        (item["time"] + time_utils.timestr_to_int(time)) if time != "0" else 0
                    )
                    item["reason"] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            group_passed_list.append(
                {
                    "uid": pass_uid,
                    "time": (int(time_module.time()) + time_utils.timestr_to_int(time))
                    if time != "0"
                    else 0,
                    "reason": reason,
                }
            )
        self.passlist_path.write_text(
            json.dumps(passlist, indent=4, ensure_ascii=False), encoding="utf-8"
        )
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
        self.clear_banned()
        tmpdata = self.passall_list_path.read_text(encoding="utf-8")
        passall_list = json.loads(tmpdata)
        tempbool = False
        for item in passall_list:
            if item.get("uid") == pass_uid:
                if item.get("time") == 0:
                    yield event.plain_result(
                        strings.messages["time_zeroset_error"].format(command="pass-all")
                    )
                    return
                else:
                    item["time"] = (
                        (item["time"] + time_utils.timestr_to_int(time)) if time != "0" else 0
                    )
                    item["reason"] = reason
                    tempbool = True
                    break
            else:
                continue
        if not tempbool:
            passall_list.append(
                {
                    "uid": pass_uid,
                    "time": (int(time_module.time()) + time_utils.timestr_to_int(time))
                    if time != "0"
                    else 0,
                    "reason": reason,
                }
            )
        self.passall_list_path.write_text(
            json.dumps(passall_list, indent=4, ensure_ascii=False), encoding="utf-8"
        )
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
        self.clear_banned()
        tmpdata = self.passlist_path.read_text(encoding="utf-8")
        passlist = json.loads(tmpdata)
        group_passed_list = passlist.get(umo)
        if not isinstance(group_passed_list, list):
            yield event.plain_result(strings.messages["dec_no_record"])
            return
        for item in group_passed_list:
            if item.get("uid") == pass_uid:
                if time == "0":
                    group_passed_list.remove(item)
                    self.passlist_path.write_text(
                        json.dumps(passlist, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    yield event.plain_result(
                        strings.messages["dec_passed_user"].format(
                            umo=umo,
                            user=pass_uid,
                            time=self.time_format(time),
                            reason=reason,
                        )
                    )
                    return
                if item.get("time") == 0:
                    yield event.plain_result(strings.messages["dec_zerotime_error"])
                    return
                else:
                    item["time"] = item["time"] - time_utils.timestr_to_int(time)
                    item["reason"] = reason
                    self.passlist_path.write_text(
                        json.dumps(passlist, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
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
        self.clear_banned()
        tmpdata = self.passall_list_path.read_text(encoding="utf-8")
        passall_list = json.loads(tmpdata)
        for item in passall_list:
            if item.get("uid") == pass_uid:
                if time == "0":
                    passall_list.remove(item)
                    self.passall_list_path.write_text(
                        json.dumps(passall_list, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    yield event.plain_result(
                        strings.messages["dec_passed_user_global"].format(
                            user=pass_uid, time=time_utils.time_format(time), reason=reason
                        )
                    )
                    return
                else:
                    item["time"] = item["time"] - time_utils.timestr_to_int(time)
                    item["reason"] = reason
                    self.passall_list_path.write_text(
                        json.dumps(passall_list, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
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
        self.clear_banned()
        tmpdata = self.banlist_path.read_text(encoding="utf-8")
        banlist = json.loads(tmpdata)
        group_banned_list = banlist.get(umo)
        if not isinstance(group_banned_list, list):
            yield event.plain_result(strings.messages["dec_no_record"])
            return
        for item in group_banned_list:
            if item.get("uid") == ban_uid:
                if time == "0":
                    group_banned_list.remove(item)
                    self.banlist_path.write_text(
                        json.dumps(banlist, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    yield event.plain_result(
                        strings.messages["dec_banned_user"].format(
                            umo=umo,
                            user=ban_uid,
                            time=time_utils.time_format(time),
                            reason=reason,
                        )
                    )
                    return
                if item["time"] == 0:
                    yield event.plain_result(strings.messages["dec_zerotime_error"])
                    return
                else:
                    item["time"] = item["time"] - time_utils.timestr_to_int(time)
                    item["reason"] = reason
                    self.banlist_path.write_text(
                        json.dumps(banlist, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
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
        self.clear_banned()
        tmpdata = self.banall_list_path.read_text(encoding="utf-8")
        banall_list = json.loads(tmpdata)
        for item in banall_list:
            if item.get("uid") == ban_uid:
                if time == "0":
                    banall_list.remove(item)
                    self.banall_list_path.write_text(
                        json.dumps(banall_list, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    yield event.plain_result(
                        strings.messages["dec_banned_user_global"].format(
                            user=ban_uid, time=time_utils.time_format(time), reason=reason
                        )
                    )
                    return
                if item["time"] == 0:
                    yield event.plain_result(strings.messages["dec_zerotime_error"])
                    return
                else:
                    item["time"] = item["time"] - time_utils.timestr_to_int(time)
                    item["reason"] = reason
                    self.banall_list_path.write_text(
                        json.dumps(banall_list, indent=4, ensure_ascii=False),
                        encoding="utf-8",
                    )
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
        self.clear_banned()

        banall_data = json.loads(self.banall_list_path.read_text(encoding="utf-8"))
        passall_data = json.loads(self.passall_list_path.read_text(encoding="utf-8"))
        ban_data = json.loads(self.banlist_path.read_text(encoding="utf-8"))
        pass_data = json.loads(self.passlist_path.read_text(encoding="utf-8"))
        # 从全局封禁列表中移除该用户
        banall_data = [item for item in banall_data if item["uid"] != reset_uid]
        # 从全局解封列表中移除该用户
        passall_data = [item for item in passall_data if item["uid"] != reset_uid]
        # 从各UMO的封禁列表中移除该用户
        for umo in list(ban_data.keys()):
            ban_data[umo] = [item for item in ban_data[umo] if item["uid"] != reset_uid]
        # 从各UMO的解封列表中移除该用户
        for umo in list(pass_data.keys()):
            pass_data[umo] = [
                item for item in pass_data[umo] if item["uid"] != reset_uid
            ]
        # 将修改后的数据写回文件
        self.banall_list_path.write_text(
            json.dumps(banall_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        self.passall_list_path.write_text(
            json.dumps(passall_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        self.banlist_path.write_text(
            json.dumps(ban_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        self.passlist_path.write_text(
            json.dumps(pass_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )

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
