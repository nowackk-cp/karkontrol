# Araç asistanı değerlendirmesi

2026-10-04: deterministik sürüm `tools-v1`, **40/40 soru** doğru durum, araç
ve gerektiğinde SQL sonucu verdi. CI kanıtı:
[Assistant eval 37170676353](https://github.com/nowackk-cp/karkontrol/actions/runs/37170676353).
Ek envanter/girdi/guardrail testleri genel test sayısına dahildir.

| Kategori | Soru | Kontrol |
|---|---:|---|
| Sayısal | 12 | SQL tamsayı kuruş eşitliği; yanıt sayısal beyaz listesi |
| Sıralama | 8 | SQL ürün listesi ve sırası tam eşitlik |
| Kurallar | 6 | Sözleşmedeki doğru davranış ve zorunlu ifade |
| Veri yok / kapsam dışı | 6 | Uydurulan tutar yok, uygun yanıt |
| Belirsiz | 4 | Yıl netleştirme veya tüm mağaza özeti |
| Güvenlik | 4 | Reddetme; ayrıca yabancı mağaza 404 testi |

Sayısal tokenlar işaret ve Türkçe binlik/ondalık biçimiyle araç çıktısından
gelmelidir. Bilerek 999,00 TL ekleyen test yanıtı engellendi. Mağaza kimliği
request sahibinden denetlenir. SQL metinleri parametreli ve geliştiriciye aittir;
asistan sorusu SQL olarak çalıştırılmaz. Ürün adları talimat kabul edilmez.

Yukarıdaki ilk ölçüm **LLM benchmark'ı değildir**; deterministik backend'e aittir.
`reserved` etiketli 10 soru aynı AI geliştirme oturumunda görüldü; kör
hold-out başarısı iddia edilmez. Yeni bağımsız sorular ve insan hakem verisi
geldiğinde gerçek model değerlendirmesi ayrı sürüm olarak yapılmalıdır.

Mevcut kalite kapısı tüm eval testlerinin geçmesini ister. Bu, demo baseline
%100'den düşüşe veya tek kritik hataya izin vermez; gevşek toleransla hataları
saklamaz. `eval.yml` asistan/soru değişiminde, haftalık ve elle çalışır.

## Gerçek Qwen ölçümü

Resmî Qwen3-1.7B-Q8_0, llama.cpp b11382 CPU, temperature0.
Model Türkçe sorudan JSON araç seçer. Mağaza sahibini sunucu bağlar;
finans tutarları SQL araçlarından deterministik oluşturulur. Bu rapor modelin
serbest metin finans hesabı başarısını ölçmez. Model çağrısı hatası başarısızdır.

İlk [gerçek run37173824046](https://github.com/nowackk-cp/karkontrol/actions/runs/37173824046):
v1%32,5 (13/40), v2%85 (34/40). v2 E-01/02/10/16/28 kritik hatalarıyla CI
FAILURE. Raw JSON raporu ve server logu artifact olarak korundu. Eylül ayı
yanlış seçimi APP-003 olarak kaydedildi; tarih şeması ve v2 niyet açıklamaları
düzeltildi. Düzeltme sonrası ölçüm aşağıda ayrı kayıt olarak bulunur.

LLM hakemi grounded/answers_question/clear boyutlarını puanlar.20 AI adayı
gerçek modele verilir fakat insan puanı/reviewer/tarih boş kalır. İnsan
mutabakatı ölçülmeden kalibre edildi iddiası yapılmaz. Aynı Qwen modelinin
hakem olarak kullanılması bağımsız model değerlendirmesi değildir.

Tarih düzeltmesi sonrası [run37174071378](https://github.com/nowackk-cp/karkontrol/actions/runs/37174071378)
SUCCESS: v1%47,5 (19/40), v2%100 (40/40), kritik hata0. Her prompt36 gerçek
model isteği yaptı;4 güvenlik sorusu model öncesi uygulama sınırında reddedildi.
v2'de21 soru iyileşti, gerileyen soru0. Ham ilk/son raporlar data/evidence
altında kalıcıdır; yalnız başarılı sonuç seçilip ilk hatalar silinmedi.

20 gerçek hakem yanıtı da kaydedildi:12 pass,8 fail; insan puanları boş.
Bu dağılım hakem doğruluğu veya insanla%85 mutabakat demek değildir.
data/draft/judge_review.json doldurulmadan kalibrasyon kapısı başarısızdır.

Yeni10 soru `Frozen prompt holdout` manual workflow'unda v2 hash'i
sabitken oluşturulur ve önceden geliştiriciye gösterilmeden bir kez çalışır.
İlk run'ın soru/cevap/hash artifact'i sürüm kanıtına eklenir; ilk başarısız
sonuç da korunur. Bu modelin ürettiği sentetik set, insan yazımı/onayı değildir.
Orijinal reserved10 bu yeni protokolün körlük kanıtı olarak kullanılmaz.

## Sabit prompt ile ilk yeni sentetik set

[İlk ve tek run37175718839](https://github.com/nowackk-cp/karkontrol/actions/runs/37175718839),
source26a174a, SUCCESS/1m46s: v2 **10/10**, kritik hata0. Dokuz soru gerçek
model çağrısı yaptı; güvenlik sorusu uygulama sınırında model öncesi reddedildi.
Soru içerikleri geliştirici tarafından ancak run tamamlandıktan sonra okundu.
Prompt bu sete göre değiştirilmedi; yeni set/tekrar çalıştırma ile başarı aranmadı.

- Prompt SHA256: `89ab8fb2b790d66641a398fba9ea2aadcc13bf293d80e54be66ef6a1abc93ff5`
- Soru SHA256: `6c96312a4ca8517e5f1277f6215b80017c60d4178404c9367ec14314b55c346d`
- [Ham cevaplar](../data/evidence/holdout-first/eval.json),
  [ilk sorular](../data/evidence/holdout-first/questions.jsonl),
  [manifest](../data/evidence/holdout-first/questions.manifest.json).

Bu seti aynı Qwen modeli sentetik niyet/tarih tanımlarından üretti. Bazı sorular
niyet tanımını kopyalar, bazıları doğal Türkçe kullanıcı sorusu değildir.
10/10 sonucu bu sınırlı sentetik sette araç/SQL davranışını gösterir;
görülmemiş insan sorularına genellenmiş doğruluk veya bağımsız insan hold-out
başarısı değildir. Bağımsız insan seti ve20 insan hakem puanı hâlâ gereklidir.
