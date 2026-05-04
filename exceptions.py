class AtUserCountError(ValueError):
    """
    At 数量错误（EventUtils.get_event_at() 获取@用户时，如果 At 用户数量大于 1，会抛出此错误）
    """

    pass


class TimestrValueError(ValueError):
    """
    时间字符串格式错误（tiime_utils.timestr_to_int() 转换时间字符串时，如果时间字符串格式错误，会抛出此错误）
    """

    def __init__(self, timestr: str):
        self.invalid_timestr: str = timestr
        super().__init__(f"Invalid time string: {timestr!r}")

    pass


class TimeNegativeError(ValueError):
    """
    时间负数错误（使用 DataModel 的 update_data() 方法时，如果 time 参数为负数，会抛出此错误）
    """

    pass


class PermanentRecordTimeError(ValueError):
    """
    永久记录时间错误（是 PermanentRecordTimeAdditionError 和 PermanentRecordTimeSubtractionError 的基类）
    """

    pass


class PermanentRecordTimeAdditionError(PermanentRecordTimeError):
    """
    永久记录时间添加错误（使用 DataModel 的 add_time() 方法时，如果实例为永久记录，会抛出此错误）
    """

    pass


class PermanentRecordTimeSubtractionError(PermanentRecordTimeError):
    """
    永久记录时间减法错误（使用 DataModel 的 subtract_time() 方法时，如果对永久记录减去有限时间，会抛出此错误）
    """

    pass


class WALFileExistsError(RuntimeError):
    """WAL 文件已存在（使用 DatafileManager 的 _write_commits() 方法时，如果 WAL 相关文件存在，会抛出此错误）"""

    pass
