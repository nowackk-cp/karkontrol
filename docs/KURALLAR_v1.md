# KârKontrol demo hesap sözleşmesi v1

Bu sözleşme AI tarafından hazırlanmış uygulama politikasıdır; insan denetimli
altın veri değildir. Gerçek pazaryeri sözleşmesi veya vergi danışmanlığı yerine
geçmez. Kullanıcının kesintisiz tamamlama talimatıyla geliştirme bu açık
varsayımlar üzerinden sürdürülür. İnsan doğrulaması ayrı kabul koşuludur.

1. Girdiler sonlu, negatif olmayan Decimal; adet pozitif tamsayıdır. Para
   ROUND_HALF_UP ile kuruşa yuvarlanır. Raporlar yuvarlanmış satırları toplar.
2. Satıcı indirimi satırın tüm adedi içindir. Satıcı tahsilatı brüt satıştan
   satıcı indirimi düşülerek bulunur. Platform kuponunu platform karşılar:
   müşteri daha az öder, satıcının tahsilatı ve komisyon matrahı değişmez.
3. Kısmi iadede kalan tahsilat = indirimli brüt × kalan adet / ilk adet,
   kuruşa yuvarlanır. Net satış = kalan tahsilat / (1 + satış KDV oranı).
   Komisyon kalan tahsilat üzerinden hesaplanır. İade edilen stok geri alınır;
   maliyeti kârdan düşülmez. Kupon ve indirim iade oranıyla çözülür.
4. Demo TRY kargo: indirim sonrası ilk sipariş tutarı <=300 TL ise 30 TL,
   <=600 TL ise 60 TL, üstünde 80 TL net. Sipariş desisi, satırdaki desi ile
   ağırlığın büyüğünün adetle çarpımının toplamını yukarı tamsayıya yuvarlar.
   İlk üç birim dahil, sonraki her birim 5 TL net eklenir. Tam eşik alt tarifededir.
5. Kargo sipariş başına bir kez alınır. Gidiş kargosu iadede geri ödenmez.
   Herhangi bir iade varsa bir dönüş kargosu daha alınır; yalnız iade edilen
   satırlara iade edilen brüt tutar ağırlığıyla dağıtılır. Hizmet sipariş başına
   10 TL net; satırlara ilk brütle dağıtılır ve iade oranında geri ödenir.
6. Sipariş ücretleri kuruş cinsinden en büyük kalan yöntemiyle dağıtılır.
   Eşit kalanlarda düşük satır numarası önce gelir. Sıfır tutarlı siparişte
   ağırlık adet olur. Sıfır tutarlı iadede ağırlık iade adedidir.
7. Komisyon/kargo/hizmet fatura KDV'si %20. Maliyet KDV'si ayrı girdi, varsayılan
   %20. Stopaj kalan KDV hariç satışın %1'i; kâr gideri değildir, hakedişi azaltır.
8. Kâr = net satış − net komisyon − net gidiş/dönüş kargo − net hizmet − net maliyet.
   Hakediş = kalan brüt − KDV dahil platform ücretleri − stopaj.
   Net ödenecek KDV = satış KDV'si − ücret KDV'si − maliyet KDV'si.
   Çapraz kontrol: hakediş − brüt maliyet − net ödenecek KDV + stopaj = kâr.
9. İade aynı satış tarihine düzeltme olarak yansır. Ayrı iade dönemi muhasebesi
   bu demo kapsamına girmez. İade edilen kısmın stopajı aynı dönemde ters çevrilir.
10. Satır maliyeti her zaman KDV hariçtir. Tam iade kârı gidiş+dönüş kargosundan
    dolayı negatif olabilir. Tahsilat veya hakediş negatifliği hata değildir.

Kaynak: kullanıcının plandaki 600 TL örneği ve [resmî kaynak özeti](ALAN_BILGISI.md).
Tarifeler sentetiktir. Motorun kendi çıktısı hiçbir zaman altın beklenti sayılmaz.
