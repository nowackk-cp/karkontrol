# AI ajanının yazdığı kâr/hakediş uygulamasını denetleyen test sistemi

Codex'e pazaryeri siparişleri için KârKontrol uygulamasını yazdırdım. Kuruş hesaplarını, dosya aktarımını, mağaza sahipliğini ve asistan yönlendirmesini testlerle denetlettim. LLM koşusunda yanlış dönem/niyet, dış incelemede ise kuruş dağıtımı ve Excel oranı hataları bulundu; bunları regresyonlarıyla düzelttirdim.

[![CI](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml)
[![Model eval](https://github.com/nowackk-cp/karkontrol/actions/workflows/llm.yml/badge.svg)](https://github.com/nowackk-cp/karkontrol/actions/workflows/llm.yml)

Uygulama CSV/XLSX sipariş aktarır, aktarımı geri alır, iadeleri günceller, filtreli kâr/hakediş raporu ve Excel uyumlu CSV üretir. TRY ve sabit kurla Amazon USD/EUR demo hesapları, örnek abonelik ödemesi ve rapor araçlarına bağlı asistan vardır.

## Ne kanıtlıyor

- Belgelenen demo sözleşmesinin kuruş, iade, eşik ve rapor davranışları otomatik kontrollerden geçiyor.
- Sahiplik, CSRF, dosya atomikliği ve tarayıcıda para gösterimi ayrı katmanlarda denetleniyor.
- İlk hatalar, düzeltmeler ve ham model cevapları korunuyor; ölçümler kaynak commit'e bağlı.

## Henüz ne kanıtlamıyor

- Bağımsız insan finans kabulü: insan beklenenleri 0/40. En az 10, hedef 40 insan hesabı, kural kararları ve ilk karşılaştırma gerekiyor. Tarifeler sentetik; üretim dağıtımı ve gerçek pazaryeri uyumu yapılmadı.
- Görülmemiş insan sorularına genelleme: aynı geliştirme setindeki prompt ayarı ve AI'nın ürettiği sentetik ilk set bunu ölçmez. Yeni kör insan seti gerekiyor.
- Kalibre edilmiş hakem veya kişisel alan yeterliği: yeni 30 benzersiz adayın insan etiketleri boş. Ayrı model puanı, kör insan incelemesi, alan anlatımı ve başvuru son redaksiyonu gerekiyor.

## Yakalanan hatalar

| Hata | Yakalayan | Satıcı etkisi |
|---|---|---|
| APP-001 — yabancı mağazaya POST 405 | Entegrasyon testi | Beklenen 404 sözleşmesi bozuldu; finans farkı yok |
| APP-002 — çok uzun adet 500 | Girdi testi | Aktarım açıklayıcı hata veremedi; kayıt oluşmadı |
| APP-003 — Eylül yerine Kasım | İlk LLM koşusu | −60,00 TL zarar “veri yok” cevabında gizlendi |
| APP-004 — ürün/iade için yanlış araç | İlk LLM koşusu | Yanlış rapor/kural cevabı; ayrı TL farkı ölçülmedi |
| ENG-001 — eşit kalan sırası | Dış inceleme ve regresyon | 10 TL dağıtımında 8,33/0,84/0,83 yerine 8,34/0,83/0,83 gerekir |
| ENG-002 — yüksek hassasiyette kur | Bağımsız mutasyon incelemesi | Kabul edilen çok hassas kurda brüt/hakediş 0,01 TRY sapıyordu; tam ara hesapla düzeltildi |
| IMP-001 — yüzde biçimli Excel oranı | Dış inceleme ve regresyon | Yanlış oranla kayıt oluşabiliyordu; artık atomik reddedilir |
| IMP-002/003 — geri alma/kısa CSV | Dış inceleme ve regresyon | Hatalı yeni satırlar kaldı veya kısa satır kabul edildi |
| REP/CFG/AI/JDG | Dış inceleme ve çapraz test | Arama, eksik rapor, sınır, dönem ve ölçüm sözleşmesi düzeltildi |

Ayrıntılar ve issue bağlantıları [BUGS.md](BUGS.md) içinde. Testten önce issue açılma sırası ve sonradan belgelenen eski hatalar açıkça ayrılır.

## Ölçümler

Bu tablo güncel sayısal ölçümlerin tek özetidir. Tarihî kanıtlar değiştirilmez.

| Ölçüm | Sonuç / kaynak |
|---|---|
| Çekirdek testler | Son yerel kaynakta 542 geçti; yeni Linux CI bekleniyor |
| Chromium E2E | 13 geçti; gerçek tarayıcı, yeni üç para kartı ve farklı satırlar |
| Dev-only, Playwright yok | Son kaynakta 542 geçti / 1 opsiyonel paket atlandı |
| Mobil Chromium | 390×844 dokunmatik görünümde 13 geçti |
| Güncel motor dal kapsamı | Son yerel kaynakta 50/50 = %100; yeni Linux CI bekleniyor |
| Tarihî dışlamalı mutasyon | 342/369 = %92,68; 27 kalan mutant: 14 mesaj, 9 davranış farkı, 3 strict eşdeğeri, 1 precision adayı |
| İlk dışlamasız mutasyon | 423/436 = %97,02; 13 kalan / 0 diğer. [Koşu](https://github.com/nowackk-cp/karkontrol/actions/runs/37249153652), c1481f4 kaynak sürümü; incelemesi ENG-002'yi buldu. Son düzeltme ölçümü bekleniyor |
| İlk v2 geliştirme ölçümü | 34/40, 5 kritik hata → aynı sette prompt ayarı sonrası 40/40; genelleme kanıtı değildir |
| Modele atfedilebilir yönlendirici doğruluğu | İlk 30/36 → düzeltilmiş 36/36; 4 model öncesi güvenlik reddi ayrı. İnceleme notundaki 34/36 ham JSON ile uyuşmuyor |
| Anahtar kelime tabanı | Tarihî 40/40; yeni dönem geliştirme setinde yerel 52/52 |
| İlk v3 Qwen geliştirme ölçümü | 49/52; modele atfedilebilir 41/44, 2 kritik hata. [İlk ham yanıt](data/evidence/external-review/llm-v3-first/eval.json); düzeltme sonrası ölçüm bekleniyor |
| İkinci v3 Qwen ölçümü | 51/52; modele atfedilebilir 43/44, kritik hata 0. [İkinci ham yanıt](data/evidence/external-review/llm-v3-second/eval.json); kalan E-35 için yönerge düzeltildi, son ölçüm bekleniyor |

[Son main CI](https://github.com/nowackk-cp/karkontrol/actions/workflows/ci.yml?query=branch%3Amain) · [HTML raporları](https://nowackk-cp.github.io/karkontrol/) · [İlk başarısız LLM koşusu](https://github.com/nowackk-cp/karkontrol/actions/runs/37173824046) · [Düzeltilmiş ham rapor](data/evidence/llm-corrected.json).

## Bulgular ve kalite kapısı

Sentetik baremde fiyatı 300,00 TL'den 300,01 TL'ye artırmak kârı **29,99 TL düşürebilir**: kargo bandı 30 TL artar. Bu test fiyat artışıyla kârın her zaman yükseldiği varsayımını engeller.

Main'de quality ve model-eval kontrolleri zorunlu; yönetici de kurala tabidir. [Eski PR #4](https://github.com/nowackk-cp/karkontrol/pull/4) kasıtlı stopaj değişikliğiyle kırmızı kaldı ve birleştirilmeden kapandı. Yeni APP-001 demo PR'ı/eşleşen ekran bu düzeltmelerin birleşik CI kontrolünden sonra kaydedilecek. İnsan PR onayı yok; bu ayrı bir insan inceleme kanıtı sayılmaz.

## Üç komutla çalıştırma

Python 3.13 ve [uv](https://docs.astral.sh/uv/) gerekir.

```powershell
uv sync --locked --extra dev --extra e2e
uv run python manage.py bootstrap_demo
uv run python manage.py runserver 127.0.0.1:8001
```

[Yerel uygulama](http://127.0.0.1:8001/) — `demo-satici / demo-only-pass-2026`. Demo kurulumu yalnız DEBUG açıkken çalışır; mevcut şifre/iade bilgisine dokunmaz. UI'dan kayıt ve yeni mağaza oluşturulabilir.

Kontroller: `uv run ruff check .`, `uv run ruff format --check .`, `uv run python -m pytest -n 2 --cov`, `uv run python -m playwright install chromium`, `uv run python -m pytest tests/e2e -m e2e --browser chromium`. İnsan mutabakatı ayrıca `uv run python -m pytest tests/reconciliation -m reconciliation` ile çalışır; boş insan kanıtı başarısızdır. Linux mutasyonu: `uv sync --locked --extra dev --extra mutation`, `uv run mutmut run --max-children 2`.

[Kurallar](docs/KURALLAR.md) · [Alan kaynakları](docs/ALAN_BILGISI.md) · [Mimari/dosya sözleşmesi](docs/MIMARI.md) · [QA ve mutant incelemesi](docs/QA_STRATEJISI.md) · [İnsan altın seti](docs/ALTIN_SET.md) · [Eval protokolü](docs/EVAL_RAPORU.md) · [AI çalışma kaydı](docs/AI_ILE_CALISMA.md).
