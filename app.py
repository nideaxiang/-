from flask import Flask, render_template, request, jsonify,redirect
import requests
import json

app = Flask(__name__)

history_baidu = []
max_history_number = 8

def get_access_token():
    url = ("https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=R52N3JUDpuo94W5NiU0rTPoX"
           "&client_secret=8aPYgzwN4vLCOBie5rTBXkL2Ef76a0Eq")

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def process_message(message):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + get_access_token()

    if len(history_baidu) <= max_history_number * 2:
        history_baidu.append({
            "role": "user",
            "content": message
        })
    else:
        history_baidu.pop(0)
        history_baidu.append({
            "role": "user",
            "content": message
        })

    payload = json.dumps({
        "messages": history_baidu,
        "stream": True
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, stream=True)

    whole_sentence = ""
    for line in response.iter_lines():
        string_data = line.decode('utf-8')
        if '{' in string_data and 'result' in string_data:
            start_index = string_data.index('{')
            end_index = string_data.rindex('}') + 1
            dict_string = string_data[start_index:end_index]
            dict_data = json.loads(dict_string)
            whole_sentence += dict_data['result']

    if len(history_baidu) <= max_history_number * 2:
        history_baidu.append({
            "role": "assistant",
            "content": whole_sentence
        })
    else:
        history_baidu.pop(0)
        history_baidu.append({
            "role": "assistant",
            "content": whole_sentence
        })

    return whole_sentence




@app.route('/')
def page01():
    return render_template('page01.html')

@app.route('/chat', methods=['GET'])
def chat_page():
    return render_template('index.html')

@app.route('/twins',methods=['GET'])
def page02():
    return redirect('http://localhost:5174/')
# 处理对话请求的路由处理函数
@app.route('/api', methods=['POST'])
def chat():
    message = request.json.get('message')
    # 处理对话逻辑的函数，这里用 process_message() 代替，你可以修改为你自己的函数
    response = process_message(message)
    return jsonify({'response': response})

# 处理开始游戏的路由
@app.route('/start-game', methods=['POST'])
def start_game():
    # 向 AI 发送开始游戏指令
    game_message = "我们来玩多轮的古诗词飞花令游戏，关键字是“月”，你先出题，然后我来回答，不要透露答案"
    # 处理游戏指令的逻辑，发送给 AI 或者进行其他操作
    # 在这里，您可以添加发送消息给 AI 的代码，类似于处理 chat() 函数中的部分
    return jsonify({'response': game_message})

if __name__ == '__main__':
    app.run(debug=True)
