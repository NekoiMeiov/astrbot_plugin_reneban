"""
Datafile manager for ReNeBan plugin
Handles file operations for ban lists and other data storage
"""
import json
from pathlib import Path


class DatafileManager:
    """
    Manages data files for the ReNeBan plugin
    """
    
    def __init__(self, data_dir: Path):
        """
        初始化数据文件管理器
        
        Args:
            data_dir: 数据目录的Path对象
        """
        self.data_dir = data_dir
        # 定义文件路径
        self.banlist_path = self.data_dir / "ban_list.json"
        self.banall_list_path = self.data_dir / "banall_list.json"
        self.passlist_path = self.data_dir / "passlist.json"
        self.passall_list_path = self.data_dir / "passall_list.json"
        
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
    
    @staticmethod
    def read_file(file_path: Path) -> dict | list | object:
        """
        读取JSON文件内容

        Args:
            file_path: 要读取的文件路径

        Returns:
            解析后的JSON数据
        """
        raw_data = file_path.read_text(encoding="utf-8")
        return json.loads(raw_data)

    @staticmethod
    def write_file(file_path: Path, data: dict | list | object) -> None:
        """
        将数据写入JSON文件

        Args:
            file_path: 要写入的文件路径
            data: 要写入的数据
        """
        file_path.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
    
    def _clear_expired_data(self, data: dict | list, is_dict: bool = False) -> dict | list:
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

    def _clear_redundant_banned(self) -> None:
        """
        清除冗余的禁用数据
        """
        # 加载所有数据
        banall_data = DatafileManager.read_file(self.banall_list_path)
        passall_data = DatafileManager.read_file(self.passall_list_path)
        ban_data = DatafileManager.read_file(self.banlist_path)
        pass_data = DatafileManager.read_file(self.passlist_path)

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
        清除过期和冗余的禁用数据
        """
        self._clear_expired_banned()
        self._clear_redundant_banned()