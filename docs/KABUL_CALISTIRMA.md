# Eksik bağımsız kabul kanıtlarını çalıştırma

## İnsan finans mutabakatı

`data/draft/insan_inceleme.xlsx` dosyasının Inceleme sekmesinde 40 siparişin
7 beklenen tutarını bağımsız hesaplayın. Beklenenler TRY cinsindendir.
İnceleyen, YYYY-MM-DD tarih ve kaynak hesap/kurallar referansı her satırda
gerekir. Formüller görünür tutulabilir; Excel'de hesaplayıp kaydettikten sonra:

```powershell
uv run python scripts/export_human_review.py data/draft/insan_inceleme.xlsx --output data/golden/altin_set.csv
uv run python scripts/check_golden.py --review data/golden/altin_set.csv
```

Komut tam 40 benzersiz kayıt ister. Tek kuruş fark bile satır/kalem/beklenen/
gerçekleşen fark raporuna girer. Boş alanlar, AI inceleyen adı, geçersiz sayı
ve gelecekteki inceleme tarihi kabul edilmez. Kaynağı doldurmak tek başına
insan incelemesinin gerçekten yapıldığını kanıtlamaz; kaynak hesap korunur.

## Gerçek yerel LLM

Resmî Qwen3-1.7B-Q8_0 ve llama.cpp b11382 CPU sürümleri SHA256 ile sabittir.
Portable dosyalar .local altında, Git dışında tutulur. Kurulum yaklaşık 1,8 GB
model indirir; Windows ve Ubuntu x64 desteklenir.

```powershell
uv run python scripts/setup_local_llm.py
.local/llm/runtime/llama-server.exe -m .local/llm/Qwen3-1.7B-Q8_0.gguf --host 127.0.0.1 --port 8081 -c 4096 -t 4 --parallel 1 --jinja
uv run python manage.py evaluate_assistant --backend local --versions v1,v2
```

Ubuntu binary arşivinde executable alt klasörde olabilir; `find` ile gerçek
yolu kullanın. Adaptör yalnız loopback HTTP adresine istek gönderir.
UI için KARKONTROL_ASSISTANT_BACKEND=local; varsayılan offline'dır.
Model araç/tarih seçer; para çıktısı sunucunun SQL araçlarından oluşturulur.
Bu bir serbest metin finans cevabı üretme testi değildir. Model kesildiğinde
unavailable gösterilir; sessiz offline başarıya dönüşmez.

Eval fixture tek transaction içinde kurulur ve her durumda geri alınır.
JSON raporu iki promptun hash'ini, bütün cevaplarını, SQL uyumunu ve gerileyen
soruları saklar. Son prompt baseline'dan3 puandan fazla düşerse veya tek bir
kritik soru başarısız olursa komut exit1 döner. Offline çalıştırma gerçek LLM
kanıtı sayılmaz.

## İnsan hakem ve görülmemiş set

20 hakem cevabı için bağımsız insan puanı, inceleyen ve tarih gerekir.
AI bu alanları dolduramaz. qa.acceptance.calibrate en az%85 uyum ister.
`uv run python manage.py evaluate_judge` gerçek modelden20 rubrik puanı ve
boş insan alanlarını reports/judge-review.json dosyasına yazar. Bu20 aday
AI tarafından hazırlanmış olumlu/olumsuz örneklerdir; insan puanı değildir.
İnsan incelemesi sonrası `evaluate_judge --human-review DOSYA` ile mutabakat
kapısı çalıştırılır. Aynı Qwen modeli asistan ve hakem olarak kullanıldığı
için öz değerlendirme yanlılığı bağımsız insan kalibrasyonuyla ölçülmelidir.
Mevcut reserved10 geliştirici AI tarafından görüldü; kör set değildir.
Yeni set yalnız prompt sürümleri sabitlendikten sonra hazırlanıp bir kez
çalıştırılmalı; set görüldükten sonra aynı prompt üzerinde ayar yapılmamalı.

Bu bilgisayarda Windows Code Integrity, portable runtime'ın ggml.dll
dosyasını engelledi (0xC0E90002, olay3077/3033). Güvenlik ayarı değiştirilmez.
Gerçek model ölçümü `.github/workflows/llm.yml` Linux runner üzerinde yapılır;
Windows kurulum dosyasının varlığı başarılı model çalıştırması sayılmaz.
