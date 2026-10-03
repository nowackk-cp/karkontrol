# Kâr kuralları v1 — karar taslağı

**Durum: onaylanmış kurallar değildir.** Plan gereği alan kuralları ve
altın beklenenler bağımsız insan denetiminden geçmeden `ai-v1` motoru üretilmez.

## Önerilen hesap sözleşmesi

- R-01: Para `Decimal`; `float` girişleri reddedilir. Para birimi v1'de TRY.
- R-02: Para her satır/kalemde kuruşa `ROUND_HALF_UP` ile yuvarlanır.
  Toplam, yuvarlanmış kalemlerin toplamıdır.
- R-03: KDV hariç satış = KDV dahil satır geliri / (1 + satır KDV oranı).
- R-04: Kâr = net satış − net komisyon − net kargo − net hizmet − net maliyet.
- R-05: Hakediş = tahsil edilecek brüt gelir − KDV dahil platform ücretleri − stopaj.
  Ürün alış maliyeti hakedişten düşülmez; satıcının ayrı nakit çıkışıdır.
- R-06: Stopaj net satış üzerinden ayrı kalemdir; kârdan gider olarak düşülmez.
- R-07: Maliyet girdisinin net/brüt niteliği ve KDV'si açık alanlarla verilir.
- R-08: Adet pozitif tamsayı, iade adedi 0…adet aralığında; fiyat/maliyet sonlu
  ve negatif olmayan Decimal olmalıdır.

## Motor öncesi çözülecek kararlar

1. Kargo barem tutarı ve tam eşikte hangi tarifenin seçileceği.
2. Desinin yukarı tamsayıya mı yuvarlanacağı; ağırlıkla karşılaştırma birimi.
3. Çok satırlı kupon/indirimin dağılımı ve kalan kuruşun hangi satıra yazılacağı.
4. Platform finansmanlı kuponun satıcı tahsilatı ve komisyon matrahına etkisi.
5. Tam/kısmi iadede komisyon, hizmet ve gidiş/dönüş kargosu politikası.
6. Satış ve iade tarihlerinin farklı aylarda raporlanma yöntemi.
7. Stopajın iadede ters kayıt ve ödeme dönemi davranışı.
8. Vergi/ücret faturası yuvarlamasının çapraz nakit eşitliğine etkisi.

Mevcut plandaki 600 TL örneği kullanıcı kaynaklıdır; yeni bir insan kontrolü
ve 30 siparişlik bağımsız setin yerine geçmez. Bu dosyada yeni beklenen rakam
hesaplanmadı. Kaynak özeti: [ALAN_BILGISI.md](ALAN_BILGISI.md).
