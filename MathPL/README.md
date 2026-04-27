# MathPL — Math Programming Language

Язык программирования для математики, игр и искусственного интеллекта.

## Особенности

- **Математика из коробки** — тензоры, матрицы, конвейеры
- **Игры** — 2D/3D координаты, WASD, игровой цикл
- **ИИ** — нейросети за пару строк
- **Реактивность** — переменные с `dep` обновляются автоматически
- **Веб** — DOM-манипуляции, серверы
- **Модульность** — `funct`, `play-module`, библиотеки

## Быстрый старт

```bash
# Клонировать
git clone https://github.com/by-kitra/mathpl.git
cd mathpl

# Запустить REPL
python src/mathpl.py

# Запустить пример
python src/mathpl.py examples/hello.mpl
```

## Пример кода

```
task#
    base = a, b, c
    a = 25
    b = 27
    c = a + b = (say "Сумма")
close
```

## Движение игрока

```
task#
    base = objp = "Player" and function and moveLiB
    launch centre = 3D
    request access keyboard = keys WASD
    key W = function to forward else to (0:1:0)
    key A = function to left else to (-1:0:0)
    key S = function to back else to (0:-1:0)
    key D = function to right else to (1:0:0)
    wait = access keys
    if work function = start function()
    if unwork function = error-mode
    start function()
close
```

## Документация

- [Синтаксис](docs/SYNTAX.md)
- [Учебник](docs/TUTORIAL.md)
- [Ключевые слова](docs/KEYWORDS.md)

## Лицензия

MIT License

## Внимание!

> ⚠️ **Ранний доступ (Early Access)**
> 
> MathPL находится в активной разработке. Некоторые функции могут быть 
> неполными или изменяться в будущих версиях.
> 
> Текущая версия: **v0.2.0** | Статус: **Pre-Alpha**
