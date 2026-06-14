from ortools.sat.python import cp_model
from collections import defaultdict


def algorytm_planu_lekcji(db_data):
    sale = {c["id"]: {"typ": c["type_id"]} for c in db_data["classrooms"]}
    przedmioty = {s["id"]: {"typ_sali": s["type_id"]} for s in db_data["subjects"]}

    nauczyciele_per_przedmiot = defaultdict(list)
    for t in db_data["teachers"]:
        nauczyciele_per_przedmiot[t["subject_id"]].append(t["id"])

    dni = [1, 2, 3, 4, 5]
    godziny = [1, 2, 3, 4, 5, 6, 7, 8]

    wymagane_lekcje = []
    globalny_id_lekcji = 1

    for d in db_data["demands"]:
        sub_id = d["subject_id"]
        group_id = d["group_id"]
        hours = d["hours"]

        if sub_id not in przedmioty:
            continue

        dostepni_nauczyciele = nauczyciele_per_przedmiot.get(sub_id, [])
        if not dostepni_nauczyciele:
            continue

        wymagany_typ_sali = przedmioty[sub_id]["typ_sali"]
        dostepne_sale = [
            s_id for s_id, s_dane in sale.items()
            if s_dane["typ"] == wymagany_typ_sali
        ]

        if not dostepne_sale:
            continue

        # Na razie nauczyciel jest przypisywany przed solverem.
        # To proste rozwiązanie, ale w przyszłości można zrobić teacher_id jako zmienną solvera.
        index_nauczyciela = group_id % len(dostepni_nauczyciele)
        t_id = dostepni_nauczyciele[index_nauczyciela]

        for _ in range(hours):
            wymagane_lekcje.append({
                "id": globalny_id_lekcji,
                "group_id": group_id,
                "subject_id": sub_id,
                "teacher_id": t_id
            })
            globalny_id_lekcji += 1

    if not wymagane_lekcje:
        return []

    model = cp_model.CpModel()
    zmienne_lekcji = {}

    min_sala_id = min(sale.keys())
    max_sala_id = max(sale.keys())

    for lekcja in wymagane_lekcje:
        l_id = lekcja["id"]

        dzien = model.NewIntVar(min(dni), max(dni), f"dzien_l{l_id}")
        godzina = model.NewIntVar(min(godziny), max(godziny), f"godzina_l{l_id}")
        sala = model.NewIntVar(min_sala_id, max_sala_id, f"sala_l{l_id}")

        zmienne_lekcji[l_id] = {
            "dzien": dzien,
            "godzina": godzina,
            "sala": sala,
            "dane": lekcja
        }

    # ------------------------------------------------------------
    # OGRANICZENIE: sala musi mieć typ zgodny z wymaganiem przedmiotu
    # ------------------------------------------------------------

    for l_id, zm in zmienne_lekcji.items():
        sub_id = zm["dane"]["subject_id"]
        wymagany_typ = przedmioty[sub_id]["typ_sali"]

        dozwolone_sale_id = [
            [s_id] for s_id, s_dane in sale.items()
            if s_dane["typ"] == wymagany_typ
        ]

        if not dozwolone_sale_id:
            return []

        model.AddAllowedAssignments([zm["sala"]], dozwolone_sale_id)

    # ------------------------------------------------------------
    # OGRANICZENIE: maksymalnie 2 lekcje tego samego przedmiotu
    # dla tej samej grupy jednego dnia
    # ------------------------------------------------------------

    lekcje_wg_grupy_i_przedmiotu = defaultdict(list)

    for l_id, zm in zmienne_lekcji.items():
        g_id = zm["dane"]["group_id"]
        s_id = zm["dane"]["subject_id"]
        lekcje_wg_grupy_i_przedmiotu[(g_id, s_id)].append(l_id)

    for (g_id, s_id), l_ids in lekcje_wg_grupy_i_przedmiotu.items():
        if len(l_ids) > 2:
            for d in dni:
                lekcje_w_dniu = []

                for l_id in l_ids:
                    czy_w_tym_dniu = model.NewBoolVar(f"l_{l_id}_w_dniu_{d}")

                    model.Add(zmienne_lekcji[l_id]["dzien"] == d).OnlyEnforceIf(czy_w_tym_dniu)
                    model.Add(zmienne_lekcji[l_id]["dzien"] != d).OnlyEnforceIf(czy_w_tym_dniu.Not())

                    lekcje_w_dniu.append(czy_w_tym_dniu)

                model.Add(sum(lekcje_w_dniu) <= 2)

    # ------------------------------------------------------------
    # OGRANICZENIA KOLIZJI:
    # - ta sama grupa nie może mieć dwóch lekcji jednocześnie
    # - ten sam nauczyciel nie może mieć dwóch lekcji jednocześnie
    # - ta sama sala nie może być użyta w tym samym czasie
    # ------------------------------------------------------------

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

            model.AddBoolAnd([
                ten_sam_dzien,
                ta_sama_godzina
            ]).OnlyEnforceIf(ten_sam_czas)

            model.AddBoolOr([
                ten_sam_dzien.Not(),
                ta_sama_godzina.Not()
            ]).OnlyEnforceIf(ten_sam_czas.Not())

            if zm_a["dane"]["group_id"] == zm_b["dane"]["group_id"]:
                model.Add(ten_sam_czas == 0)

            if zm_a["dane"]["teacher_id"] == zm_b["dane"]["teacher_id"]:
                model.Add(ten_sam_czas == 0)

            model.Add(zm_a["sala"] != zm_b["sala"]).OnlyEnforceIf(ten_sam_czas)

    # ------------------------------------------------------------
    # ZMIENNE POMOCNICZE DO FUNKCJI CELU
    # Potrzebne do wykrywania okienek w planie.
    # ------------------------------------------------------------

    is_day = {}
    is_hour = {}
    is_at = {}

    for l_id, zm in zmienne_lekcji.items():
        for d in dni:
            b = model.NewBoolVar(f"lesson_{l_id}_is_day_{d}")

            model.Add(zm["dzien"] == d).OnlyEnforceIf(b)
            model.Add(zm["dzien"] != d).OnlyEnforceIf(b.Not())

            is_day[(l_id, d)] = b

        for h in godziny:
            b = model.NewBoolVar(f"lesson_{l_id}_is_hour_{h}")

            model.Add(zm["godzina"] == h).OnlyEnforceIf(b)
            model.Add(zm["godzina"] != h).OnlyEnforceIf(b.Not())

            is_hour[(l_id, h)] = b

        for d in dni:
            for h in godziny:
                b = model.NewBoolVar(f"lesson_{l_id}_is_at_d{d}_h{h}")

                model.AddBoolAnd([
                    is_day[(l_id, d)],
                    is_hour[(l_id, h)]
                ]).OnlyEnforceIf(b)

                model.AddBoolOr([
                    is_day[(l_id, d)].Not(),
                    is_hour[(l_id, h)].Not()
                ]).OnlyEnforceIf(b.Not())

                is_at[(l_id, d, h)] = b

    def policz_okienka(prefix, lekcje_wg_zasobu):

        okienka = []

        for zasob_id, lesson_ids in lekcje_wg_zasobu.items():
            has_lesson = {}

            for d in dni:
                for h in godziny:
                    b = model.NewBoolVar(f"{prefix}_{zasob_id}_has_lesson_d{d}_h{h}")

                    model.AddMaxEquality(
                        b,
                        [is_at[(l_id, d, h)] for l_id in lesson_ids]
                    )

                    has_lesson[(d, h)] = b

            for d in dni:
                for h in godziny[1:-1]:
                    ma_lekcje_wczesniej = model.NewBoolVar(
                        f"{prefix}_{zasob_id}_before_d{d}_h{h}"
                    )

                    ma_lekcje_pozniej = model.NewBoolVar(
                        f"{prefix}_{zasob_id}_after_d{d}_h{h}"
                    )

                    okienko = model.NewBoolVar(
                        f"{prefix}_{zasob_id}_gap_d{d}_h{h}"
                    )

                    model.AddMaxEquality(
                        ma_lekcje_wczesniej,
                        [
                            has_lesson[(d, prev_h)]
                            for prev_h in godziny
                            if prev_h < h
                        ]
                    )

                    model.AddMaxEquality(
                        ma_lekcje_pozniej,
                        [
                            has_lesson[(d, next_h)]
                            for next_h in godziny
                            if next_h > h
                        ]
                    )

                    model.AddBoolAnd([
                        ma_lekcje_wczesniej,
                        ma_lekcje_pozniej,
                        has_lesson[(d, h)].Not()
                    ]).OnlyEnforceIf(okienko)

                    model.AddBoolOr([
                        ma_lekcje_wczesniej.Not(),
                        ma_lekcje_pozniej.Not(),
                        has_lesson[(d, h)]
                    ]).OnlyEnforceIf(okienko.Not())

                    okienka.append(okienko)

        return okienka

    lekcje_wg_grupy = defaultdict(list)
    lekcje_wg_nauczyciela = defaultdict(list)

    for l_id, zm in zmienne_lekcji.items():
        lekcje_wg_grupy[zm["dane"]["group_id"]].append(l_id)
        lekcje_wg_nauczyciela[zm["dane"]["teacher_id"]].append(l_id)

    okienka_klas = policz_okienka("group", lekcje_wg_grupy)
    okienka_nauczycieli = policz_okienka("teacher", lekcje_wg_nauczyciela)

    # ------------------------------------------------------------
    # FUNKCJA CELU
    # Najważniejsze: minimalizacja okienek klas.
    # Potem: minimalizacja okienek nauczycieli.
    # Na końcu: preferowanie wcześniejszych godzin.
    # ------------------------------------------------------------

    model.Minimize(
        1000 * sum(okienka_klas)
        + 200 * sum(okienka_nauczycieli)
        + 150 * sum(zm["godzina"] for zm in zmienne_lekcji.values())
    )

    # ------------------------------------------------------------
    # SOLVER
    # ------------------------------------------------------------

    solver = cp_model.CpSolver()

    solver.parameters.max_time_in_seconds = 120.0
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42

    status = solver.Solve(model)

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

        return wygenerowany_plan

    return []