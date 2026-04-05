#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import string

SPECIAL_WORDS = ["a", "an", "A", "An", "aN", "AN"]
SENTENCE_ENDINGS = [".", "!", "?", ";", ":"] 
TEST_EXAMPLES = [
    "",  # Empty string
    "word",  # Single word
    "a ",  # Article with space
    "an ",  # Article with space
    "a.b",  # Dot inside word
    "A! test",  # Exclamation after article
    "AN unusual CASE",  # Uppercase article
] + SPECIAL_WORDS + SENTENCE_ENDINGS


def create_random_text(min_words=3, max_words=15):
    if random.random() < 0.05:
        return random.choice(TEST_EXAMPLES)
    
    words = []
    word_count = random.randint(min_words, max_words)
    
    if random.random() < 0.3:
        words.append(random.choice(SPECIAL_WORDS))
    
    for _ in range(word_count):
        word_length = random.randint(2, 10)
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))
        
        if random.random() < 0.2:
            word = word.capitalize()
        
        words.append(word)
    
    sentence = ' '.join(words)
    
    if random.random() < 0.7:
        sentence += random.choice(SENTENCE_ENDINGS)
    
    return sentence


def transform_line(text, line_number):
    words = text.split()
    
    if words and words[0].lower() in [w.lower() for w in SPECIAL_WORDS]:
        words = words[1:]  # Remove the first article
    
    result = ' '.join(words)
    
    if line_number % 2 == 1: 
        result = result.upper()
    else: 
        result = result.lower()
        
    if not result or result[-1] not in SENTENCE_ENDINGS:
        result += '.'
    
    return result


def save_test_files(test_number, input_lines, expected_lines):
    input_file = f"tests/test_{test_number}_input.txt"
    expected_file = f"tests/test_{test_number}_expected.txt"
    
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(input_lines))
    
    with open(expected_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(expected_lines))
    
    print(f"  Test {test_number}: {len(input_lines)} lines")


def generate_all_tests(count=10):
    print(f"Generating {count} tests in 'tests' folder...")
    
    os.makedirs('tests', exist_ok=True)
    
    for test_num in range(1, count + 2):
        input_data = []
        expected_data = []
        
        if test_num == 1:
            print("\nCreating special test with edge cases...")
            input_data = TEST_EXAMPLES
            for idx, line in enumerate(TEST_EXAMPLES, 1):
                expected_data.append(transform_line(line, idx))
        else:
            lines_count = random.randint(1, 1000)
            print(f"\nTest {test_num}: {lines_count} random lines")
            
            for line_idx in range(1, lines_count + 1):
                original = create_random_text()
                input_data.append(original)
                expected_data.append(transform_line(original, line_idx))
        
        save_test_files(test_num, input_data, expected_data)
    
    print(f"\n✅ Done! Generated {count} tests in 'tests' folder")
    print("Files: test_N_input.txt and test_N_expected.txt")


def show_usage():
    """Shows program usage information."""
    print("Usage:")
    print("  python gen.py [number_of_tests]")
    print("  Example: python gen.py 15")
    sys.exit(1)


if __name__ == "__main__":
    tests_count = 10 
    
    if len(sys.argv) > 2:
        print("❌ Error: too many arguments")
        show_usage()
    elif len(sys.argv) == 2:
        try:
            tests_count = int(sys.argv[1])
            if tests_count < 1:
                print("❌ Number of tests must be positive")
                show_usage()
        except ValueError:
            print("❌ Error: argument must be a number")
            show_usage()
            
    generate_all_tests(tests_count)
