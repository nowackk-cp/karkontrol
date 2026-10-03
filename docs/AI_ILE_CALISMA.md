# AI ile çalışma kaydı

## 2026-10-04 — Başlangıç

Araç: Codex. Bu çalışmanın Claude Code ile yapıldığı iddia edilmez.
Kullanıcı talebi: projeye başla; her tamamlanan işlemi `projede yapılanlar.md`
dosyasına yaz ve bunu altın kural olarak ekle; soru sormadan ilerle;
bağlam dolduğunda compact yap.

| Karar | Sonuç | Gerekçe |
|---|---|---|
| Python 3.13 + Django 5.2 altyapısı | Kabul | Ana planla uyumlu |
| İnsan kontrolü olmayan AI altın hesapları | Ret | Bağımsız kâhin kuralını ihlal eder |
| Ölçülmemiş CI/kapsam/mutasyon rozeti | Ret | Gerçek kanıt yok |
| Giriş ve sağlık kontrolü testleri | Kabul | Çalışır altyapı ve güvenlik doğrulanır |
| Üretim ve yerel ayarları ayırma | Kabul | Yerel kolaylıklar üretime taşınmaz |
| Kaynaklardan alan araştırma özeti | Kabul, taslak | İnsan yazarlığı/onayı iddia edilmez |

### Bağlam devamlılığı

Compact işlemi uygulamanın otomatik bağlam yönetimine bağlıdır; bu oturumda
çağrılabilir bir compact aracı bulunmadı. `AGENTS.md`, işlem günlüğü ve
`DEVAM_NOTU.md` dosyaları sonraki oturumların aynı işten devam etmesini sağlar.

### Motor bağımsızlığı

Henüz motor üretilmedi, `ai-v1` etiketi konmadı. Kurallar ve bağımsız altın set
tamamlandığında ayrı oturumda yalnızca onaylı kurallar gösterilecek. Gerçek
prompt ve ilk sürüm o aşamada kaydedilecek.
