import os
from django import forms
from django.conf import settings
from .models import ChatMessage, ChatAttachment

class ChatAttachmentForm(forms.ModelForm):
    """チャット添付ファイルフォーム"""
    class Meta:
        model = ChatAttachment
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return None

        # ファイルサイズ制限（settings.pyで定義）
        if file.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise forms.ValidationError(f'ファイルサイズは{max_mb}MB以下にしてください。')

        # 許可する拡張子（settings.pyで定義）
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            allowed = ', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)
            raise forms.ValidationError(f'許可されているファイル形式: {allowed}')

        return file