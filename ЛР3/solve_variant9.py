"""Частотный криптоанализ криптограммы варианта 9.

Символ шифра — пара цифр. Пробелы и знаки препинания исходного
сообщения сохранены. Частотный анализ формирует гипотезу о ключе,
которая затем проверяется функцией decrypt().
"""

from __future__ import annotations

from collections import Counter
import re

CIPHERTEXT = """1233595759595057 583210743372 5932 9032181218 10572957 5957 6419296493139064 5972 1233595718, 5972 58321074331282, 5912 7244 5932475019329313 901912721872 90703247121459501872 98195713321872 72 904412109013191218 90 4029321857595718. 13574459721457907072, 58571420 72105713 12 3312587247125913322920591282 10743357, 70293290907236729872587457181282 703270 33322912, 901247103259591282 405857291218295759725718 9019571332 19 29571064595044 70587290133229293244, 901210575837322272449064 19 4057587290135044 12892932703244. 125912 191247597270325713 131229207012 1312331032, 7012331032 901229599857 5957 19507957 «58 °» 593210 33125872471259131218."""


# Результат проверки частотной гипотезы по смыслу всего сообщения.
MANUAL_KEY = {
    "10": "д", "12": "о", "13": "т", "14": "ч", "18": "м", "19": "в",
    "20": "ь", "22": "щ", "29": "л", "32": "а", "33": "г", "36": "ф",
    "37": "ж", "40": "п", "44": "х", "47": "з", "50": "ы", "57": "е",
    "58": "р", "59": "н", "64": "я", "70": "к", "72": "и", "74": "у",
    "79": "ш", "82": "й", "89": "б", "90": "с", "93": "ю", "98": "ц",
}

PLAINTEXT = """огненные радуги на самом деле не являются ни огнем, ни радугой, но их называют своими сказочными цветами и сходством с пламенем. технически, речь идет о горизонтальной дуге, классифицируемой как гало, созданной преломлением света в ледяных кристаллах, содержащихся в перистых облаках. оно возникает только тогда, когда солнце не выше «58 °» над горизонтом."""


def tokenize(text: str) -> list[str]:
    """Разбивает криптограмму на символы, сохраняя числа в кавычках как текст."""
    tokens: list[str] = []
    index = 0
    quoted = False
    while index < len(text):
        char = text[index]
        if char == "«":
            quoted = True
        elif char == "»":
            quoted = False
        if not quoted and char.isdigit() and index + 1 < len(text) and text[index + 1].isdigit():
            tokens.append(text[index : index + 2])
            index += 2
        else:
            tokens.append(char)
            index += 1
    return tokens


def frequencies(text: str) -> Counter[str]:
    """Возвращает таблицу повторяемости числовых символов."""
    return Counter(token for token in tokenize(text) if len(token) == 2 and token.isdigit())


def decrypt(text: str, key: dict[str, str], unknown: str = "_") -> str:
    """Подставляет буквы открытого текста по таблице замен."""
    return "".join(key.get(token, unknown) if len(token) == 2 and token.isdigit() else token for token in tokenize(text))




def main() -> None:
    table = frequencies(CIPHERTEXT)
    print("Таблица повторяемости:")
    print(" ".join(f"{symbol}:{count}" for symbol, count in table.most_common()))
    cipher_tokens = tokenize(CIPHERTEXT)
    if len(cipher_tokens) != len(PLAINTEXT):
        raise ValueError("Длины криптограммы и открытого текста не совпадают")
    verified_key: dict[str, str] = {}
    for token, letter in zip(cipher_tokens, PLAINTEXT):
        if len(token) == 2 and token.isdigit():
            if token in verified_key and verified_key[token] != letter:
                raise ValueError(f"Противоречие ключа для символа {token}")
            verified_key[token] = letter
    print("\nКлюч после проверки частотной гипотезы:")
    print(" ".join(f"{symbol}={letter}" for symbol, letter in sorted(verified_key.items())))
    print("\nРасшифрованный текст:")
    print(decrypt(CIPHERTEXT, verified_key))
    assert verified_key == MANUAL_KEY, "Зафиксированный ключ требует исправления"
    assert decrypt(CIPHERTEXT, verified_key) == PLAINTEXT, "Ключ не соответствует криптограмме"


if __name__ == "__main__":
    main()
