from app import app, db
from models import User, Admin, Ewaste, Schedule

with app.app_context():
    print(f'Users: {User.query.count()}')
    print(f'Admins: {Admin.query.count()}')
    print(f'E-waste items: {Ewaste.query.count()}')
    print(f'Schedules: {Schedule.query.count()}')
    
    if User.query.count() > 0:
        print("\nUser Details:")
        for user in User.query.all():
            print(f"- {user.username} (ID: {user.id}, Eco points: {user.eco_points})")

    if Ewaste.query.count() > 0:
        print("\nE-waste Items:")
        for ewaste in Ewaste.query.all():
            print(f"- {ewaste.ewaste_type} (ID: {ewaste.id}, User ID: {ewaste.user_id})")

    if Schedule.query.count() > 0:
        print("\nSchedules:")
        for schedule in Schedule.query.all():
            print(f"- ID: {schedule.id}, User ID: {schedule.user_id}, E-waste ID: {schedule.ewaste_id}, Status: {schedule.status}")