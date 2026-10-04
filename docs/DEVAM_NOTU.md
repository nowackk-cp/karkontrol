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

## Aktif doğrulama

Python 3.13.14 ve Django 5.2.17 kuruldu; `uv.lock` hazır. Başlangıçta indirme,
sürüm bağlantısı ve kilit sorunu yaşandı; yorumlayıcı ve ortam sonradan doğrulandı.

Yerelde 22 test geçti (3,67 saniye pytest süresi, iki worker); altyapı kapsamı
%91. Motor kapsamı ölçülmedi. Ruff lint/format, Django check, migration drift
ve yerel migrate başarılı. Windows console launcher engeli nedeniyle
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
- Yerel sunucu http://127.0.0.1:8000/ adresinde başlatıldı. Ana sayfa, health
  ve login gerçek HTTP üzerinden 200 verdi. Sonraki oturumda sunucu durumunu kontrol et.
- Başlangıç altyapısı tamamlandı; sıradaki asıl faz, kesin kurallar ve bağımsız
  insan doğrulamalı altın veri. Motorun önce yazılmaması kuralını koru.

Başlangıç kanıtları için PR: https://github.com/nowackk-cp/karkontrol/pull/1.
PR'ın en son durumunu GitHub'dan kontrol et; tamamlanmamış bir merge'i varsayma.
