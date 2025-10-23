from app import create_app, db
from app.models.user import User
from app.services.progression import ProgressionService

app = create_app()
with app.app_context():
    test_user = User.query.filter_by(username='admin').first()
    print(f'Current: Level {test_user.level}, Points {test_user.points}')
    
    # Award many reading points to trigger level up
    for i in range(15):
        result = ProgressionService.award_points(test_user.id, 'read_chapter', i+20)
        if result and result['level_up']:
            print(f'🎉 LEVEL UP! Now level {result["new_level"]} - {result["rank_title"]}')
            break
        elif result:
            print(f'Read chapter {i+20}: +{result["points_earned"]} points (total: {result["total_points"]})')
        else:
            print(f'No points awarded for chapter {i+20} (daily limit reached)')
    
    # Show final stats
    db.session.refresh(test_user)
    print(f'\nFinal: Level {test_user.level}, Points {test_user.points}')
    print(f'Rank: {test_user.get_rank_title()} ({test_user.get_rank_type_display()})')
    print(f'Progress to next: {test_user.get_progress_to_next_level():.1f}%')