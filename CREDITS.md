# Credits

## Шрифты

Оба семейства распространяются под **SIL Open Font License 1.1**. Файлы взяты
из npm-пакетов Fontsource (версия 5.3.0); в репозиторий скопированы только
подмножества latin и cyrillic в формате woff2. Полный текст лицензии лежит
рядом с файлами шрифта.

| Семейство | Начертания | Источник | Лицензия |
|---|---|---|---|
| IBM Plex Sans | 400, 600 | `@fontsource/ibm-plex-sans@5.3.0` | OFL 1.1 — `assets/fonts/ibm-plex-sans/OFL.txt` |
| IBM Plex Mono | 400, 500 | `@fontsource/ibm-plex-mono@5.3.0` | OFL 1.1 — `assets/fonts/ibm-plex-mono/OFL.txt` |

Copyright © IBM Corp. «Plex» — зарезервированное имя шрифта (Reserved Font
Name) по условиям OFL; шрифты используются без изменений, в виде подмножеств,
подготовленных Fontsource.

## Изображения

Все изображения прототипа нарисованы кодом — inline SVG, CSS-градиенты и SVG,
сгенерированные скриптом `tools/gen_art.py` из геометрии. Сторонних
изображений, фотографий, стоков и CC0-файлов нет.

| Что | Файл | Как сделано |
|---|---|---|
| Пятиугольный знак (A и B) | inline SVG в `index.html` | вручную + вычисленная шкала насечек |
| Фон первого экрана A | `assets/img/hero-a.svg` | `tools/gen_art.py` |
| Фон первого экрана B | `assets/img/hero-b.svg` | `tools/gen_art.py` |
| «Сканирующая» линия, затемнение фона | CSS в `assets/css/base.css` | CSS |
| Условный «3D-шкаф» A и B | `assets/img/cabinet-a.svg`, `assets/img/cabinet-b.svg` | `tools/gen_art.py` |
| Логотип-плейсхолдер | inline SVG в шапке страниц | вручную |
| Фавикон | `assets/img/favicon.svg` | вручную |
| «Чертёжная» сетка | CSS-градиенты в `assets/css/base.css` | CSS |
