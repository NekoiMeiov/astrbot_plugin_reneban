from astrbot.api.event import AstrMessageEvent
import astrbot.api.message_components as Comp
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


def get_real_umo(event: AstrMessageEvent) -> str:
    """
    获取真实的会话 UMO，绕过隔离会话（unique_session）对 session_id 的改写。
    使用 message_obj.session_id，该值由平台适配器设置，不受 unique_session 影响。
    """
    original_session_id = event.message_obj.session_id
    platform_id = event.get_platform_id()
    msg_type = event.get_message_type().value
    return f"{platform_id}:{msg_type}:{original_session_id}"


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
    def is_banned(enable: bool, data_manager: DatafileManager, event: AstrMessageEvent):
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
        umo = get_real_umo(event)
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
