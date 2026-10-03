# Altın veri hazırlığı

Durum: **senaryo taslağı; beklenen sayısal sonuç içermiyor.**

Motorun altın veriden önce üretilmemesi ve AI tarafından hesaplanan beklenenlerin
elle doğrulanmış diye sunulmaması ana planın 2. altın kuralıdır.

| Sipariş | Senaryo | İlgili kural |
|---|---|---|
| SIP-01 | %1 KDV, tek ürün | R-03, R-04 |
| SIP-02 | %10 KDV, tek ürün | R-03, R-04 |
| SIP-03 | %20 KDV, tek ürün | R-03, R-04 |
| SIP-04 | Düşük komisyon kategorisi | R-04, R-05 |
| SIP-05 | Yüksek komisyon kategorisi | R-04, R-05 |
| SIP-06 | Aynı üründen çok adet | R-02, R-08 |
| SIP-07 | Farklı KDV'li çok satır | R-02, R-03 |
| SIP-08 | Çok satırda dağıtılan indirim | Karar 3 |
| SIP-09 | Barem eksi 0,01 TL | Karar 1 |
| SIP-10 | Tam barem eşiği | Karar 1 |
| SIP-11 | Barem artı 0,01 TL | Karar 1 |
| SIP-12 | Desi sınırı | Karar 2 |
| SIP-13 | Ağırlık hacimden yüksek | Karar 2 |
| SIP-14 | Satıcı finansmanlı indirim | Karar 3 |
| SIP-15 | Pazaryeri finansmanlı kupon | Karar 4 |
| SIP-16 | İndirim ve kupon birlikte | Karar 3, 4 |
| SIP-17 | Yüksek indirim | R-08, Karar 3 |
| SIP-18 | Tam iade | Karar 5, 7 |
| SIP-19 | Kısmi iade | Karar 5, 7 |
| SIP-20 | Dönüş kargolu iade | Karar 5 |
| SIP-21 | Kargoya verilmeden iptal | Karar 5 |
| SIP-22 | İndirimli sipariş iadesi | Karar 3, 5 |
| SIP-23 | Yarım kuruş komisyon | R-02 |
| SIP-24 | Yarım kuruş vergi | R-02, R-03 |
| SIP-25 | 149,99 TL ve %10 KDV | R-02, R-03 |
| SIP-26 | Satır ve toplam yuvarlama farkı | R-02 |
| SIP-27 | Zarar eden sipariş | R-04, R-05 |
| SIP-28 | Maliyeti sıfır ürün | R-07, R-08 |
| SIP-29 | 0,01 TL tutar | R-01, R-02 |
| SIP-30 | 250.000 TL tutar | R-01, R-04 |

Kapsama matrisi bu aşamada taslaktır. Kesin kuralların her birinin en az üç
senaryoda karşılandığı nihai veriyle tekrar kontrol edilecek.

## Kabul kanıtı

Kurallar netleştirilir; satırlar ve hesap adımları motor çıktısı kullanılmadan
insan tarafından yazılır. En az beş sipariş ikinci yöntemle kontrol edilir.
Ertesi gün ikinci gözden geçirme ve tarihli kontrol kaydı gerekir. Onaylı CSV
motor commit'inden önce Git'e kaydedilir. Bu aşamada boş dosya başarılı
mutabakat testi diye çalıştırılmaz.
