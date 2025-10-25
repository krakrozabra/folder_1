from __future__ import annotations

from typing import Dict, List, Tuple

import cv2
import numpy as np
from skimage.feature import blob_log


def _to_grayscale_8bit(image_bgr: np.ndarray) -> np.ndarray:
	gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
	if gray.dtype != np.uint8:
		gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
	return gray


def detect_stars(
	image_bgr: np.ndarray,
	*,
	min_sigma: float = 1.0,
	max_sigma: float = 8.0,
	num_sigma: int = 7,
	threshold: float = 0.03,
	overlap: float = 0.5,
	denoise_h: int = 7,
	clahe_clip: float = 3.0,
) -> Tuple[np.ndarray, List[Dict[str, int]]]:
	"""
	Выделение звёзд на зашумлённых снимках.

	Последовательность:
	- перевод в градации серого
	- подавление шума fastNlMeansDenoising
	- локальное выравнивание контраста (CLAHE)
	- оценка фона (median blur) и вычитание
	- blob detection (Laplacian of Gaussian)

	Возвращает размеченное изображение BGR и список центров/радиусов звёзд.
	"""
	gray8 = _to_grayscale_8bit(image_bgr)

	# Подавление шума (хорошо работает на слабых звёздах на шумном фоне)
	denoised = cv2.fastNlMeansDenoising(gray8, h=max(1, int(denoise_h)), templateWindowSize=7, searchWindowSize=21)

	# Усиление локального контраста
	clahe = cv2.createCLAHE(clipLimit=max(0.5, float(clahe_clip)), tileGridSize=(8, 8))
	enhanced = clahe.apply(denoised)

	# Оценка фона и подавление крупных градиентов/виньетирования
	bg = cv2.medianBlur(enhanced, ksize=21)
	fg = cv2.subtract(enhanced, bg)

	# Нормализация к [0,1] для skimage
	fg_float = cv2.normalize(fg.astype(np.float32), None, 0.0, 1.0, cv2.NORM_MINMAX)

	# Поиск блобов LoG
	blobs = blob_log(
		fg_float,
		min_sigma=max(0.5, float(min_sigma)),
		max_sigma=max(float(min_sigma) + 0.5, float(max_sigma)),
		num_sigma=max(3, int(num_sigma)),
		threshold=max(1e-4, float(threshold)),
		overlap=float(overlap),
	)

	# Радиус ~ sqrt(2)*sigma
	stars: List[Dict[str, int]] = []
	annotated = image_bgr.copy()
	for (y, x, sigma) in blobs:
		radius = int(max(1.0, np.sqrt(2.0) * float(sigma)))
		x_i = int(round(float(x)))
		y_i = int(round(float(y)))
		stars.append({"x": x_i, "y": y_i, "r": radius})
		cv2.circle(annotated, (x_i, y_i), radius=radius, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
		cv2.circle(annotated, (x_i, y_i), radius=1, color=(0, 255, 255), thickness=-1, lineType=cv2.LINE_AA)

	return annotated, stars

