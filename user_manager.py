"""
用户(禁用)数据模型，获取at，判断是否禁用，并提供操作接口
"""

from astrbot.api.event import AstrMessageEvent
import astrbot.api.message_components as Comp


class AtNumberError(ValueError):
    """
    At 数量错误（ReNeBan.get_event_at() 获取@用户时，如果 At 用户数量大于 1，会抛出此错误）
    """

    pass


class InvalidKeyError(KeyError):
    pass


class UserDataModel(dict):
    __slots__ = ("_initialized", "uid", "time", "reason")  # 定义属性槽和初始化标志
    ALLOWED_KEYS = frozenset({"uid", "time", "reason"})
    IMMUTABLE_KEYS = frozenset({"uid"})  # 真正只读字段

    # ---------- 构造 ----------
    def __init__(self, uid: str, time: int, reason: str = "无理由"):
        super().__init__(uid=uid, time=time, reason=reason)
        # 直接设置属性，绕过 __setattr__ 检查
        object.__setattr__(self, "uid", uid)
        object.__setattr__(self, "time", time)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "_initialized", True)

    # ---------- 反序列化 ----------
    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "UserDataModel":
        filtered_data = {k: v for k, v in data.items() if k in cls.ALLOWED_KEYS}
        return cls(**filtered_data)

    # ---------- 字典通道 ----------
    def __setitem__(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise InvalidKeyError(key)
        if key in self.IMMUTABLE_KEYS and key in self:
            raise InvalidKeyError(f"{key} is immutable")
        super().__setitem__(key, value)
        object.__setattr__(self, key, value)

    # ---------- 属性通道 ----------
    def __setattr__(self, name, value):
        if name in self.ALLOWED_KEYS:
            # 使用字典通道以确保验证
            self[name] = value
        elif name.startswith("_") or getattr(self.__class__, name, None):
            super().__setattr__(name, value)
        else:
            raise InvalidKeyError(name)

    # ---------- 属性访问 ----------
    def __getattr__(self, name):
        # 为 uid, time, reason 提供属性访问方式
        if name in self.ALLOWED_KEYS:
            return self[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    # ---------- 业务接口 ----------
    def update_data(self, *, time: int | None = None, reason: str | None = None):
        if time is not None:
            self["time"] = time
        if reason is not None:
            self["reason"] = reason

    def add_time(self, seconds: int, reason: str | None = None):
        """
        增加时间（秒）或设置为永久
        - 如果当前为永久（time=0），则抛出异常
        - 如果传入的秒数为0，表示将记录设置为永久
        - 否则，在当前时间基础上增加相应秒数
        - reason: 可选的理由
        """
        if self.time == 0:
            raise ValueError("Cannot add time to a permanent record")

        if seconds == 0:
            # 传入0表示设为永久
            self.update_data(time=0, reason=reason)
        else:
            new_time = self.time + seconds
            self.update_data(time=new_time, reason=reason)

    def subtract_time(self, seconds: int, reason: str | None = None):
        """
        减少时间（秒）
        - 如果当前为永久且要减少的时间不为0，抛出异常
        - 如果要减少的时间为0，将时间戳设置为1（过期）
        - 否则从当前时间中减去相应秒数
        - reason: 可选的理由
        """
        if self.time == 0 and seconds != 0:
            raise ValueError("Cannot subtract time from a permanent record")

        if seconds == 0:
            # 如果减少的时间为0，将时间戳设置为1（必然过期）
            new_time = 1
        else:
            new_time = self.time - seconds

        self.update_data(time=new_time, reason=reason)


class UserDataList(list):
    """
    存放 UserDataModel 实例的列表
    """

    def __init__(self, iterable=None):
        super().__init__()
        if iterable:
            for item in iterable:
                self.append(item)

    def append(self, obj: UserDataModel):
        """
        添加一个 UserDataModel 实例到列表中
        """
        if not isinstance(obj, UserDataModel):
            raise TypeError(f"只能添加 UserDataModel 实例，但传入了 {type(obj)}")
        super().append(obj)

    def extend(self, iterable):
        """
        扩展列表，只接受 UserDataModel 实例
        """
        for item in iterable:
            self.append(item)

    def insert(self, index: int, obj: UserDataModel):
        """
        在指定位置插入 UserDataModel 实例
        """
        if not isinstance(obj, UserDataModel):
            raise TypeError(f"只能插入 UserDataModel 实例，但传入了 {type(obj)}")
        super().insert(index, obj)

    def find_by_uid(self, uid: str) -> UserDataModel | None:
        """
        根据 uid 查找用户数据
        """
        for user_data in self:
            if user_data.uid == uid:
                return user_data
        return None

    def remove_by_uid(self, uid: str) -> bool:
        """
        根据 uid 移除用户数据
        :param uid: 要移除的用户 ID
        :return: 如果找到并移除则返回 True，否则返回 False
        """
        for i, user_data in enumerate(self):
            if user_data.uid == uid:
                self.pop(i)
                return True
        return False

    def update_user(self, uid: str, new_time: int, reason: str | None = None) -> bool:
        """
        更新指定用户的禁用时间
        :param uid: 用户 ID
        :param new_time: 新的禁用时间
        :param reason: 更新理由（可选）
        :return: 如果找到用户并更新成功则返回 True，否则返回 False
        """
        user_data = self.find_by_uid(uid)
        if user_data:
            user_data.update_data(time=new_time, reason=reason)
            return True
        return False

    def update_user_reason(self, uid: str, new_reason: str) -> bool:
        """
        更新指定用户的禁用理由
        :param uid: 用户 ID
        :param new_reason: 新的禁用理由
        :return: 如果找到用户并更新成功则返回 True，否则返回 False
        """
        user_data = self.find_by_uid(uid)
        if user_data:
            user_data.update_data(reason=new_reason)
            return True
        return False

    def update_user_full(
        self, uid: str, new_time: int | None = None, new_reason: str | None = None
    ) -> bool:
        """
        更新指定用户的禁用时间与理由
        :param uid: 用户 ID
        :param new_time: 新的禁用时间（可选）
        :param new_reason: 新的禁用理由（可选）
        :return: 如果找到用户并更新成功则返回 True，否则返回 False
        """
        user_data = self.find_by_uid(uid)
        if user_data:
            user_data.update_data(time=new_time, reason=new_reason)
            return True
        return False

    def add_time_to_user(
        self, uid: str, seconds: int, reason: str | None = None
    ) -> bool:
        """
        为指定用户增加时间
        :param uid: 用户 ID
        :param seconds: 要增加的时间（秒）
        :param reason: 操作理由（可选）
        :return: 如果找到用户并操作成功则返回 True，否则返回 False
        """
        user_data = self.find_by_uid(uid)
        if user_data:
            try:
                user_data.add_time(seconds, reason)
                return True
            except ValueError:
                return False  # 如果是永久记录则无法增加时间
        return False

    def subtract_time_from_user(
        self, uid: str, seconds: int, reason: str | None = None
    ) -> bool:
        """
        为指定用户减少时间
        :param uid: 用户 ID
        :param seconds: 要减少的时间（秒）
        :param reason: 操作理由（可选）
        :return: 如果找到用户并操作成功则返回 True，否则返回 False
        """
        user_data = self.find_by_uid(uid)
        if user_data:
            try:
                user_data.subtract_time(seconds, reason)
                return True
            except ValueError:
                return False  # 如果是永久记录则无法减少时间
        return False


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
            raise AtNumberError("消息中包含多个非bot自身的 At 标记")

        # 返回第一个（也是唯一一个）At 用户，如果没有则返回 None
        return at_users[0] if at_users else None

    @staticmethod
    def is_banned(
        enable: bool, data_manager: "DatafileManager", event: AstrMessageEvent
    ):
        """
        判断用户是否被禁用，以及其理由
        """
        # 禁用功能未启用
        if not enable:
            return (False, None)
        # pass > ban > pass-all > ban-all
        # 检查缓存是否有效，如果无效则调用clear_banned重建缓存
        if not data_manager._is_cache_valid():
            data_manager.clear_banned()

        # 获取UMO
        umo = event.unified_msg_origin
        # pass - 使用缓存数据
        # 如果不存在则返回空列表
        umo_pass_list = (
            data_manager._passlist_cache.get(umo)
            if isinstance(data_manager._passlist_cache.get(umo), UserDataList)
            else UserDataList()
        )
        # 遍历umo_pass_list中用户数据的uid
        for item in umo_pass_list:
            if item.uid == event.get_sender_id():
                return (False, item.reason)
        # ban - 使用缓存数据
        # 如果不存在则返回空列表
        umo_ban_list = (
            data_manager._banlist_cache.get(umo)
            if isinstance(data_manager._banlist_cache.get(umo), UserDataList)
            else UserDataList()
        )
        # 遍历umo_ban_list中用户数据的uid
        for item in umo_ban_list:
            if item.uid == event.get_sender_id():
                return (True, item.reason)
        # pass-all - 使用缓存数据
        # 遍历passall_list中用户数据的uid
        for item in data_manager._passall_list_cache:
            if item.uid == event.get_sender_id():
                return (False, item.reason)
        # ban-all - 使用缓存数据
        # 遍历banall_list中用户数据的uid
        for item in data_manager._banall_list_cache:
            if item.uid == event.get_sender_id():
                return (True, item.reason)
        return (False, None)
