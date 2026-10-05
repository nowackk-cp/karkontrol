# AI ile çalışma kaydı

Kod ve otomatik testler Codex ile geliştirildi. İnsan altın finans hesabı, kör sorular ve hakem etiketleri bu süreçte üretilmedi. Aşağıdaki anlatım teknik kayıt taslağıdır; kişinin kendi emeğine ilişkin son anlatımı kendisinin yazması gerekir.

Kullanılan talepler: “projeye başla”, “bütün planı tamamla” ve dış inceleme için “oku ve hepsini bitir sonra bitirdiklerini de kontrol et”. Sürüm kontrollü model talimatları `apps/assistant/prompts/` altında birebir bulunur. Ayrı onaylı kurallarla başlayan bağımsız `ai-v1` geliştirme oturumu yapılmadı; böyle bir izolasyon vaadi başarı olarak sunulmaz.

| Öneri/karar | Karar ve gerekçe |
|---|---|
| Motor çıktısını altın beklenti yapmak | Reddedildi; aynı hata iki tarafta saklanabilir |
| Nakit özdeşliğini iki bağımsız hesap diye sunmak | Dış incelemede düzeltildi; girdi temelli ayrı hakediş/KDV kontrolleri yazıldı |
| Ay sayısını modele tahmin ettirmek | Şemaya bağlandı; yanlış dönemin zararı gizlemesi kayıt altına alındı |
| Başarısız ölçümü silip yalnız son başarıyı bırakmak | Reddedildi; ilk ham sonuç ve eski etiketler korundu |
| Testi geçirmek için bekleneni gevşetmek | Reddedildi; kaynak davranışı düzeltildi |
| Windows model korumasını kapatmak | Reddedildi; Linux runner kullanıldı |
| Aynı model hakemini insan mutabakatı saymak | Reddedildi; ayrı model ve kör insan etiketleri ayrıldı |
| Eşit kalanları Decimal bölümüyle sıralamak | Dış incelemede tam Fraction/divmod ile düzeltildi |
| Büyük dosya için yalnız import kontrolüne güvenmek | Streaming HTTP sınırı ve atomik testler eklendi |

AI tarafından kod/test üretildiğinde bağımsızlık sınırlıdır. Çapraz ajan incelemesi farklı hata bulma fırsatı sağlar, insan alan doğrulamasının yerine geçmez. Tamamlanan otomatik işlemler yerel günlükte tutulur. Güncel rakamlar ve kabul sınırları [README](../README.md) içindedir.
