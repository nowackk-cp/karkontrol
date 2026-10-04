# Teknik anlatım notları

## Kısa demo

Hesap oluştur → mağaza aç → örnek CSV yükle → tekrar yükleyip mükerrerliği
göster → rapor kartı/satır/ay toplamını karşılaştır → iadeyi değiştir →
asistana net kârı sor → sahte failed/timeout/success ödeme sonucunu göster.

## Savunulabilir iddialar

- Para Decimal ve HALF_UP; SQL kuruşları tamsayıdır.
- Saf motorun 44 dalı testlerle çalıştırılır; kapsam tek başına doğruluk değildir.
- Kullanıcı kaynaklı 600 TL örneği iki hesap yolunu bağlar; Fraction ve
  Hypothesis aritmetik/yüzde/yuvarlama sınırlarını farklı yoldan kontrol eder.
- CSV/XLSX hatasının son satırda olması bile hiçbir yarım kayıt bırakmaz.
- İade kargo giderini koruyabilir; tam iadenin kârı negatif olabilir.
- Satış fiyatı barem eşiğini bir kuruş aşınca kargo artışı kârı azaltabilir:
  bu belgelenmiş politika sonucu, uydurulmuş yazılım hatası değildir.
- Gerçek APP-001, APP-002 ve APP-003 hata kayıtları test/model kanıtıyla anlatılabilir.
- Kullanılan araç Codex'tir. Claude Code ile izolasyon yapıldığı veya insan
  tarafından 40 altın sipariş hesaplandığı söylenmez.
- Varsayılan offline asistanın 40/40 sonucu deterministik niyet/SQL kontrolüdür.
  Ayrı Qwen3-1.7B-Q8_0 ölçümünde v1 19/40 → v2 40/40; 21 iyileşme ve 0 gerileme
  vardır. Model araç seçer; finans tutarını sunucu üretir. Windows native runtime
  güvenlik politikasıyla engellendi; gerçek model Linux CI'da çalıştı.
- 20 gerçek model hakem puanı vardır; insan puanları boş olduğundan bağımsız
  kalibrasyon iddiası yoktur. Yeni 10 soru prompt sabitlenince üretilip ilk
  çalıştırmada değerlendirilir; AI yazarlı set bağımsız insan hold-out sayılmaz.

CV proje bölümü ve gönderilmemiş ön yazı [başvuru materyalinde](BASVURU_MATERYALI.md).

## Sonraki ürün ölçeği

SQLite ve Django geliştirme sunucusu portföy demosu içindir. Gerçek SaaS'ta
PostgreSQL, iş kuyruğu, rate limiting, gerçek tarife sürümleri, sipariş/iade
olay tarihleri, ödeme webhook imzaları ve mutabakatın insan denetimi gerekir.
Bu projede olmayan özellikler ürün ölçeğinde varmış gibi sunulmaz.
