# Yeni pazaryeri kabul kontrolü

- Oranları tarihli resmî sözleşmeden alın; sentetik tarife ise açıkça belirtin.
- Ücretin sipariş/satır/adet tabanını, KDV dahil/hariç niteliğini belirleyin.
- İndirim/kupon finansmanını, komisyon matrahını ve kalan kuruş politikasını yazın.
- Para birimi/kur kaynağı, hassasiyet ve geçmiş sipariş kurunun değişmezliğini doğrulayın.
- Kısmi/tam iade, stok geri kazanımı, dönüş kargosu ve ücret geri ödemesini kontrol edin.
- KDV, stopaj, dönemsellik, net kâr/hakediş/nakit çapraz eşitliğini doğrulayın.
- Geçersiz negatif/NaN/Infinity/float/rate/adet girdisini test edin.
- Eşik ±1 kuruş, desi sınırı, çok satırlı dağıtım ve yüksek tutar sınırlarını test edin.
- İnsan doğrulamalı beklenenleri kaynağıyla alın; motor çıktısını beklenen yapmayın.
- Önce/sonra mevcut pazaryeri regresyonunu, SQL toplamlarını ve tenant izolasyonunu çalıştırın.
- Aktarım, rapor, iade E2E'si; asistan sayısal/güvenlik eval'i; dal kapsamı ve
  mutasyon sonucunu kanıtlarıyla değerlendirin. Başarı olmayan metrik için rozet eklemeyin.
