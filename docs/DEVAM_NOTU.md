# Sonraki oturum için devam notu

Tarih: 2026-10-04 (Europe/Istanbul). Proje: KârKontrol.

## Önce oku

`AGENTS.md`, `projede yapılanlar.md`, bu dosya, yereldeki
`KarKontrol_Proje_Plani.md` ve `git status --short`.

## Kullanıcı talimatı

Soru sormadan ilerle. Tamamlanan her işlemi hemen işlem günlüğüne yaz.
Bağlam dolduğunda otomatik compact sonrasında dosyalardan devam et.
Çağrılabilir bir manuel compact aracı bulunmadı.

## Hazır olanlar

- Kalıcı altın kural ve işlem günlüğü.
- Python 3.13/Django 5.2/uv yapılandırması.
- Django paketleri, ana sayfa, giriş/çıkış, DB sağlık kontrolü.
- Ayrı test/yerel/üretim ayarları; üretimde zorunlu güvenlik değişkenleri.
- Oturum/CSRF/admin/sağlık testleri; üretim güvenlik testi.
- CI dosyası, Issue/PR şablonları, dürüst BUGS başlangıcı.
- QA stratejisi, kaynak araştırma özeti, kural ve 30 senaryo taslağı.
- Store/OrderLine/ImportBatch modelleri ve migration'ları.
- Mağaza oluşturma, kullanıcı izolasyonu, atomik CSV/XLSX aktarımı, mükerrer
  önleme, tarih/ürün filtresi, sayfalama ve iade adedi ekranları.
- Yalnızca DEBUG ortamında çalışan, tekrar kullanılabilir sentetik demo komutu.

## Aktif doğrulama

Python 3.13.14 ve Django 5.2.17 kuruldu; `uv.lock` hazır. Başlangıçta indirme,
sürüm bağlantısı ve kilit sorunu yaşandı; yorumlayıcı ve ortam sonradan doğrulandı.

İlk kurulumda 22 test/%91 kapsam vardı. Son turda **75 test geçti** (3,09 saniye,
iki worker); uygulama toplam kapsamı **%96**. Motor kapsamı ölçülmedi.
Ruff lint/format, Django check, migration drift ve yerel migrate başarılı.
Windows console launcher engeli nedeniyle
`uv run python -m pytest` kullan; sistem güvenlik politikasını değiştirme.
Raporlar `reports/tests.html`, `reports/junit.xml`, `reports/coverage.xml`,
`htmlcov/index.html` içinde ve Git dışında.

## Sıra

1. Nihai alan kurallarını ve insan doğrulamalı altın veriyi tamamla.
2. Yalnızca kuralları gören ayrı motor oturumu ve gerçek `ai-v1` etiketi.
3. Mutabakat/property/entegrasyon testleri; gerçek hatalar ve motor kalite kapısı.
4. E2E, asistan eval ve yeni pazaryeri modülü.

## Kanıt sınırları

Henüz onaylı `KURALLAR_v1.md`, `altin_set.csv/xlsx`, motor, mutasyon sonucu,
LLM eval, ödeme entegrasyonu veya E2E paketi yok. İnsan kontrolü yapılmamış AI
hesaplarını elle doğrulanmış altın veri diye sunma. Başvuru notlarını içeren
ana plan `.gitignore` ile yerelde tutulur.

## Güncel GitHub / servis kanıtı

- Public depo: https://github.com/nowackk-cp/karkontrol.
- İlk CI başarılı: https://github.com/nowackk-cp/karkontrol/actions/runs/37163642871.
  `quality` işi 15 saniye, toplam run 16 saniye; rapor artifact'ı doğrulandı.
- `main` korumalı: güncel dal, `quality`, PR zorunlu; yönetici muafiyeti yok.
  İnsan onay sayısı 0; force push ve dal silme kapalı.
- Bu nedenle sonraki kod değişikliklerini ayrı dal ve PR üzerinden gönder.
- Güncel sunucu http://127.0.0.1:8001/ adresinde. Demo hesabı `demo-satici` /
  `demo-only-pass-2026`. Seed yalnızca DEBUG altında çalışır.
- Browser becerisiyle giriş, mağaza, filtre, dosya yükleme/tekrar yükleme ve
  iade doğrulandı; ekran kanıtı `reports/screens/store-orders.png` (Git dışında).
  Sonraki oturumda sunucu durumunu kontrol et; eski 8000 bootstrap sürecine güvenme.
- Başlangıç altyapısı tamamlandı; sıradaki asıl faz, kesin kurallar ve bağımsız
  insan doğrulamalı altın veri. Motorun önce yazılmaması kuralını koru.

Başlangıç PR #1, başarılı CI'nin doğru commit'i doğrulandıktan sonra squash merge edildi.
Güncel çalışma dalı: `feat/store-order-import`; bunun PR/CI durumunu GitHub'dan kontrol et.
Son üretim kontrolü `check --deploy --settings config.settings.production`
geçici test ortam değişkenleriyle 0 sorun verdi. Dış sunucuya dağıtım yapılmadı.

## Veri akışı sınırları ve kanıtlar

- Dosya sözleşmesi: `docs/VERI_AKTARIMI.md`. CSV UTF-8, tek sayfalı XLSX,
  TRY, Decimal, 5 MB dosya / 25 MB açılmış XLSX / 5000 satır.
- Kimlik mağaza+numara+satır; farklı içerikte çelişki tüm transaction'ı geri alır.
- APP-001 (sahiplik/HTTP kontrol sırası) ve APP-002 (çok uzun adet ValueError)
  gerçek testlerle bulundu ve beklentiler değiştirilmeden düzeltildi.
  Bunlar motor hatası/finansal doğruluk kanıtı değildir.
- Otomatik Playwright suite, SQL kâr raporu, billing ve asistan hâlâ bekliyor.
