# Alan bilgisi — kaynak özeti

Durum: **AI araştırma özeti; insan tarafından yazılmış/onaylanmış belge değildir.**
Erişim tarihi: 2026-10-04. Gerçek satıcı sözleşmesi veya mali müşavir görüşü yerine geçmez.

## Stopaj: resmî kaynakta doğrulananlar

GİB'in e-ticaret tevkifatı bilgi notunda 1 Ocak 2025 başlangıcı ve %1 oranı
belirtiliyor. Matrah KDV hariç satış/hizmet bedelidir; komisyon ve kargo gibi
kesintiler matrahı azaltmaz. Kesinti geçici veya yıllık gelir/kurumlar vergisinden
mahsup edilir. İstisnalar ayrıca tanımlanmıştır; v1 bunları kapsam dışında tutar.
Bu nedenle eğitim modelinde stopaj, hakedişi azaltan ayrı kalem olarak ele
alınacak. Ekonomik kârın gideri sayılmaması proje modelleme kararıdır.

Kaynak: [GİB e-ticaret tevkifatı bilgi notu](https://cdn.gib.gov.tr/api/gibportal-file/file/getFileResources?objectKey=arsiv/yardim-kaynaklar/infografikler/pdfs/eticarettevkifat.pdf).
Ek mevzuat bağlantısı: [GİB tebliğ sayfası](https://gib.gov.tr/mevzuat/kanun/433/teblig/6659).
Tebliğ sayfasının tam metni tarayıcı çıktısında alınamadı; yukarıdaki özet bilgi
notuna dayanır. 2026'da olası mevzuat değişiklikleri ayrıca incelenmeli;
v1 oranı tarihli eğitim varsayımı olarak kullanılacak.

## Sözleşmeye bağlı konular ve açık varsayımlar

| Konu | Durum | v1 için önerilen eğitim varsayımı |
|---|---|---|
| Komisyon matrahı | Satıcı sözleşmesi doğrulanmadı | Satıcı indirimi sonrası KDV dahil tutar |
| Komisyon faturası KDV'si | Doğrulanmadı | Ayrı, açıkça verilen oran |
| Kargo baremi | Gerçek tarife alınmadı | Projeye özel sabit örnek tarife |
| Desi böleni | Taşıyıcı sözleşmesine bağlı | 3000; ölçü birimi cm |
| Hizmet bedeli | Doğrulanmadı | Sipariş başına örnek sabit net ücret |
| Hakediş tarihi | Pazaryeri/sözleşmeye bağlı | Ödeme takvimi v1 dışında |
| İade kargo ve ücretleri | Doğrulanmadı | Durumlara göre açık test sözleşmesi gerekli |
| Kupon finansmanı | Doğrulanmadı | Satıcı/pazaryeri katkısı ayrı alanlar |
| KDV oranları | Ürün sınıfı mevzuatı araştırılmadı | Test senaryosunda açık girdi |

Gerçek pazaryeri oranı iddiası yok. Komisyon, iade ve tarife belirsizlikleri
kesin kurala dönüştürülmeden motor uygulanmamalı.
