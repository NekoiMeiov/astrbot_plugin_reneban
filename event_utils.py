from astrbot.api.event import AstrMessageEvent
import astrbot.api.message_components as Comp
from astrbot.api.star import Context
from .user_manager import (
    UserDataModel,
    UserDataList,
    UmoDataModel,
    UmoDataList,
    BaseDataModel,
    BaseModelList,
)
from .datafile_manager import DatafileManager
from .exceptions import AtUserCountError


class EventUtils:
    """
    事件工具类，包含处理事件的静态方法
    """

    @staticmethod
    def get_event_at(event: AstrMessageEvent) -> str | None:
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
            raise AtUserCountError("消息中包含多个非bot自身的 At 标记")

        # 返回第一个（也是唯一一个）At 用户，如果没有则返回 None
        return at_users[0] if at_users else None

    @staticmethod
    def is_banned(
        enable: bool,
        data_manager: DatafileManager,
        context: Context,
        event: AstrMessageEvent,
    ) -> tuple[bool, str | None]:
        """
        判断用户是否被禁用，以及其理由
        """
        # 禁用功能未启用
        if not enable:
            return (False, None)

        # 检查缓存是否有效
        if data_manager.is_cache_valid():
            data_dict: dict[str, dict[str, UserDataList] | BaseModelList] = (
                data_manager.get_clear_data()
            )
        else:
            data_dict: dict[str, dict[str, UserDataList] | BaseModelList] = (
                data_manager.get_data()
            )

        # 获取UMO与UID
        umo = EventUtils.get_event_umo(context, event)
        uid = event.get_sender_id()

        # pass
        pass_data: UserDataModel | None = (
            data_dict["pass"].get(umo, UserDataList()).find_by_id(uid)
        )
        if pass_data:
            return (False, pass_data.reason)
        # ban
        ban_data: UserDataModel | None = (
            data_dict["ban"].get(umo, UserDataList()).find_by_id(uid)
        )
        if ban_data:
            return (True, ban_data.reason)
        # pass-all
        passall_data: UserDataModel | None = data_dict["passall"].find_by_id(uid)
        if passall_data:
            return (False, passall_data.reason)
        # ban-all
        banall_data: UserDataModel | None = data_dict["banall"].find_by_id(uid)
        if banall_data:
            return (True, banall_data.reason)
        # pass-umo
        passumo_data: UmoDataModel | None = data_dict["umopass"].find_by_id(umo)
        if passumo_data:
            return (False, passumo_data.reason)
        # ban-umo
        banumo_data: UmoDataModel | None = data_dict["umoban"].find_by_id(umo)
        if banumo_data:
            return (True, banumo_data.reason)
        return (False, None)

    @staticmethod
    def get_event_umo(context: Context, event: AstrMessageEvent) -> str:
        """
        获取 umo 信息 （当 unique_session 为 True 时，仍返回 platform_id:message_type:group_id 以便处理）
        """
        if (
            context.get_config()["platform_settings"]["unique_session"]
            and event.get_group_id()
        ):
            return f"{event.session.platform_id}:{event.session.message_type.value}:{event.get_group_id()}"
        return event.unified_msg_origin
