# Amazon demo ve sabit döviz kuru

Amazon demo sentetik bir modüldür; güncel Amazon ücret tablosu değildir.
TRY, USD ve EUR desteklenir. Yabancı para dosyasında pozitif `doviz_kuru`
zorunludur: bir birim yabancı para kaç TRY eder. Kur sipariş satırına sabit
kaydedilir; canlı kur servisi ve kur değişiminde geçmişe dönük yeniden değerleme yoktur.

Fiyat, indirim, kupon ve net maliyet sipariş para birimindedir. İndirim sonrası
ilk brüt gelir ve kalan maliyet kurla çevrilip kuruşa yuvarlanır. Diğer tüm
hesaplar ve raporlar TRY üzerinden yürür. Komisyon dosyadan, yoksa mağaza
varsayılanından gelir. Sipariş başına 80 TL net lojistik ve sıfır hizmet ücreti
varsayılır. İade, vergi ve stopaj sözleşmesi demo-v1 ile aynıdır. Bu varsayımlar
ABD/AB gerçek vergilemesi veya Amazon FBA tarifesi iddiası taşımaz.

Yeni pazaryeri eklenmesi mevcut demo TRY davranışını değiştirmemelidir.
