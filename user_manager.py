from collections.abc import MutableMapping
import copy
import time as time_module
from .strings import noreason_to_none
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor

from .exceptions import (
    PermanentRecordTimeSubtractionError,
    TimeNegativeError,
    PermanentRecordTimeAdditionError,
)


class _ModelListRegistry:
    """全局 BaseModelList 过期清理注册器

    维护所有活跃 BaseModelList 的弱引用，由一个后台线程定期清理过期记录。
    当 BaseModelList 实例被 GC 回收时，弱引用自动移除，无需显式反注册。
    """

    def __init__(self):
        self._lists: weakref.WeakSet["BaseModelList"] = weakref.WeakSet()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._clear_loop, daemon=True, name="ModelListClearer"
        )
        self._thread.start()

    def register(self, lst: "BaseModelList") -> None:
        """注册一个 BaseModelList 到清理任务"""
        with self._lock:
            self._lists.add(lst)

    def _clear_loop(self) -> None:
        """后台清理任务循环，每秒扫描所有注册的列表"""
        while not self._stop_event.is_set():
            # 在锁外获取快照，避免持有锁时遍历耗时
            with self._lock:
                snapshots = list(self._lists)
            for lst in snapshots:
                with lst._lock:
                    lst[:] = [
                        item
                        for item in lst
                        if item.time == 0 or item.time > time_module.time()
                    ]
                    lst._ids: set[str] = {item._get_id_field_value() for item in lst}
            snapshots = []
            self._stop_event.wait(1)


_MODEL_LIST_REGISTRY = _ModelListRegistry()


class BaseDataModel(MutableMapping):
    """基础数据模型，提供通用的数据管理功能"""

    __slots__ = ("_data", "_allowed_keys", "_id_field")

    def __init__(
        self, id_field: str, id_value: str, time: int, reason: str | None = None
    ):
        object.__setattr__(
            self,
            "_data",
            {id_field: id_value, "time": time, "reason": noreason_to_none(reason)},
        )
        object.__setattr__(
            self, "_allowed_keys", frozenset((id_field, "time", "reason"))
        )
        object.__setattr__(self, "_id_field", id_field)
        # object.__setattr__(self, "_lock", threading.RLock())

    def __getitem__(self, key):
        return object.__getattribute__(self, "_data")[key]

    def __setitem__(self, key, value):
        if key not in object.__getattribute__(self, "_allowed_keys"):
            raise KeyError(key)
        if key == self._get_id_field_name():
            raise TypeError(f"primary key {key!r} is read-only")
        if key == "time" and not isinstance(value, int):
            raise TypeError(f"time must be int, got {type(value).__name__}")
        if key == "reason" and value is not None and not isinstance(value, str):
            value = noreason_to_none(str(value))
        object.__getattribute__(self, "_data")[key] = value

    def __delitem__(self, key):
        raise TypeError("deletion is not allowed")

    def __getattr__(self, name):
        if name in object.__getattribute__(self, "_allowed_keys"):
            return self[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in object.__getattribute__(self, "_allowed_keys"):
            self[name] = value
        else:
            raise AttributeError(f"'{name}' is not a valid attribute")

    def __delattr__(self, name):
        raise TypeError("deletion is not allowed")

    def __iter__(self):
        return iter(object.__getattribute__(self, "_data"))

    def __len__(self):
        return len(object.__getattribute__(self, "_data"))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return dict(self.items()) == dict(other.items())

    def __copy__(self):
        return self.__class__(
            id_field=self._get_id_field_name(),
            id_value=self._get_id_field_value(),
            time=self.time,
            reason=self.reason,
        )

    def __deepcopy__(self):
        return copy.copy(self)

    def _get_id_field_name(self) -> str:
        """获取 id 字段名称"""
        return object.__getattribute__(self, "_id_field")

    def _get_id_field_value(self) -> str:
        """获取 id 字段值"""
        return getattr(self, self._get_id_field_name())

    def update_data(self, time: int | None = None, reason: str | None = None):
        """
        更新数据
        """
        if time is not None:
            if time < 0:
                raise TimeNegativeError("Time must be non-negative")
            self.time = time
        self.reason = noreason_to_none(reason)

    def add_time(self, time: int, reason: str | None = None):
        """
        添加时间
        """
        if time < 0:
            raise TimeNegativeError("Time must be non-negative")
        if self.time == 0:
            raise PermanentRecordTimeAdditionError(
                "Cannot add time to a permanent record"
            )
        self.update_data(time=0 if time == 0 else self.time + time, reason=reason)

    def subtract_time(self, time: int, reason: str | None = None):
        """
        减去时间
        """
        if time < 0:
            raise TimeNegativeError("Time must be non-negative")
        if self.time == 0 and time != 0:
            raise PermanentRecordTimeSubtractionError(
                "Cannot subtract a finite amount of time from a permanent record"
            )
        self.update_data(
            time=1 if time == 0 else max(1, self.time - time), reason=reason
        )

    def to_dict(self) -> dict[str, str | int]:
        """转换为字典"""
        return {
            k: v
            for k, v in object.__getattribute__(self, "_data").items()
            if v is not None
        }


class BaseModelList(list):
    """基础模型列表，提供通用的列表管理功能"""

    def __init__(self, model_class: type[BaseDataModel], iterable: list | None = None):
        super().__init__()
        self.model_class = model_class
        self._ids: set[str] = set()
        self._lock = threading.RLock()
        _MODEL_LIST_REGISTRY.register(self)
        if iterable:
            self.extend(iterable)

    def __setitem__(self, key, value):
        with self._lock:
            if not isinstance(value, self.model_class):
                raise TypeError(
                    f"{self.__class__.__name__} can only hold instances of {self.model_class.__name__}, but {type(value)} was passed in."
                )

            if value._get_id_field_value() in self._ids:
                self.remove_by_id(value._get_id_field_value())
            else:
                self._ids.add(value._get_id_field_value())
            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            self._ids.remove(self[key]._get_id_field_value())
            super().__delitem__(key)

    def __copy__(self):
        return self.__class__(model_class=self.model_class, iterable=self)

    def __deepcopy__(self):
        return self.__class__(
            model_class=self.model_class, iterable=[copy.copy(m) for m in self]
        )

    def remove(self, value):
        with self._lock:
            self._ids.remove(value._get_id_field_value())
            super().remove(value)

    def append(self, value):
        with self._lock:
            if not isinstance(value, self.model_class):
                raise TypeError(
                    f"{self.__class__.__name__} can only hold instances of {self.model_class.__name__}, but {type(value)} was passed in."
                )

            if value._get_id_field_value() in self._ids:
                self.remove_by_id(value._get_id_field_value())
            else:
                self._ids.add(value._get_id_field_value())
            super().append(value)

    def extend(self, iterable):
        with self._lock:
            for item in iterable:
                self.append(item)

    def find_by_id(self, id_value: str, no_copy: bool = False) -> BaseDataModel | None:
        """根据ID查找数据"""
        with self._lock:
            for item in self:
                if item._get_id_field_value() == id_value:
                    return item if no_copy else copy.copy(item)
            return None

    def remove_by_id(self, id_value: str) -> bool:
        """根据ID移除数据"""
        with self._lock:
            for idx, item in enumerate(self):
                if item._get_id_field_value() == id_value:
                    del self[idx]
                    return True
            return False

    def update_data(
        self, id_value: str, time: int | None = None, reason: str | None = None
    ) -> bool:
        """更新数据"""
        with self._lock:
            item = self.find_by_id(id_value, no_copy=True)
            if item is None:
                return False
            item.update_data(time=time, reason=reason)
            return True

    def add_time_to_data(
        self, id_value: str, time: int, reason: str | None = None
    ) -> bool:
        """为指定数据增加时间"""
        with self._lock:
            item = self.find_by_id(id_value, no_copy=True)
            if item is None:
                return False
            item.add_time(time=time, reason=reason)
            return True

    def subtract_time_from_data(
        self, id_value: str, time: int, reason: str | None = None
    ) -> bool:
        """为指定数据减少时间"""
        with self._lock:
            item = self.find_by_id(id_value, no_copy=True)
            if item is None:
                return False
            item.subtract_time(time=time, reason=reason)
            return True

    def to_list(self) -> list[dict[str, str | int]]:
        with self._lock:
            return [m.to_dict() for m in self]


class UserDataModel(BaseDataModel):
    """用户数据模型，继承自 BaseDataModel，使用 uid 作为主键"""

    def __init__(self, id_value: str, time: int, reason: str | None = None):
        super().__init__(id_field="uid", id_value=id_value, time=time, reason=reason)

    def __copy__(self):
        return self.__class__(
            id_value=self._get_id_field_value(),
            time=self.time,
            reason=self.reason,
        )


class UserDataList(BaseModelList):
    """用户数据列表，继承自 BaseModelList，使用 uid 作为主键"""

    def __init__(self, iterable: list | None = None):
        super().__init__(model_class=UserDataModel, iterable=iterable)


class UmoDataModel(BaseDataModel):
    """用户数据模型，继承自 BaseDataModel，使用 umo 作为主键"""

    def __init__(self, id_value: str, time: int, reason: str | None = None):
        super().__init__(id_field="umo", id_value=id_value, time=time, reason=reason)

    def __copy__(self):
        return self.__class__(
            id_value=self._get_id_field_value(),
            time=self.time,
            reason=self.reason,
        )


class UmoDataList(BaseModelList):
    """用户数据列表，继承自 BaseModelList，使用 umo 作为主键"""

    def __init__(self, iterable: list | None = None):
        super().__init__(model_class=UmoDataModel, iterable=iterable)
