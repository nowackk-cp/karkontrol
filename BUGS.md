# Kanıtlanmış hatalar

Kasıtlı CI demosu veya mutasyon, yeni uygulama hatası sayılmaz. Aşağıdaki bulgular gerçek başarısız test/ham model yanıtına bağlıdır. “Motorda hata yok” iddiası dış incelemede ENG-001 ile geçersiz kaldı.

## APP-001 — yabancı mağazaya POST durum kodu

Düşük önem. Sahiplik kontrolünden önce HTTP metodu denetlendiği için iki read-only mağaza rotasına yabancı POST 404 yerine 405 döndü. `test_foreign_store_routes_return_404` kaynak düzeltmesiyle geçti; beklenti gevşetilmedi. Veri sızıntısı veya TL farkı yok. **Yerel test turunda yakalandı, hatalı hâli commit edilmedi; issue sonradan belgelendi.** [#7](https://github.com/nowackk-cp/karkontrol/issues/7), fix 766a433, PR #2.

## APP-002 — uzun adet kontrolsüz istisna

Orta önem. 5000 basamaklı adet Python int dönüşümünde ValueError üretti. Beklenen satır numaralı ImportValidationError ve sıfır kayıttı. Basamak ve 32-bit değer sınırı dönüşümden önce eklendi. TL farkı yok. **Yerel test turunda yakalandı, hatalı hâli commit edilmedi; issue sonradan belgelendi.** [#8](https://github.com/nowackk-cp/karkontrol/issues/8), fix ab1dc62, PR #2.

## APP-003 — yanlış dönem zararı gizliyor

**Yüksek önem.** İlk Qwen koşusunda E-01/E-02/E-10 için Eylül yerine Kasım seçildi. Beklenen SQL net kâr −60,00 TL iken kullanıcı “veri yok” cevabı aldı; kayıtlı rapor doğruydu. Tarih kullanıcı sorusundan JSON şemasına bağlandı, geçerli fakat yanlış model ayı reddedildi. Kaynak [llm-first.json](data/evidence/llm-first.json); regresyonlar `test_turkish_month_is_constrained_before_model` ve `test_valid_but_wrong_month_is_rejected`. [#9](https://github.com/nowackk-cp/karkontrol/issues/9), fix 1ac5699, PR #6; issue geçmiş düzeltmeden sonra açıldı.

## APP-004 — yanlış ürün/iade aracı

Yüksek önem. İlk model koşusunda E-16 ve E-28 ürün niyeti summary'ye, E-23 iade kuralı yanlış konuya gitti. v2 ürün/kural tanımlarıyla düzeltildi; aynı sette yeniden ölçüldü. Beklenen kaynak soru sözleşmesi ve SQL'dir; TL hesap farkı ölçülmedi. [#21](https://github.com/nowackk-cp/karkontrol/issues/21) bu tarihî bulguyu sonradan belgeler; ilk başarısız ham rapor korunur.

## ENG-001 — tam eşit kalan sırası

Orta önem; **dış inceleme ile bulundu**. 10 TL'nin 100:10:10 dağılımı eski kodda 8,33/0,84/0,83; kural §6'ya göre 8,34/0,83/0,83 olmalıydı. Sipariş toplamı değişmez; satır ücreti 0,01 TL yanlış yere yazılır. İade ağırlıklarının önceden Decimal bölünmesi de tam eşitliği bozuyordu. Fraction/divmod ve `(-kalan, index)` sırası düzeltildi. Ayrıca kuruş altı para reddi ve işaretli sıfır normalizasyonu eklendi. `test_allocate_equal_remainders_prefer_lower_line` ve dönüş dağıtımı karşı örneği. [#11](https://github.com/nowackk-cp/karkontrol/issues/11), issue kaynak düzeltmesinden önce açıldı.

## ENG-002 — yüksek hassasiyette erken kur yuvarlaması

Bağımsız mutasyon incelemesinde bulundu. Kabul edilen 51 basamaklı USD kuru `1.005` eşiğinin hemen altındayken precision=50 ara hesabı brütü 1,00 yerine 1,01 TRY'ye yuvarladı. Bu örnekte brüt/hakediş farkı 0,01 TRY. [13 mutant incelemesi ve tam rasyonel karşı örnek](data/evidence/external-review/mutation-first/current-survivors-review.md) korunur. [#27](https://github.com/nowackk-cp/karkontrol/issues/27) düzeltmeden önce açıldı. Kur/oran/iade/desi ara hesapları Fraction ve tamsayı kuruşa taşındı; 51/101 basamak, yarım kuruş, desi ve context regresyonları önce başarısız, sonra başarılı oldu. İthalatçı kur basamağını sınırlar; bu bulgu motorun kabul ettiği daha geniş Decimal sözleşmesine aittir.

## IMP-001 — Excel yüzde biçimli oran

Yüksek önem; **dış inceleme ile bulundu**. Hücrenin %20 görünümündeki 0,20 ham değeri oran olarak kabul ediliyordu. Yüzde biçimi artık açıklayıcı hata ile reddedilir; KDV beyaz listesi 0/1/10/20, komisyon en az 1. Yanlış defter üretimi kayıt öncesinde durur; hedef regresyon TL farkını ayrıca hesaplamadı. `test_xlsx_percent_formatted_rates_are_rejected` ve oran sınır testleri. [#12](https://github.com/nowackk-cp/karkontrol/issues/12), issue önce açıldı.

## IMP-002 — aktarımın geri alınamaması

Yüksek önem; **dış inceleme ile bulundu**. Parti kaydı vardı fakat yeni satırları kaynağına bağlayan FK ve geri alma yoktu. Sahiplik kontrollü POST, atomik silme/yeniden hesaplama eklendi; UI iadesi kaynak iadesinden ayrıldı. Yanlış sipariş kalmasının TL etkisi girdiye bağlı; tek tutar ölçülmedi. `test_wrong_import_can_be_undone_atomically`. [#14](https://github.com/nowackk-cp/karkontrol/issues/14), issue önce açıldı.

## IMP-003 — kısa CSV satırı

Orta önem; **dış inceleme ile bulundu**. Eksik sütunlar boş değer gibi dolduruluyordu. Başlıkla eşit genişlik ve sıfır kısmi kayıt regresyonu eklendi. `test_csv_short_row_is_rejected`. Ayrı TL farkı yok. [#13](https://github.com/nowackk-cp/karkontrol/issues/13), issue önce açıldı.

## REP-001/002/003 — arama ve rapor bütünlüğü

**Dış inceleme ile bulundu**. SQLite Türkçe casefold yapmadığından İ/I aramaları kaçırıyordu; normalize search_text ve backfill eklendi ([#15](https://github.com/nowackk-cp/karkontrol/issues/15)). Eksik defter CSV'de 500 üretiyordu; açık eksiklik uyarısı ve 409 eklendi ([#16](https://github.com/nowackk-cp/karkontrol/issues/16)). Amazon satırı yanlış demo sürümü ve CSV değişken ondalıkla sunuluyordu; pazaryerine göre sürüm ve sabit iki ondalık/BOM düzeltildi ([#17](https://github.com/nowackk-cp/karkontrol/issues/17)). Ayrı TL farkı ölçülmedi; hedef rapor/import regresyonları ve CSV/SQL tutarlılığı doğrular. Üç issue düzeltmelerden önce açıldı.

## CFG-001/002/003 — üretim, dotenv ve HTTP sınırları

**Dış inceleme ile bulundu**. Sunucu varsayılanı production'a çevrildi; gerekli ortam eksikse kapanır. dotenv ayarlar öncesine alındı. Proxy/CSRF ortam doğrulaması, toplam 5 MiB streaming upload ve cache giriş sınırı eklendi. Multipart ilk dosya küçük/sonraki büyükken importer çağrısını da durduran regresyon var. `test_runtime_settings` ve `test_http_security`; TL farkı ölçülmedi. [#18](https://github.com/nowackk-cp/karkontrol/issues/18), issue önce açıldı.

## AI-001 — tarih ve kelime sınırı

Yüksek önem; **dış inceleme ile bulundu**. 2000 TL yılı 2000 sanılıyordu; “aralıkta” Aralık, “Kargo” kâr niyetiyle eşleşiyordu. Açık/göreli tarih, ASCII Türkçe ve çok ay netleştirme eklendi; dönem yanıta yazılır. Çapraz inceleme “bu ayakkabı”, 2000,00 TL ve adet bağlamını da düzeltti. Yanlış dönem raporu saklayabiliyordu; ayrı TL farkı ölçülmedi. `test_date_routing`; [#19](https://github.com/nowackk-cp/karkontrol/issues/19), issue önce açıldı.

## JDG-001 — tekrarlar kalibrasyon örneği sayılıyor

**Dış inceleme ile bulundu**. Eski hakem hazırlığı farklı ID'lerle aynı cevapları tekrarlıyordu. Benzersiz cevap SHA, kör insan dosyası, ayrı model koşulu ve Cohen κ eklendi; boş insan verisi kabul edilmez. Finans TL etkisi yok; ölçüm güvenilirliği sorunu. [#20](https://github.com/nowackk-cp/karkontrol/issues/20), issue önce açıldı.

## CI-001 — Playwright olmadan collection

Orta önem; **dış inceleme ile bulundu**. Opsiyonel tarayıcı importu ana pytest toplanmasını kırıyordu. importorskip ve ayrı dev-only ortam doğrulamasıyla düzeltildi; TL etkisi yok. [#22](https://github.com/nowackk-cp/karkontrol/issues/22), küçük conftest düzeltmesinden sonra geriye dönük açıldı.

## QA-001 / EVAL-001 — çağrı atfı ve güvenlik fixture'ı

Bağımsız ajan incelemesinde bulundu. Başarısız model çağrısı `selection` üretmediği için doğruluk paydasından düşebiliyordu; Haiku yanıtı local etiketi taşıyordu. Foreign sentinel fixture ile eşleşmiyor, talimat SKU top sıralamada görünmüyordu. Bütün başlayan çağrılar doğru backend ile sayılır; geçersiz tool yanıtları ve token sınırları güvenli reddedilir. Fixture marker bütün yanıt nesnesinde, talimat SKU da sıralama çıktısında kontrol edilir. [#23](https://github.com/nowackk-cp/karkontrol/issues/23) ve aynı ölçüm kapsamlı [#24](https://github.com/nowackk-cp/karkontrol/issues/24), source düzeltmesinden önce açıldı. Ayrı finans TL farkı yok; bu ölçüm güvenilirliği sorunudur.

## APP-005 — v3 tarihsiz soru ve fiyat niyeti

Yeni gerçek Qwen geliştirme koşusunda bulundu. E-35 genel tavsiye sorusu yanlış netleştirildi; E-43 tarihsiz kâr özeti netleştirmeye, E-50 kargo fiyatı isteği kural açıklamasına yönlendirildi. Ayrı finans TL farkı ölçülmedi. [İlk ham yanıt](data/evidence/external-review/llm-v3-first/eval.json) saklandı; [#26](https://github.com/nowackk-cp/karkontrol/issues/26) düzeltmeden önce açıldı. v3 tarih yokluğu, kural/fiyat ve genel soru tanımları ayrıldı. Geliştirme vakaları ve eşikler değiştirilmedi; v2 prompt ve ilk sentetik set korunur.

## APP-006 — desteklenen KDV kuralının reddi

Gerçek Qwen v3 yönerge ayarı sonrasında E-24 “KDV nasıl hesaplanır?” sorusu unsupported'a döndü. [Üçüncü ham koşu](data/evidence/external-review/llm-v3-third/eval.json) ve [#28](https://github.com/nowackk-cp/karkontrol/issues/28) kaynak düzeltmesinden önce kaydedildi. Finans kuralının hesaplama yöntemini açıklamak ile serbest para hesabı yapmak yönergede ayrıldı. Beklenen vaka, v2 ve kapı eşiği değiştirilmedi; ayrı TL farkı ölçülmedi.

## JDG-002 — hakem çağrılarında zaman aşımı ve kaybolan sonuçlar

Ayrı Qwen3-0.6B hakeminin [ilk Linux koşusu](https://github.com/nowackk-cp/karkontrol/actions/runs/37251524081) bütün çağrılarda 45 saniye sınırına takıldı; 20 dakika sonunda job iptal edildi. Döngü yalnız sonunda JSON yazdığı için tamamlanan denemeler de sonuç dosyasına girmedi. [İlk ham log ve protokol](data/evidence/external-review/judge-first/protocol.json) korunur; [#31](https://github.com/nowackk-cp/karkontrol/issues/31) kaynak düzeltmesinden önce açıldı. Finans TL farkı yok; hakem araçlarının çalışabilirliği ve kanıt korunması sorunu. [Sabit runtime'ın resmi grammar rehberi](https://github.com/ggml-org/llama.cpp/blob/b11382/grammars/README.md#efficient-optional-repetitions) bazı sınırlı tekrarların yavaş sampling üretebildiğini açıklar. Bu koşunun sebebi aynı prompt/model ile kontrollü karşılaştırılacak; uygulama yanıt uzunluğu sınırı ve insan kalibrasyonu koşulları korunur.

Fix commit gövdeleri issue kapanışlarını taşır. Kod/ölçüm değişiklikleri kendi kaynak SHA'sıyla review edilir; main geçmişi, ilk başarısız raporlar ve sürüm etiketleri değiştirilmez.
