# Распознавание звёзд (OpenCV + Flask)

Простое веб-приложение для распознавания звёзд на зашумлённых астроснимках. Используются OpenCV, scikit-image (blob LoG) и Flask.

## Установка

Требуется Python 3.10+.

```powershell
cd C:\Users\dns\cursor\folder_1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

Если установка `opencv-python` не удаётся, попробуйте `pip install opencv-contrib-python`.

## Запуск

```powershell
$env:FLASK_APP="app.py"
python app.py
```

Откройте в браузере: http://127.0.0.1:5000

## Использование

- Загрузите изображение (желательно исходник с минимальной компрессией)
- При необходимости подстройте параметры:
  - `min_sigma`/`max_sigma` — диапазон размеров звёзд (в пикселях)
  - `num_sigma` — дискретизация сигм
  - `threshold` — порог отклика при поиске блобов (0..1)
  - `overlap` — допустимое перекрытие найденных блобов
  - `denoise_h` — сила подавления шума NLM
  - `clahe_clip` — усиление локального контраста
- Нажмите «Распознать», получите количество и превью разметки.

## Структура

```
app.py                 # Flask + API /api/detect
star_detector.py       # Алгоритм обработки и поиска звёзд
requirements.txt       # Зависимости
templates/index.html   # Веб-страница
static/js/app.js       # Логика на клиенте
static/css/style.css   # Стили
```

## Примечания

- Обработка выполняется на сервере в памяти, файлы не сохраняются на диск.
- Алгоритм устойчив к шуму благодаря NLM + CLAHE + вычитанию фона.
- Для очень больших изображений увеличьте предел `MAX_CONTENT_LENGTH` в `app.py`.

