import os, json, datetime
from flask import Flask, render_template, abort, request


app = Flask(__name__)  # по умолчанию static/ и templates/

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/factory')
def factory():
    return render_template('factory.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

# необязательный: безопасный динамический маршрут (если захотишь)
ALLOWED = {'index': 'index.html', 'factory': 'factory.html', 'cart': 'cart.html'}
@app.route('/page/<name>')
def page(name):
    if name in ALLOWED:
        return render_template(ALLOWED[name])
    abort(404)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    if not data:
        return "Ошибка: нет данных", 400

    os.makedirs('requests', exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"requests/{timestamp}_{data['name']}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))

    return "Заявка сохранена! Спасибо 😺"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)