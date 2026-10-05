# Test stratejisi ve kanıt incelemesi

Güncel ölçümlerin tek tablosu [README](../README.md) içindedir. Bir testin geçmesi alan kuralının insan tarafından doğru seçildiğini kanıtlamaz.

| Risk | Kontrol |
|---|---|
| Kuruş, eşik ve iade dağıtımı | Sözleşme örnekleri, Fraction/tamsayı referansı, property testleri |
| Yanlış oran/dosya ve yarım kayıt | XLSX hücre biçimi, CSV genişliği, atomik rollback ve undo |
| Mağaza izolasyonu | Bütün store rotaları; yabancı GET ve CSRF-geçerli POST; DB değişmezliği |
| Rapor toplamı | Parametreli aylık SQL, motor ve filtreli CSV/ekran tutarlılığı |
| UI para gösterimi | Farklı senaryolar, tüm finans sütunları, üç kart, dışlayan filtre |
| Asistan dönemi ve niyeti | Kritik tarih vakaları, tam cümle sözleşmesi, eşit olmayan ürün sırası |
| İnsan finans doğruluğu | Her insan inceleme satırında ayrı mutabakat testi |

Nakit/kâr eşitliği motorun alanlarından türeyen özdeşliktir; ikinci bağımsız finans hesabı değildir. Hakediş ve KDV testleri girdi oranlarından Fraction/tamsayı ile ayrıca hesaplanır. Bunlar ayrı aritmetik uygulamadır; insan altın kanıtı sayılmaz.

## CI

quality lint, format, ayar/migration, unit/integration/eval, kapsam ve Chromium akışlarını denetler. Playwright bulunmayan dev ortamı tarayıcı paketini atlar. Model değişiklikleri changes job'uyla tespit edilir; required model-eval kontrolü her PR'da sonuç bildirir. İlgili değişiklik yoksa model indirmesi atlanır. Haftalık/elle koşu model ölçümünü zorlar. PR'lar eski koşuyu iptal eder; main koşuları iptal edilmez.

İnsan mutabakatı ayrı, henüz zorunlu olmayan kırmızı job'dur; boş kanıtı başarı saymaz. CODEOWNERS insan veri dizinini işaretler. İnsan hakem job'u kaliteyi engellemez. Pages başarılı main CI'ın JUnit sayılarından dinamik HTML oluşturur. Release JUnit/HTML/kapsam/mutasyon ve model JSON'larını süreli artifact dışında saklar.

## Mutasyon

Hata mesajları da test sözleşmesidir; güncel mutasyon ayarında `raise ValueError` dışlaması kaldırılmıştır. Test seçimi motor sözleşme testlerini içerir. Eski dışlamalı sonuç güncel motorun skoru olarak kullanılmaz. Önceki kalan mutantların tek tek farkları ve inceleme sınıfları bu belgenin ekinde korunur. Eşdeğerlik her girdi için gerekçe ister; yalnız teste yakalanmamak eşdeğerlik değildir. Zaman aşımı/çalışma hatası kill sayılmaz. Dışlamasız puan ölçülmeden tahmin rakamı yazılmaz.

Güncel ham [mutasyon özeti](../data/evidence/external-review/mutation-final/reports/mutation-summary.json) ve [kalan mutant incelemesi](../data/evidence/external-review/mutation-final/final-six-survivors.md) ayrı tutulur. İkinci ajan kaynak/metaveri hash'lerini, çıkış kodlarını, AST farklarını ve doğrudan karşılaştırmaları denetledi. Eşdeğer sınıflaması desteklenen API ve standart girdi tipleriyle sınırlıdır; yan etkili özel subclass veya eşzamanlı girdi değişikliği bu sözleşmede yoktur. İnceleme ham mutasyon skorunu değiştirmez.

## Kalite kapısı demosu

[PR #4](https://github.com/nowackk-cp/karkontrol/pull/4) eski kasıtlı stopaj değişikliğinin başarısız CI kaydıdır ve birleştirilmeden kapandı. Sentetik API animasyonu kaldırıldı. [Yeni PR #29](https://github.com/nowackk-cp/karkontrol/pull/29) tek sahiplik/metot sırası değişikliğiyle entegrasyon testlerini kırdı ve birleştirilmeden kapandı. Açık PR'ın BLOCKED API kaydı, kapanış JSON'u, ham CI logu ve gerçek GitHub kontrol ekranı README'de bağlanır. Görüntüde oturum gerektiren merge kutusu yoktur. Kasıtlı değişiklik BUGS'a yeni AI hatası diye eklenmez.

## Yeni pazaryeri ve Shopify hazırlığı

Önce tarihli resmi ücret/sözleşme, sipariş-satır-adet matrahı, vergi niteliği, indirim finansmanı, kur kaynağı, iade/mahsup dönemi ve kuruş dağıtımı seçilir. Sonra en az beş insan hesabı karşılaştırmadan önce commit edilir; mevcut pazaryeri regresyonları, SQL toplamları ve izolasyon aynı kalmalıdır.

Shopify bir pazaryeri kesintisinin birebir kopyası değildir. [Shopify Payments](https://help.shopify.com/en/manual/payments/shopify-payments) ve [üçüncü taraf ücretleri](https://help.shopify.com/en/manual/your-account/manage-billing/billing-charges/types-of-charges/third-party-charges) ödeme sağlayıcısına bağlı ayrı ücretleri açıklar. Erişim 2026-10-04. Hazırlanacak beş insan senaryosu: yerel kart, üçüncü taraf sağlayıcı, indirimli çok satır, kısmi iade, dövizli satış. Hesapları ve ülke/tarife kararları henüz verilmedi; Shopify motor desteği eklenmiş sayılmaz.

## Tarihî kalan mutant incelemesi

### Tarihî 27 kalan mutant incelemesi

Kaynak: 40c5442508633acd8f03ec8715494a7dce04f8b1; mutmut 3.8.0.
Eski skorun sayısal özeti README'dedir.
Tüm mutant kimlikleri ve kaynak fonksiyon hashleri arşiv metadata ile aynı
olacak şekilde saf mutant üreticisiyle yeniden oluşturuldu. Ham diffler
[mutant farkları](../data/evidence/external-review/historical-survivors-diffs.txt), doğrudan karşı örnekler
[karşı örnekler](../data/evidence/external-review/historical-witnesses.json) içindedir. Linux mutant test koşusu tekrarlanmadı.
Bu tarihî skor yeni motorun skoru değildir.

14 hata mesajı farkı, 9 kanıtlı giriş/hesap/çıktı farkı, 3 kaynak akışında eşdeğer
strict değişikliği ve 1 precision eşdeğerlik adayı bulunuyor. Hata mesajı
farkları finans tutarlarını korur; tam kamu hata sözleşmesinde eşdeğer değildir.
Precision adayı için tüm geçerli Decimal girdilerinde eşdeğerlik kanıtı yoktur.
18/9 tahmini bu sayılarla doğrulanmış kabul edilmez.

| Mutant (engine.profit öneki) | Gerçek diff | Sınıf ve kanıt |
|---|---|---|
| LineInput.validate 40 | `name` → `None` | Hata mesajı farkı; float fiyat için alan adı kaybolur |
| LineInput.validate 58 | `name` → `None` | Hata mesajı farkı; KDV 101 için alan adı kaybolur |
| LineInput.validate 67 | para birimi/kur koşulunda `or` → `and` | Kanıtlı boşluk: Amazon'da GBP kabul edilir |
| LineInput.validate 75 | kur `<= 0` → `< 0` | Kanıtlı boşluk: Amazon USD kur 0 kabul edilir |
| LineInput.validate 85 | fiyat `* quantity` → `/ quantity` | Kanıtlı boşluk: 2×600 TL, 600 TL indirim geçerliyken reddedilir |
| allocate 6 | `"weight"` → `None` | Hata mesajı farkı; float ağırlık alan adı |
| allocate 9 | `"weight"` → `"XXweightXX"` | Hata mesajı farkı; float ağırlık alan adı |
| allocate 10 | `"weight"` → `"WEIGHT"` | Hata mesajı farkı; float ağırlık alan adı |
| allocate 12 | `"total"` → `None` | Hata mesajı farkı; negatif toplam alan adı |
| allocate 15 | `"total"` → `"XXtotalXX"` | Hata mesajı farkı; negatif toplam alan adı |
| allocate 16 | `"total"` → `"TOTAL"` | Hata mesajı farkı; negatif toplam alan adı |
| allocate 42 | `exact[i] - base[i]` → `exact[i] + base[i]` | Kanıtlı boşluk: 0,02 TL / [1,2], [0,01;0,01] → [0;0,02] |
| shipping_fee 4 | `"gross"` → `None` | Hata mesajı farkı; negatif brüt alan adı |
| shipping_fee 7 | `"gross"` → `"XXgrossXX"` | Hata mesajı farkı; negatif brüt alan adı |
| shipping_fee 8 | `"gross"` → `"GROSS"` | Hata mesajı farkı; negatif brüt alan adı |
| shipping_fee 10 | `"desi"` → `None` | Hata mesajı farkı; negatif desi alan adı |
| shipping_fee 13 | `"desi"` → `"XXdesiXX"` | Hata mesajı farkı; negatif desi alan adı |
| shipping_fee 14 | `"desi"` → `"DESI"` | Hata mesajı farkı; negatif desi alan adı |
| calculate_order 9 | `prec = 50` → `51` | Eşdeğerlik adayı; bütün geçerli Decimal oranlarda kanıtlanmadı |
| _calculate 14 | ilk brüt ağırlık koşuluna `and False` | Kanıtlı boşluk: 100+200 TL kargo [10;20] → [15;15] |
| _calculate 15 | ilk brüt ağırlık koşuluna `or True` | Kanıtlı boşluk: sıfır brüt, adet [2;1] kargo [20;10] → [15;15] |
| _calculate 53 | iade ağırlığı `/ quantity` → `* quantity` | Kanıtlı boşluk: farklı adetli kısmi iadede kargo [35;25] → [44;16] |
| _calculate 57 | `strict=True` → `None` | Kaynak akışında eşdeğer: original ve lines aynı comprehensions uzunluğunda |
| _calculate 60 | `strict=True` kaldırılır | Kaynak akışında eşdeğer: original ve lines aynı uzunlukta |
| _calculate 61 | `strict=True` → `False` | Kaynak akışında eşdeğer: original ve lines aynı uzunlukta |
| _calculate 102 | maliyet `* exchange_rate` → `/ exchange_rate` | Kanıtlı boşluk: 250 USD ×40 maliyet 10.000,00 → 6,25 TL |
| _calculate 114 | `line_number` → `None` | Kanıtlı boşluk: kamu çıktı satır kimliği kaybolur |

Tarihî kaynağın dışlanan raise satırları için test sonuçları olmadığı için
%83,8 tahmini ölçüm diye yazılamaz. Güncel motor ve genişletilmiş testlerin
yeni Linux ölçümü README'dedir; yeni mutant kimlikleri tarihî üretimden farklıdır.
