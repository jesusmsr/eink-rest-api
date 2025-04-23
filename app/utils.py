from PIL import Image
import os

def process_image(image_path):
    # Here you can resize and convert to monochrome, 800x480 for example
    im = Image.open(image_path)
    im = im.convert("RGB").resize((800, 480))
    output_path = image_path.replace(".", "_processed.")
    im.save(output_path)
    return output_path
