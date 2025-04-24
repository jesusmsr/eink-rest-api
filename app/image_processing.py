# app/image_processing.py
from PIL import Image

# Define los colores aproximados de la pantalla ACeP (pueden ajustarse)
ACeP_PALETTE = [
    (0, 0, 0),        # Negro
    (255, 255, 255),  # Blanco
    (255, 0, 0),      # Rojo
    (0, 255, 0),      # Verde
    (0, 0, 255),      # Azul
    (255, 255, 0),    # Amarillo
    (255, 165, 0),    # Naranja
]

def closest_color(rgb):
    return min(ACeP_PALETTE, key=lambda color: sum((c - r) ** 2 for c, r in zip(color, rgb)))

def process_image_for_epaper(input_path, output_path, size=(800, 480)):
    image = Image.open(input_path).convert('RGB')
    image = image.resize(size)

    processed = Image.new("RGB", image.size)
    pixels = processed.load()

    for y in range(image.height):
        for x in range(image.width):
            original = image.getpixel((x, y))
            pixels[x, y] = closest_color(original)

    processed.save(output_path)
