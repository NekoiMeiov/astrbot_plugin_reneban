"""
Datafile manager for ReNeBan plugin
Handles file operations for ban lists and other data storage
"""

import json
import copy
import time as time_module
import threading
import msgpack
from typing import Literal, overload
from pathlib import Path
from .user_manager import (
    UserDataModel,
    UserDataList,
    UmoDataModel,
    UmoDataList,
    BaseDataModel,
    BaseModelList,
)

from astrbot.api import logger


class DatafileManager:
    """
    Manages data files for ReNeBan plugin
    """

    def __init__(self, data_dir: Path, cache_ttl: int = 60):
        """
        初始化数据文件管理器

        Args:
            data_dir: 数据目录的Path对象
            cache_ttl: 缓存存活时间（秒），默认60秒
        """
        self.data_dir = data_dir
        # 定义文件路径/文件名
        self.banlist_filename = "ban_list.json"
        self.banall_list_filename = "banall_list.json"
        self.passlist_filename = "pass_list.json"
        self.passall_list_filename = "passall_list.json"
        self.umo_ban_list_filename = "umo_ban_list.json"
        self.umo_pass_list_filename = "umo_pass_list.json"

        self._WAL_path = self.data_dir / ".WAL.msgpack"
        self._WAL_ready_path = self.data_dir / ".WAL.ready"

        # sync锁
        self._sync_lock = threading.Lock()

        # 写入提交变量
        self._commits: dict[str, str] = {}

        # 初始化缓存相关变量
        self._passlist_cache: dict[str, UserDataList]  # 会话解禁列表缓存
        self._banlist_cache: dict[str, UserDataList]  # 会话禁用列表缓存
        self._passall_list_cache: UserDataList  # 全局解禁列表缓存
        self._banall_list_cache: UserDataList  # 全局禁用列表缓存
        self._umo_ban_list_cache: UmoDataList  # UMO禁用列表缓存
        self._umo_pass_list_cache: UmoDataList  # UMO解禁列表缓存
        self._cache_timestamp: int = 0  # 缓存创建时间戳
        self._cache_ttl: int = cache_ttl  # 缓存存活时间（秒）

        # 初始化文件
        self._initialize_files()

        if self._WAL_path.exists() and self._WAL_ready_path.exists():
            # 崩溃重放
            self._WAL_write(False)

        self.sync_and_clean_data(no_return=True)

    def _initialize_files(self):
        """初始化所有必要数据文件"""
        # 迁移：旧版 passlist.json -> 新版 pass_list.json，banlist同理
        old_passlist = self.data_dir / "passlist.json"
        old_banlist = self.data_dir / "banlist.json"
        if (
            old_passlist.exists()
            and not (self.data_dir / self.passlist_filename).exists()
        ):
            old_passlist.rename(self.data_dir / self.passlist_filename)
        if (
            old_banlist.exists()
            and not (self.data_dir / self.banlist_filename).exists()
        ):
            old_banlist.rename(self.data_dir / self.banlist_filename)

        # 这些文件是字典结构，应初始化为空字典
        for path in [
            self.data_dir / self.passlist_filename,
            self.data_dir / self.banlist_filename,
        ]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text("{}", encoding="utf-8")

        # 这些文件是列表结构，应初始化为空列表
        for path in [
            self.data_dir / self.banall_list_filename,
            self.data_dir / self.passall_list_filename,
            self.data_dir / self.umo_ban_list_filename,
            self.data_dir / self.umo_pass_list_filename,
        ]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text("[]", encoding="utf-8")

    def is_cache_valid(self) -> bool:
        """
        检查缓存是否有效

        Returns:
            bool: 如果缓存存在且未过期则返回 True，否则返回 False
        """
        return (
            all(
                cache is not None
                for cache in [
                    self._passlist_cache,
                    self._banlist_cache,
                    self._passall_list_cache,
                    self._banall_list_cache,
                    self._umo_ban_list_cache,
                    self._umo_pass_list_cache,
                ]
            )
            and int(time_module.time()) - self._cache_timestamp < self._cache_ttl
        )

    def _invalidate_and_reload_cache(
        self,
        banall_data: UserDataList,
        passall_data: UserDataList,
        ban_data: dict[str, UserDataList],
        pass_data: dict[str, UserDataList],
        umoban_data: UmoDataList,
        umopass_data: UmoDataList,
    ) -> None:
        """
        内部方法：清理并重新加载缓存
        """
        self._passlist_cache = pass_data
        self._banlist_cache = ban_data
        self._passall_list_cache = passall_data
        self._banall_list_cache = banall_data
        self._umo_ban_list_cache = umoban_data
        self._umo_pass_list_cache = umopass_data
        self._cache_timestamp = int(time_module.time())

    def _safe_pathjoin(self, dir_path: Path, filename: str) -> Path:
        """
        在 filename 可能来源于外部输入时，安全的使拼接的路径在 dir_path 内（不支持跨出 dir_path 目录的符号链接）

        Args:
            dir_path: 要拼接的父路径，应是一个目录
            filename: 要拼接的子路径

        Return:
            拼接后的路径（若超出则返回dir_path）
        """
        full_path = (dir_path / filename).resolve()
        return full_path if full_path.is_relative_to(dir_path) else dir_path

    def _read_file(self, filename: str) -> dict[str, UserDataList] | BaseModelList:
        """
        读取JSON文件内容

        Args:
            filename: 要读取的文件名（支持使用“/”读取子目录）

        Returns:
            解析后的JSON数据，字典结构的键为字符串，值为UserDataList；列表结构为UserDataList
        """
        file_path = self._safe_pathjoin(self.data_dir, filename)
        if not file_path.exists():
            logger.error(f"{file_path} 不存在")
            raise FileNotFoundError(f"{file_path} 不存在")
        if file_path.is_dir():
            logger.error(f"{file_path} 是目录，无法读取")
            raise IsADirectoryError(f"{file_path} 是目录，无法读取")

        try:
            raw_data = file_path.read_text(encoding="utf-8")
            data = json.loads(raw_data)
        except Exception as e:
            backup_filename = (
                f"{file_path.stem}_{int(time_module.time())}{file_path.suffix}.bak"
            )
            file_path.rename(file_path.parent / backup_filename)
            self._initialize_files()
            logger.error(
                f"文件 {file_path} 解析失败：{e}\n已将其重命名为 {backup_filename} 并重新初始化必要数据文件。读取操作继续。"
            )
            raw_data = file_path.read_text(encoding="utf-8")
            data = json.loads(raw_data)

        # 根据文件路径判断结构并转换为相应的对象
        if file_path.name in (self.banlist_filename, self.passlist_filename):
            # 验证数据类型是字典
            if not isinstance(data, dict):
                logger.error(
                    f"文件 {file_path} 应该是字典类型，但实际是 {type(data).__name__}。返回空字典。"
                )
                return {}

            # 这些是字典结构 {umo: [items]}
            result = {}
            for key, value in data.items():
                # 验证字典中的值是列表类型
                if not isinstance(value, list):
                    logger.error(
                        f"文件 {file_path} 中键 '{key}' 的值应该是列表类型，但实际是 {type(value).__name__}。跳过该键。"
                    )
                    continue
                result[key] = UserDataList(
                    [
                        UserDataModel(
                            uid=item["uid"],
                            time=item["time"],
                            reason=item.get("reason"),
                        )
                        for item in value
                        if "uid" in item
                        and "time" in item
                        and isinstance(item["uid"], str)
                        and isinstance(item["time"], int)
                        and (
                            item.get("reason") is None
                            or isinstance(item.get("reason"), str)
                        )
                    ]
                )
            return result
        elif file_path.name in (self.banall_list_filename, self.passall_list_filename):
            # 验证数据类型是列表
            if not isinstance(data, list):
                logger.error(
                    f"文件 {file_path} 应该是列表类型，但实际是 {type(data).__name__}。返回空列表。"
                )
                return UserDataList([])

            # 这些是列表结构 [items]
            return UserDataList(
                [
                    UserDataModel(
                        uid=item["uid"],
                        time=item["time"],
                        reason=item.get("reason"),
                    )
                    for item in data
                    if "uid" in item
                    and "time" in item
                    and isinstance(item["uid"], str)
                    and isinstance(item["time"], int)
                    and (
                        item.get("reason") is None
                        or isinstance(item.get("reason"), str)
                    )
                ]
            )
        elif file_path.name in (
            self.umo_ban_list_filename,
            self.umo_pass_list_filename,
        ):
            # 验证数据类型是列表
            if not isinstance(data, list):
                logger.error(
                    f"文件 {file_path} 应该是列表类型，但实际是 {type(data).__name__}。返回空列表。"
                )
                return UmoDataList([])

            # 这些是列表结构 [items]
            return UmoDataList(
                [
                    UmoDataModel(
                        umo=item["umo"],
                        time=item["time"],
                        reason=item.get("reason"),
                    )
                    for item in data
                    if "umo" in item
                    and "time" in item
                    and isinstance(item["umo"], str)
                    and isinstance(item["time"], int)
                    and (
                        item.get("reason") is None
                        or isinstance(item.get("reason"), str)
                    )
                ]
            )
        else:
            return data

    def _write_file_commit(
        self, filename: str, data: dict[str, UserDataList] | BaseModelList
    ):
        """
        将需要写入的数据提交

        Args:
            filename: 要写入的文件名（支持使用“/”创建子目录）
            data: 要写入的数据
        """
        # 将 ModelList/Model 对象转换为普通字典/列表
        if isinstance(data, BaseModelList):
            serializable_data: list[dict[str, str | int]] = data.to_list()
        elif isinstance(data, dict):
            serializable_data: dict[str, list[dict[str, str | int]]] = {}
            for key, value in data.items():
                if isinstance(value, UserDataList):
                    serializable_data[key] = value.to_list()
                else:
                    logger.error(f"无法序列化数据：{value}")
                    serializable_data[key] = value
        else:
            logger.error(f"无法序列化数据：{data}")
            serializable_data = data

        # 写入 self._commits
        self._commits[filename] = json.dumps(
            serializable_data, indent=4, ensure_ascii=False
        )

    def _write_commits(self):
        """
        将提交写入相应的文件
        """
        if self._WAL_path.exists() and self._WAL_ready_path.exists():
            # 通常因用户手动创建了相关文件导致
            WAL_backup_filename = f"WAL_{str(int(time_module.time()))}.bak"
            self._WAL_path.rename(self.data_dir / WAL_backup_filename)
            logger.warning(f"存在 WAL 文件，已将其重命名为 {WAL_backup_filename}")
        self._WAL_path.write_bytes(msgpack.packb(self._commits, use_bin_type=True))
        # 用户可能手动创建了 WAL ready 文件，而没有创建 WAL 文件
        self._WAL_ready_path.touch(exist_ok=True)
        self._WAL_write(True)

    def _WAL_write(self, from_syncfun: bool):
        """
        真正写入数据的方法，请确保 WAL 文件存在

        Args:
            from_syncfun: 若调用来源是 sync_and_clean_data() 方法，则请置为True；若调用来源是 __init__() （崩溃重放），则请置为False
        """

        def unpack_WAL() -> dict[str, str]:
            """
            WAL 文件解包器
            """
            try:
                data = msgpack.unpackb(self._WAL_path.read_bytes(), raw=False)
                if not isinstance(data, dict):
                    raise ValueError("WAL 解包出的对象类型不合法")
                for key, value in data.items():
                    if not isinstance(key, str) or not isinstance(value, str):
                        raise ValueError("WAL 解包出的对象类型不合法")
                return data
            except Exception as e:
                WAL_backup_filename = "WAL_" + str(int(time_module.time())) + ".bak"
                self._WAL_path.rename(self.data_dir / WAL_backup_filename)
                logger.error(
                    f"在 WAL 解包时出现异常：{e}\n已将其重命名为 {WAL_backup_filename}，并跳过本次数据写入"
                )
                # 直接返回空字典，即无任何需写入数据
                return {}

        datas: dict[str, str] = self._commits if from_syncfun else unpack_WAL()
        for filename, data in datas.items():
            file_path = self._safe_pathjoin(self.data_dir, filename)
            if file_path.is_dir() and file_path.exists():
                logger.error(f"{file_path} 是一个目录，无法写入数据，将跳过该写入操作")
                continue
            file_path.write_text(data, encoding="utf-8")
        self._WAL_ready_path.unlink()
        # 可能因解包失败导致 WAL 文件不存在
        self._WAL_path.unlink(missing_ok=True)

    @overload
    def get_data(self, data_name: str) -> dict[str, UserDataList] | BaseModelList: ...

    @overload
    def get_data(
        self, data_name: list[str] | None = None
    ) -> dict[str, dict[str, UserDataList] | BaseModelList]: ...

    def get_data(self, data_name=None):
        """
        获取数据

        Args:
            data_name: 要获取的数据的名称，可以是单个字符串或列表。如果为None，则返回所有数据；如果为列表，则返回包含指定名称的数据项的的字典；如果为单个字符串，则返回指定名称的数据项。

        Returns:
            包含指定名称的数据项的字典（dict[str, dict[str, UserDataList] | BaseModelList]）或指定名称的数据项（dict[str, UserDataList] | BaseModelList）
        """
        if isinstance(data_name, str):
            return self.sync_and_clean_data(need_data=[data_name])[data_name]
        else:
            return self.sync_and_clean_data(need_data=data_name)

    @overload
    def write_data(
        self, data_name: str, data: dict[str, UserDataList] | BaseModelList
    ) -> None: ...

    @overload
    def write_data(
        self, data_name: list[str], data: list[dict[str, UserDataList] | BaseModelList]
    ) -> None: ...

    def write_data(self, data_name, data):
        if isinstance(data_name, str):
            return self.sync_and_clean_data(no_return=True, have_data={data_name: data})
        else:
            return self.sync_and_clean_data(
                no_return=True,
                have_data=dict(zip(data_name, data)),
            )

    def _clear_redundant_banned(
        self,
        banall_data: UserDataList,
        passall_data: UserDataList,
        ban_data: dict[str, UserDataList],
        pass_data: dict[str, UserDataList],
        umoban_data: UmoDataList,
        umopass_data: UmoDataList,
    ) -> tuple[
        UserDataList,
        UserDataList,
        dict[str, UserDataList],
        dict[str, UserDataList],
        UmoDataList,
        UmoDataList,
    ]:
        """
        清除冗余的禁用数据
        """

        # 1. 处理 pass > ban 的情况：如果 pass_time > ban_time（且 ban_time != 0）或 pass_time == 0，移除 ban
        for umo in list(ban_data.keys()):
            if umo in pass_data:
                pass_list: UserDataList = pass_data[umo]
                ban_list: UserDataList = ban_data[umo]

                # 创建pass项的uid到time的映射
                pass_time_map: dict[str, int] = {
                    item.uid: item.time for item in pass_list
                }

                # 过滤ban_list，移除被pass覆盖的记录
                # 如果用户有pass记录，只有在pass时间不晚于ban时间且两者都不是永久时才保留ban
                # 永久pass会覆盖永久ban，所以如果pass是永久，ban要被移除
                ban_data[umo] = UserDataList(
                    [
                        ban_item
                        for ban_item in ban_list
                        if ban_item.uid not in pass_time_map
                        or (
                            pass_time_map[ban_item.uid] < ban_item.time
                            and pass_time_map[ban_item.uid] != 0
                        )
                        or (ban_item.time == 0 and pass_time_map[ban_item.uid] != 0)
                    ]
                )

                # 如果该umo下没有ban项了，删除空键
                if not ban_data[umo]:
                    del ban_data[umo]

        # 2. 处理 pass_all > ban_all 的情况：如果 pass_all_time > ban_all_time（且 ban_all_time != 0）或 pass_all_time == 0，移除 ban_all
        passall_time_map: dict[str, int] = {
            item.uid: item.time for item in passall_data
        }

        banall_data = UserDataList(
            [
                ban_item
                for ban_item in banall_data
                if ban_item.uid not in passall_time_map
                or (
                    passall_time_map[ban_item.uid] < ban_item.time
                    and passall_time_map[ban_item.uid] != 0
                )
                or (ban_item.time == 0 and passall_time_map[ban_item.uid] != 0)
            ]
        )

        umopass_time_map: dict[str, int] = {
            item.umo: item.time for item in umopass_data
        }

        umoban_data = UmoDataList(
            [
                ban_item
                for ban_item in umoban_data
                if ban_item.umo not in umopass_time_map
                or (
                    umopass_time_map[ban_item.umo] < ban_item.time
                    and umopass_time_map[ban_item.umo] != 0
                )
                or (ban_item.time == 0 and umopass_time_map[ban_item.umo] != 0)
            ]
        )

        # 3. 清理冗余的pass记录：pass_umo依赖ban_umo，pass_all依赖ban_all&任意的ban_umo，pass依赖与它一致的umo的ban&ban_all&任意的ban_umo
        # 3a. 清理pass_umo：只保留有对应ban_umo的umo
        banumo_umos: set[str] = {item.umo for item in umoban_data}
        umopass_data = UmoDataList(
            [item for item in umopass_data if item.umo in banumo_umos]
        )
        # 3b. 清理pass_all：只保留有对应ban_all的uid
        # 在umoban_data不为空的情况下，clear_all不执行
        if not umoban_data:
            banall_uids: set[str] = {item.uid for item in banall_data}
            passall_data = UserDataList(
                [item for item in passall_data if item.uid in banall_uids]
            )
            # 3c. 清理pass：只保留有对应ban或banall的uid
            # 在umoban_data不为空的情况下，clear不执行
            for umo in list(pass_data.keys()):
                combined_ban_uids: set[str] = set(banall_uids)
                combined_ban_uids.update(
                    item.uid for item in ban_data.get(umo, UserDataList())
                )
                pass_data[umo] = UserDataList(
                    [item for item in pass_data[umo] if item.uid in combined_ban_uids]
                )
                # 如果该umo下没有pass项了，删除空键
                if not pass_data[umo]:
                    del pass_data[umo]

        return banall_data, passall_data, ban_data, pass_data, umoban_data, umopass_data

    @overload
    def sync_and_clean_data(
        self,
        no_return: Literal[True],
        need_data: list[str] | None = None,
        have_data: dict[str, dict[str, UserDataList] | BaseModelList] | None = None,
        no_copy: bool = False,
    ) -> None: ...

    @overload
    def sync_and_clean_data(
        self,
        no_return: Literal[False] = False,
        need_data: list[str] | None = None,
        have_data: dict[str, dict[str, UserDataList] | BaseModelList] | None = None,
        no_copy: bool = False,
    ) -> dict[str, dict[str, UserDataList] | BaseModelList]: ...

    def sync_and_clean_data(
        self, no_return=False, need_data=None, have_data=None, no_copy=False
    ) -> dict[str, dict[str, UserDataList] | BaseModelList] | None:
        """
        清洗数据并同步至磁盘

        Args:
            no_return: 是否不返回数据，默认返回
            need_data: 若需要返回数据，则此处为需要的数据名（ban/pass/banall/passall/umoban/umopass）
            have_data: 替代从磁盘中读出的数据，通常用于写入相关方法
            no_copy: 直接返回相应的对象，该对象与缓存指向的对象一致

        Returns:
            清理后的数据/None
        """
        # 获取锁，避免并发问题
        with self._sync_lock:
            # 提交置空
            self._commits = {}
            # 取数据（优先从 have_data 获取）
            # 将 None 初始化为空字典（因为我懒得加 if 了）
            have_data: dict[str, dict[str, UserDataList] | BaseModelList] = (
                {} if have_data is None else have_data
            )
            banall_data: UserDataList = (
                copy.deepcopy(have_data["banall"])
                if "banall" in have_data
                and isinstance(have_data["banall"], UserDataList)
                else self._read_file(self.banall_list_filename)
            )
            passall_data: UserDataList = (
                copy.deepcopy(have_data["passall"])
                if "passall" in have_data
                and isinstance(have_data["passall"], UserDataList)
                else self._read_file(self.passall_list_filename)
            )
            ban_data: dict[str, UserDataList] = (
                copy.deepcopy(have_data["ban"])
                if "ban" in have_data and isinstance(have_data["ban"], dict)
                else self._read_file(self.banlist_filename)
            )
            pass_data: dict[str, UserDataList] = (
                copy.deepcopy(have_data["pass"])
                if "pass" in have_data and isinstance(have_data["pass"], dict)
                else self._read_file(self.passlist_filename)
            )
            umoban_data: UmoDataList = (
                copy.deepcopy(have_data["umoban"])
                if "umoban" in have_data
                and isinstance(have_data["umoban"], UmoDataList)
                else self._read_file(self.umo_ban_list_filename)
            )
            umopass_data: UmoDataList = (
                copy.deepcopy(have_data["umopass"])
                if "umopass" in have_data
                and isinstance(have_data["umopass"], UmoDataList)
                else self._read_file(self.umo_pass_list_filename)
            )

            # 开始清理
            (
                banall_data,
                passall_data,
                ban_data,
                pass_data,
                umoban_data,
                umopass_data,
            ) = self._clear_redundant_banned(
                banall_data,
                passall_data,
                ban_data,
                pass_data,
                umoban_data,
                umopass_data,
            )

            self._write_file_commit(self.banall_list_filename, banall_data)
            self._write_file_commit(self.passall_list_filename, passall_data)
            self._write_file_commit(self.banlist_filename, ban_data)
            self._write_file_commit(self.passlist_filename, pass_data)
            self._write_file_commit(self.umo_ban_list_filename, umoban_data)
            self._write_file_commit(self.umo_pass_list_filename, umopass_data)

            self._write_commits()

            self._invalidate_and_reload_cache(
                banall_data,
                passall_data,
                ban_data,
                pass_data,
                umoban_data,
                umopass_data,
            )

            if no_return:
                return None

            full_data: dict[str, dict[str, UserDataList] | BaseModelList] = {
                "banall": banall_data,
                "passall": passall_data,
                "ban": ban_data,
                "pass": pass_data,
                "umoban": umoban_data,
                "umopass": umopass_data,
            }

            if not no_copy:
                full_data = {
                    key: copy.deepcopy(value) for key, value in full_data.items()
                }

            if need_data and all(key in full_data for key in need_data):
                return {key: full_data[key] for key in need_data}
            return full_data

    @overload
    def get_clear_data(
        self, data_name: str
    ) -> dict[str, UserDataList] | BaseModelList: ...

    @overload
    def get_clear_data(
        self, data_name: list[str] | None = None
    ) -> dict[str, dict[str, UserDataList] | BaseModelList]: ...

    def get_clear_data(self, data_name=None, no_copy=False):
        """
        获取缓存数据

        Args:
            data_name: 要获取的缓存数据的名称，可以是单个字符串或列表。如果为None，则返回所有数据；如果为列表，则返回包含指定名称的数据项的的字典；如果为单个字符串，则返回指定名称的数据项。
            no_copy: 直接返回相应的对象，该对象与缓存指向的对象一致

        Returns:
            包含指定名称的数据项的字典（dict[str, dict[str, UserDataList] | BaseModelList]）或指定名称的数据项（dict[str, UserDataList] | BaseModelList）
        """
        full_data = {
            "banall": self._banall_list_cache,
            "passall": self._passall_list_cache,
            "ban": self._banlist_cache,
            "pass": self._passlist_cache,
            "umoban": self._umo_ban_list_cache,
            "umopass": self._umo_pass_list_cache,
        }
        if not no_copy:
            full_data = {key: copy.deepcopy(value) for key, value in full_data.items()}
        if isinstance(data_name, str):
            return full_data[data_name]
        elif data_name and all(key in full_data for key in data_name):
            return {key: full_data[key] for key in data_name}
        return full_data
