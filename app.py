from __future__ import annotations

import base64
import io
import json
from typing import Any, Dict, List

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

from star_detector import detect_stars


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB


@app.route("/")
def index():
	return render_template("index.html")


@app.post("/api/detect")
def api_detect():
	if "image" not in request.files:
		return jsonify({"ok": False, "error": "Файл изображения не передан (form field 'image')."}), 400

	file = request.files["image"]
	file_bytes = np.frombuffer(file.read(), dtype=np.uint8)
	image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
	if image_bgr is None:
		return jsonify({"ok": False, "error": "Не удалось прочитать изображение."}), 400

	# Параметры с безопасными значениями по умолчанию
	def _get_float(name: str, default: float) -> float:
		try:
			return float(request.form.get(name, default))
		except Exception:
			return default

	def _get_int(name: str, default: int) -> int:
		try:
			return int(request.form.get(name, default))
		except Exception:
			return default

	params = {
		"min_sigma": _get_float("min_sigma", 1.0),
		"max_sigma": _get_float("max_sigma", 8.0),
		"num_sigma": _get_int("num_sigma", 7),
		"threshold": _get_float("threshold", 0.03),
		"overlap": _get_float("overlap", 0.5),
		"denoise_h": _get_int("denoise_h", 7),
		"clahe_clip": _get_float("clahe_clip", 3.0),
	}

	annotated_bgr, stars = detect_stars(image_bgr, **params)

	# Кодируем результат в PNG base64 для удобной отдачи в JSON
	ok, buf = cv2.imencode(".png", annotated_bgr)
	if not ok:
		return jsonify({"ok": False, "error": "Не удалось закодировать результат."}), 500
	b64 = base64.b64encode(buf.tobytes()).decode("ascii")
	data_url = f"data:image/png;base64,{b64}"

	return jsonify({
		"ok": True,
		"count": len(stars),
		"stars": stars,
		"preview": data_url,
	})


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)

