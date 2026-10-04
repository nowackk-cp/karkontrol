# Sipariş dosyası sözleşmesi

Durum: uygulanmış girdi sözleşmesi, 2026-10-04. Kâr motoru kuralları veya
bağımsız altın veri değildir; yalnızca sentetik veriyle kullanılır.

## Biçim

CSV UTF-8 veya UTF-8 BOM, ayraç virgül/noktalı virgül. XLSX tek çalışma
sayfası; ilk satır sütun adları. Boş satırlar atlanır. Formüller ve bilinmeyen/
tekrarlanan sütunlar reddedilir. Başlıksız/boş dosyada kayıt oluşturulmaz.

| Zorunlu sütun | Anlam |
|---|---|
| siparis_no | En fazla 64 karakterlik sentetik numara |
| satir_no | Sipariş içinde pozitif tamsayı satır kimliği |
| tarih | YYYY-AA-GG veya GG.AA.YYYY; Excel tarih hücresi de desteklenir |
| urun_adi | En fazla 200 karakter |
| urun_kodu | En fazla 64 karakter |
| adet | Pozitif tamsayı |
| birim_fiyat_kdv_dahil | Brüt birim satış fiyatı |
| kdv_orani | Yüzde girdisi; 20 yazılır, 0.20 yazılmaz |
| birim_maliyet_kdv_haric | Net birim alış maliyeti |

İsteğe bağlı: `komisyon_orani`, `satici_indirimi`, `pazaryeri_kuponu`,
`iade_adet`, `para_birimi`, `desi`, `agirlik_kg`, `maliyet_kdv_orani`, `doviz_kuru`.
Komisyon boşsa aktarım anındaki mağaza oranı
satıra kaydedilir. İndirim/kupon/iade boşsa 0; para birimi boşsa TRY kabul edilir.
İndirimler satır toplamıdır. Desi/ağırlık birim ürüne aittir, boşsa 0;
maliyet KDV'si boşsa %20, TRY kuru 1'dir. Kayıtlar aynı transaction içinde
[demo finans sözleşmesine](KURALLAR_v1.md) göre hesaplanır.

## Doğrulama

- Tutarlar negatif olamaz; en fazla 10 tam ve 2 ondalık basamak.
- Ondalık ayırıcı `.` veya `,`; binlik ayraç ve bilimsel gösterim kullanılmaz.
- Excel'in sayısal hücreleri metin adaptöründen Decimal'e çevrilir. Dosya
  kütüphanesinin sayılarıyla finansal aritmetik yapılmaz. Sonuç model alanları Decimal'dir.
- Yüzdeler 0…100; iadeler 0…sipariş adedi; satır/adet/iade tamsayıları
  en fazla 10 basamak ve 2147483647 sınırında.
- İndirim + kupon, birim brüt fiyat × adet tutarını aşamaz.
- Demo TRY mağazasında yalnız TRY. Amazon demo ayrıca USD/EUR destekler;
  yabancı parada pozitif sabit `doviz_kuru` zorunludur, en fazla altı ondalık
  basamak. Bir siparişin tüm satırları aynı para birimi/kur kullanır.
- Tutar ve indirim/maliyet kendi para birimindedir; rapor TRY kuruşlarıyla çalışır.
  Finans satırı en fazla 9.000.000.000.000.000 mutlak kuruş; mağaza toplam
  mutlak tutarı 9.000.000.000.000.000.000 kuruş sınırını aşamaz.
- Ücretsiz hesap bütün mağazalarda toplam100 satır; Demo Pro bu kotayı kaldırır.
- Dosya ≤ 5 MB, açılmış XLSX toplamı ≤ 25 MB ve en fazla 200 ZIP girdisi,
  başlık dışında ≤ 5000 veri satırı. Sınırı aşan dosyada kısmi kayıt yok.

## Atomiklik ve tekrar aktarım

Bütün satırlar önce doğrulanır; kayıtlar
[Django atomic transaction](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
içinde yazılır. Aynı dosya özeti aynı mağazada tekrar kayda yol açmaz. Farklı
dosyada aynı mağaza/sipariş/satır kimliği ve aynı değerler atlanır; çelişen
değer tüm yeni kayıtları ve import partisini geri alır. Farklı mağazalarda
aynı sentetik sipariş numarası kullanılabilir.

Tekrar aktarım güncelleme değildir. İade değişikliği iade ekranından yapılır.
Aynı dosyayı tekrar yüklemek mevcut iade bilgisini sıfırlamaz. Güncel veriyle
çelişen farklı dosya ayrıca reddedilir. Liste 50 satırlık sayfalarla gösterilir;
filtreler mağaza izolasyonundan sonra uygulanır.

## Finans sonuçları

Yeni satır eklenince siparişin bütün satırları yeniden hesaplanır; kargo bir
sipariş ücreti olarak dağıtılır. İade değişimi aynı satış tarihindeki hesapları
düzeltir. Kaynak kayıt/hesap/kota çatışmasının tümü atomiktir. Çok satırlı
siparişi farklı dosyalarda aktarmak mümkündür; son aktarımın dağıtımı günceldir.
`rebuild_reports` mevcut kayıtları demo-v1 ile atomik olarak yeniden üretir.
Kur ve komisyon satır snapshot'ıdır; dış servis veya bugünkü kurla değişmez.

XLSX için XML koruması, [openpyxl'in resmî güvenlik belgesinde](https://openpyxl.readthedocs.io/en/stable/)
belirtilen defusedxml paketiyle etkinleştirilmiştir. Boyut limitleri ayrıca uygulanır.
