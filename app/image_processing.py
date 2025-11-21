# app/image_processing.py
from PIL import Image

ACeP_COLORS = [
    (0, 0, 0),         # Black
    (255, 255, 255),   # White
    (255, 0, 0),       # Red
    (255, 255, 0),     # Yellow
    (255, 165, 0),     # Orange
    (0, 0, 255),       # Blue
    (0, 128, 0)        # Green
]

def closest_color(rgb):
    r, g, b = rgb
    return min(ACeP_COLORS, key=lambda c: (r - c[0])**2 + (g - c[1])**2 + (b - c[2])**2)

def process_image_for_epaper(input_path, output_path):
    TARGET_W = 800
    TARGET_H = 480

    with Image.open(input_path) as img:
        img = img.convert("RGB")

        # 2️⃣ Luego adaptamos a 800×480 (horizontal)
        img = resize_and_crop(img, TARGET_W, TARGET_H)

        # 3️⃣ Dithering ACeP
        dithered = img.copy()
        pixels = dithered.load()

        for y in range(dithered.height):
            for x in range(dithered.width):
                old_pixel = pixels[x, y]
                new_pixel = closest_color(old_pixel)
                pixels[x, y] = new_pixel

                quant_error = tuple(old - new for old, new in zip(old_pixel, new_pixel))

                for dx, dy, factor in [(1, 0, 7/16), (-1, 1, 3/16), (0, 1, 5/16), (1, 1, 1/16)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < TARGET_W and 0 <= ny < TARGET_H:
                        r, g, b = pixels[nx, ny]
                        r = min(255, max(0, int(r + quant_error[0] * factor)))
                        g = min(255, max(0, int(g + quant_error[1] * factor)))
                        b = min(255, max(0, int(b + quant_error[2] * factor)))
                        pixels[nx, ny] = (r, g, b)

        # 4️⃣ Guardamos ya como 800×480 listo para GxEPD2
        dithered.save(output_path, format="BMP")

def resize_and_crop(img, target_width, target_height):
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        scale_height = target_height
        scale_width = int(scale_height * img_ratio)
    else:
        scale_width = target_width
        scale_height = int(scale_width / img_ratio)

    img_resized = img.resize((scale_width, scale_height), Image.LANCZOS)

    left = (img_resized.width - target_width) // 2
    top = (img_resized.height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img_resized.crop((left, top, right, bottom))
