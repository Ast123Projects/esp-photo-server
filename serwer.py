from flask import Flask, request, render_template_string
from PIL import Image
import io

app = Flask(__name__)
current_image_data = None

# Poprawiony HTML z pełną interpunkcją CSS
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ESP8266 Photo Upload</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; background-color: #f4f4f4; }
        .box { background: white; padding: 20px; border-radius: 10px; display: inline-block; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        input { margin: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Wgraj zdjęcie na ESP8266</h2>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <input type="file" name="image" accept="image/*"><br>
            <input type="submit" value="Wyślij do ekranu" style="padding:10px 20px; cursor:pointer;">
        </form>
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
