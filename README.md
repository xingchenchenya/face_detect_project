项目说明
1.运行环境
python 3.11.7
dlib 19.24.0
cmake 3.25.2
face_recognition 1.3.0
flask 2.2.5
opencv-python 4.10.0.84
oss2 2.19.1 （使用阿里云充当了数据库）
cvzone 1.6.1 （是为了画检测框的）
2. 运行顺序
需自己预处理n张250*250像素的人脸面部图像放于img文件夹中，运行EncodeGenerator，主目录下将生成img文件夹中全部图像的encoding.p文件
然后运行AddDataToDB和AddImgToOss，需注意修改oss的配置，填入有权限的RAM用户信息，并且在img中的图像命名要与AddDataToDB中json文件的命名一致
最后运行main，即可开启摄像头完成人脸检测

为便于观察，也可以开启videoDetect完成视频的人脸检测，PhotoToVideo是将部分照片生成视频的文件，也需提前运行好，生成output_video.mp4方可运行