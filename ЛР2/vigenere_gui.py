"""Лабораторная работа № 2: шифр Виженера (вариант 9)."""

import tkinter as tk
from tkinter import messagebox, ttk

ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
VARIANT_TEXT = (
    "Криптосистема является криптостойкой, если предпринятые "
    "криптоаналитические атаки не достигают положительного результата"
)
VARIANT_KEY = "компьютер"


def key_to_numbers(key: str) -> list[int]:
    """Преобразует ключевое слово в номера букв русского алфавита."""
    normalized = key.lower()
    invalid = sorted({char for char in normalized if char not in ALPHABET})
    if invalid:
        raise ValueError("Ключ должен содержать только буквы русского алфавита.")
    if not normalized:
        raise ValueError("Введите ключевое слово.")
    return [ALPHABET.index(char) for char in normalized]


def transform(text: str, key: str, direction: int) -> str:
    """Шифрует (direction=1) или дешифрует (direction=-1) текст Виженером."""
    key_numbers = key_to_numbers(key)
    result: list[str] = []
    key_index = 0

    for char in text:
        lower_char = char.lower()
        if lower_char not in ALPHABET:
            result.append(char)
            continue

        position = ALPHABET.index(lower_char)
        shifted = ALPHABET[(position + direction * key_numbers[key_index % len(key_numbers)]) % len(ALPHABET)]
        result.append(shifted.upper() if char.isupper() else shifted)
        key_index += 1

    return "".join(result)


class VigenereApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ЛР2 — Шифр Виженера")
        self.geometry("920x690")
        self.minsize(760, 570)
        self.configure(padx=18, pady=14)

        self.key_var = tk.StringVar(value=VARIANT_KEY)
        self.numeric_key_var = tk.StringVar()
        self._build_ui()
        self.source_text.insert("1.0", VARIANT_TEXT)
        self.update_numeric_key()

    def _build_ui(self) -> None:
        ttk.Label(
            self,
            text="Шифрование с использованием системы Виженера",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self,
            text="Вариант 9. Русский алфавит из 33 букв, включая «ё». Нумерация букв начинается с 0.",
        ).pack(anchor="w", pady=(2, 12))

        key_frame = ttk.Frame(self)
        key_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(key_frame, text="Ключевое слово:").grid(row=0, column=0, sticky="w")
        key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=28)
        key_entry.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        key_entry.bind("<KeyRelease>", lambda _event: self.update_numeric_key())
        ttk.Label(key_frame, text="Числовой ключ:").grid(row=0, column=2, sticky="w")
        ttk.Entry(key_frame, textvariable=self.numeric_key_var, state="readonly", width=36).grid(
            row=0, column=3, sticky="ew", padx=(8, 0)
        )
        key_frame.columnconfigure(1, weight=1)
        key_frame.columnconfigure(3, weight=2)

        ttk.Label(self, text="Исходный текст:").pack(anchor="w")
        self.source_text = tk.Text(self, height=9, wrap="word", font=("Segoe UI", 11))
        self.source_text.pack(fill="both", expand=True, pady=(3, 10))

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(button_frame, text="Зашифровать →", command=lambda: self.process(1)).pack(side="left")
        ttk.Button(button_frame, text="← Дешифровать", command=lambda: self.process(-1)).pack(side="left", padx=8)
        ttk.Button(button_frame, text="Очистить", command=self.clear).pack(side="left")
        ttk.Button(button_frame, text="Загрузить вариант 9", command=self.load_variant).pack(side="right")

        ttk.Label(self, text="Шифрованное / дешифрованное сообщение:").pack(anchor="w")
        self.result_text = tk.Text(self, height=9, wrap="word", font=("Segoe UI", 11))
        self.result_text.pack(fill="both", expand=True, pady=(3, 0))

    def update_numeric_key(self) -> None:
        try:
            numbers = key_to_numbers(self.key_var.get().strip())
            self.numeric_key_var.set(" ".join(map(str, numbers)))
        except ValueError:
            self.numeric_key_var.set("Некорректный ключ")

    def process(self, direction: int) -> None:
        text = self.source_text.get("1.0", "end-1c")
        try:
            result = transform(text, self.key_var.get().strip(), direction)
        except ValueError as error:
            messagebox.showerror("Ошибка ввода", str(error))
            return
        self.update_numeric_key()
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", result)

    def clear(self) -> None:
        self.source_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")

    def load_variant(self) -> None:
        self.key_var.set(VARIANT_KEY)
        self.update_numeric_key()
        self.source_text.delete("1.0", "end")
        self.source_text.insert("1.0", VARIANT_TEXT)
        self.result_text.delete("1.0", "end")


if __name__ == "__main__":
    VigenereApp().mainloop()
