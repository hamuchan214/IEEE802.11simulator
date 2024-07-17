from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    # Get the value of the 'option' query parameter, default to 0 if not provided
    option = request.args.get('option', default=0, type=int)
    
    # Return 'hello matlab' if option is 1, otherwise return 'hello'
    if option == 1:
        return 'hello matlab'
    else:
        return 'hello'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
