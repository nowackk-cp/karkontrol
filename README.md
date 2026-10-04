# KârKontrol

Pazaryeri satışının kârını ve hakedişini görünür kılan, doğruluğunu testlerle kanıtlayan bağımsız demo.

**v1.0.0 demo sürümü** — işlevsel ürün ve otomatik QA tamamlandı;
bağımsız insan finans kabulünün durumu aşağıda açıkça belirtilir.

[![CI](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml)
[![Araç asistanı eval](https://github.com/nowackk-cp/karkontrol/actions/workflows/eval.yml/badge.svg)](https://github.com/nowackk-cp/karkontrol/actions/workflows/eval.yml)
[![Mutasyon](https://github.com/nowackk-cp/karkontrol/actions/workflows/nightly.yml/badge.svg)](https://github.com/nowackk-cp/karkontrol/actions/workflows/nightly.yml)

Hesap/mağaza oluşturun, CSV veya Excel siparişlerini yükleyin, kâr/hakediş
raporunu filtreleyin, iadeleri güncelleyin. Amazon demo sabit USD/EUR kuru,
CSV rapor indirme, sahte abonelik ödemesi ve araçlara dayalı asistan dahildir.
[Demo sözleşmesi](docs/KURALLAR_v1.md) · [Amazon demo](docs/KURALLAR_v2.md) ·
[Mimari](docs/MIMARI.md) · [Kapsam ve kabul durumu](docs/PROJE_DURUMU.md).

## Başlatma

Python 3.13 ve [uv](https://docs.astral.sh/uv/guides/install-python/) gerekir.

```powershell
uv sync --locked --extra dev --extra e2e
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py rebuild_reports
uv run python manage.py runserver 127.0.0.1:8001
```

[Yerel uygulama](http://127.0.0.1:8001/) — demo:
**demo-satici / demo-only-pass-2026**. Kendi hesabınızı kayıt ekranında da
oluşturabilirsiniz. Seed yalnız DEBUG açıkken çalışır, mevcut parolayı/iade
durumunu değiştirmez; KARKONTROL_DEMO_PASSWORD ile demo parolasını belirleyin.

Mağazada örnek CSV indirilebilir. Aynı dosya yeni kayıt yaratmaz; son satırdaki
hata bile bütün aktarımı geri alır. Ücretsiz hesap toplam100 satır; sahte
ödeme Demo Pro'yu etkinleştirir. Kart veya gerçek tahsilat yoktur.
[Dosya sözleşmesi ve sınırlar](docs/VERI_AKTARIMI.md).

## Doğrulanmış kalite

| Katman | Kanıt |
|---|---|
| Unit, sınır, property, entegrasyon, SQL ve eval | 261 test; sonuçlar CI ve işlem günlüğünde |
| E2E | 12 bağımsız Chromium senaryosu: import, iade, rapor, ödeme, izolasyon |
| Motor dal kapsamı | 44/44 = %100; CI alt sınırı %90 |
| Mutasyon | 342/369 = %92,68; 27 survivor, gecelik alt sınır %85 |
| Araç asistanı | 40/40 soru; SQL eşitliği ve sayısal guardrail; LLM skoru değildir |

[CI kanıtı](https://github.com/nowackk-cp/karkontrol/actions/runs/37170676379) ·
[Mutasyon kanıtı](https://github.com/nowackk-cp/karkontrol/actions/runs/37171192788) ·
[Mutasyon incelemesi](docs/MUTASYON_RAPORU.md) ·
[Eval raporu](docs/EVAL_RAPORU.md) · [QA stratejisi](docs/QA_STRATEJISI.md) ·
[HTML rapor yayını](https://nowackk-cp.github.io/karkontrol/).

Kapsam tek başına kalite değildir. Motor Decimal/HALF_UP, ikinci aritmetik yol
Fraction/tamsayıdır; Hypothesis nakit/kâr eşitliğini ve kuruş dağıtımını kontrol
eder. SQL tamsayı kuruş toplar. Mutasyonun kalan kuruş sırası ve maliyet KDV'sinde
gösterdiği test boşlukları güçlendirildi. Gerçek uygulama hataları
[BUGS.md](BUGS.md) içinde; kasıtlı CI demo hatası AI bug olarak sayılmaz.

## Kontroller

```powershell
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python -m pytest -n 2 --cov --cov-report=json:reports/coverage.json --cov-report=html --html=reports/tests.html --self-contained-html
uv run python scripts/check_coverage.py reports/coverage.json
uv run python -m playwright install chromium
uv run python -m pytest tests/e2e -m e2e --browser chromium --tracing retain-on-failure --screenshot only-on-failure
uv run python -m pytest tests/eval
```

Windows'ta console launcher engellenirse python modül çağrısı kullanılır.
Mutmut fork gerektirir: Linux/WSL'de `uv sync --extra dev --extra mutation`,
`uv run mutmut run --max-children 2`, ardından
`uv run python scripts/check_mutation.py mutants/engine`.
[Resmî mutmut yönergeleri](https://mutmut.readthedocs.io/en/latest/).

CI lint/format/migration/test/coverage/E2E kapılarını uygular; main protected,
quality kontrolü zorunludur ve yöneticiler de kurallara tabidir. İnsan PR onayı
sayısı0; bu insan review kanıtı değildir. Raporlar14 gün artifact olarak
saklanır. Pages yalnız başarılı ana dal push CI çıktısını yayımlar.

## Kabul sınırları

Ücretler sentetiktir; gerçek pazaryeri sözleşmesi veya canlı döviz kullanılmaz.
30 TRY +10 Amazon [sentetik girdi](data/draft/inputs.json) ve
[boş insan inceleme şablonu](data/draft/manual_review.csv) hazırdır. İnsan
doğrulamalı altın beklenenler yoktur; bağımsız finans kabulü tamamlanmış sayılmaz.
Kullanıcının600 TL örneği kaynaklı kontrol ayrıca test edilir.

Asistan dış LLM kullanmaz; sabit niyet seçimi ve finans araçlarıyla yanıt verir.
İnsan judge kalibrasyonu, prompt v1/v2 karşılaştırması ve kör hold-out yapılmadı.
Reserved10 soru geliştirici AI tarafından görüldü. Kullanılan araç Codex'tir;
Claude izolasyonu iddia edilmez. İşlevsel demo ile bu insan kanıtları ayrıdır.

Üretim ayarları DJANGO_SETTINGS_MODULE=config.settings.production,
DJANGO_SECRET_KEY ve DJANGO_ALLOWED_HOSTS gerektirir. Mevcut çalıştırma Django
geliştirme sunucusudur; üretim dağıtımı yapılmadı.

Her tamamlanan işlem [günlüğe](projede%20yapılanlar.md) hemen yazılır.
[AI kararları](docs/AI_ILE_CALISMA.md) · [Mülakat notları](docs/MULAKAT_NOTLARI.md) ·
[Devam notu](docs/DEVAM_NOTU.md). Bağımsız eğitim projesidir; pazaryerleriyle ilişkisi yoktur.
