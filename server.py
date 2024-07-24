from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    # 受け取ったデータをバイナリとして保存
    data = request.data
    # データのサイズを表示
    print(f'Received data size: {len(data)} bytes')
    # データをファイルに保存
    with open('received_frame.bin', 'wb') as f:
        f.write(data)
    return 'Data received successfully'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
