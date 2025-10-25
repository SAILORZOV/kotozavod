import os, json, datetime
from flask import Flask, render_template, abort, request, jsonify
import socket
import ssl
import base64
import requests
from PIL import Image
from io import BytesIO

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


def create_cat_image(cat_parts):
    """Создает изображение кота из частей"""
    try:
        # Базовые размеры
        width, height = 300, 300

        # Создаем прозрачный canvas
        canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Загружаем и накладываем части кота в правильном порядке
        parts_order = ['body', 'paws', 'tail', 'head']  # Порядок наложения

        for part in parts_order:
            if part in cat_parts:
                part_url = cat_parts[part]
                try:
                    response = requests.get(part_url, timeout=5)
                    if response.status_code == 200:
                        part_img = Image.open(BytesIO(response.content))
                        part_img = part_img.convert('RGBA')

                        # Масштабируем и центрируем
                        part_img = part_img.resize((width, height), Image.Resampling.LANCZOS)

                        # Накладываем на canvas
                        canvas = Image.alpha_composite(canvas, part_img)
                except Exception as e:
                    print(f"Ошибка загрузки {part}: {e}")

        # Сохраняем изображение во временный файл
        temp_file = f"temp_cat_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        canvas.save(temp_file, format="PNG")

        # Читаем файл и конвертируем в base64
        with open(temp_file, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()

        # Удаляем временный файл
        os.remove(temp_file)

        return img_data

    except Exception as e:
        print(f"Ошибка создания изображения кота: {e}")
        return None


def send_smtp_email(recipient, subject, message, cats, comment):
    try:
        smtp_server = "smtp.mail.ru"
        smtp_port = 465
        username = "smtp1231@mail.ru"
        password = "G0MdCCsxKu9hORwnZ3QI"

        print(f"🔧 Подключаемся к {smtp_server}:{smtp_port}")

        context = ssl.create_default_context()
        with socket.create_connection((smtp_server, smtp_port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=smtp_server) as ssock:

                response = ssock.recv(1024).decode()
                print(f"SMTP: {response.strip()}")

                def send_cmd(cmd):
                    ssock.send((cmd + '\r\n').encode())
                    return ssock.recv(1024).decode()

                ehlo_response = send_cmd(f'EHLO {socket.gethostname()}')
                print(f"EHLO: {ehlo_response.strip()}")

                auth1 = send_cmd('AUTH LOGIN')
                auth2 = send_cmd(base64.b64encode(username.encode()).decode())
                auth3 = send_cmd(base64.b64encode(password.encode()).decode())

                if "235" not in auth3 and "2.7.0" not in auth3:
                    return False

                print("✅ Аутентификация успешна!")

                send_cmd(f'MAIL FROM:<{username}>')
                send_cmd(f'RCPT TO:<{recipient}>')
                send_cmd('DATA')

                # Создаем MIME сообщение с прикрепленными картинками
                boundary = "===============CAT_FACTORY==============="

                email_content = f"""From: {username}
To: {recipient}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
Content-Type: text/html; charset=utf-8

<html>
<body style="font-family: Arial, sans-serif; background: #f7f9fc; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h1 style="color: #4a90e2; text-align: center;">🐱 Ваши котики с Котозавода! 🐱</h1>

    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3 style="color: #2c6ed5;">📦 Детали заказа:</h3>
        <p><strong>Количество котов:</strong> {len(cats)}</p>
        <p><strong>Комментарий:</strong> {comment if comment else 'Не указан'}</p>
    </div>
"""

                # Добавляем информацию о котах
                for i, cat in enumerate(cats, 1):
                    parts_text = ""
                    if cat.get('parts'):
                        parts = cat['parts']
                        parts_text = f"Тело:{parts.get('body', 1)} Голова:{parts.get('head', 1)} Лапы:{parts.get('paws', 1)} Хвост:{parts.get('tail', 1)}"

                    email_content += f"""
    <div style="border: 2px solid #4a90e2; border-radius: 15px; padding: 20px; margin: 15px 0; background: #fafcff;">
        <h3 style="color: #2c6ed5; margin-top: 0;">🐱 Кот #{i}: {cat.get('name', 'Безымянный')}</h3>
        <p><strong>💰 Цена:</strong> {cat.get('price', 0)}₽</p>
        <p><strong>📋 Конфигурация:</strong> {parts_text if parts_text else 'Стандартный кот'}</p>
        <div style="text-align: center; margin: 15px 0;">
            <p>🖼️ Изображение кота прикреплено к письму (cat_{i}.png)</p>
        </div>
    </div>
"""

                email_content += f"""
    <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin-top: 20px; text-align: center;">
        <p style="margin: 0; font-size: 16px; color: #2e7d32;">
            <strong>Спасибо за заказ! 🐾</strong><br>
            Мы скоро свяжемся с вами для уточнения деталей.
        </p>
    </div>

    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
        <p style="color: #666; font-size: 14px;">
            С уважением,<br>
            <strong>Команда Котозавода</strong> 🐈
        </p>
    </div>
</div>
</body>
</html>

"""

                # Прикрепляем картинки котов как файлы
                for i, cat in enumerate(cats, 1):
                    # Создаем URL для частей кота
                    cat_parts_urls = {}
                    if cat.get('parts'):
                        for part_name, part_num in cat['parts'].items():
                            cat_parts_urls[
                                part_name] = f"http://127.0.0.1:8000/static/pics/cat_parts/{part_name}/{part_name}{part_num}.png"

                    # Создаем изображение кота
                    cat_image_data = create_cat_image(cat_parts_urls)

                    if cat_image_data:
                        email_content += f"""
--{boundary}
Content-Type: image/png; name="cat_{i}.png"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="cat_{i}.png"

{cat_image_data}
"""

                email_content += f"""
--{boundary}--
.
"""

                ssock.send(email_content.encode())
                final_response = ssock.recv(1024).decode()
                print(f"FINAL: {final_response.strip()}")

                if "250" in final_response:
                    print("✅ Письмо с картинками отправлено успешно!")
                    send_cmd('QUIT')
                    return True
                else:
                    return False

    except Exception as e:
        print(f"❌ Ошибка SMTP: {e}")
        return False


@app.route('/send_cats_email', methods=['POST'])
def send_cats_email():
    try:
        data = request.json
        user_email = data.get('email')
        comment = data.get('comment', '')
        cats = data.get('cats', [])

        if not user_email:
            return jsonify({'error': 'Email обязателен'}), 400

        if not cats:
            return jsonify({'error': 'Нет выбранных котов'}), 400

        subject = f"🐱 Заказ {len(cats)} котиков с Котозавода!"
        message = f"""Заказ с Котозавода!

Вы заказали {len(cats)} котов:

"""
        for i, cat in enumerate(cats, 1):
            message += f"""
Кот #{i}:
🐱 Имя: {cat.get('name', 'Безымянный')}
💰 Цена: {cat.get('price', 0)}₽
"""
            if cat.get('parts'):
                parts = cat['parts']
                message += f"📋 Конфигурация: Тело:{parts.get('body', 1)} Голова:{parts.get('head', 1)} Лапы:{parts.get('paws', 1)} Хвост:{parts.get('tail', 1)}\n"

        message += f"""
💬 Комментарий: {comment if comment else 'Не указан'}

С уважением, Котозавод 🐾
"""

        success = send_smtp_email(user_email, subject, message, cats, comment)

        if success:
            return jsonify({
                'success': True,
                'message': f'Письмо с {len(cats)} котами отправлено на {user_email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Ошибка отправки email. Попробуйте позже.'
            })

    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)