# Mutasyon ölçümü

Güçlendirilmiş testlerle güncel sonuç: **342/369 = %92,68**, 27 survived,
diğer durum 0. Kaynak commit40c5442:
[run37171192788](https://github.com/nowackk-cp/karkontrol/actions/runs/37171192788).
Yedi ek mutant yakalandı; yaşayan27 oran hesabından çıkarılmadı.

İlk Linux mutmut3.8 ölçümü: **335 killed /369 toplam =%90,79**, 34 survived,
timeout/suspicious yok. Export için geçersiz junitxml komutu ilk workflow'u
kırdı; desteklenen metadata/results çıktılarına geçilince ölçüm doğrulandı:
[başarılı run37170823038](https://github.com/nowackk-cp/karkontrol/actions/runs/37170823038).

## İncelenen boşluklar

| Mutant | Değişiklik | Sonuç |
|---|---|---|
| allocate36 | Kalan kuruş sıralamasında key=None | Kuruş korunur ama yanlış satıra gider; ağırlık/sıra testi eklendi |
| calculate151 | Maliyet KDV'sinde /100 yerine ×100 | Nakit eşitliğinde karşılıklı iptal nedeniyle kaçıyordu; KDV kalemleri test edildi |
| validate16 | Maksimum adet/satır <2147483647 | Geçerli sınırı reddeder; tam sınır ve+1 testi eklendi |
| shipping4 | Hata alan adı gross yerine None | Finans davranışı aynı; raporda yaşayan olarak korunur |

Bu değişiklikler mutasyon aracının geçici kopyasında çalışır. Gerçek motor bu
hataları içermez; AI'ın yazdığı gerçek bug olarak BUGS.md'ye eklenmez.
Testler sonucu değiştirilerek geçirilmedi; ek kontroller mevcut sözleşmeyi doğrular.

## Metrik sınırları

Kapsam engine/ saf fonksiyonlarıdır. Exception raise satırlarının mesajları
mutate edilmez; koşul ve aritmetik dahil. Mutmut3 modül globals/dataclass
varsayılanlarını mutate etmez. Skor tam üretilen set üzerinden hesaplanır;
yaşayan/eşdeğer/time-out mutantları keyfi düşerek skor yükseltilmez. Yalnız
exit1 öldürülen sayılır, boş set veya <%85 skoru workflow'u kırar.

Gerçek finans doğruluğu yalnız bu oranla kanıtlanmaz: insan sözleşme/golden
kabulü gerekir. Metadata, survivor listesi ve commit kimliği workflow
artifact'ında saklanır; gecelik ölçüm yeniden üretilebilir.
