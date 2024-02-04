from app.models.user_types import UserType
from app.models.user import User
from app.auth.auth import get_hashed_password
from app.utils.create import create_vertical


def create_admin_user(db):
    # check if admin user exists email or username
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        user = db.query(User).filter(User.email == "admin@localhost").first()
        if not user:
            user = User(
                username="admin",
                email="admin@localhost",
                password=get_hashed_password("admin"),
                user_type=UserType.ADMIN.value,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print("Admin user already exists")
    else:
        print("Admin user already exists")


# to create
#         water quality- WQ
# water quantity -WF
# waste management- WM
# streetlights-ST
# Energy Monitoring -EM
# Air Quality -AQ
def create_initial_verticals(db):
    verticals = [
        {
            "name": "Water Quality",
            "short_name": "WQ",
            "description": "Water Quality",
            "labels": ["WQ"],
        },
        {
            "name": "Water Quantity",
            "short_name": "WF",
            "description": "Water Quantity",
            "labels": ["WF"],
        },
        {
            "name": "Waste Management",
            "short_name": "WM",
            "description": "Waste Management",
            "labels": ["WM"],
        },
        {
            "name": "Streetlights",
            "short_name": "ST",
            "description": "Streetlights",
            "labels": ["ST"],
        },
        {
            "name": "Energy Monitoring",
            "short_name": "EM",
            "description": "Energy Monitoring",
            "labels": ["EM"],
        },
        {
            "name": "Air Quality",
            "short_name": "AQ",
            "description": "Air Quality",
            "labels": ["AQ"],
        },
    ]
    for vertical in verticals:
        status = create_vertical(
            vertical["name"],
            vertical["short_name"],
            vertical["description"],
            vertical["labels"],
            db,
        )
        if status == 201:
            pass
        elif status == 409:
            print(f"Vertical {vertical['name']} already exists")
        else:
            print(f"Error creating vertical {vertical['name']}")
    print("Verticals created")
    pass


def initial_setup(db):
    create_admin_user(db)
    create_initial_verticals(db)
    print("Initial setup complete")
