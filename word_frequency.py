import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt
import multiprocessing
from colorama import Fore, init
import time

# Ініціалізація colorama для автоматичного скидання кольорів
init(autoreset=True)


def get_text(url):
    """Завантажує текст із заданого URL."""
    print(" ")
    print(Fore.MAGENTA + "[INFO] Чекайте, завантажую та обробляю текст...")
    print(" ")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(Fore.GREEN + "[INFO] Текст успішно завантажено.")
        print(" ")
        return response.text
    except requests.RequestException as e:
        print(Fore.RED + f"[ERROR] Помилка при завантаженні тексту: {e}")
        return None


def remove_punctuation(text):
    """Видаляє знаки пунктуації з тексту."""
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    """Mapper функція для створення пари (слово, 1)."""
    return word, 1


def shuffle_function(mapped_values):
    """Функція для групування слів після мапінгу."""
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    """Reducer функція для підсумовування частоти слів."""
    key, values = key_values
    return key, sum(values)


def map_reduce(text, num_workers=None, search_words=None):
    """Реалізація MapReduce для підрахунку частоти слів."""
    text = remove_punctuation(text)
    words = text.lower().split()
    total_words = len(words)

    if search_words:
        words = [word for word in words if word in search_words]

    if not num_workers:
        num_workers = multiprocessing.cpu_count()

    # Паралельний маппінг
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        mapped_values = list(executor.map(map_function, words))

    # Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельний редьюс
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values), total_words


def visualize_top_words(word_counter, top_n=10):
    """Візуалізує топ-N слів за частотою."""
    top_words = sorted(word_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]

    if not top_words:
        print(Fore.YELLOW + "[INFO] Немає даних для візуалізації.")
        return

    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color="skyblue")
    plt.xlabel("Слова")
    plt.ylabel("Кількість")
    plt.title(f"Топ {top_n} найчастіше вживаних слів")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    # URL для завантаження тексту
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"

    # Завантаження тексту
    text = get_text(url)
    if not text:
        return

    print(Fore.CYAN + "[INFO] Виконується аналіз частоти слів...")

    # Заданий список слів для аналізу
    search_words = ["war", "peace", "love", "business", "book"]

    # Виконання MapReduce для підрахунку частоти слів
    word_counter, total_words = map_reduce(text)

    # Підрахунок для заданих слів
    specific_word_counts, _ = map_reduce(text, search_words=search_words)

    # Виведення результатів у консоль
    print(Fore.YELLOW + "\nРезультат підрахунку слів:")
    print(" ")
    for word in search_words:
        print(f"{Fore.WHITE}{word}: {Fore.MAGENTA}{specific_word_counts.get(word, 0)}")

    print(Fore.CYAN + f"\nЗагальна кількість слів у тексті: {Fore.RED}{total_words}")

    print(" ")

    # Візуалізація результатів
    visualize_top_words(word_counter, top_n=10)


if __name__ == "__main__":
    main()
