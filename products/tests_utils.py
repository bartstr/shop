import os
from shop.settings import PROJECT_PATH


def delete_test_image():
    images_path = os.path.join(PROJECT_PATH, 'media/images')
    files = [i for i in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, i))
             and i.startswith('test_image_')]
    for file in files:
        os.remove(os.path.join(images_path, file))
