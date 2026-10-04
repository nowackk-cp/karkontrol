# Gerçek tarifeler ile demo politikası karşılaştırması

Erişim: 2026-10-04. Kamuya açık resmî belgelerin AI incelemesi.
Gerçek satıcı hesabı/sözleşmesi ve insan finans kabulü sağlanmadı.

[Amazon Türkiye ücretlendirme](https://satis.amazon.com.tr/ucretlendirme)
sayfasında komisyonun toplam alıcı bedelinden alındığı açıklanıyor; alıcıya
yansıtılan kargo da matraha giriyor. Örnek kategori oranları: bilgisayar %7,
kitap %10,2, giyim %15,5. Komisyon faturasına KDV ekleniyor. İadede işlem
ücreti kesilebildiği belirtiliyor; tam kesinti politikası satıcı paneline bağlı.

[16 Nisan 2026 FBA ücret çizelgesi](https://m.media-amazon.com/images/G/41/SOA/PricingFiles/FBA_Domestic_Rate_Card_202604_Final.pdf)
boyut/ağırlığa göre **ürün başına** net lojistik ücretleri içeriyor. Küçük zarf
53,80 TL, standart paket 0,25 kg'a kadar 59,15 TL. PDF'deki Mayıs–Temmuz %50
kampanyası erişim tarihinde sona ermiştir. PDF, satış fiyatı 300 TL'den az
olduğunda 25 TL ücret söylüyor; tam 300 TL için metin açık sınır belirtmiyor.
Bu belirsizlik üretim politikasına varsayımla dönüştürülmedi.

| Alan | Mevcut demo | Gerçek kabul için gereken |
|---|---|---|
| Komisyon | Satırda kullanıcı oranı, indirimli brüt matrah | Kategori, tarih, kampanya ve alıcı kargo bedeli |
| FBA lojistik | Sipariş başına sabit 80 TRY | Ürün boyutları, ağırlık, adet ve tarihli ücret bandı |
| İade | Komisyon tam geri, dönüş kargosu | Satıcı hesabındaki iade işlem ücreti/politikası |
| USD/EUR | Siparişte sabit TRY kur | İlgili ülke tarifesi, vergi ve fatura kur politikası |
| Kabul | Teknik testler | Tarihli sözleşme + insan mutabakatı |

Bu karşılaştırma, gerçek tarifenin bulunduğunu ve demo ile farklarının
tanımlandığını kanıtlar. Mevcut motoru gerçek Amazon/FBA uyumlu ilan etmek
için yeterli değildir. Resmî tarifelerin yayın tarihi ile erişim tarihi ayrı
tutuldu; bitmiş promosyonlar güncel oran gibi kullanılmadı.
