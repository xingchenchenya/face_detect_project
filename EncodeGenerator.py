# 图像编码类 为face-recognition实现添加数据
import os
import cv2
import face_recognition
import pickle

# 添加学生面部图像
folderImg = 'img'
facesList = os.listdir(folderImg)
facesImg = []
facesId = []
for face in facesList:
    facesImg.append(cv2.imread(os.path.join(folderImg, face)))
    # print(os.path.splitext(face))
    facesId.append(os.path.splitext(face)[0])
print(facesId)


def findEncodings(imgList):
    encodingList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodingList.append(encode)
    return encodingList


facesEncodingList = findEncodings(facesImg)
# print(facesEncodingList)
encodingWithIds = [facesEncodingList, facesId]

file = open("encodings.p", "wb")
pickle.dump(encodingWithIds, file)
file.close()
print("转储完成")
