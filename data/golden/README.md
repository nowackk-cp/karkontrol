# Bağımsız altın veri

Bu klasörde henüz onaylı altın veri bulunmuyor. Altın setin yokluğu gizlenmez;
boş veriyle başarılı mutabakat sonucu üretilmez.

Hazırlık: [senaryo matrisi](../../docs/ALTIN_VERI_HAZIRLIK.md).
Nihai kurallar henüz taslak: [karar taslağı](../../docs/KURALLAR_v1_TASLAK.md).

Kabul öncesi gerekli kanıtlar:

1. Kesin kural sürümü ve kullanılan tarihli tarifeler.
2. İnsan tarafından yazılan hesap adımları; motordan alınmayan beklenen değerler.
3. En az beş sipariş için ikinci kontrol ve ertesi gün tüm setin gözden geçirilmesi.
4. Onaylı `altin_set.xlsx` ve dışa aktarılmış `altin_set.csv`.
5. Motorun ilk commit'inden önce veri commit'i ve doğrulama kaydı.

Dosyalar yalnızca sentetik siparişler içerir. Beklenen sütunlar:
`kdv_haric_satis`, `komisyon`, `kargo`, `hizmet_bedeli`, `stopaj`, `net_kar`, `hakedis`.
