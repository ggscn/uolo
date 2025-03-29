from werkzeug.utils import secure_filename
from flask import current_app
import os
import uuid
from PIL import Image
from io import BytesIO
from binascii import unhexlify
import base64
import chardet


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
EXTENSION_MAP = {
    '.png':'PNG',
    '.jpg':'JPEG',
    '.jpeg':'JPEG'
}


def unique_id():
    return str(uuid.uuid4())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image_to_file(f, optimize_photo=True, generate_thumnail=True):
    unique_id_str = unique_id(),
    filename = secure_filename('{}-{}'.format(unique_id_str, f.filename))
    filepath = os.path.join(
        os.environ.get('IMAGE_TMP_PATH'), 
        filename
    )

    if generate_thumnail:
        thumbnail_filename = secure_filename('thumb-{}-{}'.format(unique_id_str, f.filename))
        thumbnail_filepath = os.path.join(
            os.environ.get('IMAGE_TMP_PATH'), 
            thumbnail_filename
        )

    f.save(filepath)
    
    img = Image.open(filepath)
    img.save(filepath,optimize=optimize_photo,quality=85)

    file_obj = {
        'filepath':filepath,
        'filename':filename
    }

    if generate_thumnail:
        img.thumbnail((512,512), Image.ANTIALIAS)
        img.save(thumbnail_filepath, optimize=optimize_photo, quality=85)

        file_obj['thumbnail_filename'] = thumbnail_filename
        file_obj['thumbnail_filepath'] = thumbnail_filepath

    return file_obj

def save_image_to_bytes(f, optimize_photo=True, generate_thumnail=True):
    unique_id_str = unique_id()
    
    filename = secure_filename(
        '{}-{}'.format(unique_id_str, f.filename))

    extension = EXTENSION_MAP[
        os.path.splitext(filename)[1].lower()]
    
    image_stream = f.stream.read()

    with BytesIO(image_stream) as img_string_buffer:
        img = Image.open(img_string_buffer)
        img.save(
            img_string_buffer, optimize=optimize_photo, quality=85, format=extension)
        
        img_b64 = base64.b64encode(
            img_string_buffer.getvalue()).decode('UTF-8')
        
        file_obj = {
            'img_b64': img_b64,
            'filename':filename,
            'extension': extension
        }

    if generate_thumnail:
        thumbnail_filename = secure_filename(
            'thumb-{}-{}'.format(unique_id_str, f.filename))
            
        with BytesIO() as thumbnail_string_buffer: 
            img.thumbnail((512,512), Image.ANTIALIAS)
            img.save(
                thumbnail_string_buffer, optimize=optimize_photo, quality=85, format=extension)

            img_thumbnail_b64 = base64.b64encode(
                thumbnail_string_buffer.getvalue()).decode('UTF-8')

            file_obj['thumbnail_filename'] = thumbnail_filename
            file_obj['img_thumbnail_b64'] = img_thumbnail_b64

    return file_obj

def delete_image(filename):
    os.remove(filename)