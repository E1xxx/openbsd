#!/bin/sh

set -e

trap 'echo "Error: Script failed at line $LINENO" >&2; exit 1' ERR

usage() {
    for msg in "$@"; do printf "%s\n" "${0##*/}: $msg" >&2; done
    echo "usage: ${0##*/} [-v] book_file book_name price author ..." >&2
    exit 1
}


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


if [ ! -f "$BOOK_FILE" ]; then
    echo "${0##*/}: book file '$BOOK_FILE' does not exist" >&2
    exit 1
fi


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


FINAL_BOOK_NAME=$(find_unique_filename "$BOOK_NAME")
FINAL_BOOK_PATH="$BOOKS_DIR/$FINAL_BOOK_NAME"

if [ "$VERBOSE" -eq 1 ]; then
    echo "Final book name: $FINAL_BOOK_NAME" >&2
fi


TMP_BOOK_NAME="tmp_book_$$_$(date +%s%N)"
TMP_BOOK_PATH="$TMP_DIR/$TMP_BOOK_NAME"

if [ "$VERBOSE" -eq 1 ]; then
    echo "Copying to tmp: $TMP_BOOK_PATH" >&2
fi

cp "$BOOK_FILE" "$TMP_BOOK_PATH" || {
    echo "${0##*/}: failed to copy book file to temp directory" >&2
    exit 1
}


mv "$TMP_BOOK_PATH" "$FINAL_BOOK_PATH"


chmod 664 "$FINAL_BOOK_PATH"


if [ -n "$PRICE" ] && [ "$PRICE" != "-" ]; then
    PRICE_FILE="$PRICES_DIR/${FINAL_BOOK_NAME}.price"
    echo "$PRICE" > "$PRICE_FILE"
    chmod 644 "$PRICE_FILE" 
    if [ "$VERBOSE" -eq 1 ]; then
        echo "Created price file: $PRICE_FILE" >&2
    fi
fi


for author in $AUTHORS; do
    AUTHOR_DIR="$AUTHORS_DIR/$author"
    

    if [ ! -d "$AUTHOR_DIR" ]; then
        mkdir "$AUTHOR_DIR"
        AUTHOR_DIR_PERMS=$(stat -c "%a" "$AUTHORS_DIR")
        chmod "$AUTHOR_DIR_PERMS" "$AUTHOR_DIR"
    fi
    
    AUTHOR_BOOK_LINK="$AUTHOR_DIR/$FINAL_BOOK_NAME"
    ln "$FINAL_BOOK_PATH" "$AUTHOR_BOOK_LINK"
    
    if [ "$VERBOSE" -eq 1 ]; then
        echo "Created link for author '$author': $AUTHOR_BOOK_LINK" >&2
    fi
done

if [ "$VERBOSE" -eq 1 ]; then
    echo "Book '$BOOK_NAME' added successfully as '$FINAL_BOOK_NAME'" >&2
fi
