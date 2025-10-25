(function() {
	const form = document.getElementById('detectForm');
	const fileInput = document.getElementById('image');
	const inputPreview = document.getElementById('inputPreview');
	const resultImg = document.getElementById('resultImage');
	const countEl = document.getElementById('count');

	fileInput.addEventListener('change', () => {
		const file = fileInput.files && fileInput.files[0];
		if (!file) {
			inputPreview.removeAttribute('src');
			return;
		}
		const reader = new FileReader();
		reader.onload = () => {
			inputPreview.src = reader.result;
		};
		reader.readAsDataURL(file);
	});

	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		const file = fileInput.files && fileInput.files[0];
		if (!file) {
			alert('Выберите файл изображения');
			return;
		}
		const formData = new FormData(form);
		try {
			countEl.textContent = 'Обработка...';
			resultImg.removeAttribute('src');
			const resp = await fetch('/api/detect', { method: 'POST', body: formData });
			const data = await resp.json();
			if (!data.ok) {
				countEl.textContent = data.error || 'Ошибка обработки';
				return;
			}
			countEl.textContent = `Найдено звёзд: ${data.count}`;
			resultImg.src = data.preview;
		} catch (err) {
			console.error(err);
			countEl.textContent = 'Ошибка сети или сервера';
		}
	});
})();

