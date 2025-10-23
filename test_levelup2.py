from app import create_app, db
from app.models.user import User
from app.services.progression import ProgressionService

app = create_app()
with app.app_context():
    test_user = User.query.filter_by(username='admin').first()
    print(f'Starting: Level {test_user.level}, Points {test_user.points}')
    
    # Award different types of points to reach level up
    activities = [
        ('comment', 100),
        ('comment', 101), 
        ('comment', 102),
        ('rating', 200),
        ('rating', 201),
    ]
    
    for activity_type, ref_id in activities:
        result = ProgressionService.award_points(test_user.id, activity_type, ref_id)
        if result and result['level_up']:
            print(f'🎉 LEVEL UP! {activity_type} triggered level up to {result["new_level"]} - {result["rank_title"]}!')
            break
        elif result:
            print(f'{activity_type} {ref_id}: +{result["points_earned"]} points (total: {result["total_points"]})')
        else:
            print(f'No points for {activity_type} {ref_id}')
    
    # Show final stats  
    db.session.refresh(test_user)
    stats = ProgressionService.get_user_stats(test_user.id)
    print(f'\n=== Final Stats ===')
    print(f'Level: {test_user.level}')
    print(f'Points: {test_user.points}')
    print(f'Rank: {test_user.get_rank_title()} ({test_user.get_rank_type_display()})')
    print(f'Progress to next: {test_user.get_progress_to_next_level():.1f}%')
    print(f'Total activities: Reads={stats["total_reads"]}, Comments={stats["total_comments"]}, Ratings={stats["total_ratings"]}')
    print(f'Badges earned: {stats["badge_count"]}')
    
    # Show badges
    if test_user.user_badges:
        print(f'\n=== Earned Badges ===')
        for user_badge in test_user.user_badges:
            badge = user_badge.badge
            print(f'{badge.icon} {badge.name}: {badge.description}')