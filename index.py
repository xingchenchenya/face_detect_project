#阿里云oss中的统计信息
from flask import Flask, render_template
import oss2
import json

app = Flask(__name__, template_folder='Resources')

# 填写RAM用户的访问密钥（AccessKey ID和AccessKey Secret）。
accessKeyId = 'YOUR_OWN_ACCESS_KEY_ID'
accessKeySecret = 'YOUR_OWN_ACCESS_KEY_SECRET'
# 使用代码嵌入的RAM用户的访问密钥配置访问凭证。
auth = oss2.Auth(accessKeyId, accessKeySecret)
# yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
endpoint = 'https://oss-cn-chengdu.aliyuncs.com'
# 填写Bucket名称。# yourBucketName填写存储空间名称。
bucket_name = 'face-detect-csy'

# 创建 Bucket 对象
bucket = oss2.Bucket(auth, endpoint, bucket_name)


def get_json_files_from_oss(prefix):
    try:
        # 使用 bucket 对象调用 list_objects_v2 方法
        response = bucket.list_objects_v2(prefix=prefix)
        contents = response.object_list
        data = []
        for obj in contents:
            if obj.key.endswith('.json'):
                result = bucket.get_object(obj.key)
                # print(obj.key)
                content = result.read().decode('utf-8')
                json_data = json.loads(content)
                # 提取文件名中的 id 部分
                file_name = obj.key
                id_part = file_name.split('/')[-1].rsplit('.', 1)[0]  # 获取 '/' 后和 '.json' 前的部分
                # 将 id 添加到 json_data 中
                json_data['id'] = id_part

                data.append(json_data)
        return data
    except Exception as e:
        print(f"Error fetching data from OSS: {e}")
        return []


@app.route('/')
def index():
    prefix = 'StudentInfos/'
    data = get_json_files_from_oss(prefix)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)