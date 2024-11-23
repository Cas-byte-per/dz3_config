import re
import sys
import yaml

# Словарь для хранения глобальных переменных (констант)
variables = {}


# Функция для получения значения переменной или числа
def get_value(operand):
    """
    Возвращает значение переменной или преобразует операнд в число или строку.
    """
    # Проверка на число
    try:
        return int(operand)
    except ValueError:
        pass

    # Проверка на строку
    if operand.startswith('"') and operand.endswith('"'):
        return operand[1:-1]  # Возвращаем строку без кавычек

    # Если это переменная, возвращаем ее значение
    if operand in variables:
        return variables[operand]

    raise SyntaxError(f"Неизвестный операнд: {operand}")


# Функция для вычисления выражений в формате ?{операция операнд1 операнд2}
def evaluate_expression(expression):
    """
    Вычисляет выражение вида ?{операция операнд1 операнд2}.
    """
    # Находим позиции символов ?{ и }
    start_idx = expression.find("?{")  # Находим начало выражения
    end_idx = expression.find("}", start_idx)  # Находим конец выражения

    if start_idx == -1 or end_idx == -1:
        raise SyntaxError(f"Неверный синтаксис выражения: {expression}")

    # Извлекаем содержимое между ?{ и }
    content = expression[start_idx + 2:end_idx].strip()

    if not content:
        raise SyntaxError(f"Пустое выражение: {expression}")

    # Разделяем строку по пробелам, при этом строки в кавычках не будут разделяться
    parts = re.findall(r'"[^"]*"|\S+', content)
    if len(parts) < 2:
        raise SyntaxError(f"Неполное выражение: {expression}")

    operation = parts[0]
    operands = parts[1:]

    # Проверяем операцию
    if operation == '+':  # Сложение чисел
        return sum(get_value(operand) for operand in operands)
    elif operation == 'concat':  # Конкатенация строк
        return ''.join(str(get_value(operand)) for operand in operands)
    else:
        raise SyntaxError(f"Неизвестная операция: {operation}")


# Функция для обработки значений (массивы, строки и выражения)
def parse_value(value):
    """
    Обрабатывает значение: массивы, строки и выражения.
    """
    value = value.strip()

    # Проверяем, является ли это выражением
    start_idx = value.find("?{")  # Ищем начало выражения
    if start_idx != -1 and value.find("}", start_idx) != -1:  # Если есть ?
        return evaluate_expression(value)

    # Если это массив, обрабатываем его элементы, но не вычисляем
    if value.startswith('(') and value.endswith(')'):  # Если это массив
        elements = re.findall(r'"[^"]*"|\S+', value[1:-1])  # Разделяем элементы массива
        return elements  # Просто возвращаем элементы массива, не вычисляя их

    # Для всего остального — проверяем как простое значение
    return get_value(value)


# Функция для обработки конфигурационного текста
def process_config(config_text):
    """
    Обрабатывает строки конфигурации.
    """
    global variables  # Используем глобальные переменные

    for line in config_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue  # Пропускаем пустые строки

        # Обрабатываем объявление глобальной переменной
        if line.startswith("global "):
            parts = line[7:].split(" = ")
            if len(parts) != 2:
                raise SyntaxError(f"Неверный синтаксис глобальной переменной: {line}")
            name, value = parts
            variables[name] = parse_value(value)

        # Обрабатываем присваивание значения переменной
        else:
            name, value = line.split(" = ", 1)
            name = name.strip()
            value = value.strip()
            variables[name] = parse_value(value)  # Сохраняем результат в обычные переменные


# Основная функция
def main():
    # Проверка аргументов командной строки
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к выходному файлу")
        sys.exit(1)

    # Путь к выходному файлу
    output_file = sys.argv[1]

    # Печатаем инструкции для пользователя
    print("Введите конфигурацию. Для завершения ввода используйте Ctrl+D (или Ctrl+Z на Windows).")

    # Считываем конфигурацию с ввода
    config_text = ""
    while True:
        try:
            line = input()  # Чтение строки с консоли
            config_text += line + "\n"  # Добавляем строку в текст
        except EOFError:  # Завершаем ввод по Ctrl+D или Ctrl+Z
            break

    # Обрабатываем конфигурацию
    process_config(config_text)

    # Записываем результат в файл в формате YAML
    with open(output_file, 'w') as file:
        yaml.dump(variables, file, allow_unicode=True)

    print(f"Результат записан в файл: {output_file}")


if __name__ == "__main__":
    main()
