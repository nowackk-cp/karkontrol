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

Python 3.13 kurulumu sürüyor. İlk indirme uzadı; paralel `uv sync` Python
kurulum kilidinde zaman aşımına uğradı. Yeniden başlatılan kurulumun sonucu
alınmadan başarılı kurulum veya test iddiası yazma. Çalışan süreçleri kontrol et;
başka oturumların süreçlerine müdahale etme.

Kurulum sonrası: `uv sync --extra dev` → `ruff check`/`format` → Django
check/migrate/migration drift → pytest ve raporlar. `uv.lock` depoya girmeli.

## Sıra

1. Altyapıyı yerelde doğrula ve küçük commit'lerle kaydet.
2. Ana plandaki `nowackk-cp/karkontrol` public depo ve gerçek CI durumunu kur/doğrula.
   GitHub CLI oturumu hazır; ilk kontrolde hedef depo bulunmadı.
3. Nihai alan kurallarını ve insan doğrulamalı altın veriyi tamamla.
4. Yalnızca kuralları gören ayrı motor oturumu ve gerçek `ai-v1` etiketi.
5. Mutabakat/property/entegrasyon testleri; gerçek hatalar ve kalite kapısı.

## Kanıt sınırları

Henüz onaylı `KURALLAR_v1.md`, `altin_set.csv/xlsx`, motor, mutasyon sonucu,
LLM eval, ödeme entegrasyonu veya E2E paketi yok. İnsan kontrolü yapılmamış AI
hesaplarını elle doğrulanmış altın veri diye sunma. Başvuru notlarını içeren
ana plan `.gitignore` ile yerelde tutulur.
