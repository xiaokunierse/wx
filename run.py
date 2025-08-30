from flask import Flask, request, make_response
import xml.etree.ElementTree as ET
from datetime import datetime

app = Flask(__name__)

# 设置一个令牌(Token)，需要与微信公众平台后台配置的Token一致
TOKEN = "YourWeChatTokenHere" # 请修改为你自己设置的、安全的Token

def parse_xml(data):
    """解析微信传来的XML数据"""
    xml_rec = ET.fromstring(data)
    msg_type = xml_rec.find('MsgType').text
    from_user = xml_rec.find('FromUserName').text
    to_user = xml_rec.find('ToUserName').text
    content = xml_rec.find('Content').text if msg_type == 'text' else ''
    return msg_type, from_user, to_user, content

def build_text_xml(from_user, to_user, content):
    """构建文本类型的回复XML"""
    xml_form = """
    <xml>
        <ToUserName><![CDATA[{0}]]></ToUserName>
        <FromUserName><![CDATA[{1}]]></FromUserName>
        <CreateTime>{2}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{3}]]></Content>
    </xml>
    """
    return xml_form.format(from_user, to_user, int(datetime.now().timestamp()), content)

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    """微信消息处理核心入口"""
    if request.method == 'GET':
        # 首次URL验证：验证消息的确来自微信服务器
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        # 这里应实现校验逻辑（例如使用hashlib.sha1验证signature）
        # 为简化示例，此处直接返回echostr，生产中务必验证！
        return echostr
    else:
        # 处理微信服务器POST来的用户消息
        xml_data = request.data
        msg_type, from_user, to_user, content = parse_xml(xml_data)

        # 定义你的关键词“密码”
        keyword_password = "时间密码"

        if msg_type == 'text' and content.strip() == keyword_password:
            # 获取当前时间并格式化
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reply_content = f"当前服务器时间是：{current_time}"
            # 构建回复XML
            response_xml = build_text_xml(to_user, from_user, reply_content)
            response = make_response(response_xml)
            response.content_type = 'application/xml'
            return response
        else:
            # 如果不是指定关键词，可以选择不回复，或回复其他提示
            # 此处示例为不回复（微信服务器要求5秒内必须回复，否则会重试。
            # 不回复且不报错，微信则不会重试）
            return 'success'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
