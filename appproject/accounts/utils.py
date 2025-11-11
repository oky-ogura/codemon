from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.exceptions import ValidationError

def validate_avatar_image(image):
    """アバター画像のバリデーション"""
    # ファイルサイズチェック（1MB制限）
    if image.size > 1024 * 1024:
        raise ValidationError('画像サイズは1MB以下にしてください')

    # 画像フォーマットチェック
    try:
        with Image.open(image) as img:
            if img.format.upper() not in ['JPEG', 'PNG']:
                raise ValidationError('JPEGまたはPNG形式の画像をアップロードしてください')
    except Exception as e:
        raise ValidationError('無効な画像ファイルです')

def resize_avatar_image(image_field):
    """アバター画像のリサイズ処理"""
    if not image_field:
        return None

    image_file = image_field.file
    # PILでイメージを開く
    image = Image.open(image_file)
    
    # 元のフォーマットを保持
    format = image.format
    
    # 最大サイズを設定（例：200x200）
    max_size = (200, 200)
    
    # アスペクト比を維持しながらリサイズ
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # 正方形に切り抜き
    size = min(image.size)
    left = (image.width - size) // 2
    top = (image.height - size) // 2
    right = left + size
    bottom = top + size
    image = image.crop((left, top, right, bottom))
    
    # BytesIOにJPEG形式で保存
    temp_thumb = BytesIO()
    image.save(temp_thumb, format=format, quality=90)
    temp_thumb.seek(0)
    
    # Djangoのファイルフィールドに保存
    return File(temp_thumb, name=image_field.name)