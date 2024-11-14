import os
import asyncio
import aiofiles
from pathlib import Path
import argparse
import logging
from colorama import Fore, Style, init

# Ініціалізуємо colorama для кольорового виводу в консоль
init(autoreset=True)

# Налаштування логування
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def copy_file(src: Path, dest_folder: Path):
    """Асинхронне копіювання файлу у відповідну папку за розширенням"""
    try:
        # Створюємо папку для файлів з таким розширенням, якщо її немає
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / src.name

        # Перевіряємо, чи файл вже існує у цільовій папці
        if dest_path.exists():
            print(Fore.YELLOW + f"[SKIP] Файл {src} вже існує у {dest_folder}")
            return

        # Виконуємо асинхронне копіювання файлу
        async with aiofiles.open(src, "rb") as src_file:
            async with aiofiles.open(dest_path, "wb") as dest_file:
                while chunk := await src_file.read(1024):
                    await dest_file.write(chunk)

        print(Fore.GREEN + f"[INFO] Файл {src} скопійовано до {dest_folder}")

    except Exception as e:
        logging.error(f"Помилка під час копіювання файлу {src}: {e}")
        print(Fore.RED + f"[ERROR] Помилка під час копіювання файлу {src}: {e}")


async def read_folder(src_folder: Path, dest_folder: Path):
    """Асинхронне читання папки та копіювання файлів"""
    tasks = []
    for root, _, files in os.walk(src_folder):
        for file in files:
            file_path = Path(root) / file
            file_extension = file_path.suffix[1:].lower() or "unknown"
            target_folder = dest_folder / file_extension
            tasks.append(copy_file(file_path, target_folder))

    await asyncio.gather(*tasks)


def main():
    # Парсер для аргументів командного рядка
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширенням"
    )
    parser.add_argument(
        "--source", "-s", required=True, type=str, help="Шлях до вихідної папки"
    )
    parser.add_argument(
        "--output", "-o", required=True, type=str, help="Шлях до цільової папки"
    )
    args = parser.parse_args()

    # Ініціалізуємо шляхи
    source_folder = Path(args.source)
    output_folder = Path(args.output)

    # Перевірка, чи існують шляхи
    if not source_folder.exists():
        print(Fore.RED + f"[ERROR] Вихідна папка {source_folder} не існує")
        return

    if not output_folder.exists():
        print(Fore.YELLOW + f"[INFO] Створення цільової папки {output_folder}")
        output_folder.mkdir(parents=True)

    # Запускаємо асинхронну функцію для сортування файлів
    asyncio.run(read_folder(source_folder, output_folder))
    print(Fore.CYAN + "[DONE] Усі файли оброблено")


if __name__ == "__main__":
    main()


# Як правильно запустити скрипт

"""python3 sort_files.py --source ./source --output ./output"""
