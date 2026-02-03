"""
実績チェック・付与ユーティリティ
"""
from django.utils import timezone
from django.db import transaction
from codemon.models import Achievement, UserAchievement, UserStats, UserCoin
from datetime import date


def check_and_grant_achievements(user, category, current_value=None):
    """
    実績をチェックして達成していれば付与する
    
    Args:
        user: ユーザーオブジェクト
        category: 実績カテゴリー ('system', 'algorithm', 'login', 'consecutive_login', 'ai_chat', 
                  'ai_chat_consecutive', 'checklist_create', 'checklist_complete', 'accessory')
        current_value: 現在の値（オプション、指定しない場合はUserStatsから取得）
    
    Returns:
        list: 新しく達成した実績のリスト
    """
    newly_achieved = []
    
    # UserStatsを取得または作成
    stats, _ = UserStats.objects.get_or_create(user=user)
    
    # カテゴリーごとに現在値を取得
    if current_value is None:
        if category == 'system':
            current_value = stats.total_systems
        elif category == 'algorithm':
            current_value = stats.total_algorithms
        elif category == 'login':
            current_value = stats.total_login_days
        elif category == 'consecutive_login':
            current_value = stats.consecutive_login_days
        elif category == 'ai_chat':
            current_value = stats.total_ai_chats
        elif category == 'ai_chat_consecutive':
            current_value = stats.consecutive_ai_chat_days
        elif category == 'checklist_create':
            current_value = stats.total_checklists_created
        elif category == 'checklist_complete':
            current_value = stats.total_checklist_items_completed
        elif category == 'accessory':
            current_value = stats.total_accessories_purchased
        else:
            return newly_achieved
    
    # 該当カテゴリーの全実績を取得
    achievements = Achievement.objects.filter(category=category).order_by('target_count')
    
    with transaction.atomic():
        for achievement in achievements:
            # ユーザー実績を取得または作成
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
                defaults={'current_count': current_value}
            )
            
            # 既に達成済みならスキップ
            if user_achievement.is_achieved:
                continue
            
            # カウントを更新
            user_achievement.current_count = current_value
            
            # 目標達成チェック
            if current_value >= achievement.target_count:
                user_achievement.is_achieved = True
                user_achievement.achieved_at = timezone.now()
                newly_achieved.append(achievement)
            
            user_achievement.save()
    
    return newly_achieved


def grant_achievement_rewards(user, achievements):
    """
    実績の報酬を付与する
    
    Args:
        user: ユーザーオブジェクト
        achievements: 実績のリスト
    
    Returns:
        int: 付与したコインの合計
    """
    total_coins = 0
    
    with transaction.atomic():
        user_coin, _ = UserCoin.objects.get_or_create(user=user)
        
        for achievement in achievements:
            # UserAchievementを取得
            try:
                user_achievement = UserAchievement.objects.get(
                    user=user,
                    achievement=achievement
                )
                
                # 既に報酬受取済みならスキップ
                if user_achievement.is_rewarded:
                    continue
                
                # コイン付与
                user_coin.balance += achievement.reward_coins
                user_coin.total_earned += achievement.reward_coins
                total_coins += achievement.reward_coins
                
                # 報酬受取済みフラグを立てる
                user_achievement.is_rewarded = True
                user_achievement.rewarded_at = timezone.now()
                user_achievement.save()
                
            except UserAchievement.DoesNotExist:
                continue
        
        user_coin.save()
    
    return total_coins


def update_system_count(user):
    """システム作成数を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    from codemon.models import System
    stats.total_systems = System.objects.filter(user=user).count()
    stats.save()
    
    newly_achieved = check_and_grant_achievements(user, 'system', stats.total_systems)
    return newly_achieved


def update_algorithm_count(user):
    """アルゴリズム作成数を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    from codemon.models import Algorithm
    stats.total_algorithms = Algorithm.objects.filter(user=user).count()
    stats.save()
    
    newly_achieved = check_and_grant_achievements(user, 'algorithm', stats.total_algorithms)
    return newly_achieved


def update_login_stats(user):
    """ログイン統計を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    today = date.today()
    newly_achieved = []
    
    # 最終ログイン日をチェック
    if stats.last_login_date != today:
        # 総ログイン日数を増やす
        stats.total_login_days += 1
        
        # 連続ログイン判定
        if stats.last_login_date:
            days_diff = (today - stats.last_login_date).days
            if days_diff == 1:
                # 連続ログイン継続
                stats.consecutive_login_days += 1
            else:
                # 連続ログイン途切れ
                stats.consecutive_login_days = 1
        else:
            # 初回ログイン
            stats.consecutive_login_days = 1
        
        stats.last_login_date = today
        stats.save()
        
        # 実績チェック
        newly_achieved.extend(check_and_grant_achievements(user, 'login', stats.total_login_days))
        newly_achieved.extend(check_and_grant_achievements(user, 'consecutive_login', stats.consecutive_login_days))
    
    return newly_achieved


def update_ai_chat_count(user):
    """AI会話数と連続会話日数を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    today = date.today()
    newly_achieved = []
    
    # AI会話数を増やす（毎回のメッセージでカウント）
    stats.total_ai_chats += 1
    
    # 連続AI会話日数を更新
    if stats.last_ai_chat_date != today:
        # 最終AI会話日をチェック
        if stats.last_ai_chat_date:
            days_diff = (today - stats.last_ai_chat_date).days
            if days_diff == 1:
                # 連続会話継続
                stats.consecutive_ai_chat_days += 1
            else:
                # 連続会話途切れ
                stats.consecutive_ai_chat_days = 1
        else:
            # 初回会話
            stats.consecutive_ai_chat_days = 1
        
        stats.last_ai_chat_date = today
    
    stats.save()
    
    # 実績チェック
    newly_achieved.extend(check_and_grant_achievements(user, 'ai_chat', stats.total_ai_chats))
    newly_achieved.extend(check_and_grant_achievements(user, 'ai_chat_consecutive', stats.consecutive_ai_chat_days))
    
    return newly_achieved


def update_checklist_create_count(user):
    """チェックリスト作成数を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    from codemon.models import Checklist
    stats.total_checklists_created = Checklist.objects.filter(user=user).count()
    stats.save()
    
    newly_achieved = check_and_grant_achievements(user, 'checklist_create', stats.total_checklists_created)
    return newly_achieved


def update_checklist_complete_count(user):
    """チェックリスト完了項目数を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    from codemon.models import ChecklistItem
    stats.total_checklist_items_completed = ChecklistItem.objects.filter(
        checklist__user=user, 
        is_done=True
    ).count()
    stats.save()
    
    newly_achieved = check_and_grant_achievements(user, 'checklist_complete', stats.total_checklist_items_completed)
    return newly_achieved


def update_accessory_purchase_count(user):
    """アクセサリー購入数を更新して実績チェック"""
    stats, _ = UserStats.objects.get_or_create(user=user)
    from codemon.models import UserAccessory
    stats.total_accessories_purchased = UserAccessory.objects.filter(user=user).count()
    stats.save()
    
    newly_achieved = check_and_grant_achievements(user, 'accessory', stats.total_accessories_purchased)
    return newly_achieved


def get_user_achievements_progress(user):
    """
    ユーザーの全実績の進捗状況を取得
    各カテゴリで次に達成すべき実績（または最後に達成した実績）のみを返す
    
    Returns:
        dict: カテゴリー別の実績進捗（各カテゴリ1つずつ）
    """
    stats, _ = UserStats.objects.get_or_create(user=user)
    all_achievements = Achievement.objects.all().order_by('category', 'target_count')
    
    progress = {
        'system': None,
        'algorithm': None,
        'login': None,
        'consecutive_login': None,
        'ai_chat': None,
        'ai_chat_consecutive': None,
        'checklist_create': None,
        'checklist_complete': None,
        'accessory': None,
    }
    
    category_values = {
        'system': stats.total_systems,
        'algorithm': stats.total_algorithms,
        'login': stats.total_login_days,
        'consecutive_login': stats.consecutive_login_days,
        'ai_chat': stats.total_ai_chats,
        'ai_chat_consecutive': stats.consecutive_ai_chat_days,
        'checklist_create': stats.total_checklists_created,
        'checklist_complete': stats.total_checklist_items_completed,
        'accessory': stats.total_accessories_purchased,
    }
    
    for category in progress.keys():
        current_value = category_values[category]
        category_achievements = all_achievements.filter(category=category).order_by('target_count')
        
        # カテゴリに実績がない場合はスキップ
        if not category_achievements.exists():
            continue
        
        # 次に達成すべき実績を探す
        next_achievement = None
        for achievement in category_achievements:
            user_achievement, _ = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
            
            # 達成状態を現在値で判定（is_achievedフラグが更新されていない可能性があるため）
            is_actually_achieved = current_value >= achievement.target_count
            
            # 現在値とパーセンテージを計算
            progress_percentage = min(100, int(current_value / achievement.target_count * 100)) if achievement.target_count > 0 else 0
            remaining = max(0, achievement.target_count - current_value)
            
            # まだ達成していない実績、または達成したばかりで次がない実績を表示
            if not is_actually_achieved:
                # 未達成の実績が見つかったらそれを表示
                next_achievement = {
                    'achievement': achievement,
                    'user_achievement': user_achievement,
                    'current_count': current_value,
                    'target_count': achievement.target_count,
                    'progress_percentage': progress_percentage,
                    'remaining': remaining,
                }
                break
        
        # 全て達成済みの場合は最後の実績を表示
        if next_achievement is None:
            last_achievement = category_achievements.last()
            user_achievement, _ = UserAchievement.objects.get_or_create(
                user=user,
                achievement=last_achievement
            )
            next_achievement = {
                'achievement': last_achievement,
                'user_achievement': user_achievement,
                'current_count': current_value,
                'target_count': last_achievement.target_count,
                'progress_percentage': 100,
                'remaining': 0,
            }
        
        progress[category] = next_achievement
    
    return progress
