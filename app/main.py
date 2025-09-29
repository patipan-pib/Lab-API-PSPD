from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# ฟังก์ชันตรวจสอบว่าตัวเลขเป็นจำนวนเฉพาะหรือไม่
def is_prime(n):
    if not isinstance(n, int) or n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# ฟังก์ชันหาจำนวนเฉพาะในช่วง [start, end]
def get_primes_in_range(start, end):
    return [num for num in range(max(2, start), end + 1) if is_prime(num)]

# Endpoint ตรวจสอบว่าตัวเลขเป็นจำนวนเฉพาะหรือไม่
@app.route('/is_prime/<int:num>', methods=['GET'])
def check_prime(num):
    result = is_prime(num)
    return jsonify({
        'number': num,
        'is_prime': result
    })

# Endpoint หาจำนวนเฉพาะในช่วง
@app.route('/primes', methods=['GET'])
def primes_in_range():
    start = request.args.get('start', default=1, type=int)
    end = request.args.get('end', default=100, type=int)
    
    if start > end:
        return jsonify({'error': 'start must be less than or equal to end'}), 400
    
    primes = get_primes_in_range(start, end)
    return jsonify({
        'start': start,
        'end': end,
        'primes': primes,
        'count': len(primes)
    })

if __name__ == '__main__':
    app.run(debug=True)