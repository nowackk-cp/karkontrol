# İnsan altın seti hazırlığı

Girdiler AI tarafından hazırlanmış sentetik taslaktır; beklenen finans değerleri boş tutulur. İnsan karşılaştırmasından önce [kurallardaki](KURALLAR.md) dört karar gerekçesiyle verilmelidir.

## Gerçek girdi matrisi

Aşağıdaki tablo `data/draft/inputs.json` alanlarından oluşturulmuştur. Eski senaryo adları girdilerle uyuşmadığı için kaldırıldı. Bu liste çok satırlı sipariş veya iptal kapsamını varmış gibi göstermez; mevcut girdiler tek satırlıdır.

| ID | Pazar / para | Adet / iade | Brüt birim / net maliyet | KDV / komisyon | İndirim / kupon | Desi / ağırlık | Kur |
|---|---|---|---|---|---|---|---|
| SIP-01 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-02 | demo_tr / TRY | 1 / 0 | 0 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-03 | demo_tr / TRY | 1 / 0 | 600 / 250 | 0 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-04 | demo_tr / TRY | 1 / 0 | 600 / 250 | 1 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-05 | demo_tr / TRY | 1 / 0 | 600 / 250 | 10 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-06 | demo_tr / TRY | 2 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-07 | demo_tr / TRY | 3 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-08 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 0 | 0 / 0 | 1 / 0 | 1 |
| SIP-09 | demo_tr / TRY | 1 / 0 | 299.99 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-10 | demo_tr / TRY | 1 / 0 | 300 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-11 | demo_tr / TRY | 1 / 0 | 300.01 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-12 | demo_tr / TRY | 1 / 0 | 600.01 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-13 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 3.01 / 0 | 1 |
| SIP-14 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 3 / 0 | 1 |
| SIP-15 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 4.01 | 1 |
| SIP-16 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 100 / 0 | 1 / 0 | 1 |
| SIP-17 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 100 | 1 / 0 | 1 |
| SIP-18 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 50 / 50 | 1 / 0 | 1 |
| SIP-19 | demo_tr / TRY | 1 / 1 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-20 | demo_tr / TRY | 3 / 1 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-21 | demo_tr / TRY | 3 / 2 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-22 | demo_tr / TRY | 3 / 3 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-23 | demo_tr / TRY | 1 / 0 | 0.01 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-24 | demo_tr / TRY | 1 / 0 | 0.05 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-25 | demo_tr / TRY | 1 / 0 | 600 / 0 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-26 | demo_tr / TRY | 1 / 0 | 600 / 1000 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-27 | demo_tr / TRY | 1 / 0 | 9999999.99 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-28 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 100 | 0 / 0 | 1 / 0 | 1 |
| SIP-29 | demo_tr / TRY | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-30 | demo_tr / TRY | 7 / 0 | 1.01 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 1 |
| SIP-31 | amazon_demo / EUR | 1 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-32 | amazon_demo / USD | 2 / 1 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-33 | amazon_demo / EUR | 3 / 2 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-34 | amazon_demo / USD | 4 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-35 | amazon_demo / EUR | 5 / 1 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-36 | amazon_demo / USD | 6 / 2 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-37 | amazon_demo / EUR | 7 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-38 | amazon_demo / USD | 8 / 1 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-39 | amazon_demo / EUR | 9 / 2 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |
| SIP-40 | amazon_demo / USD | 10 / 0 | 600 / 250 | 20 / 20 | 0 / 0 | 1 / 0 | 40.123456 |

## İnsan prosedürü

`golden/insan-v1` dalında, motor dosyasını ve çıktısını açmadan önce en az 10, hedef bütün 40 siparişi yalnız kural metninden hesaplayın. `data/draft/insan_inceleme.xlsx` boş inceleme şablonudur. Beklenen yedi tutar TRY, inceleyen, tarih ve kaynak her satırda gerekir.

İnsan çalışma kitabına Hesap sayfası eklemeli: indirimli brüt, kalan brüt, net satış/satış KDV'si, komisyon, desi, gidiş/dönüş, hizmet, maliyet/maliyet KDV'si, stopaj, ücret KDV'si, kâr, hakediş ve nakit farkı. Formüller motor çıktısından türetilmez. SIP-05/15/18/20/27/31/33 kâğıt-kalem ikinci kontrolden, sonra bütün set ertesi gün yeniden incelemeden geçmelidir. AI bu hesapları tamamlamaz.

Karşılaştırmadan önce CSV, dosya SHA ve kaynak kural SHA commit edilmeli; yöntem ve “motor çıktılarına bakılmadı” beyanı yalnız gerçekten yapan kişi tarafından yazılmalıdır. Motor daha önce geliştirildiğinden geçmişe dönük bağımsızlık iddiası konulmaz.

```powershell
uv run python scripts/export_human_review.py data/draft/insan_inceleme.xlsx --output data/golden/altin_set.csv
uv run python scripts/check_golden.py --review data/golden/altin_set.csv --output data/evidence/golden-first-run.json
uv run python -m pytest tests/reconciliation -m reconciliation
```

Runner varsayılan tam seti ister. İlk 10 insan satırı için `check_golden.py --review data/golden/altin_set.csv --required-count 10 --output reports/golden-ten.json` kullanılabilir; rapor tam finans kabulünü yalnız bütün hedef satırlar varsa onaylar. İlk karşılaştırmanın dosyası mevcutsa üzerine yazılması engellenir. Her fark için motor/insan hesabı/kural araştırılır, issue ve ayrı düzeltme commit'i saklanır. Beklenenleri motorla eşitlemek için değişiklik yapılmaz. Boş insan verisi ayrı CI mutabakat işinde kırmızı görünür; otomatik kalite başarısına dahil edilmez.
