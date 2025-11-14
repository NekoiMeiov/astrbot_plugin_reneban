"""
用户(禁用)数据模型，获取at，判断是否禁用，并提供操作接口
"""


class InvalidKeyError(KeyError):
    pass


class BanPassUserData(dict):
    __slots__ = ()                                # 防止再挂新属性
    ALLOWED_KEYS = frozenset({"uid", "time", "reason"})
    IMMUTABLE_KEYS = frozenset({"uid"})           # 真正只读字段

    # ---------- 构造 ----------
    def __init__(self, uid: str, time: int, reason: str = "无理由"):
        super().__init__(uid=uid, time=time, reason=reason)
        for k in self.ALLOWED_KEYS:
            super().__setattr__(k, self[k])

    # ---------- 反序列化 ----------
    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BanPassUserData":
        return cls(**{k: v for k, v in data.items() if k in cls.ALLOWED_KEYS})

    # ---------- 字典通道 ----------
    def __setitem__(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise InvalidKeyError(key)
        if key in self.IMMUTABLE_KEYS and key in self:
            raise InvalidKeyError(f"{key} is immutable")
        super().__setitem__(key, value)
        super().__setattr__(key, value)

    # ---------- 属性通道 ----------
    def __setattr__(self, name, value):
        if name in self.ALLOWED_KEYS:
            self[name] = value          # 走字典通道，保证统一校验
        elif name.startswith("_") or getattr(self.__class__, name, None):
            super().__setattr__(name, value)
        else:
            raise InvalidKeyError(name)

    # ---------- 业务接口 ----------
    def update_data(self, *, time: int | None = None, reason: str | None = None):
        if time is not None:
            self["time"] = time
        if reason is not None:
            self["reason"] = reason

    # ---------- 只读属性 ----------
    @property
    def uid(self) -> str:
        return self["uid"]

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
