from flask import Flask, request, render_template_string
from PIL import Image
import io

app = Flask(__name__)
current_image_data = None

# Poprawiony HTML z pełną interpunkcją CSS
HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Panel Sterowania ESP</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            margin: 0; 
            padding: 20px; 
            background-color: #121212; 
            color: white;
        }
        .container { 
            max-width: 500px; 
            margin: 0 auto; 
            background: #1e1e1e; 
            padding: 30px; 
            border-radius: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        h2 { margin-bottom: 30px; font-size: 28px; }
        
        /* Styl dla wyboru pliku - robimy go czytelnym */
        input[type="file"] { 
            display: block;
            width: 100%;
            margin-bottom: 30px;
            font-size: 18px;
            padding: 10px;
            background: #333;
            border-radius: 10px;
            color: #ccc;
        }

        /* WIELKI PRZYCISK WYSYŁANIA */
        input[type="submit"] { 
            background: linear-gradient(135deg, #00b4db, #0083b0);
            color: white; 
            border: none; 
            padding: 25px; 
            width: 100%; 
            font-size: 22px; 
            font-weight: bold; 
            text-transform: uppercase;
            border-radius: 15px; 
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,180,219,0.4);
            transition: all 0.3s ease;
        }
        
        input[type="submit"]:active {
            transform: scale(0.95);
            box-shadow: 0 2px 10px rgba(0,180,219,0.2);
        }

        .footer { margin-top: 30px; font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h2>FOTO DO ESP</h2>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <input type="file" name="image" accept="image/*">
            <input type="submit" value="WYŚLIJ NA EKRAN">
        </form>
        <div class="footer">Po kliknięciu odczekaj chwilę na przetworzenie</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/upload', methods=['POST'])
def upload():
    global current_image_data
    if 'image' not in request.files:
        return "Brak pliku"
    
    file = request.files['image']
    if file.filename == '':
        return "Nie wybrano zdjęcia"

    # Przetwarzanie obrazu
    img = Image.open(file.stream).convert('RGB')
    img = img.resize((128, 160)) 
    
    pixels = img.load()
    rgb565_data = bytearray()
    
    for y in range(160):
        for x in range(128):
            r, g, b = pixels[x, y]
            # Konwersja na format RGB565 (16-bit)
            color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            rgb565_data.append((color >> 8) & 0xFF)
            rgb565_data.append(color & 0xFF)
            
    current_image_data = bytes(rgb565_data)
    print("Otrzymano i przetworzono zdjęcie!")
    return "<h3>Zdjęcie gotowe! ESP może je pobrać.</h3><a href='/'>Wróć</a>"

@app.route('/image')
def get_image():
    if current_image_data:
        return current_image_data
    return "Brak obrazu", 404

if __name__ == '__main__':
    # Uruchomienie serwera
    app.run(host='0.0.0.0', port=5000)
