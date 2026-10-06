"""Фактическая проверка артефактов ЛР5 средствами GnuPG и SHA-256."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(label: str, args: list[str], expected: int = 0, cwd: Path = ROOT) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    print((result.stdout + result.stderr).strip())
    if result.returncode != expected:
        raise SystemExit(f"Неожиданный код завершения: {result.returncode}, ожидался {expected}")


def main() -> None:
    print("ЛР5: проверка цифровой подписи и контрольной суммы")
    run("Корректная отсоединённая подпись", ["gpg", "--verify", "notion.doc.sig", "notion.doc"])
    run("Подпись после изменения документа (ожидается BAD signature)",
        ["gpg", "--verify", "notion.doc.sig", "notion_modified.doc"], expected=1)
    run("Контрольная сумма после изменения файла (ожидается FAILED)",
        ["sha256sum", "--check", "ЛР5/checksum_note.sha256"], expected=1,
        cwd=ROOT.parent)
    print("\nРезультат: неизменённый документ имеет действительную подпись;")
    print("изменение данных обнаружено и подписью, и контрольной суммой.")


if __name__ == "__main__":
    main()
