import math
import tkinter as tk
from tkinter import messagebox, ttk


def norm_cdf(x: float) -> float:
    """Функція розподілу стандартного нормального розподілу N(0, 1)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def on_tournament_change(event=None):
    """Показує/ховає поле для власного коефіцієнта MWF."""
    if combo_tournament.get() == "Власний коефіцієнт (Custom)":
        lbl_custom_mwf.grid(row=2, column=2, padx=5, pady=4, sticky="e")
        entry_custom_mwf.grid(row=2, column=3, padx=5, pady=4, sticky="w")
    else:
        entry_custom_mwf.grid_remove()
        lbl_custom_mwf.grid_remove()


def calculate():
    try:
        t1_name = entry_t1_name.get().strip() or "Команда 1"
        t2_name = entry_t2_name.get().strip() or "Команда 2"

        raw_score1 = entry_t1_score.get().strip().replace(",", ".")
        raw_score2 = entry_t2_score.get().strip().replace(",", ".")

        if not raw_score1 or not raw_score2:
            messagebox.showwarning(
                "Увага",
                "Будь ласка, заповніть рейтингові бали для обох збірних."
            )
            return

        wrs1 = float(raw_score1)
        wrs2 = float(raw_score2)

        tourney_choice = combo_tournament.get()
        if tourney_choice == "Власний коефіцієнт (Custom)":
            mwf = float(entry_custom_mwf.get().strip().replace(",", "."))
        else:
            mwf = float(tournaments[tourney_choice])

        if mwf <= 0:
            raise ValueError("MWF має бути більшим за 0")

    except ValueError:
        messagebox.showerror(
            "Помилка введення",
            "Перевірте коректність введених числових значень балів та коефіцієнта MWF."
        )
        return

    # Розрахунок різниці сили команд за регламентом FIVB
    delta = 8.0 * (wrs1 - wrs2) / 1000.0  #[cite: 2, 3]
    c = [-1.060, -0.394, 0.0, 0.394, 1.060]  #[cite: 2]

    # Розрахунок імовірностей
    p = [
        norm_cdf(c[0] + delta),
        norm_cdf(c[1] + delta) - norm_cdf(c[0] + delta),
        norm_cdf(c[2] + delta) - norm_cdf(c[1] + delta),
        norm_cdf(c[3] + delta) - norm_cdf(c[2] + delta),
        norm_cdf(c[4] + delta) - norm_cdf(c[3] + delta),
        1.0 - norm_cdf(c[4] + delta)
    ]  #[cite: 2, 3]

    scenarios = [
        ("3-0",  2.0, True),
        ("3-1",  1.5, True),
        ("3-2",  1.0, True),
        ("2-3", -1.0, False),
        ("1-3", -1.5, False),
        ("0-3", -2.0, False)
    ]  #[cite: 2, 3]

    emr = sum(prob * ssv for prob, (_, ssv, _) in zip(p, scenarios))  #[cite: 2, 3]

    for row in tree.get_children():
        tree.delete(row)

    tree.heading("t1_pts", text=f"Δ {t1_name}")
    tree.heading("t1_new", text=f"Разом {t1_name}")
    tree.heading("t2_pts", text=f"Δ {t2_name}")
    tree.heading("t2_new", text=f"Разом {t2_name}")

    lbl_info.config(
        text=f"Параметри матчу: Δ = {delta:.4f}  |  EMR = {emr:+.4f}  |  MWF = {mwf:.0f}"
    )

    for prob, (score, ssv, team1_won) in zip(p, scenarios):
        wr_value = ssv - emr  #[cite: 2, 3]
        raw_pts = wr_value * mwf / 8.0  #[cite: 2, 3]

        # Захист команди-переможця від втрати балів
        if team1_won and raw_pts <= 0:
            pts1 = 0.01  #[cite: 2]
        elif not team1_won and raw_pts >= 0:
            pts1 = -0.01
        else:
            pts1 = raw_pts

        pts2 = -pts1  #[cite: 2, 3]

        tree.insert(
            "",
            "end",
            values=(
                score,
                f"{prob * 100:.2f}%",
                f"{pts1:+.2f}",
                f"{wrs1 + pts1:.2f}",
                f"{pts2:+.2f}",
                f"{wrs2 + pts2:.2f}"
            )
        )


# --- Графічний інтерфейс ---
root = tk.Tk()
root.title("Калькулятор рейтингових очок FIVB")
root.geometry("800x530")
root.minsize(760, 490)

style = ttk.Style()
style.theme_use("clam")

frame_inputs = ttk.LabelFrame(root, text=" Вхідні дані матчу та бали збірних ", padding=12)
frame_inputs.pack(fill="x", padx=12, pady=8)

# Рядок 1: Команда 1 (поля залишено пустими)
ttk.Label(frame_inputs, text="Збірна 1:").grid(row=0, column=0, sticky="w", pady=4)
entry_t1_name = ttk.Entry(frame_inputs, width=18)
entry_t1_name.grid(row=0, column=1, padx=5, pady=4, sticky="w")

ttk.Label(frame_inputs, text="Поточні бали:").grid(row=0, column=2, sticky="e", pady=4, padx=5)
entry_t1_score = ttk.Entry(frame_inputs, width=12)
entry_t1_score.grid(row=0, column=3, padx=5, pady=4, sticky="w")

# Рядок 2: Команда 2 (поля залишено пустими)
ttk.Label(frame_inputs, text="Збірна 2:").grid(row=1, column=0, sticky="w", pady=4)
entry_t2_name = ttk.Entry(frame_inputs, width=18)
entry_t2_name.grid(row=1, column=1, padx=5, pady=4, sticky="w")

ttk.Label(frame_inputs, text="Поточні бали:").grid(row=1, column=2, sticky="e", pady=4, padx=5)
entry_t2_score = ttk.Entry(frame_inputs, width=12)
entry_t2_score.grid(row=1, column=3, padx=5, pady=4, sticky="w")

# Рядок 3: Турніри та MWF
tournaments = {
    "Чемпіонат Континенту (MWF 40)": 40,
    "Ліга націй / VNL (MWF 40)": 40,
    "Олімпійські ігри (MWF 50)": 50,
    "Кубок світу (MWF 50)": 50,
    "Щорічні континентальні змагання (MWF 30)": 30,
    "Зональні турніри (MWF 20)": 20,
    "Власний коефіцієнт (Custom)": 0
}

ttk.Label(frame_inputs, text="Турнір:").grid(row=2, column=0, sticky="w", pady=4)

# Розширено поле списку для повного відображення довгих назв турнірів
combo_tournament = ttk.Combobox(
    frame_inputs,
    values=list(tournaments.keys()),
    state="readonly",
    width=42
)
combo_tournament.grid(row=2, column=1, sticky="w", padx=5, pady=4)
combo_tournament.current(0)
combo_tournament.bind("<<ComboboxSelected>>", on_tournament_change)

lbl_custom_mwf = ttk.Label(frame_inputs, text="MWF:")
entry_custom_mwf = ttk.Entry(frame_inputs, width=8)
entry_custom_mwf.insert(0, "30")

# Кнопка розрахунку
btn_calc = ttk.Button(frame_inputs, text="Розрахувати бали", command=calculate)
btn_calc.grid(row=0, column=4, rowspan=3, padx=15, sticky="nsew")

# Інформаційна плашка
lbl_info = ttk.Label(
    root,
    text="Введіть бали обох збірних та натисніть «Розрахувати бали»",
    font=("Segoe UI", 9, "italic")
)
lbl_info.pack(anchor="w", padx=14, pady=2)

# Таблиця результатів
frame_table = ttk.Frame(root, padding=12)
frame_table.pack(fill="both", expand=True)

columns = ("score", "prob", "t1_pts", "t1_new", "t2_pts", "t2_new")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=7)

tree.heading("score", text="Рахунок")
tree.heading("prob", text="Ймовірність")
tree.heading("t1_pts", text="Δ Збірна 1")
tree.heading("t1_new", text="Разом 1")
tree.heading("t2_pts", text="Δ Збірна 2")
tree.heading("t2_new", text="Разом 2")

col_widths = [80, 105, 115, 125, 115, 125]
for col, width in zip(columns, col_widths):
    tree.column(col, width=width, anchor="center")

tree.pack(fill="both", expand=True)

root.mainloop()