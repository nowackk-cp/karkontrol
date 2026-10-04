# Doğrulanmış başvuru materyali

2026-10-04. Bu dosya mevcut CV'ye eklenebilecek proje bölümünü ve ön yazı
taslağını içerir. Kişisel eğitim/iş geçmişi uydurulmamıştır. Başvuru, LinkedIn
mesajı veya e-posta gönderilmemiştir.

## CV proje bölümü

**KârKontrol — Python/Django kalite otomasyonu projesi**
[Kaynak kod](https://github.com/nowackk-cp/karkontrol) ·
[HTML test/kapsam raporları](https://nowackk-cp.github.io/karkontrol/)

- Decimal/HALF_UP tabanlı kâr/hakediş motoru; CSV/XLSX aktarımı, SQL raporları,
  iade ve kullanıcı izolasyonu. Sentetik Amazon USD/EUR senaryoları.
- 316 unit/property/integration/eval test ve 12 Playwright E2E; motor dal
  kapsamı 44/44 = %100, mutasyon skoru 342/369 = %92,68.
- GitHub Actions, yöneticilere de uygulanan required kontroller ve Pages raporları.
  Kontrollü hatalı PR CI'da başarısız oldu ve birleştirilmeden kapatıldı.
- Gerçek Qwen araç seçimi + SQL oracle: v1 19/40 → v2 40/40, kritik hata 0.
  20 model hakem puanı ve bağımsız insan incelemesi için kabul araçları hazır.

Sayısal başarılar demo sözleşmesine aittir. İnsan doğrulamalı 40 sipariş golden
seti veya 20 cevaplık hakem kalibrasyonu yapıldığı söylenmez. Finans motorunda
gerçek bug sayısı 0; üç gerçek uygulama/model hatası BUGS.md'de ayrı kaydedilir.
Kullanılan geliştirme aracı Codex'tir; Claude Code izolasyonu iddia edilmez.

## Ön yazı taslağı

Merhaba, kalite güvence otomasyonu yaklaşımımı göstermek için KârKontrol adlı
bağımsız bir demo hazırladım. Python/Django uygulamasının kâr/hakediş kurallarını,
CSV/XLSX içe aktarmasını ve SQL raporlarını 316 test ve 12 Playwright akışıyla
kontrol ettim. Motor dal kapsamı %100, mutasyon skoru %92,68; başarısız bir kontrolün
birleştirmeyi engellediği PR kanıtı ve HTML raporları repoda bulunuyor. Gerçek Qwen
asistanını SQL sonuçlarına karşı değerlendirdim; düzeltilmiş v2 prompt40/40 soruyu
geçti. Bağımsız insan finans ve hakem kabulünü ayrı, açık bir gereksinim olarak
tutuyorum. Bu yaklaşımı ekibinizin gerçek ürün akışlarına uygulamak isterim.

Kaynak kod: https://github.com/nowackk-cp/karkontrol

## Mülakatta gösterilecek kanıtlar

[Hata kayıtları](../BUGS.md), [kalite kapısı](CI_KAPISI_KANITI.md),
[eval raporu](EVAL_RAPORU.md), [mutasyon incelemesi](MUTASYON_RAPORU.md),
[mülakat notları](MULAKAT_NOTLARI.md) ve [kabul sınırları](PROJE_DURUMU.md).
Süreç ya da ölçüm geçmişe dönük değiştirilmez; ilk başarısız model raporu korunur.
