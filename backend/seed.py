import random
from faker import Faker
from database import engine, SessionLocal, Base
from models import Teacher, StudentGroup, Subject, Classroom, ClassroomType, LessonCount

# Inicjalizacja Fakera z polskimi danymi
fake = Faker('pl_PL')

# Tworzymy osobną sesję do bazy specjalnie dla tego skryptu
db = SessionLocal()

def seed_data():
    print("[*] Czyszczenie starej bazy danych...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("[*] Rozpoczynam 'sianie' zbalansowanych danych...")

    # 1. Typy sal
    print(" -> Tworzenie typów sal")
    types = ["Ogólna", "Informatyczna", "Gimnastyczna", "Chemiczna", "Językowa"]
    db_types = {}
    for t_name in types:
        new_type = ClassroomType(name=t_name)
        db.add(new_type)
        db_types[t_name] = new_type
    db.commit()

    # 2. Klasy (Grupy uczniów)
    print(" -> Tworzenie klas")
    groups = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]
    db_groups = []
    for g_name in groups:
        new_group = StudentGroup(name=g_name)
        db.add(new_group)
        db_groups.append(new_group)
    db.commit()

    # 3. Przedmioty i przypisanie do typów sal
    print(" -> Tworzenie przedmiotów")
    subjects_data = [
        ("Matematyka", "Ogólna"), 
        ("Język Polski", "Ogólna"),
        ("Historia", "Ogólna"), 
        ("Fizyka", "Ogólna"),
        ("Informatyka", "Informatyczna"), 
        ("Wychowanie Fizyczne", "Gimnastyczna"),
        ("Chemia", "Chemiczna"), 
        ("Język Angielski", "Językowa")
    ]
    db_subjects = {}
    for s_name, t_name in subjects_data:
        new_subject = Subject(name=s_name, classroom_type_id=db_types[t_name].id)
        db.add(new_subject)
        db_subjects[s_name] = new_subject
    db.commit()

    # 4. Sale lekcyjne (Kontrolowany przydział zamiast czystego randoma)
    print(" -> Tworzenie zbalansowanych sal lekcyjnych")
    room_distribution = {
        "Ogólna": 10,
        "Informatyczna": 3,
        "Gimnastyczna": 3,
        "Chemiczna": 2,
        "Językowa": 2
    }
    room_counter = 101
    for t_name, count in room_distribution.items():
        for _ in range(count):
            new_classroom = Classroom(name=f"Sala {room_counter}", classroom_type_id=db_types[t_name].id)
            db.add(new_classroom)
            room_counter += 1
    db.commit()

    # 5. Nauczyciele (Każdy przedmiot ma gwarantowanych 3 nauczycieli)
    print(" -> Tworzenie zbalansowanej kadry nauczycielskiej")
    for s_name, subject_obj in db_subjects.items():
        for _ in range(3):
            new_teacher = Teacher(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                subject_id=subject_obj.id
            )
            db.add(new_teacher)
    db.commit()

    # 6. Siatka Godzin (Standardowy etat 25h dla każdej klasy)
    print(" -> Generowanie realistycznej siatki godzin (Brak bezrobocia)")
    # Razem dokładnie 25 godzin tygodniowo (idealnie po 5 godzin dziennie)
    standard_curriculum = {
        "Matematyka": 5,
        "Język Polski": 5,
        "Język Angielski": 4,
        "Wychowanie Fizyczne": 3,
        "Informatyka": 2,
        "Historia": 2,
        "Fizyka": 2,
        "Chemia": 2
    }

    for group in db_groups:
        for s_name, hours in standard_curriculum.items():
            new_count = LessonCount(
                student_group_id=group.id,
                subject_id=db_subjects[s_name].id,
                hours=hours
            )
            db.add(new_count)
    db.commit()

    print("[+] Gotowe! Baza danych zaludniona danymi zoptymalizowanymi pod solver OR-Tools.")

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"[-] Wystąpił błąd podczas siania danych: {e}")
    finally:
        db.close()