#工具类 向oss中传输图像数据
import oss2
import os

# 填写RAM用户的访问密钥（AccessKey ID和AccessKey Secret）。
accessKeyId = 'YOUR_OWN_ACCESS_KEY_ID'
accessKeySecret = 'YOUR_OWN_ACCESS_KEY_SECRET'
# 使用代码嵌入的RAM用户的访问密钥配置访问凭证。
auth = oss2.Auth(accessKeyId, accessKeySecret)
# yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
endpoint = 'https://oss-cn-chengdu.aliyuncs.com'
# 填写Endpoint对应的Region信息，例如cn-hangzhou。注意，v4签名下，必须填写该参数
region = "cn-chengdu"
# 填写Bucket名称。# yourBucketName填写存储空间名称。
bucket = oss2.Bucket(auth, endpoint, 'face-detect-csy',region=region)


def upload_folder_to_oss(local_folder, oss_folder):
    """
    将本地文件夹的内容上传到 OSS 指定文件夹
    :param local_folder: 本地文件夹路径
    :param oss_folder: OSS 目标文件夹路径
    """
    for root, dirs, files in os.walk(local_folder):
        for file_name in files:
            # 获取本地文件路径
            local_file_path = os.path.join(root, file_name)

            # 构造 OSS 路径
            relative_path = os.path.relpath(local_file_path, local_folder)  # 相对路径
            oss_file_path = os.path.join(oss_folder, relative_path).replace("\\", "/")  # 替换为 OSS 兼容的路径

            # 上传文件到 OSS
            try:
                with open(local_file_path, 'rb') as file_obj:
                    bucket.put_object(oss_file_path, file_obj)
                print(f"成功上传：{local_file_path} 到 OSS 路径：{oss_file_path}")
            except Exception as e:
                print(f"上传失败：{local_file_path}, 错误信息：{e}")


# 示例：将项目目录下的 img 文件夹内容上传到 OSS 的 img 文件夹
local_img_folder = './img'  # 本地 img 文件夹路径
oss_target_folder = 'img'  # OSS 中的目标文件夹
upload_folder_to_oss(local_img_folder, oss_target_folder)