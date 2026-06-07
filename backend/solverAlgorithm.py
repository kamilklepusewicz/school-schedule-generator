from ortools.sat.python import cp_model
from algorithm_data import fetch_data_for_algorithm
from database import SessionLocal
from models import Lesson

def algorytm_planu_lekcji():
    #Pobranie Danych
    db_data = fetch_data_for_algorithm()
    
    sale = {c["id"]: {"typ": c["type_id"]} for c in db_data["classrooms"]}
    przedmioty = {s["id"]: {"typ_sali": s["type_id"]} for s in db_data["subjects"]}
    
    # Grupowanie nauczycieli po przedmiocie który mogą wykładać
    nauczyciele_per_przedmiot = {}
    for t in db_data["teachers"]:
        sub_id = t["subject_id"]
        if sub_id not in nauczyciele_per_przedmiot:
            nauczyciele_per_przedmiot[sub_id] = []
        nauczyciele_per_przedmiot[sub_id].append(t["id"])

    # Konfiguracja ram czasowych
    dni = [1, 2, 3, 4, 5]
    godziny = [1, 2, 3, 4, 5, 6, 7, 8]
    wymagane_lekcje = []
    globalny_id_lekcji = 1
    
    for d in db_data["demands"]:
        sub_id = d["subject_id"]
        # Pobieramy nauczyciela przypisanego do przedmiotu
        dostepni_nauczyciele = nauczyciele_per_przedmiot.get(sub_id, [])
        if not dostepni_nauczyciele:
            print(f"[-] Błąd: Brak nauczyciela przypisanego do przedmiotu ID: {sub_id}.")
            continue
        t_id = dostepni_nauczyciele[0]

        for _ in range(d["hours"]):
            wymagane_lekcje.append({
                "id": globalny_id_lekcji,
                "group_id": d["group_id"],
                "subject_id": sub_id,
                "teacher_id": t_id
            })
            globalny_id_lekcji += 1

    #Budowa algorytmu
    model = cp_model.CpModel()
    zmienne_lekcji = {}
    
    # Tworzenie zmiennych dla każdej pojedynczej godziny lekcyjnej
    for lekcja in wymagane_lekcje:
        l_id = lekcja["id"]
        
        dzien = model.NewIntVar(min(dni), max(dni), f"dzien_l{l_id}")
        godzina = model.NewIntVar(min(godziny), max(godziny), f"godzina_l{l_id}")
        sala = model.NewIntVar(min(sale.keys()), max(sale.keys()), f"sala_l{l_id}")
        
        zmienne_lekcji[l_id] = {
            "dzien": dzien,
            "godzina": godzina,
            "sala": sala,
            "dane": lekcja
        }

    # Nakładanie więzów typu sali
    for l_id, zm in zmienne_lekcji.items():
        sub_id = zm["dane"]["subject_id"]
        wymagany_typ = przedmioty[sub_id]["typ_sali"]
        dozwolone_sale_id = [[s_id] for s_id, s_dane in sale.items() if s_dane["typ"] == wymagany_typ]
        
        model.AddAllowedAssignments([zm["sala"]], dozwolone_sale_id)

    # Detekcja konfliktów
    lekcje_ids = list(zmienne_lekcji.keys())
    for i in range(len(lekcje_ids)):
        for j in range(i + 1, len(lekcje_ids)):
            id_a = lekcje_ids[i]
            id_b = lekcje_ids[j]
            zm_a = zmienne_lekcji[id_a]
            zm_b = zmienne_lekcji[id_b]
            
            ten_sam_czas = model.NewBoolVar(f"czas_{id_a}_{id_b}")
            ten_sam_dzien = model.NewBoolVar(f"dzien_{id_a}_{id_b}")
            ta_sama_godzina = model.NewBoolVar(f"godz_{id_a}_{id_b}")
            
            model.Add(zm_a["dzien"] == zm_b["dzien"]).OnlyEnforceIf(ten_sam_dzien)
            model.Add(zm_a["dzien"] != zm_b["dzien"]).OnlyEnforceIf(ten_sam_dzien.Not())
            model.Add(zm_a["godzina"] == zm_b["godzina"]).OnlyEnforceIf(ta_sama_godzina)
            model.Add(zm_a["godzina"] != zm_b["godzina"]).OnlyEnforceIf(ta_sama_godzina.Not())
            
            model.AddBoolAnd([ten_sam_dzien, ta_sama_godzina]).OnlyEnforceIf(ten_sam_czas)
            model.AddBoolOr([ten_sam_dzien.Not(), ta_sama_godzina.Not()]).OnlyEnforceIf(ten_sam_czas.Not())

            if zm_a["dane"]["group_id"] == zm_b["dane"]["group_id"]:
                model.Add(ten_sam_czas == 0)
                
            if zm_a["dane"]["teacher_id"] == zm_b["dane"]["teacher_id"]:
                model.Add(ten_sam_czas == 0)
                
            # Jeśli dwie lekcje trafiły na ten sam czas, to sale muszą być różne
            model.Add(zm_a["sala"] != zm_b["sala"]).OnlyEnforceIf(ten_sam_czas)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)


    #Wyrzucenie danych do zapisu
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        wygenerowany_plan = []
        for l_id, zm in zmienne_lekcji.items():
            wygenerowany_plan.append({
                "subject_id": zm["dane"]["subject_id"],
                "classroom_id": solver.Value(zm["sala"]),
                "teacher_id": zm["dane"]["teacher_id"],
                "group_id": zm["dane"]["group_id"],
                "day": solver.Value(zm["dzien"]),
                "slot": solver.Value(zm["godzina"])
            })
        zapisz_wyniki_do_bazy(wygenerowany_plan)
    else:
        print("[-] Solver nie znalazł rozwiązania spełniającego wszystkie warunki.")

def zapisz_wyniki_do_bazy(wygenerowany_plan):
    print("[+] Rozpoczynam zapis wygenerowanego planu do bazy danych...")
    
    # Otwieramy sesję do bazy danych
    db = SessionLocal()
    
    try:
        # Czyścimy całą tabelę 'lesson', żeby uniknąć duplikatów ze starego generowania
        print("[*] Czyszczenie starego planu lekcji z tabeli 'lesson'...")
        db.query(Lesson).delete()
        
        # Dodawanie nowych lekcji
        print(f"[*] Przygotowywanie {len(wygenerowany_plan)} nowych lekcji do zapisu...")
        for lekcja in wygenerowany_plan:
            # Tworzymy obiekt modelowy SQLAlchemy na podstawie słownika z OR-Tools
            nowa_lekcja = Lesson(
                subject_id=lekcja["subject_id"],
                classroom_id=lekcja["classroom_id"],
                teacher_id=lekcja["teacher_id"],
                group_id=lekcja["group_id"],
                day=lekcja["day"],
                slot=lekcja["slot"]
            )
            # Dodajemy obiekt do pamięci podręcznej sesji
            db.add(nowa_lekcja)
        
        # Zatwierdzenie zmian
        db.commit()
        print("[+] SUKCES! Nowy plan lekcji został pomyślnie zapisany w bazie danych.")
        
    except Exception as e:
        # W razie jakiegokolwiek błędu (np. błąd połączenia, naruszenie klucza obcego)
        # wycofujemy wszystkie zmiany, żeby nie zostawić bazy w niepewnym stanie.
        db.rollback()
        print(f"[-] BŁĄD podczas zapisu do bazy danych: {e}")
        print("[-] Transakcja została wycofana (Rollback).")
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        algorytm_planu_lekcji()
    except Exception as e:
        print(f"Wystąpił błąd: {e}")