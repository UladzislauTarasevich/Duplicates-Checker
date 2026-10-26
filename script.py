from collections import defaultdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def find_duplicates(directory_path, status_label, root):
  code_occurrences = defaultdict(list)
  txt_files = list(Path(directory_path).glob("*.txt"))

  if not txt_files:
    messagebox.showwarning(
        "Внимание",
        f"В выбранной папке не найдено текстовых файлов (.txt)!",
        parent=root,
    )
    status_label.config(text="Файлы .txt не найдены.")
    return

  status_label.config(
      text=f"Обработка файлов... Найдено: {len(txt_files)} шт."
  )
  root.update()

  for file_path in txt_files:
    try:
      with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
          stripped_line = line.strip()
          if not stripped_line:
            continue

          parts = stripped_line.split()
          if len(parts) >= 6:
            date = parts[0]
            time = parts[1]
            row_num = parts[2]
            camera = parts[3]
            code = parts[4]
            print_class = parts[-1]

            code_occurrences[code].append({
                "file": file_path.name,
                "file_line": line_num,
                "date": date,
                "time": time,
                "row_num": row_num,
                "camera": camera,
                "class": print_class,
            })
    except Exception as e:
      print(f"Ошибка при чтении файла {file_path.name}: {e}")

  duplicates = {
      code: occs for code, occs in code_occurrences.items() if len(occs) > 1
  }

  # Формируем текст отчета с измененным словом
  report_lines = []
  if not duplicates:
    report_lines.append("Дубликаты кодов не найдены! Все коды уникальны.")
  else:
    report_lines.append(
        f"Обнаружено кодов с дубликатами: {len(duplicates)}\n"
    )
    report_lines.append("=" * 60 + "\n")
    for code, occs in duplicates.items():
      report_lines.append(f"Код: {code} (дубликатов: {len(occs)})\n")
      for occ in occs:
        report_lines.append(
            f"  -> Файл: {occ['file']} | Строка: {occ['file_line']} |"
            f" Время: {occ['date']} {occ['time']} | Камера: {occ['camera']}\n"
        )
      report_lines.append("-" * 60 + "\n")

  full_report_text = "".join(report_lines)

  status_label.config(text="Готово!")
  show_results_window(root, full_report_text, bool(duplicates))


def show_results_window(parent, report_text, has_duplicates):
  win = tk.Toplevel(parent)
  win.title("Результаты проверки")
  win.geometry("700x500")
  win.minsize(500, 400)

  main_frame = ttk.Frame(win, padding=16)
  main_frame.pack(fill=tk.BOTH, expand=True)

  header_text = (
      "⚠️ Обнаружены дубликаты кодов:"
      if has_duplicates
      else "✅ Всё в порядке! Дубликаты не обнаружены."
  )

  lbl = ttk.Label(
      main_frame, text=header_text, font=("Segoe UI", 12, "bold")
  )
  lbl.pack(anchor="w", pady=(0, 10))

  text_frame = ttk.Frame(main_frame)
  text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

  txt_area = tk.Text(
      text_frame,
      wrap=tk.WORD,
      font=("Consolas", 10),
      bg="#F9F9F9",
      fg="#222222",
      bd=1,
      relief=tk.SOLID,
  )
  scrollbar = ttk.Scrollbar(
      text_frame, orient=tk.VERTICAL, command=txt_area.yview
  )
  txt_area.configure(yscrollcommand=scrollbar.set)

  txt_area.insert(tk.INSERT, report_text)
  txt_area.config(state=tk.DISABLED)

  txt_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
  scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

  btn_close = ttk.Button(
      main_frame, text="Закрыть", command=win.destroy, width=15
  )
  btn_close.pack(anchor="e", pady=(5, 0))


def select_folder_and_run():
  folder_selected = filedialog.askdirectory(
      title="Выберите папку с текстовыми файлами логов"
  )
  if folder_selected:
    find_duplicates(folder_selected, status_label, root)


# Главное окно в современном стиле
root = tk.Tk()
root.title("Поиск дубликатов DataMatrix")
root.geometry("460x280")
root.resizable(False, False)
style = ttk.Style()
if "clam" in style.theme_names():
  style.theme_use("clam")

container = ttk.Frame(root, padding=20)
container.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(
    container, text="Проверка дубликатов кодов", font=("Segoe UI", 16, "bold")
)
title_label.pack(anchor="center", pady=(0, 8))

desc_label = ttk.Label(
    container,
    text=(
        "Нажмите на кнопку ниже, чтобы выбрать папку\nс текстовыми файлами"
        " логов."
    ),
    font=("Segoe UI", 10),
    justify="center",
)
desc_label.pack(anchor="center", pady=(0, 20))

btn_select = ttk.Button(
    container, text="Выбрать папку и запустить", command=select_folder_and_run
)
btn_select.pack(anchor="center", ipadx=10, ipady=6, pady=(0, 15))

status_label = ttk.Label(
    container, text="Ожидание выбора папки...", font=("Segoe UI", 9)
)
status_label.pack(anchor="center", side="bottom")

if __name__ == "__main__":
  root.mainloop()
