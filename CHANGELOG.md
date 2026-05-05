# v1.1.0
引入 UMO 级别的 ban 和 pass 列表，使整个会话可以被临时或永久屏蔽或豁免。（暂未实现相关命令）
添加基于 `msgpack` 的预写日志（write-ahead logging），以便在崩溃后安全地重放挂起写入。
修改了记录数据文件名，并在旧版文件存在而无相应新版文件时自动进行迁移。
用 `BaseDataModel/BaseModelList` 层级结构替换扁平用户数据结构，以集中处理 ID/时间/原因，并自动清理过期记录。
通过带线程安全锁和共享缓存校验的 `DatafileManager.sync_and_clean_data` 统一数据加载、清理和持久化。
将事件相关的辅助函数提取到 `EventUtils` 中，并在 `strings.py` 中集中处理命令错误/原因格式化和时间解析错误消息。
在 README 中阐明 `dec-*` 命令描述和时间语义，包括如何处理零/省略的时长。
在 `requirements.txt` 中新增 `msgpack` 作为运行时依赖。
增加 `CHANGELIG.md` 更新日志。