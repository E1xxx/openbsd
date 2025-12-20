#!/bin/sh

set -e

trap 'echo "Error: Script failed at line $LINENO" >&2; exit 1' ERR

usage() {
    for msg in "$@"; do printf "%s\n" "${0##*/}: $msg" >&2; done
    echo "usage: ${0##*/} library_root group_name" >&2
    exit 1
}

test $# -eq 2 || usage "invalid number of arguments"

LIBRARY_ROOT="$1"
GROUP_NAME="$2"

# Проверка существования группы
if ! getent group "$GROUP_NAME" > /dev/null; then
    echo "${0##*/}: group '$GROUP_NAME' does not exist" >&2
    exit 1
fi

# Создание корневого каталога
mkdir -p "$LIBRARY_ROOT"

# Создание файла-маркера
echo "library v1.0" > "$LIBRARY_ROOT/.library"

# Установка прав на корневой каталог (755 - владелец полный доступ, остальные чтение+исполнение)
chmod 755 "$LIBRARY_ROOT"

# Создание подкаталогов
mkdir -p "$LIBRARY_ROOT/books"
mkdir -p "$LIBRARY_ROOT/authors"
mkdir -p "$LIBRARY_ROOT/prices"
mkdir -p "$LIBRARY_ROOT/.tmp"

# Установка прав на каталоги:

# books и authors: 755 - владелец полный доступ, остальные чтение+исполнение
chmod 755 "$LIBRARY_ROOT/books"
chmod 755 "$LIBRARY_ROOT/authors"

# prices: 750 - владелец полный доступ, группа чтение+исполнение, остальные нет доступа
chmod 750 "$LIBRARY_ROOT/prices"

# .tmp: 1770 - sticky bit + владелец и группа полный доступ, остальные нет доступа
chmod 1770 "$LIBRARY_ROOT/.tmp"

# Изменение группы для prices и .tmp
chgrp "$GROUP_NAME" "$LIBRARY_ROOT/prices"
chgrp "$GROUP_NAME" "$LIBRARY_ROOT/.tmp"

# Установка владельца файла-маркера как у корневого каталога
# (обычно это текущий пользователь, но на всякий случай копируем из корневого каталога)
if [ -e "$LIBRARY_ROOT/.library" ]; then
    LIBRARY_OWNER=$(stat -c "%u" "$LIBRARY_ROOT")
    LIBRARY_GROUP=$(stat -c "%g" "$LIBRARY_ROOT")
    chown "$LIBRARY_OWNER:$LIBRARY_GROUP" "$LIBRARY_ROOT/.library"
    chmod 644 "$LIBRARY_ROOT/.library"
fi
