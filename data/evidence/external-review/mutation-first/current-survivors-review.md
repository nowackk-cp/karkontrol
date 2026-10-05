# c1481f4 Linux mutasyon koşusu: 13 sağ kalan mutant incelemesi

2026-10-05. İncelenen kaynak: `c1481f4d7f364b13e6554912fe4a4e58e2787031`.
Gerçek Linux koşusu: GitHub Actions run `37249153652`, mutmut 3.8.0.

Ham sonuç **436 toplam / 423 killed / 13 survived / 0 other = %97.02**.
Kaynak dışlaması yok. Sınıflama skoru değiştirmez ve 3 eşdeğer mutant toplamdan
çıkarılmaz. Bu inceleme yeni bir mutasyon koşusu değildir.

Sonuç: **3 kanıtlı eşdeğer, 10 test açığı, 0 yalnız aday**. Test açıklarının
9'u gözlenebilir hata mesajı değişimi, 1'i kabul edilen FX girdisinde kuruş
yuvarlama farkıdır. FX mutantı için orijinal kaynakta da somut hata gösterildi.

## Kanıt zinciri

- `reports/review-mutation-first/mutation-evidence/reports/mutation-review-index.json`
  ve `mutation-summary.json` aynı kaynak commit'ini gösteriyor.
- `git show c1481f4:engine/profit.py` baytlarının SHA-256 değeri indeksteki
  `6c0fa1048682cdd3fb951dbda06595734e5001bf05e305f91288cf22800cbb87` ile eşleşti.
- İki ham `.meta` dosyasının SHA-256 değerleri indeksle eşleşti; 436 mutantın
  çıkış kodları `423 × 1` ve `13 × 0`. Sağ kalan 13 ID indeksle birebir eşleşti.
- Her raw diff'in mutant başlığı ve silinen/eklenen satırları ham generated
  function gövdesiyle karşılaştırıldı. Her generated original function AST'si
  commit'teki original AST ile eşleşti.
- Doğrudan problar, ham mutant function AST'sini aynı commit'ten yüklenen izole
  bellek modülünde çalıştırdı. Üretim motoru veya test dosyası değiştirilmedi.
- Her diff'in SHA-256 değeri, ham/commit function satırları ve bütün çıktılar
  [JSON raporunda](current-survivors-review.json) saklandı.

## Her mutantın sınıflaması

Diff bağlantıları `reports/review-mutation-first/mutation-evidence/reports/mutation-diffs/`
altındaki gerçek Linux çıktısına gider. Tablo ID'leri `engine.profit.` önekiyle tamdır.

| Mutant | Ham diff | Sınıf | Kanıt |
| --- | --- | --- | --- |
| `x__calculate__mutmut_62` | [09325053d5e800d8](reports/mutation-diffs/09325053d5e800d8.diff) | Kanıtlı eşdeğer | `strict=True → None`; `original` listesi `lines` üzerinden birer elemanla üretilir, uzunluklar eşittir. |
| `x__calculate__mutmut_65` | [41a288e41916a3e2](reports/mutation-diffs/41a288e41916a3e2.diff) | Kanıtlı eşdeğer | `strict` kaldırılır; aynı eşit uzunluk koşulu geçerlidir. |
| `x__calculate__mutmut_66` | [5547813b98595b1d](reports/mutation-diffs/5547813b98595b1d.diff) | Kanıtlı eşdeğer | `strict=True → False`; aynı eşit uzunluk koşulu geçerlidir. |
| `x__calculate__mutmut_9` | [3c82f73aa15bd67a](reports/mutation-diffs/3c82f73aa15bd67a.diff) | Test açığı: mesaj | `demo_tr` için USD/rate40 girdisinde `ValueError` metnine `XX` eklenir. |
| `x_allocate__mutmut_3` | [63615a9ca65042ee](reports/mutation-diffs/63615a9ca65042ee.diff) | Test açığı: mesaj | `allocate(1.00, [])` hata metni farklıdır. |
| `x_calculate_order__mutmut_13` | [e15745ab5fcca849](reports/mutation-diffs/e15745ab5fcca849.diff) | Test açığı: mesaj | Tek siparişte TRY/rate1 ve USD/rate40 hata metni farklıdır. |
| `x_calculate_order__mutmut_17` | [35dbfb9566fcb048](reports/mutation-diffs/35dbfb9566fcb048.diff) | Test açığı: finansal | `prec50 → 51`; 51 basamaklı kabul edilen kurda brüt `1.01 → 1.00`, tam oracle `1.00`. |
| `x_calculate_order__mutmut_7` | [cd19319a9fb099a9](reports/mutation-diffs/cd19319a9fb099a9.diff) | Test açığı: mesaj | `calculate_order([])` hata metni farklıdır. |
| `x_shipping_fee__mutmut_24` | [a58231397cea242e](reports/mutation-diffs/a58231397cea242e.diff) | Test açığı: mesaj | Bilinmeyen pazaryeri hata metni farklıdır. |
| `xǁLineInputǁvalidate__mutmut_109` | [72d630592d1f9a38](reports/mutation-diffs/72d630592d1f9a38.diff) | Test açığı: mesaj | TRY/rate2 hata metni farklıdır. |
| `xǁLineInputǁvalidate__mutmut_116` | [a0a634dfcd807d77](reports/mutation-diffs/a0a634dfcd807d77.diff) | Test açığı: mesaj | Brüt600/indirim601 hata metni farklıdır. |
| `xǁLineInputǁvalidate__mutmut_27` | [19705c7ed94e9bcd](reports/mutation-diffs/19705c7ed94e9bcd.diff) | Test açığı: mesaj | quantity1/returned_quantity2 hata metni farklıdır. |
| `xǁLineInputǁvalidate__mutmut_98` | [95325684224258eb](reports/mutation-diffs/95325684224258eb.diff) | Test açığı: mesaj | GBP para birimi hata metni farklıdır. |

Eşdeğerlik kanıtı desteklenen `calculate_order(list[LineInput])` yolu içindir:
`original = [... for line in lines]`, dolayısıyla `len(original) == len(lines)`.
İki liste `zip` öncesinde değiştirilmez. `strict` uzunluk farkında ayrışır;
bu koşul oluşamaz. İki satırlı iade probu da bütün `LineResult` alanlarında
eşit çıktı verdi. Monkeypatch ve eşzamanlı liste değiştirme bu kanıtın dışında.

Dokuz mesaj mutantında reddetme koşulu ve `ValueError` türü korunur, mesaj
`message → XXmessageXX` olarak değişir. Mevcut `pytest.raises(..., match=message)`
substring regex eşleşmesi bu farkı kabul eder. Her gerçek mesaj probunda eski
regex eşleşti, exact karşılaştırma eşleşmedi. Finansal sonuç farkı olduğu
iddia edilmez; tam hata mesajı sözleşmesinde eşdeğer olmadıkları gösterilir.

## ENG-002: tam FX oracle ile somut kaynak hatası

[Issue #27](https://github.com/nowackk-cp/karkontrol/issues/27) için witness:

```python
LineInput(
    line_number=1,
    quantity=1,
    unit_price_gross=Decimal("1.00"),
    unit_cost_net=Decimal("0.00"),
    vat_percent=Decimal("0"),
    commission_percent=Decimal("0"),
    currency="USD",
    exchange_rate=Decimal("1.004" + "9" * 47),
)
# calculate_order([line], marketplace="amazon_demo")
```

Kur `1.00499999999999999999999999999999999999999999999999`;
51 anlamlı basamağa sahip ve `1.005` eşiğinin hemen altında. Girdi orijinal
ve mutant `validate()` tarafından kabul edilir. Kur basamak sayısına kamu
sözleşmesinde sınır konmamıştır.

Orijinal `prec50` brüt `1.01`; ham `prec51` mutantı brüt `1.00` verir. Bağımsız
oracle, `Fraction(price) * Fraction(rate) * 100` değerinin pay/paydasını
`divmod` ile ayırır; yalnız `2 * remainder >= denominator` olduğunda kuruşu
artırır. Sonuç **100 kuruş = 1.00**. Oracle Decimal context kullanmaz.

Burada precision artırımı genel çözüm değildir: daha uzun kabul edilen kur
değerlerinde aynı erken yuvarlama tekrar oluşabilir. İlgili kur/oran/iade
işlemleri kuruş kararına kadar tam hesaplanmalıdır. Bu otomatik, sentetik
kural regresyonudur; insan altın veri doğrulaması değildir.

İnceleme sırasında üretim/test/public dosyaları, gate ve tarihî 27 mutant
kanıtı değiştirilmedi. Sonraki düzeltme/red test kanıtı ayrı kaydedilecektir.

