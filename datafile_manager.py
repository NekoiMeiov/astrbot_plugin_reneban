"""
Datafile manager for ReNeBan plugin
Handles file operations for ban lists and other data storage
"""

import json
import time
from pathlib import Path
from .user_manager import UserDataModel, UserDataList


class DatafileManager:
    """
    Manages data files for the ReNeBan plugin
    """

    def __init__(self, data_dir: Path, cache_ttl: int = 60):
        """
        初始化数据文件管理器

        Args:
            data_dir: 数据目录的Path对象
            cache_ttl: 缓存存活时间（秒），默认60秒
        """
        self.data_dir = data_dir
        # 定义文件路径
        self.banlist_path = self.data_dir / "ban_list.json"
        self.banall_list_path = self.data_dir / "banall_list.json"
        self.passlist_path = self.data_dir / "passlist.json"
        self.passall_list_path = self.data_dir / "passall_list.json"

        # 初始化缓存相关变量
        self._passlist_cache = None  # 会话解禁列表缓存 (dict[str, UserDataList])
        self._banlist_cache = None  # 会话禁用列表缓存 (dict[str, UserDataList])
        self._passall_list_cache = None  # 全局解禁列表缓存 (UserDataList)
        self._banall_list_cache = None  # 全局禁用列表缓存 (UserDataList)
        self._cache_timestamp = 0  # 缓存创建时间戳
        self._cache_ttl = cache_ttl  # 缓存存活时间（秒）

        # 初始化文件
        self._initialize_files()

    def _initialize_files(self):
        """初始化所有数据文件"""
        # 这些文件是字典结构，应初始化为空字典
        for path in [self.passlist_path, self.banlist_path]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text("{}", encoding="utf-8")

        # 这些文件是列表结构，应初始化为空列表
        for path in [self.banall_list_path, self.passall_list_path]:
            path.touch(exist_ok=True)
            if path.stat().st_size == 0:
                path.write_text("[]", encoding="utf-8")

    def _is_cache_valid(self) -> bool:
        """
        检查缓存是否有效

        Returns:
            bool: 如果缓存存在且未过期则返回 True，否则返回 False
        """
        current_time = time.time()
        return (
            all(
                cache is not None
                for cache in [
                    self._passlist_cache,
                    self._banlist_cache,
                    self._passall_list_cache,
                    self._banall_list_cache,
                ]
            )
            and current_time - self._cache_timestamp < self._cache_ttl
        )

    def _invalidate_and_reload_cache(self):
        """
        内部方法：清理并重新加载缓存
        """
        self._passlist_cache = self.read_file(self.passlist_path)
        self._banlist_cache = self.read_file(self.banlist_path)
        self._passall_list_cache = self.read_file(self.passall_list_path)
        self._banall_list_cache = self.read_file(self.banall_list_path)
        self._cache_timestamp = time.time()

    @staticmethod
    def read_file(file_path: Path) -> dict[str, UserDataList] | UserDataList:
        """
        读取JSON文件内容

        Args:
            file_path: 要读取的文件路径

        Returns:
            解析后的JSON数据，字典结构的键为字符串，值为UserDataList；列表结构为UserDataList
        """
        try:
            raw_data = file_path.read_text(encoding="utf-8")
            data = json.loads(raw_data)

            # 根据文件路径判断结构并转换为相应的对象
            if str(file_path).endswith(("ban_list.json", "passlist.json")):
                # 验证数据类型是字典
                if not isinstance(data, dict):
                    from astrbot.api import logger

                    logger.error(
                        f"文件 {file_path} 应该是字典类型，但实际是 {type(data).__name__}。返回空字典。"
                    )
                    return {}

                # 这些是字典结构 {umo: [items]}
                result = {}
                for key, value in data.items():
                    # 验证字典中的值是列表类型
                    if not isinstance(value, list):
                        from astrbot.api import logger

                        logger.error(
                            f"文件 {file_path} 中键 '{key}' 的值应该是列表类型，但实际是 {type(value).__name__}。跳过该键。"
                        )
                        continue
                    result[key] = UserDataList(
                        [UserDataModel.from_dict(item) for item in value]
                    )
                return result
            elif str(file_path).endswith(("banall_list.json", "passall_list.json")):
                # 验证数据类型是列表
                if not isinstance(data, list):
                    from astrbot.api import logger

                    logger.error(
                        f"文件 {file_path} 应该是列表类型，但实际是 {type(data).__name__}。返回空列表。"
                    )
                    return UserDataList([])

                # 这些是列表结构 [items]
                return UserDataList([UserDataModel.from_dict(item) for item in data])
            else:
                return data
        except json.JSONDecodeError as e:
            from astrbot.api import logger

            logger.error(f"无法解析JSON文件 {file_path}: {e}")
            # 根据文件路径返回对应类型的空数据结构
            if str(file_path).endswith(("ban_list.json", "passlist.json")):
                return {}
            elif str(file_path).endswith(("banall_list.json", "passall_list.json")):
                return UserDataList([])
            else:
                return {}
        except Exception as e:
            from astrbot.api import logger

            logger.error(f"读取文件 {file_path} 时发生未知错误: {e}")
            # 根据文件路径返回对应类型的空数据结构
            if str(file_path).endswith(("ban_list.json", "passlist.json")):
                return {}
            elif str(file_path).endswith(("banall_list.json", "passall_list.json")):
                return UserDataList([])
            else:
                return {}

    @staticmethod
    def write_file(
        file_path: Path, data: dict[str, UserDataList] | UserDataList
    ) -> None:
        """
        将数据写入JSON文件

        Args:
            file_path: 要写入的文件路径
            data: 要写入的数据
        """
        # 将 UserDataList/Model 对象转换为普通字典/列表
        if isinstance(data, UserDataList):
            serializable_data = [dict(item) for item in data]
        elif isinstance(data, dict):
            serializable_data = {}
            for key, value in data.items():
                if isinstance(value, UserDataList):
                    serializable_data[key] = [dict(item) for item in value]
                else:
                    serializable_data[key] = value
        else:
            serializable_data = data

        file_path.write_text(
            json.dumps(serializable_data, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    def _clear_expired_data(
        self, data: dict[str, UserDataList] | UserDataList, is_dict: bool = False
    ) -> dict[str, UserDataList] | UserDataList:
        """
        清除过期的数据项

        Args:
            data: 包含时间信息的数据
            is_dict: 是否为字典结构 (True) 或列表结构 (False)

        Returns:
            清理后的数据
        """
        import time

        current_time = int(time.time())

        if is_dict:
            # 字典结构：{umo: UserDataList}
            for key in list(data.keys()):
                # 过滤掉过期的项
                data[key] = UserDataList(
                    [
                        item
                        for item in data[key]
                        if not (item.time < current_time and item.time != 0)
                    ]
                )
                # 如果该umo下没有项目了，删除空键
                if not data[key]:
                    del data[key]
        else:
            # 列表结构：UserDataList
            # 过滤掉过期的项
            data = UserDataList(
                [
                    item
                    for item in data
                    if not (item.time < current_time and item.time != 0)
                ]
            )
        return data

    def _clear_redundant_banned(self) -> None:
        """
        清除冗余的禁用数据
        """
        # 加载所有数据
        banall_data = DatafileManager.read_file(self.banall_list_path)  # UserDataList
        passall_data = DatafileManager.read_file(self.passall_list_path)  # UserDataList
        ban_data = DatafileManager.read_file(
            self.banlist_path
        )  # dict[str, UserDataList]
        pass_data = DatafileManager.read_file(
            self.passlist_path
        )  # dict[str, UserDataList]

        # 1. 处理 pass > ban 的情况：如果 pass_time > ban_time（且 ban_time != 0）或 pass_time == 0，移除 ban
        for umo in list(ban_data.keys()):
            if umo in pass_data:
                pass_list = pass_data[umo]  # UserDataList
                ban_list = ban_data[umo]  # UserDataList

                # 创建pass项的uid到time的映射
                pass_time_map = {item.uid: item.time for item in pass_list}

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
                        or (
                            ban_item.time == 0 and pass_time_map[ban_item.uid] != 0
                        )  # 永久ban不会被非永久pass覆盖
                    ]
                )

                # 如果该umo下没有ban项了，删除空键
                if not ban_data[umo]:
                    del ban_data[umo]

        # 2. 处理 pass_all > ban_all 的情况：如果 pass_all_time > ban_all_time（且 ban_all_time != 0）或 pass_all_time == 0，移除 ban_all
        passall_time_map = {item.uid: item.time for item in passall_data}

        banall_data = UserDataList(
            [
                ban_item
                for ban_item in banall_data
                if ban_item.uid not in passall_time_map
                or (
                    passall_time_map[ban_item.uid] < ban_item.time
                    and passall_time_map[ban_item.uid] != 0
                )
                or (
                    ban_item.time == 0 and passall_time_map[ban_item.uid] != 0
                )  # 永久ban不会被非永久pass覆盖
            ]
        )

        # 3. 清理冗余的pass记录：pass_all依赖ban_all，pass依赖与它一致的umo的ban&ban_all
        # 3a. 清理passall：只保留有对应banall的uid
        banall_uids = {item.uid for item in banall_data}
        passall_data = UserDataList(
            [item for item in passall_data if item.uid in banall_uids]
        )

        # 3b. 清理pass：只保留有对应ban或banall的uid
        combined_ban_uids = set()
        # 收集所有ban_data中的uid
        for umo_ban_list in ban_data.values():
            combined_ban_uids.update(item.uid for item in umo_ban_list)
        # 添加banall_data中的uid
        combined_ban_uids.update(banall_uids)

        # 过滤pass_data
        for umo in list(pass_data.keys()):
            pass_data[umo] = UserDataList(
                [item for item in pass_data[umo] if item.uid in combined_ban_uids]
            )
            # 如果该umo下没有pass项了，删除空键
            if not pass_data[umo]:
                del pass_data[umo]

        # 保存所有数据
        DatafileManager.write_file(self.banlist_path, ban_data)
        DatafileManager.write_file(self.passlist_path, pass_data)
        DatafileManager.write_file(self.banall_list_path, banall_data)
        DatafileManager.write_file(self.passall_list_path, passall_data)

    def _clear_expired_banned(self) -> None:
        """
        清除过期的禁用数据
        """
        import time
        from astrbot.api import logger

        current_time = int(time.time())

        # 统一处理所有列表
        lists_to_clear = [
            (self.passlist_path, True),  # passlist是字典结构
            (self.banlist_path, True),  # banlist是字典结构
            (self.banall_list_path, False),  # banall_list是列表结构
            (self.passall_list_path, False),  # passall_list是列表结构
        ]

        for file_path, is_dict in lists_to_clear:
            try:
                raw_data = DatafileManager.read_file(file_path)
                cleared_data = self._clear_expired_data(raw_data, is_dict)
                DatafileManager.write_file(file_path, cleared_data)
            except Exception as e:
                # 添加错误处理，避免一个文件出错影响其他文件
                logger.error(f"清理文件 {file_path} 时出错: {e}")

    def clear_banned(self) -> None:
        """
        清除过期和冗余的禁用数据，并重建缓存
        """
        self._clear_expired_banned()
        self._clear_redundant_banned()
        # 清理并重新加载缓存
        self._invalidate_and_reload_cache()
