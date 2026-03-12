#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test data generator for laboratory work.
Creates input files and reference output files for task verification.
"""

import os
import sys
import random
import string

# Constants defining text processing rules
SPECIAL_WORDS = ["a", "an", "A", "An", "aN", "AN"]  # Words that may be removed
SENTENCE_ENDINGS = [".", "!", "?", ";", ":"]  # Punctuation marks at the end
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
    """
    Generates random text (sentence) for testing.
    
    Parameters:
        min_words: minimum number of words
        max_words: maximum number of words
    
    Returns:
        string with generated sentence
    """
    # Sometimes return one of the predefined examples (5% of cases)
    if random.random() < 0.05:
        return random.choice(TEST_EXAMPLES)
    
    words = []
    word_count = random.randint(min_words, max_words)
    
    # Sometimes add an article at the beginning (30% of cases)
    if random.random() < 0.3:
        words.append(random.choice(SPECIAL_WORDS))
    
    # Generate random words
    for _ in range(word_count):
        word_length = random.randint(2, 10)
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))
        
        # Sometimes capitalize the word (20% of cases)
        if random.random() < 0.2:
            word = word.capitalize()
        
        words.append(word)
    
    # Join words with spaces
    sentence = ' '.join(words)
    
    # Add punctuation at the end in 70% of cases
    if random.random() < 0.7:
        sentence += random.choice(SENTENCE_ENDINGS)
    
    return sentence


def transform_line(text, line_number):
    """
    Transforms a line according to task rules.
    
    Rules:
    1. Remove the first article (a/an/A/An) if present
    2. Transform case: odd lines to UPPER CASE, even lines to lower case
    3. Add a period at the end if no punctuation mark exists
    
    Parameters:
        text: original string
        line_number: line number (starting from 1)
    
    Returns:
        transformed string
    """
    # Split into words
    words = text.split()
    
    # Check if line starts with an article
    if words and words[0].lower() in [w.lower() for w in SPECIAL_WORDS]:
        words = words[1:]  # Remove the first article
    
    # Join back together
    result = ' '.join(words)
    
    # Apply case transformation based on line number
    if line_number % 2 == 1:  # Odd line
        result = result.upper()
    else:  # Even line
        result = result.lower()
    
    # Add period at the end if no punctuation mark exists
    if not result or result[-1] not in SENTENCE_ENDINGS:
        result += '.'
    
    return result


def save_test_files(test_number, input_lines, expected_lines):
    """
    Saves test data to files.
    
    Parameters:
        test_number: test number
        input_lines: list of input lines
        expected_lines: list of expected output lines
    """
    # File names
    input_file = f"tests/test_{test_number}_input.txt"
    expected_file = f"tests/test_{test_number}_expected.txt"
    
    # Write input data
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(input_lines))
    
    # Write expected results
    with open(expected_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(expected_lines))
    
    print(f"  Test {test_number}: {len(input_lines)} lines")


def generate_all_tests(count=10):
    """
    Generates the specified number of tests.
    
    Parameters:
        count: number of tests to generate
    """
    print(f"Generating {count} tests in 'tests' folder...")
    
    # Create tests folder if it doesn't exist
    os.makedirs('tests', exist_ok=True)
    
    for test_num in range(1, count + 2):  # +1 for the first special test
        input_data = []
        expected_data = []
        
        if test_num == 1:
            # First test contains all edge cases
            print("\nCreating special test with edge cases...")
            input_data = TEST_EXAMPLES
            for idx, line in enumerate(TEST_EXAMPLES, 1):
                expected_data.append(transform_line(line, idx))
        else:
            # Regular tests with random data
            lines_count = random.randint(1, 1000)
            print(f"\nTest {test_num}: {lines_count} random lines")
            
            for line_idx in range(1, lines_count + 1):
                # Generate random line
                original = create_random_text()
                input_data.append(original)
                # Transform according to rules
                expected_data.append(transform_line(original, line_idx))
        
        # Save the test
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
    # Command line arguments processing
    tests_count = 10  # Default value
    
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
    
    # Start generation
    generate_all_tests(tests_count)
