# KârKontrol

Pazaryeri kâr hesaplarının doğruluğunu bağımsız testlerle denetlemek için
geliştirilen Python/Django kalite güvence projesi.

İlk aşamada çalışma altyapısı kurulmaktadır. Kâr motoru, insan doğrulamalı altın
veri, mutasyon sonuçları ve LLM değerlendirmesi henüz tamamlanmamıştır.
Tamamlanmamış özellikler ve ölçülmemiş kalite değerleri başarı olarak sunulmaz.

## Çalıştırma

Python 3.13 ve [uv](https://docs.astral.sh/uv/guides/install-python/) kullanılır.
Django 5.2 LTS bu Python sürümünü destekler
([resmî sürüm notları](https://docs.djangoproject.com/en/5.2/releases/5.2/)).

```powershell
uv sync --locked --extra dev
uv run python manage.py migrate
uv run python manage.py runserver
```

Adres: http://127.0.0.1:8000/ — servis kontrolü: `/health/`.
Yerel ayarlar uygulamayı yalnızca geliştirme amacıyla çalıştırır. Üretim
ayarları için `DJANGO_SETTINGS_MODULE=config.settings.production`, güçlü
`DJANGO_SECRET_KEY` ve `DJANGO_ALLOWED_HOSTS` ortam değişkenlerini tanımlayın.
Üretim ortamındaki dosya `.env` üzerinden otomatik yüklenmez.

## Kontroller

```powershell
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python -m pytest -n 2 --cov --cov-report=term-missing --cov-report=html --html=reports/tests.html --self-contained-html
```

HTML raporları yerelde `reports/tests.html` ve `htmlcov/index.html` içindedir.
GitHub Actions raporları workflow artifact'ı olarak saklar.

2026-10-04 yerel başlangıç doğrulaması: **22 test geçti**; lint, format,
Django sistem kontrolü ve migration farkı kontrolü temiz. Windows'ta pytest
başlatıcısı uygulama denetimine takıldığı için `python -m pytest` kullanılır.
Başlangıç altyapısı toplam kapsamı %91; bu değer kâr motorunun kapsamı değildir.

## Çalışma ilkeleri

- Para için `Decimal`; yuvarlama için `ROUND_HALF_UP` kullanılacak.
- Beklenen sonuçlar motordan bağımsız ve insan tarafından doğrulanmış olmalı.
- Yalnızca testle kanıtlanan hatalar [BUGS.md](BUGS.md) içine kaydedilir.
- Her tamamlanan işlem [işlem günlüğüne](projede%20yapılanlar.md) yazılır.

[QA stratejisi](docs/QA_STRATEJISI.md) ·
[AI çalışma kaydı](docs/AI_ILE_CALISMA.md) ·
[devam notu](docs/DEVAM_NOTU.md)

Bağımsız eğitim projesidir, hiçbir pazaryeriyle ilişkisi yoktur; oranlar örnektir.
