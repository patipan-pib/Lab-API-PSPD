from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# ---------- Index / Welcome ----------
# 
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to Prime API 🚀",
        "endpoints": {
            "/is_prime/<num>": "Check if a number is prime",
            "/primes?start=10&end=30": "Get prime numbers in range",
            "/getcode": "Simple code check",
            "/plus/<a>/<b>": "Add two numbers"
        }
    })

# ---------- Logic ----------
def is_prime(n):
    if not isinstance(n, int) or n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_next(n):
    return n + 5

def get_primes_in_range(start, end):
    return [num for num in range(max(2, start), end + 1) if is_prime(num)]

@app.route('/next5/<string:num>', methods=['GET'])
def check_next(num):
    num = float(num)
    return jsonify({'result': num + 5})

@app.route('/is_prime/<int:num>', methods=['GET'])
def check_prime(num):
    return jsonify({'number': num, 'is_prime': is_prime(num)})


@app.route('/primes', methods=['GET'])
def primes_in_range():
    start = request.args.get('start', default=1, type=int)
    end = request.args.get('end', default=100, type=int)
    if start > end:
        return jsonify({'error': 'start must be <= end'}), 400
    primes = get_primes_in_range(start, end)
    return jsonify({'start': start, 'end': end, 'primes': primes, 'count': len(primes)})

@app.route('/getcode', methods=['GET'])
def get_code():
    return jsonify({"code": "success"})

@app.route('/plus/<int:a>/<int:b>', methods=['GET'])
def plus(a, b):
    return jsonify({'result': a + b})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
