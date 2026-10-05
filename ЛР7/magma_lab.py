"""ЛР7: реализация блочного шифра «Магма» (ГОСТ 34.12-2015)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

MASK32 = 0xFFFFFFFF
BLOCK_SIZE = 8
KEY_SIZE = 32

S_BOXES = (
    (12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
    (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
    (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
    (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
    (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
    (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
    (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
    (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2),
)


def rotate_left_11(value: int) -> int:
    return ((value << 11) | (value >> 21)) & MASK32


def substitute(value: int) -> int:
    """Заменить восемь 4-битных частей значениями S-блоков Магмы."""
    result = 0
    for index, s_box in enumerate(S_BOXES):
        result |= s_box[(value >> (4 * index)) & 0xF] << (4 * index)
    return result


def g(value: int, key: int) -> int:
    return rotate_left_11(substitute((value + key) & MASK32))


@dataclass(frozen=True)
class Magma:
    """Шифр Магма с 256-битным ключом и 64-битным блоком."""

    key: bytes

    def __post_init__(self) -> None:
        if len(self.key) != KEY_SIZE:
            raise ValueError("Ключ Магмы должен содержать ровно 32 байта")

    @property
    def round_keys(self) -> list[int]:
        parts = [int.from_bytes(self.key[i:i + 4], "big") for i in range(0, KEY_SIZE, 4)]
        return parts * 3 + list(reversed(parts))

    def encrypt_block(self, block: bytes) -> bytes:
        if len(block) != BLOCK_SIZE:
            raise ValueError("Блок Магмы должен содержать ровно 8 байт")
        left = int.from_bytes(block[:4], "big")
        right = int.from_bytes(block[4:], "big")
        for key in self.round_keys[:-1]:
            left, right = right, left ^ g(right, key)
        left ^= g(right, self.round_keys[-1])
        return left.to_bytes(4, "big") + right.to_bytes(4, "big")

    def decrypt_block(self, block: bytes) -> bytes:
        if len(block) != BLOCK_SIZE:
            raise ValueError("Блок Магмы должен содержать ровно 8 байт")
        left = int.from_bytes(block[:4], "big")
        right = int.from_bytes(block[4:], "big")
        keys = list(reversed(self.round_keys))
        for key in keys[:-1]:
            left, right = right, left ^ g(right, key)
        left ^= g(right, keys[-1])
        return left.to_bytes(4, "big") + right.to_bytes(4, "big")


def pad(data: bytes) -> bytes:
    padding = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([padding]) * padding


def unpad(data: bytes) -> bytes:
    if not data or len(data) % BLOCK_SIZE:
        raise ValueError("Недопустимая длина зашифрованных данных")
    padding = data[-1]
    if not 1 <= padding <= BLOCK_SIZE or data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Некорректное PKCS#7-дополнение: неверный ключ или данные")
    return data[:-padding]


def encrypt_data(cipher: Magma, data: bytes) -> bytes:
    raw = pad(data)
    return b"".join(cipher.encrypt_block(raw[i:i + BLOCK_SIZE]) for i in range(0, len(raw), BLOCK_SIZE))


def decrypt_data(cipher: Magma, data: bytes) -> bytes:
    raw = b"".join(cipher.decrypt_block(data[i:i + BLOCK_SIZE]) for i in range(0, len(data), BLOCK_SIZE))
    return unpad(raw)


def main() -> None:
    # Контрольный пример из ГОСТ Р 34.12-2015 / RFC 8891.
    test_key = bytes.fromhex("FFEEDDCCBBAA99887766554433221100F0F1F2F3F4F5F6F7F8F9FAFBFCFDFEFF")
    plain_block = bytes.fromhex("FEDCBA9876543210")
    expected_block = bytes.fromhex("4EE901E5C2D8CA3D")
    test_cipher = Magma(test_key)
    encrypted_block = test_cipher.encrypt_block(plain_block)
    assert encrypted_block == expected_block, "Контрольный вектор ГОСТ не совпал"
    assert test_cipher.decrypt_block(encrypted_block) == plain_block

    key = bytes.fromhex("0123456789ABCDEFFEDCBA987654321000112233445566778899AABBCCDDEEFF")
    cipher = Magma(key)
    message = "Конфиденциальное сообщение: Магма работает корректно.".encode("utf-8")
    encrypted = encrypt_data(cipher, message)
    decrypted = decrypt_data(cipher, encrypted)
    assert decrypted == message

    root = Path(__file__).resolve().parent
    (root / "encrypted_message.hex").write_text(encrypted.hex().upper() + "\n", encoding="ascii")
    (root / "decrypted_message.txt").write_bytes(decrypted)

    print("ЛР7: реализация алгоритма Магма завершена")
    print("Контрольный вектор ГОСТ Р 34.12-2015: пройден")
    print(f"Открытый блок:    {plain_block.hex().upper()}")
    print(f"Зашифрованный:    {encrypted_block.hex().upper()}")
    print(f"Расшифрованный:   {test_cipher.decrypt_block(encrypted_block).hex().upper()}")
    print(f"Длина сообщения:  {len(message)} байт")
    print(f"Длина шифртекста: {len(encrypted)} байт")
    print(f"Шифртекст (hex):  {encrypted.hex().upper()}")
    print("Проверка расшифрования пользовательского сообщения: пройдена")


if __name__ == "__main__":
    main()
