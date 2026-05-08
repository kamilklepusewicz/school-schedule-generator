import random
from faker import Faker
from database import engine, SessionLocal, Base
from models import Teacher, StudentGroup, Subject, Classroom, ClassroomType, LessonCount

# Inicjalizacja Fakera z polskimi danymi
fake = Faker('pl_PL')

# Tworzymy osobną sesję do bazy specjalnie dla tego skryptu
db = SessionLocal()

def seed_data():
    print("Czyszczenie starej bazy danych")
    # Twardy reset - usuwa wszystkie tabele i tworzy je na nowo
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Rozpoczynam 'sianie' danych")

    # 1. Typy sal
    print("Tworzenie typów sal")
    types = ["Ogólna", "Informatyczna", "Gimnastyczna", "Chemiczna", "Językowa"]
    db_types = []
    for t_name in types:
        new_type = ClassroomType(name=t_name)
        db.add(new_type)
        db_types.append(new_type)
    db.commit()

    # 2. Klasy (Grupy uczniów)
    print("Tworzenie klas")
    groups = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]
    db_groups = []
    for g_name in groups:
        new_group = StudentGroup(name=g_name)
        db.add(new_group)
        db_groups.append(new_group)
    db.commit()

    # 3. Przedmioty
    print("Tworzenie przedmiotów")
    # Przypisujemy przedmiotom odpowiednie typy sal z utworzonych wcześniej
    subjects_data = [
        ("Matematyka", db_types[0].id), ("Język Polski", db_types[0].id),
        ("Informatyka", db_types[1].id), ("Wychowanie Fizyczne", db_types[2].id),
        ("Chemia", db_types[3].id), ("Język Angielski", db_types[4].id),
        ("Historia", db_types[0].id), ("Fizyka", db_types[0].id)
    ]
    db_subjects = []
    for s_name, t_id in subjects_data:
        new_subject = Subject(name=s_name, classroom_type_id=t_id)
        db.add(new_subject)
        db_subjects.append(new_subject)
    db.commit()

    # 4. Sale lekcyjne
    print("Tworzenie sal lekcyjnych")
    db_classrooms = []
    for i in range(1, 21): # Tworzymy 20 sal
        # Losujemy typ sali dla każdego pomieszczenia
        random_type = random.choice(db_types)
        new_classroom = Classroom(name=f"Sala {100 + i}", classroom_type_id=random_type.id)
        db.add(new_classroom)
        db_classrooms.append(new_classroom)
    db.commit()

    # 5. Nauczyciele
    print("Tworzenie nauczycieli")
    for _ in range(30): # Tworzymy 30 nauczycieli
        # Losujemy przedmiot dla nauczyciela
        random_subject = random.choice(db_subjects)
        new_teacher = Teacher(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            subject_id=random_subject.id
        )
        db.add(new_teacher)
    db.commit()

    # 6. Siatka Godzin (Zapotrzebowanie)
    print("Generowanie siatki godzin")
    for group in db_groups:
        # Dla każdej klasy losujemy od 4 do 6 przedmiotów
        sampled_subjects = random.sample(db_subjects, k=random.randint(4, 6))
        for subject in sampled_subjects:
            new_count = LessonCount(
                student_group_id=group.id,
                subject_id=subject.id,
                hours=random.randint(2, 5) # Od 2 do 5 godzin w tygodniu
            )
            db.add(new_count)
    db.commit()

    print("Gotowe, baza danych została w pełni zaludniona mockowymi danymi.")

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"Wystąpił błąd podczas siania danych: {e}")
    finally:
        db.close()