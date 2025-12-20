#!/bin/sh

set -e

trap 'echo "Error: Script failed at line $LINENO" >&2; exit 1' ERR

usage() {
    for msg in "$@"; do printf "%s\n" "${0##*/}: $msg" >&2; done
    echo "usage: ${0##*/} [-v] book_file book_name price author ..." >&2
    exit 1
}

# Обработка опционального флага -v
VERBOSE=0
while getopts "v" opt; do
    case $opt in
        v) VERBOSE=1 ;;
        *) usage "invalid option" ;;
    esac
done
shift $((OPTIND-1))

test $# -ge 4 || usage "not enough arguments"

BOOK_FILE="$1"
BOOK_NAME="$2"
PRICE="$3"
shift 3
AUTHORS="$@"

# Проверка существования файла книги
if [ ! -f "$BOOK_FILE" ]; then
    echo "${0##*/}: book file '$BOOK_FILE' does not exist" >&2
    exit 1
fi

# Поиск корня библиотеки по файлу-маркеру
find_library_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/.library" ]; then
            if [ "$VERBOSE" -eq 1 ]; then
                echo "Found library root at: $dir" >&2
            fi
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    echo "${0##*/}: not in a library directory (no .library marker found)" >&2
    exit 1
}

# Начальный поиск с текущего каталога
CURRENT_DIR=$(pwd)
LIBRARY_ROOT=$(find_library_root "$CURRENT_DIR")

# Определение путей
BOOKS_DIR="$LIBRARY_ROOT/books"
AUTHORS_DIR="$LIBRARY_ROOT/authors"
PRICES_DIR="$LIBRARY_ROOT/prices"
TMP_DIR="$LIBRARY_ROOT/.tmp"

# Проверка существования необходимых каталогов
for dir in "$BOOKS_DIR" "$AUTHORS_DIR" "$PRICES_DIR" "$TMP_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "${0##*/}: required directory '$dir' does not exist" >&2
        exit 1
    fi
done

# Генерация уникального имени файла книги
find_unique_filename() {
    local base_name="$1"
    local suffix=""
    local counter=1
    
    while [ -e "$BOOKS_DIR/${base_name}${suffix}" ]; do
        suffix=".$counter"
        counter=$((counter + 1))
    done
    echo "${base_name}${suffix}"
}

# Получение уникального имени
FINAL_BOOK_NAME=$(find_unique_filename "$BOOK_NAME")
FINAL_BOOK_PATH="$BOOKS_DIR/$FINAL_BOOK_NAME"

if [ "$VERBOSE" -eq 1 ]; then
    echo "Final book name: $FINAL_BOOK_NAME" >&2
fi

# Копирование во временный каталог
TMP_BOOK_PATH="$TMP_DIR/$(basename "$BOOK_FILE")"
if [ "$VERBOSE" -eq 1 ]; then
    echo "Copying to tmp: $TMP_BOOK_PATH" >&2
fi
cp "$BOOK_FILE" "$TMP_BOOK_PATH"

# Перемещение из временного каталога в конечный
mv "$TMP_BOOK_PATH" "$FINAL_BOOK_PATH"

# Установка прав доступа на файл книги (владелец и группа: чтение+запись, остальные: только чтение)
chmod 664 "$FINAL_BOOK_PATH"

# Создание файла цены, если указана
if [ -n "$PRICE" ] && [ "$PRICE" != "-" ]; then
    PRICE_FILE="$PRICES_DIR/${FINAL_BOOK_NAME}.price"
    echo "$PRICE" > "$PRICE_FILE"
    chmod 644 "$PRICE_FILE"  # владелец: чтение+запись, остальные: только чтение
    if [ "$VERBOSE" -eq 1 ]; then
        echo "Created price file: $PRICE_FILE" >&2
    fi
fi

# Обработка авторов
for author in $AUTHORS; do
    AUTHOR_DIR="$AUTHORS_DIR/$author"
    
    # Создание каталога автора, если не существует
    if [ ! -d "$AUTHOR_DIR" ]; then
        mkdir "$AUTHOR_DIR"
        # Установка таких же прав, как у каталога authors
        AUTHOR_DIR_PERMS=$(stat -c "%a" "$AUTHORS_DIR")
        chmod "$AUTHOR_DIR_PERMS" "$AUTHOR_DIR"
    fi
    
    # Создание жесткой ссылки на книгу в каталоге автора
    AUTHOR_BOOK_LINK="$AUTHOR_DIR/$FINAL_BOOK_NAME"
    ln "$FINAL_BOOK_PATH" "$AUTHOR_BOOK_LINK"
    
    if [ "$VERBOSE" -eq 1 ]; then
        echo "Created link for author '$author': $AUTHOR_BOOK_LINK" >&2
    fi
done

if [ "$VERBOSE" -eq 1 ]; then
    echo "Book '$BOOK_NAME' added successfully as '$FINAL_BOOK_NAME'" >&2
fi
