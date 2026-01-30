import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import UserAccessory

ua = UserAccessory.objects.filter(is_equipped=True).select_related('accessory').first()
if ua:
    print(f'装備中: {ua.accessory.name}')
    print(f'use_image: {ua.accessory.use_image}')
    print(f'image_path: {ua.accessory.image_path}')
    print(f'css_class: {ua.accessory.css_class}')
else:
    print('装備中のアクセサリーはありません')
