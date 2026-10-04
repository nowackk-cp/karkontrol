# KârKontrol

[![CI](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml)

Pazaryeri kâr hesaplarının doğruluğunu bağımsız testlerle denetlemek için
geliştirilen Python/Django kalite güvence projesi.

Mağaza kurulumu, CSV/Excel sipariş aktarımı, tarih/ürün filtreleri ve iade adedi
yönetimi çalışır. Kâr motoru, insan doğrulamalı altın veri, mutasyon sonuçları
ve LLM değerlendirmesi henüz tamamlanmamıştır.
Tamamlanmamış özellikler ve ölçülmemiş kalite değerleri başarı olarak sunulmaz.

GitHub'da [ilk CI çalışması](https://github.com/nowackk-cp/karkontrol/actions/runs/37163642871)
başarılı tamamlandı; `test-reports` artifact'ı oluşturuldu. `main` dalında
`quality` kontrolü ve PR zorunlu; kurallar yöneticilere de uygulanır.
Tek geliştiricili başlangıç için insan onayı sayısı 0'dır; bu insan code review
kanıtı sayılmaz. Zorunlu kontrol, güncel dal ve PR olmadan değişiklik birleştirilemez.

## Çalıştırma

Python 3.13 ve [uv](https://docs.astral.sh/uv/guides/install-python/) kullanılır.
Django 5.2 LTS bu Python sürümünü destekler
([resmî sürüm notları](https://docs.djangoproject.com/en/5.2/releases/5.2/)).

```powershell
uv sync --locked --extra dev
uv run python manage.py migrate
uv run python manage.py runserver 127.0.0.1:8001
```

Adres: http://127.0.0.1:8001/ — servis kontrolü: `/health/`.
Yerel ayarlar uygulamayı yalnızca geliştirme amacıyla çalıştırır. Üretim
ayarları için `DJANGO_SETTINGS_MODULE=config.settings.production`, güçlü
`DJANGO_SECRET_KEY` ve `DJANGO_ALLOWED_HOSTS` ortam değişkenlerini tanımlayın.
Üretim ortamındaki dosya `.env` üzerinden otomatik yüklenmez.

## Sentetik demo

Migration sonrası yerelde `uv run python manage.py seed_demo` çalıştırın.
Giriş: **demo-satici** / **demo-only-pass-2026**. Bu komut yalnızca DEBUG açıkken
çalışır ve mevcut hesabın parolasını değiştirmez. Demo parolasını
`KARKONTROL_DEMO_PASSWORD` ortam değişkeniyle belirleyebilirsiniz.

Mağaza ekranından örnek CSV indirip yükleyebilirsiniz. Tekrar yüklemede mevcut
satırlar atlanır; hatalı veya mevcut veriye aykırı bir satırda bütün aktarım
geri alınır. Diğer kullanıcıya ait mağaza/sipariş URL'leri 404 döndürür.
[Dosya sözleşmesi ve sınırlar](docs/VERI_AKTARIMI.md).

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

2026-10-04 güncel yerel doğrulama: **75 test geçti**; lint, format,
Django sistem kontrolü ve migration farkı kontrolü temiz. Windows'ta pytest
başlatıcısı uygulama denetimine takıldığı için `python -m pytest` kullanılır.
Uygulama toplam kapsamı %96; bu değer kâr motorunun kapsamı değildir.
İlk kurulumda 22 test/%91 kapsam vardı. Yeni veri akışlarında gerçekten
yakalanıp düzeltilen iki uygulama hatası [BUGS.md](BUGS.md) içinde kayıtlıdır;
finansal motor hatası sayısı hâlâ 0'dır.

## Çalışma ilkeleri

- Para için `Decimal`; yuvarlama için `ROUND_HALF_UP` kullanılacak.
- Beklenen sonuçlar motordan bağımsız ve insan tarafından doğrulanmış olmalı.
- Yalnızca testle kanıtlanan hatalar [BUGS.md](BUGS.md) içine kaydedilir.
- Her tamamlanan işlem [işlem günlüğüne](projede%20yapılanlar.md) yazılır.

[QA stratejisi](docs/QA_STRATEJISI.md) ·
[AI çalışma kaydı](docs/AI_ILE_CALISMA.md) ·
[devam notu](docs/DEVAM_NOTU.md)

Bağımsız eğitim projesidir, hiçbir pazaryeriyle ilişkisi yoktur; oranlar örnektir.
