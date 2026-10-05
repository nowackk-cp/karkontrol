# Asistan yönlendirici değerlendirmesi

Güncel ve tarihî sayısal sonuçlar [README](../README.md) tablosundadır. Finans yanıtı sunucunun kayıtlarından oluşturulur; modelin serbest finans hesabı ölçülmez. Offline taban ile model araç seçimi ayrı raporlanır.

## Geliştirme seti ve prompt değişikliği

İlk Qwen koşusunda yanlış Eylül dönemi ve ürün/kural niyeti hataları bulundu; aynı geliştirme setinde tarih şeması ve prompt ayarı yapıldı. Son başarılı ölçüm genelleme kanıtı değildir. Ham [ilk](../data/evidence/llm-first.json) ve [düzeltilmiş](../data/evidence/llm-corrected.json) yanıtlar korunur. Model öncesi güvenlik reddi yönlendirici paydasına girmez. Güncel payda `model_attempted` ile başlayan bütün çağrıları, başarısız yanıtları da kapsar. Bu alanı içermeyen tarihî JSON'larda `selection` kaydı kullanılır; inceleme notunun tarihî modele atfedilebilir rakamı ham JSON sayımıyla düzeltilmiştir.

v2 prompt farkı: ürün niyetine ürün kârlılığı, karşılaştırma ve veri-yok durumu eklendi (satır 5); rule topic sorudaki konuya bağlandı, iade/kargo ayrımı açıklandı (satır 7); tarih yoksa null ve yıl-yalnız isteğinde month=null kuralı güçlendirildi (satır 13). Tarih eşleşmesi üretim şemasına da bağlandı. Eski v2 dosyası ilk sentetik setten sonra değiştirilmedi.

v3 yeni parserın çözdüğü dönemi modele açık verir: karaktersiz Türkçe, 09/2026, 2026-09, geçen/bu ay. Çok dönem ve tutar eşiği modelden önce ele alınır. Geliştirme soruları ayrı `questions_v3.jsonl` içindedir; göreli tarih için eval saati sabittir. Sıralama fixture'ı farklı kârlı ürünleri ve talimat içeren fakat veri olarak kalan SKU'yu içerir.

Yeni v3 geliştirmesinin [ilk](../data/evidence/external-review/llm-v3-first/eval.json), [ikinci](../data/evidence/external-review/llm-v3-second/eval.json), [üçüncü](../data/evidence/external-review/llm-v3-third/eval.json) ve [son ana dal](../data/evidence/external-review/llm-v3-final/eval.json) ölçümleri ayrı dosyalarda saklanır. Tarih şeması, desteklenmeyen serbest işlem ile desteklenen kural hesaplamasının ayrımı bu görülen hatalara göre v3'te düzeltildi. Son raporun v2 bölümü dondurulmuş eski promptun aynı yeni sorulardaki ayrı referansıdır; v3 başarısıyla birleştirilmez. Protokol source commit ve model manifestini kaydeder; eski ilk sentetik set yeniden çalıştırılmadı.

## Çalıştırma ve sürüm karşılaştırması

```powershell
uv run python scripts/setup_local_llm.py
uv run python manage.py evaluate_assistant --backend offline --versions v3 --output reports/offline-v3.json
uv run python manage.py evaluate_assistant --backend local --versions v2,v3 --baseline-file data/evidence/llm-corrected.json
```

Yerel model ayrıca 127.0.0.1:8081 üzerinde başlatılmalıdır. Model/hash/runtime manifest sabittir; Windows Code Integrity bu bilgisayarda native runtime'ı engellediğinden model Linux CI'da çalışır. Koruma kapatılmadı. Rapor vaka kimliğiyle karşılaştırır; değişen sıra başarı/gerileme eşleşmesini bozmaz. Çıktının CSV'si kategori tablosudur. Yeni sürüm raporu release `baseline.json` olarak saklanır; önceki rapor üzerine yazılmaz.

## Açık bağımsız kabul işleri

Eski [sentetik ilk set](../data/evidence/holdout-first/eval.json) aynı Qwen'in niyet şablonlarından üretildi; insan kör seti değildir. İlk sorular/manifest/sonuç değiştirilmez ve aynı ilk set yeniden başarı aramak için çalıştırılmaz. İnsan yeni soruları kendi yazmalı, içerik görülmeden SHA commit edilmeli, sabit promptla ilk tek koşu saklanmalıdır.

Eski hakem dosyasındaki tekrarlı adaylar kalibrasyon ölçümü değildir. Yeni hazırlık benzersiz cevap hash'leri ve ayrı kör insan dosyası oluşturur; insan puanları boş bırakılır. İnsan inceleme ile ayrı model puanları hash/kimlik üzerinden birleştirilir; uyum ve Cohen κ raporlanır. Tek sınıflı hakem kalibrasyon başarısı sayılmaz.

```powershell
uv run python manage.py evaluate_judge --output reports/prepared-30.json --blind-output reports/blind-30.json
uv run python manage.py evaluate_judge --score data/draft/judge_candidates30.json --output reports/score-30.json
uv run python manage.py evaluate_judge --human-review data/draft/judge_blind30.json --judge-scores reports/score-30.json
```

Score için ayrı `KARKONTROL_JUDGE_URL` ve `KARKONTROL_JUDGE_MODEL` gerekir; asistanla aynı model reddedilir. Ayrı ağırlıklar aynı model ailesindeyse bağımsız aile kanıtı olmaz. İnsan inceleyen/tarih/gerekçe alanları AI tarafından doldurulmaz.

Ayrı Qwen3-0.6B Linux [ilk koşusu](../data/evidence/external-review/judge-first/protocol.json) zaman aşımında sonuç dosyası oluşturamadı. Her deneme artık ayrı partial JSONL'ye hemen yazılır; tamamlanan final JSON ve partial kayıt yeniden kullanılmaz. [İkinci](../data/evidence/external-review/judge-second/protocol.json) ve [son](../data/evidence/external-review/judge-final/protocol.json) ham koşular ayrıdır. Format yönergesi kısa gerekçe ister; Python uzunluk/boolean doğrulaması korunur. Kullanılabilir yanıt sayısı hakem doğruluğu değildir; insan etiketleri olmadan Cohen κ veya uyum skoru verilmez. Timeout'un kesin nedeni kontrollü probe ile kanıtlanmadı.

## İsteğe bağlı Haiku

Yalnız elle tetiklenen workflow sentetik geliştirme sorularını gönderir. Anahtar GitHub `haiku-benchmark` Environment secret'ında tutulur; kişisel hesap harcama sınırı ayrıca insan hesabında ayarlanmalıdır. API hesabı/anahtar olmadığında koşu açık hata verir ve başarı yazılmaz. [Resmi fiyat](https://platform.claude.com/docs/en/about-claude/pricing), erişim 2026-10-04: Haiku 4.5 milyon giriş tokenı 1 USD, çıkış 5 USD. Sabit model `claude-haiku-4-5-20251001`; tek tur ve sınırlı cevap uzunluğu. Maliyet TRY kuruşu olarak garanti edilmez. Qwen/Haiku/offline kategori CSV'leri yalnız üç gerçek koşu mevcutsa kıyaslanabilir.
