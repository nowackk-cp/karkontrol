# Demo hesap sözleşmesi

Bu metin AI tarafından hazırlanan uygulama sözleşmesidir. Bağımsız insan kararları için dört açık nokta aşağıda korunur. Tarifeler sentetiktir.

## TRY — demo-v1

1. Para girdileri sonlu, negatif olmayan Decimal ve tam kuruş olmalıdır. Kuruş altı giriş reddedilir. Kur, oran, iade ve desi ara hesapları tam rasyonel değerlerle yapılır; kuruş kararı yalnız ROUND_HALF_UP aşamasındadır. Çıktılar iki ondalıklı Decimal'dır; işaretli sıfır normal sıfıra çevrilir. Rapor yuvarlanmış satırları toplar.
2. Satıcı indirimi bütün satır adedine aittir. İlk brüt = adet × birim fiyat − satıcı indirimi. Platform kuponunu platform karşılar; satıcı tahsilatı ve komisyon matrahı değişmez.
3. İadede kalan brüt = ilk brüt × kalan adet / ilk adet. Net satış = kalan brüt / (1 + satış KDV oranı). Komisyon kalan brüt üzerinden hesaplanır. Geri alınan ürün maliyeti kârdan düşülmez.
4. İlk indirimli sipariş toplamı en fazla 300 TL ise 30 TL, en fazla 600 TL ise 60 TL, üstünde 80 TL net gidiş kargosu alınır. Desi = Σ max(satır desisi, satır ağırlığı) × adet; toplam yukarı tamsayıya yuvarlanır. İlk üç birim dahil, sonraki birim başına 5 TL eklenir. Tam eşik alt tarifededir.
5. Gidiş kargosu sipariş başına bir kez alınır ve iadede geri ödenmez. İade varsa ilk siparişin tarifesiyle bir dönüş kargosu eklenir; iade edilen indirimli brütlerin tam rasyonel ağırlıklarıyla yalnız iade satırlarına dağıtılır. Hizmet sipariş başına 10 TL nettir, ilk brütle dağıtılır ve iade oranında geri ödenir.
6. En büyük kalan yöntemi tam rasyonel/tamsayı kuruşla uygulanır. Eşit kalanlarda düşük satır numarası kazanır. 10 TL ve 100:10:10 ağırlıklar → 8,34 / 0,83 / 0,83 TL. Sıfır tutarda adet, sıfır tutarlı iadede iade adedi ağırlıktır.
7. Ücretlerin KDV'si %20; her komisyon/kargo/hizmet kalemi satırda ayrı yuvarlanır. Maliyet KDV'si girdidir. Stopaj kalan KDV hariç satışın %1'idir; hakedişi azaltır, kâr gideri sayılmaz.
8. Kâr = net satış − net komisyon − net kargo − net hizmet − net maliyet. Hakediş = kalan brüt − KDV dahil platform ücretleri − stopaj. Satış KDV'si = brüt − net satış. Net ödenecek KDV = satış KDV'si − ücret KDV'si − maliyet KDV'si. Nakit eşitliği bir aritmetik özdeşliktir; bağımsız doğrulama sayılmaz.
9. İade satış tarihindeki kaydı düzeltir; stopaj aynı dönemde ters çevrilir. Ayrı iade/mahsup dönemi modellenmez.
10. Maliyet girdisi net alış bedelidir. Tam iadede kargo nedeniyle kâr ve hakediş negatif olabilir.

## Varsayımlar ve insan kararı gereken noktalar

| Alan | Şu an uygulanan varsayım |
|---|---|
| Komisyon | İndirimli KDV dahil brüt matrah |
| Barem | Projeye ait sentetik eşik ve tarife |
| Desi | Ağırlıkla karşılaştırılan satır değeri; sipariş toplamı sonra yuvarlanır |
| Dönüş kargosu | İlk sipariş tutarının tam tarifesi; yalnız iade tutarı tarifesi seçilmez |
| Hizmet | Sipariş ücreti; iade oranında geri ödenir |
| Kupon ve barem | Platform kuponu baremi değiştirmez |
| Stopaj iadesi | Satış dönemine geri düzeltme |
| Ücret KDV yuvarlaması | Her satır/ücret kaleminde ayrı |
| Amazon lojistiği/vergisi | Sentetik sabit ücret ve TRY demo vergileri |
| Döviz | Dosyada tarihli sabit kur; canlı kaynak yok |

**B1 insan kararı bekler:** dönüş kargosunun ilk siparişe mi iade kısmına mı bağlı olması; ücret KDV'sinin satır mı fatura mı düzeyinde yuvarlanması; kuponun barem matrahı; hizmet bedelinin iade edilmesi. Burada mevcut davranış belgelenmiştir; motor çıktısına bakılarak bağımsız karar verilmiş sayılmaz. İnsan gerekçelerini hesaplardan önce ayrı commit ile kaydetmelidir.

## Amazon — amazon-demo-v2

TRY, USD ve EUR kabul edilir. Yabancı para için bir birimin TRY karşılığı olan pozitif sabit kur gerekir. Fiyat, indirim, kupon ve maliyet sipariş para birimindedir. İndirim sonrası brüt ve kalan net maliyet kurla çevrilir, sonra kuruşa yuvarlanır. Komisyon oranı dosyadan veya mağaza anlık varsayılanından alınır. Sipariş başına 80 TL net lojistik ve sıfır hizmet ücreti vardır. Diğer iade/vergi kuralları TRY demo ile aynıdır.

USD/EUR kullanmak bu işlemi ihracat muhasebesine dönüştürmez. İhracat KDV istisnası teslimin şartlarına bağlıdır; sırf dövizle satışa Türk KDV/stopajını uygulamak ülke ve sözleşme incelemesi olmadan gerçek vergilemeyi temsil etmez. Kaynaklar [alan incelemesinde](ALAN_BILGISI.md).

## Plandaki 600 TL örneği

600 TL brüt satış, %20 satış KDV'si, %20 brüt komisyon, 250 TL net maliyet; 60 TL net kargo, 10 TL net hizmet: net satış 500 TL, komisyon 120 TL, ücret KDV'si 38 TL, stopaj 5 TL, kâr 60 TL ve hakediş 367 TL. Bu önceden verilmiş örnek yeni insan altın setinin yerine geçmez.
