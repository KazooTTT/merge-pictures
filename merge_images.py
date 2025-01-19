import io
import os
import re
from datetime import datetime
from PIL import Image
from config import IMAGE_CONFIG, OUTPUT_CONFIG


def natural_sort_key(s):
    # 将字符串中的数字部分转换为整数，用于自然排序
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split("([0-9]+)", s)
    ]


def compress_image(image, max_size_mb=IMAGE_CONFIG["MAX_SIZE_MB"]):
    """压缩图片到指定大小以下"""
    max_size_bytes = max_size_mb * 1024 * 1024
    quality = IMAGE_CONFIG["INITIAL_QUALITY"]
    output = io.BytesIO()

    image.save(output, format="JPEG", quality=quality)

    while output.tell() > max_size_bytes and quality > IMAGE_CONFIG["MIN_QUALITY"]:
        output = io.BytesIO()
        quality -= IMAGE_CONFIG["QUALITY_STEP"]
        image.save(output, format="JPEG", quality=quality, optimize=True)

    return output, quality


def merge_images_vertically(folder_path):
    # Create output directory if it doesn't exist
    output_dir = os.path.join(folder_path, OUTPUT_CONFIG["OUTPUT_DIR"])
    os.makedirs(output_dir, exist_ok=True)

    # 获取文件夹中的所有图片文件，排除指定模式的文件
    image_files = [
        f
        for f in os.listdir(folder_path)
        if f.lower().endswith(IMAGE_CONFIG["SUPPORTED_FORMATS"])
        and not any(pattern in f for pattern in IMAGE_CONFIG["EXCLUDE_PATTERNS"])
    ]

    # 使用自然排序
    image_files.sort(key=natural_sort_key)
    print("排序后的文件列表：", image_files)

    target_group = IMAGE_CONFIG["TARGET_GROUP_COUNT"]
    average_group_count = len(image_files) // target_group
    print(f"平均每组图片数量：{average_group_count}")
    # 按5张一组分组处理
    for i in range(0, len(image_files), average_group_count):
        # 获取当前组的图片（最多5张）
        current_group = image_files[i : i + average_group_count]

        # 打开当前组的所有图片，保持原始模式
        images = []
        for img_file in current_group:
            img = Image.open(os.path.join(folder_path, img_file))
            if img.mode in ["RGBA", "LA"]:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
            else:
                if img.mode != "RGB":
                    img = img.convert("RGB")
            images.append(img)

        # 找出最大宽度
        max_width = max(img.width for img in images)

        # 调整所有图片到相同宽度，保持宽高比
        resized_images = []
        total_height = 0
        for img in images:
            aspect_ratio = img.height / img.width
            new_height = int(max_width * aspect_ratio)
            resized_img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
            total_height += new_height
            img.close()

        # 创建新的空白图片
        mode = "RGB"  # 强制使用RGB模式以支持JPEG压缩
        merged_image = Image.new(mode, (max_width, total_height))

        # 垂直拼接图片
        y_offset = 0
        for img in resized_images:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            merged_image.paste(img, (0, y_offset))
            y_offset += img.height
            img.close()

        # 使用时间戳和组号创建唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        group_num = i // average_group_count + 1

        # 压缩并保存图片
        output, quality = compress_image(merged_image)
        output_filename = os.path.join(
            output_dir,
            OUTPUT_CONFIG["OUTPUT_FILENAME_TEMPLATE"].format(
                timestamp=timestamp, group_num=group_num
            ),
        )

        # 保存压缩后的图片
        with open(output_filename, "wb") as f:
            f.write(output.getvalue())

        merged_image.close()
        print(
            f"已保存第{group_num}组合并后的图片（{len(current_group)}张）：{output_filename}，压缩质量：{quality}"
        )


# 使用方法
folder_path = "."
merge_images_vertically(folder_path)
