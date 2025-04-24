from PIL import Image
import os

ACEP_PALETTE = [
    (0, 0, 0),        # Negro
    (255, 255, 255),  # Blanco
    (255, 0, 0),      # Rojo
    (255, 255, 0),    # Amarillo
    (255, 165, 0),    # Naranja
    (0, 0, 255),      # Azul
    (0, 128, 0),      # Verde
]

def closest_acep_color(rgb):
    r, g, b = rgb
    min_dist = float('inf')
    closest = (0, 0, 0)
    for color in ACEP_PALETTE:
        dr = r - color[0]
        dg = g - color[1]
        db = b - color[2]
        dist = dr * dr + dg * dg + db * db
        if dist < min_dist:
            min_dist = dist
            closest = color
    return closest

def process_image_to_acep_palette(input_path, output_path, size=(800, 480)):
    img = Image.open(input_path).convert('RGB')
    img = img.resize(size)
    
    processed_img = Image.new('RGB', img.size)
    pixels = processed_img.load()

    for y in range(img.height):
        for x in range(img.width):
            original_color = img.getpixel((x, y))
            mapped_color = closest_acep_color(original_color)
            pixels[x, y] = mapped_color

    processed_img.save(output_path, format='BMP')