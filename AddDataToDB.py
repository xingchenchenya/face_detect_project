#工具类 向oss中传输信息数据
import json
import oss2

# 自己配置阿里云的RAM用户信息

# 可能后续用得上的json文件配置 给某一用户配置face-detect bucket中的全部权限
# {
#     "Version": "1",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": "oss:*",
#             "Resource": [
#                 "acs:oss:*:*:face-detect-csy",
#                 "acs:oss:*:*:face-detect-csy/*"
#             ]
#         }
#     ]
# }

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

# 测试文件上传。。。成功！
# bucket.put_object_from_file('1.txt', '1.txt')

# 学生信息数据（以学号为键，内容为值）
students = {
    "011121": {
        "name": "Elon Musk",
        "age": 25,
        "major": "Computer Science",
        "start-year": 2021,
        "class-number": "04012101",
        "attendance": 10,
        "last-attendance-time": "2024-12-18 00:00:00"
    },
    "021123": {
        "name": "Lin-Manuel Miranda",
        "age": 20,
        "major": "Theatre Studies",
        "start-year": 2022,
        "class-number": "01022202",
        "attendance": 10,
        "last-attendance-time": "2024-12-18 00:00:00"
    },
    "021134": {
        "name": "Phillipa Soo",
        "age": 19,
        "major": "Art Studies",
        "start-year": 2023,
        "class-number": "01032301",
        "attendance": 15,
        "last-attendance-time": "2024-12-17 00:00:00"
    },
    "023244": {
        "name": "Billkin",
        "age": 19,
        "major": "Electrical automation",
        "start-year": 2023,
        "class-number": "02012301",
        "attendance": 15,
        "last-attendance-time": "2024-12-17 00:00:00"
    },
    "033599": {
        "name": "Vanessa Hudgens",
        "age": 21,
        "major": "Physics",
        "start-year": 2021,
        "class-number": "03032101",
        "attendance": 9,
        "last-attendance-time": "2024-12-17 00:00:00"
    },
    "000001": {
        "name": "Chen Shiyu",
        "age": 21,
        "major": "Software Engineering",
        "start-year": 2021,
        "class-number": "04072107",
        "attendance": 20,
        "last-attendance-time": "2024-12-18 00:00:00"
    }
}

# 上传 JSON 数据
def upload_student_info_to_oss(students, oss_folder):
    """
    将学生信息直接作为 JSON 上传到 OSS
    :param students: 学生信息字典，键为学号，值为学生信息
    :param oss_folder: OSS 目标文件夹路径
    """
    print("初始化数据开始。。。")
    for student_id, student_info in students.items():
        # 将学生信息转换为 JSON 格式字符串
        json_data = json.dumps(student_info, ensure_ascii=False, indent=2)
        oss_file_path = f"{oss_folder}/{student_id}.json"  # OSS 文件路径
        try:
            # 上传 JSON 数据
            bucket.put_object(oss_file_path, json_data)
            print(f"成功上传学号 {student_id} 的信息到 OSS 路径：{oss_file_path}")
        except Exception as e:
            print(f"上传失败：学号 {student_id} 的信息，错误信息：{e}")

oss_target_folder = 'StudentInfos'  # OSS 中的目标文件夹
upload_student_info_to_oss(students, oss_target_folder)


