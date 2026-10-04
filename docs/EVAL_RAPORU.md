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

Bu **LLM benchmark'ı değildir**. Dış modele istek yapılmadı. Prompt v1/v2
karşılaştırması, LLM-as-judge ve 20 insan puanıyla kalibrasyon yapılmadı.
`reserved` etiketli 10 soru aynı AI geliştirme oturumunda görüldü; kör
hold-out başarısı iddia edilmez. Yeni bağımsız sorular ve insan hakem verisi
geldiğinde gerçek model değerlendirmesi ayrı sürüm olarak yapılmalıdır.

Mevcut kalite kapısı tüm eval testlerinin geçmesini ister. Bu, demo baseline
%100'den düşüşe veya tek kritik hataya izin vermez; gevşek toleransla hataları
saklamaz. `eval.yml` asistan/soru değişiminde, haftalık ve elle çalışır.
