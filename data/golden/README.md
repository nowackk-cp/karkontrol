# Bağımsız altın veri

Bu klasörde henüz onaylı altın veri bulunmuyor. Altın setin yokluğu gizlenmez;
boş veriyle başarılı mutabakat sonucu üretilmez.

Hazırlık: [senaryo matrisi](../../docs/ALTIN_VERI_HAZIRLIK.md).
Uygulanan demo sözleşmesi: [kurallar](../../docs/KURALLAR_v1.md).
İnsan onayı yoktur. [40 sentetik girdi](../draft/inputs.json) ve
[beklenenleri boş inceleme şablonu](../draft/manual_review.csv) hazırdır.

Kabul öncesi gerekli kanıtlar:

1. Kesin kural sürümü ve kullanılan tarihli tarifeler.
2. İnsan tarafından yazılan hesap adımları; motordan alınmayan beklenen değerler.
3. En az beş sipariş için ikinci kontrol ve ertesi gün tüm setin gözden geçirilmesi.
4. Onaylı `altin_set.xlsx` ve dışa aktarılmış `altin_set.csv`.
5. Veri/provenans ve doğrulama commit'i. Tarihî planın “motordan önce insan veri
   commit'i” koşulu bu demo geliştirmesinde sağlanmadı; geçmiş değiştirilemez.

Dosyalar yalnızca sentetik siparişler içerir. Beklenen sütunlar:
`kdv_haric_satis`, `komisyon`, `kargo`, `hizmet_bedeli`, `stopaj`, `net_kar`, `hakedis`.
