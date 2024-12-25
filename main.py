# 实时检测人脸识别
import json
import os
import pickle
import time
import numpy as np
import cv2
import face_recognition
import cvzone
import oss2
from datetime import datetime

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
bucket = oss2.Bucket(auth, endpoint, 'face-detect-csy', region=region)


def get_json_from_oss(file_path):
    try:
        # 从 OSS 获取对象
        result = bucket.get_object(file_path)
        # 将文件内容读取为字符串
        content = result.read().decode('utf-8')
        # 将 JSON 字符串解析为 Python 字典
        json_data_dic = json.loads(content)
        return json_data_dic
    except oss2.exceptions.NoSuchKey:
        print(f"文件 {file_path} 不存在!")
        return None
    except Exception as e:
        print(f"下载文件 {file_path} 失败: {e}")
        return None


# 从 OSS 下载图片
def get_image_from_oss(object_key):
    try:
        result = bucket.get_object(object_key)
        img_data = result.read()  # 获取图片的二进制数据
        img_np = np.frombuffer(img_data, np.uint8)  # 转换为 NumPy 数组
        img_f = cv2.imdecode(img_np, cv2.IMREAD_COLOR)  # 解码为 OpenCV 图像
        print("get the img")
        return img_f
    except Exception as e:
        print(f"Error downloading image from OSS: {e}")
        return None


def upload_json_to_oss(file_path, json_data):
    try:
        # 将 Python 字典转换为 JSON 字符串
        content = json.dumps(json_data, ensure_ascii=False)

        # 将 JSON 数据上传到 OSS
        bucket.put_object(file_path, content)
        print(f"文件 {file_path} 上传成功!")

    except Exception as e:
        print(f"上传文件 {file_path} 失败: {e}")


cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources\Background.png')

# 加载mode中的资源照片 以便于后续状态切换
folderPath = 'Resources\Modes'
modes = os.listdir(folderPath)
imgModeList = []
# print(modes)
for mode in modes:
    imgModeList.append(cv2.imread(os.path.join(folderPath, mode)))

# 加载编码文件
print("加载编码文件。。。")
file = open('encodings.p', 'rb')
encodingListWithIds = pickle.load(file)
file.close()
facesEncodingList, facesId = encodingListWithIds
# print(facesEncodingList)

# 模式选项  0为初始页 1为签到成功，显示个人信息
#          2为签到失败 3为重复签到
modeType = 0
# display_mode_start_time = time.time()  # 记录模式切换到 imgModeList[2] 的时间
tagged_faces = {}  # 存储已经被标记过的学生信息

# 全局变量初始化
display_mode_start_time = None
pause_duration = 2  # 暂停时间（秒）
is_paused = False


def draw_student_info(img, student_info, modeType):
    if modeType == 1:
        cv2.putText(img, f"Name: {student_info['name']}", (840, 450), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(img, f"Major: {student_info['major']}", (840, 500), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(img, f"Class number: {student_info['class-number']}", (840, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                    (0, 0, 0), 1)
        cv2.putText(img, f"Attendance: {student_info['attendance']}", (840, 600), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                    (0, 0, 0), 1)
    elif modeType == 3:
        cv2.putText(img, f"Name: {student_info['name']}", (840, 500), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(img, f"Last Attendance: {student_info['last-attendance-time']}", (840, 550),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)


def update_attendance(faceId, current_time, tagged_faces, facesId, imgModeList, imgBackground):
    global display_mode_start_time, is_paused
    student_info = tagged_faces[faceId]
    current_date = current_time.strftime("%Y-%m-%d")
    last_attendance_date = datetime.strptime(student_info['last-attendance-time'], "%Y-%m-%d %H:%M:%S").strftime(
        "%Y-%m-%d")

    if current_date == last_attendance_date:
        modeType = 3
        draw_student_info(imgBackground, student_info, modeType)
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        display_mode_start_time = time.time()
        is_paused = True
        return modeType

    else:
        modeType = 1
        student_info["attendance"] += 1
        student_info["last-attendance-time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        json_data = tagged_faces[faceId]
        upload_json_to_oss(f"StudentInfos/{faceId}.json", json_data)
        curImg = get_image_from_oss(f"img/{faceId}.png")

        # 显示curImg在状态图之上
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        imgBackground[60:60 + 250, 890:890 + 250] = curImg  # 确保curImg尺寸与预留位置匹配
        draw_student_info(imgBackground, student_info, modeType)

        display_mode_start_time = time.time()
        is_paused = True
        return modeType


# 主循环
while True:
    success, img = cap.read()
    if not success:
        continue

    # 继续获取并显示摄像头帧
    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # 如果处于暂停状态且未超时，仅进行面部检测并绘制边界框，不进行签到处理
    if is_paused and time.time() - display_mode_start_time < pause_duration:
        faceCurFrame = face_recognition.face_locations(imgSmall)
        for faceLoc in faceCurFrame:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

        cv2.imshow("Attendance", imgBackground)
        cv2.waitKey(1)
        continue

    # 面部检测和处理
    faceCurFrame = face_recognition.face_locations(imgSmall)
    encodeCurFrame = face_recognition.face_encodings(imgSmall, faceCurFrame)

    if len(faceCurFrame) == 0:
        modeType = 0
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(facesEncodingList, encodeFace, tolerance=0.45)
            faceDis = face_recognition.face_distance(facesEncodingList, encodeFace)
            matchedIndex = np.argmin(faceDis)

            if matches[matchedIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                faceId = facesId[matchedIndex]
                current_time = datetime.now()

                if faceId in tagged_faces:
                    modeType = update_attendance(faceId, current_time, tagged_faces, facesId, imgModeList,
                                                 imgBackground)
                    continue

                if faceId not in tagged_faces:
                    try:
                        json_data = get_json_from_oss(f"StudentInfos/{faceId}.json")
                        tagged_faces[faceId] = {
                            "name": json_data.get("name", "Unknown"),
                            "major": json_data.get("major", "Unknown"),
                            "class-number": json_data.get("class-number", "Unknown"),
                            "attendance": json_data.get("attendance", 0),
                            "last-attendance-time": json_data.get("last-attendance-time", "1970-01-01 00:00:00"),
                            "age": json_data.get("age", 0),
                            "start-year": json_data.get("start-year", 0)
                        }
                    except Exception as e:
                        print(f"Error fetching data from OSS: {e}")
                        continue

                modeType = update_attendance(faceId, current_time, tagged_faces, facesId, imgModeList, imgBackground)

            else:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0, colorC=(0, 0, 200))
                if modeType != 2:
                    display_mode_start_time = time.time()
                    modeType = 2

    if modeType in [1, 2, 3]:
        if time.time() - display_mode_start_time < pause_duration:
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType == 1 or modeType == 3:
                draw_student_info(imgBackground, tagged_faces[faceId], modeType)
                if modeType == 1:
                    curImg = get_image_from_oss(f"img/{faceId}.png")
                    imgBackground[55:55 + 250, 890:890 + 250] = curImg  # 确保curImg尺寸与预留位置匹配
        else:
            modeType = 0
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    cv2.imshow("Attendance", imgBackground)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
