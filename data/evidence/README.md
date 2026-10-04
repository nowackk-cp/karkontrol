# Gerçek model ölçüm kayıtları

Sentetik SQL fixture üzerinde gerçek Qwen/llama.cpp CPU çağrıları.
Tutarlar model tarafından hesaplanmaz; araç seçimi ve SQL eşitliği ölçülür.

- llm-first.json: [37173824046](https://github.com/nowackk-cp/karkontrol/actions/runs/37173824046),
  sourcea293f20, v1%32,5 / v2%85; workflow FAILURE,5kritik v2 hatası.
- llm-corrected.json: [37174071378](https://github.com/nowackk-cp/karkontrol/actions/runs/37174071378),
  source1ac5699, v1%47,5 / v2%100; workflow SUCCESS,0kritik v2 hatası.

Her rapor prompt ve soru SHA256'sı,36 gerçek istek+4uygulama reddi, ham araç
seçimi ve yanıtı içerir. İlk başarısız rapor silinmez. Hakem puan şablonu
data/draft/judge_review.json; insan puanları boştur,20 model puanı insan
kalibrasyonu yerine geçmez. Yeni holdout raporu ilk çalıştırma sonrası eklenir.
