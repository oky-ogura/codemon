import re

with open('codemon/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. インポート部分の置換
content = re.sub(
    r'from \.models import \(\s*Checklist, ChecklistItem, ChatThread, ChatScore, ChatMessage, ChatAttachment,\s*Group, GroupMember, AIConversation, AIMessage\s*\)',
    'from .models import (\n    Checklist, ChecklistItem, ChatThread, ChatScore, ChatMessage, ChatAttachment,\n    MessegeGroup, MessegeMember, AIConversation, AIMessage\n)',
    content
)

# 2. クラスメソッド内のGroup参照を置換
content = re.sub(r'\bGroup\.objects\b', 'MessegeGroup.objects', content)
content = re.sub(r'\bGroupMember\.objects\b', 'MessegeMember.objects', content)
content = re.sub(r'\bGroupMember\.DoesNotExist\b', 'MessegeMember.DoesNotExist', content)

# 3. ローカルインポートの置換
content = re.sub(
    r'from codemon\.models import .*?Group.*?\n',
    'from codemon.models import MessegeGroup, MessegeMember\n',
    content,
    flags=re.MULTILINE
)

with open('codemon/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('views.py置換完了')
