# Sürüm geçmişi

## 1.1.0 — gerçek model ve bağımsız kabul araçları

Qwen3-1.7B yerel JSON araç seçimi, sunucu tarih/owner sınırı, gerçek v1/v2
SQL eval ve LLM hakem çalıştırıcısı eklendi. Gerçek Linux ölçümünde v1%47,5
→ v2%100; kritik hata0, gerileyen soru0. İlk başarısız%85 ölçüm korunur;
APP-003 yanlış ay hatası düzeltildi.316 core test ve12 E2E geçti.
40 sipariş XLSX/CSV insan inceleme akışı ve kuruş mutabakat kapısı hazır;
20 insan/hakem puanı için%85 kalibrasyon kapısı vardır. İnsan alanları boş.
Yeni10 soru prompt sabitleme workflow'u ve resmî Amazon tarife farkları
belgelendi. Windows native LLM çalışması Code Integrity engeline tabidir.

## 1.0.0 — çalışan portföy demosu

Demo ürün ve otomatik kalite katmanları tamamlandı: 261 test, 12 Chromium
E2E, mobilde aynı 12 akış, %100 motor dal kapsamı ve %92,68 ham mutasyon.
Ana dal raporları Pages'te yayımlanır; kasıtlı hatalı PR kalite kapısıyla
engellenip birleştirilmeden kapatıldı. Mimari/QA/eval/alan/mülakat belgeleri hazır.
Bağımsız insan golden kabulü ve gerçek LLM/judge kanıtları ayrı kabul işidir.

## 0.2.0 — finans demo sürümü

Decimal motoru, sipariş başına ücret dağıtımı, kısmi/tam iade, integer-cents
SQL raporu, sabit USD/EUR Amazon demo, CSV export, hesap oluşturma,
ücretsiz kota/sahte ödeme ve araç asistanı eklendi. Unit/property/SQL/eval,
12 E2E ve Linux mutasyon kapıları çalışır; main kalite korumalıdır.
İnsan golden/judge/kör holdout ve gerçek pazaryeri tarifesi kapsam dışıdır.

## 0.1.0 — başlangıç

Django altyapısı, protected GitHub main, CSV/XLSX atomik aktarım, mağaza
izolasyonu, filtre/sayfalama ve iade giriş ekranı. APP-001/APP-002 gerçek
regresyon testleriyle düzeltildi. İlk 22 test, sonra75 test kanıtı günlüktedir.
