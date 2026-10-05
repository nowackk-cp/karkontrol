# Son altı mutant — bağımsız ikinci inceleme

2026-10-05, imports_reports. Gerçek Linux mutasyon koşusu [37250701744](https://github.com/nowackk-cp/karkontrol/actions/runs/37250701744), kaynak `2207c894c4ff35307e2644160649531d9253059b`, mutmut 3.8.0.

Desteklenen normal API yollarında **6 kanıtlı eşdeğer, 0 test açığı, 0 belirsiz** bulundu. Ham sonuç **513 toplam / 507 killed / 6 survived / 0 diğer = %98,83** olarak korunur. Bu sınıflama skoru yükseltmez; kaynak dışlaması veya mutation ayarı değiştirilmedi.

## Kanıt zinciri

- [İndeks](reports/mutation-review-index.json) ve [ham özet](reports/mutation-summary.json) aynı kaynak commit'ini gösterir. Git'ten okunan `engine/profit.py` SHA256 değeri `25d13efa08dd0b61822aae5884746f42f1523b07a79b7291b716f7ef360a0ffb` ile eşleşir.
- İndeksteki iki `.meta` dosyasının SHA256 değerleri doğrulandı. Birleştirilen 513 metadata çıkış kodunda 507 killed ve 6 survived; altı ID indeksle aynı. Hata/zaman aşımı kill sayılmadı.
- Altı ham mutantın `_orig` fonksiyon AST'si commit kaynak fonksiyonuyla aynı. Her diff'in tek değişikliği yeniden uygulanıp ham mutant AST'siyle tam eşleştirildi. Diff ve raw kaynak hash'leri [JSON raporunda](final-six-survivors.json) saklandı.
- `source_exclusions=[]`; gerçek test seçimi `tests/unit/test_profit.py` ve `tests/unit/test_profit_contract.py`. Kaynak, test, insan beklenenleri ve eski kanıtlar değiştirilmedi.

## Her mutantın gerekçesi

| Mutant — engine.profit öneki | Ham değişiklik | Sonuç / kanıt |
|---|---|---|
| `x__calculate__mutmut_75` | [strict=True → None](reports/mutation-diffs/b0330dcc5b32fece.diff) | Eşdeğer. `original`, aynı `lines` listesinden bire bir comprehension ile oluşur; iki liste zip'e kadar değişmez. Uzunluklar eşittir. |
| `x__calculate__mutmut_78` | [strict kaldırılır](reports/mutation-diffs/ab291395d6519ff2.diff) | Eşdeğer. Aynı uzunluk invariantı; strict yalnız uzunluk farkında davranışı değiştirir. |
| `x__calculate__mutmut_79` | [strict=True → False](reports/mutation-diffs/6578dad1d31dbb0d.diff) | Eşdeğer. Eşit uzunluklarda aynı çiftler ve hesap sonuçları oluşur. |
| `x__round_half_up__mutmut_16` | [value < 0 → value <= 0](reports/mutation-diffs/6af370ecdbd50914.diff) | Eşdeğer. Koşullar yalnız Fraction(0)'da ayrılır; quotient/remainder/rounded sıfır, Python int `-0 == 0`. Fraction işaretli sıfır taşımaz. Sıfır dışındaki bütün rasyoneller aynı dalı seçer. |
| `x_money__mutmut_3` | [ROUND_HALF_UP → None](reports/mutation-diffs/b59ffd39b63f74c3.diff) | Eşdeğer. Sonlu Decimal girdiler değiştirilmiş dala girmez. Sonlu olmayan değerlerde quantize NaN propagation/InvalidOperation davranışı verir; yuvarlanacak sonlu katsayı yoktur. Context rounding seçimi sonuç/payload/işaret/istisna/flag'i değiştirmez. |
| `x_money__mutmut_5` | [rounding parametresi kaldırılır](reports/mutation-diffs/2b327f8fcca1e251.diff) | Eşdeğer. Aynı nonfinite gerekçesi. `LineInput.validate` sonlu olmayan finans girdilerini money çağrısından önce reddeder; doğrudan money uyumluluk yolu da kontrol edildi. |

## Doğrudan çalıştırılan kontroller

Problar doğrulanmış ham fonksiyon AST'lerini yalnız izole bellekte çalıştırdı; bu bir yeni Linux mutasyon koşusu değildir. Sınıflama sonlu örneklerden ibaret değildir: yukarıdaki kontrol akışı ve aritmetik gerekçeleri genel desteklenen yolları açıklar.

- `_round_half_up`: pay −257…257, payda 1…97 olan **49.955 Fraction girdisi**. Mutant ve kaynak aynı Python int sonucunu verdi; negatif değerler, yarımlar ve sıfır dahil.
- Her `money` mutantı: **2.944 girdi/context birleşimi**, bunun **1.408'i nonfinite**. Sekiz Decimal yuvarlama modu; precision 1/3/28/50; clamp 0/1; InvalidOperation trap açık/kapalı. NaN/sNaN/Infinity'nin işaret ve payload örnekleri ile sonlu kuruş sınırları kontrol edildi. Sonuç tuple'ı, istisna türü/args ve context flag'leri bire bir aynı.
- Her altı varyant için **24 public sipariş/context birleşimi**: tek TRY, sırasız çok satır/kısmi iade, sıfır brüt iadeler, tam iade, önceki #27 uzun kur örneği ve çok satırlı Amazon. Precision 1/3/28/50 ile Inexact/Rounded trap'leri açıkken bütün rapor alanları, cash property ve flag'ler kaynakla aynı.

Gerçek davranış farkı üreten witness bulunmadı. Desteklenen scope normal built-in Decimal/Fraction ve somut `list[LineInput]` yoludur; yan etkili özel subclass, monkeypatch veya eşzamanlı liste değiştirme bu API sözleşmesinin parçası değildir. Bu teknik inceleme insan golden finans kabulü veya üretim doğrulaması sayılmaz.

Makine okunur ayrıntılar: [final-six-survivors.json](final-six-survivors.json).

