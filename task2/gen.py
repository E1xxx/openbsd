#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генератор тестовых данных для лабораторной работы.
Создаёт входные файлы и эталонные выходные файлы для проверки заданий.
"""

import os
import sys
import random
import string

# Константы, определяющие правила обработки текста
SPECIAL_WORDS = ["a", "an", "A", "An", "aN", "AN"]  # Слова, которые могут удаляться
SENTENCE_ENDINGS = [".", "!", "?", ";", ":"]  # Знаки препинания в конце
TEST_EXAMPLES = [
    "",  # Пустая строка
    "word",  # Одно слово
    "a ",  # Артикль с пробелом
    "an ",  # Артикль с пробелом
    "a.b",  # Точка внутри слова
    "A! test",  # Восклицание после артикля
    "AN unusual CASE",  # Артикль заглавными
] + SPECIAL_WORDS + SENTENCE_ENDINGS


def create_random_text(min_words=3, max_words=15):
    """
    Генерирует случайный текст (предложение) для тестирования.
    
    Параметры:
        min_words: минимальное количество слов
        max_words: максимальное количество слов
    
    Возвращает:
        строку с сгенерированным предложением
    """
    # Иногда возвращаем один из предопределённых примеров (5% случаев)
    if random.random() < 0.05:
        return random.choice(TEST_EXAMPLES)
    
    words = []
    word_count = random.randint(min_words, max_words)
    
    # Иногда добавляем артикль в начало (30% случаев)
    if random.random() < 0.3:
        words.append(random.choice(SPECIAL_WORDS))
    
    # Генерируем случайные слова
    for _ in range(word_count):
        word_length = random.randint(2, 10)
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))
        
        # Иногда делаем слово с заглавной буквы (20% случаев)
        if random.random() < 0.2:
            word = word.capitalize()
        
        words.append(word)
    
    # Соединяем слова пробелами
    sentence = ' '.join(words)
    
    # В 70% случаев добавляем знак препинания в конце
    if random.random() < 0.7:
        sentence += random.choice(SENTENCE_ENDINGS)
    
    return sentence


def transform_line(text, line_number):
    """
    Преобразует строку согласно правилам задания.
    
    Правила:
    1. Удалить первый артикль (a/an/A/An), если он есть
    2. Преобразовать регистр: нечётные строки в ВЕРХНИЙ, чётные в нижний
    3. Добавить точку в конце, если нет знака препинания
    
    Параметры:
        text: исходная строка
        line_number: номер строки (начиная с 1)
    
    Возвращает:
        преобразованную строку
    """
    # Разбиваем на слова
    words = text.split()
    
    # Проверяем, начинается ли строка с артикля
    if words and words[0].lower() in [w.lower() for w in SPECIAL_WORDS]:
        words = words[1:]  # Удаляем первый артикль
    
    # Собираем обратно
    result = ' '.join(words)
    
    # Применяем преобразование регистра по номеру строки
    if line_number % 2 == 1:  # Нечётная строка
        result = result.upper()
    else:  # Чётная строка
        result = result.lower()
    
    # Добавляем точку в конце, если нет знака препинания
    if not result or result[-1] not in SENTENCE_ENDINGS:
        result += '.'
    
    return result


def save_test_files(test_number, input_lines, expected_lines):
    """
    Сохраняет тестовые данные в файлы.
    
    Параметры:
        test_number: номер теста
        input_lines: список входных строк
        expected_lines: список ожидаемых выходных строк
    """
    # Имена файлов
    input_file = f"tests/test_{test_number}_input.txt"
    expected_file = f"tests/test_{test_number}_expected.txt"
    
    # Запись входных данных
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(input_lines))
    
    # Запись ожидаемых результатов
    with open(expected_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(expected_lines))
    
    print(f"  Тест {test_number}: {len(input_lines)} строк")


def generate_all_tests(count=10):
    """
    Генерирует указанное количество тестов.
    
    Параметры:
        count: количество тестов для генерации
    """
    print(f"Генерация {count} тестов в папке 'tests'...")
    
    # Создаём папку для тестов, если её нет
    os.makedirs('tests', exist_ok=True)
    
    for test_num in range(1, count + 2):  # +1 для первого специального теста
        input_data = []
        expected_data = []
        
        if test_num == 1:
            # Первый тест содержит все граничные случаи
            print("\nСоздание специального теста с граничными случаями...")
            input_data = TEST_EXAMPLES
            for idx, line in enumerate(TEST_EXAMPLES, 1):
                expected_data.append(transform_line(line, idx))
        else:
            # Обычные тесты со случайными данными
            lines_count = random.randint(1, 1000)
            print(f"\nТест {test_num}: {lines_count} случайных строк")
            
            for line_idx in range(1, lines_count + 1):
                # Генерируем случайную строку
                original = create_random_text()
                input_data.append(original)
                # Преобразуем согласно правилам
                expected_data.append(transform_line(original, line_idx))
        
        # Сохраняем тест
        save_test_files(test_num, input_data, expected_data)
    
    print(f"\n✅ Готово! Сгенерировано {count} тестов в папке 'tests'")
    print("Файлы: test_N_input.txt и test_N_expected.txt")


def show_usage():
    """Показывает справку по использованию программы."""
    print("Использование:")
    print("  python gen.py [количество_тестов]")
    print("  Пример: python gen.py 15")
    sys.exit(1)


if __name__ == "__main__":
    # Обработка аргументов командной строки
    tests_count = 10  # Значение по умолчанию
    
    if len(sys.argv) > 2:
        print("❌ Ошибка: слишком много аргументов")
        show_usage()
    elif len(sys.argv) == 2:
        try:
            tests_count = int(sys.argv[1])
            if tests_count < 1:
                print("❌ Количество тестов должно быть положительным числом")
                show_usage()
        except ValueError:
            print("❌ Ошибка: аргумент должен быть числом")
            show_usage()
    
    # Запуск генерации
    generate_all_tests(tests_count)
