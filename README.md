# Домашнее задание №3
## Описание проекта
Этот скрипт обрабатывает конфигурационный текст, вводимый пользователем, и преобразует его в формат `YAML`.
Конфигурация поддерживает:
- Объявление и присваивание переменных.
- Вычисление выражений (арифметических операций, конкатенации строк).
- Обработку массивов.
- Результат сохраняется в файл, указанный пользователем.

## Основные функции
1. ### `get_value(operand)`
Возвращает значение переменной, числа или строки. 
Если переданный операнд является:
- Числом, оно преобразуется в `int`.
- Строкой (в кавычках), возвращается без кавычек.
- Переменной, возвращается её значение из глобального словаря `variables`.
```python
def get_value(operand):
    try:
        return int(operand)
    except ValueError:
        pass
    if operand.startswith('"') and operand.endswith('"'):
        return operand[1:-1]
    if operand in variables:
        return variables[operand]
    raise SyntaxError(f"Неизвестный операнд: {operand}")
```
2. ### `evaluate_expression(expression)`
Обрабатывает выражения в формате `?{операция операнд1 операнд2}`.

Поддерживаемые операции:
- `+` — сложение чисел.
- `concat` — объединение строк.
  
```python
def evaluate_expression(expression):
    start_idx = expression.find("?{")
    end_idx = expression.find("}", start_idx)
    if start_idx == -1 or end_idx == -1:
        raise SyntaxError(f"Неверный синтаксис выражения: {expression}")
    content = expression[start_idx + 2:end_idx].strip()
    parts = re.findall(r'"[^"]*"|\S+', content)
    if len(parts) < 2:
        raise SyntaxError(f"Неполное выражение: {expression}")
    operation = parts[0]
    operands = parts[1:]
    if operation == '+':
        return sum(get_value(operand) for operand in operands)
    elif operation == 'concat':
        return ''.join(str(get_value(operand)) for operand in operands)
    else:
        raise SyntaxError(f"Неизвестная операция: {operation}")
```

3. ### `parse_value(value)`
Обрабатывает значения: `массивы`, `строки` и `выражения`.
- Если значение — выражение, оно вычисляется.
- Если значение — массив (в круглых скобках), элементы извлекаются без вычислений.
```python
def parse_value(value):
    value = value.strip()
    start_idx = value.find("?{")
    if start_idx != -1 and value.find("}", start_idx) != -1:
        return evaluate_expression(value)
    if value.startswith('(') and value.endswith(')'):
        elements = re.findall(r'"[^"]*"|\S+', value[1:-1])
        return elements
    return get_value(value)
```

4. ### `process_config(config_text)`
Обрабатывает строки конфигурации. Поддерживает:
- Объявление глобальных переменных:
  - Формат: `global имя = значение`.
- Присваивание переменным значений:
  - Формат: `имя = значение`.
    
```python
def process_config(config_text):
    global variables
    for line in config_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("global "):
            parts = line[7:].split(" = ")
            if len(parts) != 2:
                raise SyntaxError(f"Неверный синтаксис глобальной переменной: {line}")
            name, value = parts
            variables[name] = parse_value(value)
        else:
            name, value = line.split(" = ", 1)
            name = name.strip()
            value = value.strip()
            variables[name] = parse_value(value)
```
5. ### `main()`
Основная функция:
- Считывает конфигурацию из консоли.
- Обрабатывает её через `process_config`.
- Сохраняет результат в файл в формате `YAML`.
Пример:
```bash
$ python main.py output.yaml
Введите конфигурацию. Для завершения ввода используйте Ctrl+D (или Ctrl+Z на Windows).
global a = 5
global b = 10
result = ?{+ a b 20}
^D
Результат записан в файл: output.yaml
```

```python
def main():
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к выходному файлу")
        sys.exit(1)
    output_file = sys.argv[1]
    print("Введите конфигурацию. Для завершения ввода используйте Ctrl+D (или Ctrl+Z на Windows).")
    config_text = ""
    while True:
        try:
            line = input()
            config_text += line + "\n"
        except EOFError:
            break
    process_config(config_text)
    with open(output_file, 'w') as file:
        yaml.dump(variables, file, allow_unicode=True)
    print(f"Результат записан в файл: {output_file}")
```
## Пример использования
1. ### `Подготовка к запуску`
Убедитесь, что Python установлен, и библиотека `pyyaml` доступна. Установить её можно с помощью:
```bash
pip install pyyaml
```
2. ### `Запуск`
Выполните команду:
```bash
python main.py output.yaml
```
Где `output.yaml` — файл для сохранения результата.

3. ### `Пример конфигурации`
```sql
global x = 10
global y = 20
result = ?{+ x y}
text = ?{concat "Привет, " "мир!"}
array = (1 2 3)
greeting = "Hello, world!"
```
4. ### `Результат`
Содержимое файла `output.yaml`:
```yaml
array:
- 1
- 2
- 3
result: 30
text: Привет, мир!
x: 10
y: 20
greeting: Hello, world!
```
