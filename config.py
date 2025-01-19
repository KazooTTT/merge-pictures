# 图片处理相关配置
IMAGE_CONFIG = {
    # 支持的图片格式
    "SUPPORTED_FORMATS": (".png", ".jpg", ".jpeg"),
    # 排除包含以下字符串的文件
    "EXCLUDE_PATTERNS": ["_not"],
    # 目标分组数量
    "TARGET_GROUP_COUNT": 9,
    # 压缩设置
    "MAX_SIZE_MB": 7,
    # 初始压缩质量
    "INITIAL_QUALITY": 95,
    # 最低压缩质量
    "MIN_QUALITY": 5,
    # 质量递减步长
    "QUALITY_STEP": 5,
}

# 输出相关配置
OUTPUT_CONFIG = {
    # 输出目录名
    "OUTPUT_DIR": "output",
    # 输出文件名格式
    "OUTPUT_FILENAME_TEMPLATE": "merged_result_{timestamp}_group{group_num}.jpg",
}
