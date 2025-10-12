from flask import Flask, render_template, abort

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
