#工具类 将已有照片生成视频
import cv2
import os
import numpy as np

# 定义视频文件路径
video_path = "DB/output_video.mp4"
image_folder = "DB"

# 获取文件夹中的所有图像文件
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# 检查是否有图像文件
if not image_files:
    print("文件夹中没有图像文件。")
    exit()

# 定义视频的宽度和高度
width, height = 640, 480

# 定义视频编码器和帧率
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 2  # 每秒1帧，因为每个图像停留5秒

# 创建视频写入对象
out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

# 写入每个图像到视频文件
for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    image = cv2.imread(image_path)

    # 计算调整后的图像大小以保持比例
    aspect_ratio = image.shape[1] / image.shape[0]
    if aspect_ratio > width / height:
        new_width = width
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = height
        new_width = int(new_height * aspect_ratio)

    # 调整图像大小
    image = cv2.resize(image, (new_width, new_height))

    # 创建一个新的空白图像并粘贴调整后的图像
    new_image = np.zeros((height, width, 3), dtype=np.uint8)
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2
    new_image[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = image

    for _ in range(5):
        out.write(new_image)

# 释放视频写入对象
out.release()

print(f"视频已生成: {video_path}")