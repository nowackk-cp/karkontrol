# KârKontrol çalışma talimatları

## Altın kural: işlem bittiğinde kayıt tut

Tamamlanan **her işlem**, hemen ardından kökteki `projede yapılanlar.md`
dosyasına yazılır. Kayda tarih, yapılan değişiklik, doğrulama sonucu ve varsa
engel eklenir. Yapılmayan iş tamamlanmış gibi yazılmaz. Bu kural tüm sonraki
oturumlar için geçerlidir. Günlük ve kişisel çalışma notları yalnız yerelde
tutulur; Git'e eklenmez.

## Çalışma biçimi

- Yapılacak işi mevcut proje kuralları ve ilgili hata kanıtıyla doğrula.
- Para alanlarında yalnızca `Decimal` kullan; kuruşa `ROUND_HALF_UP` uygula.
- Altın verinin beklenen değerlerini motor çıktısından veya AI hesabından üretme.
  İnsan doğrulaması yapılmayan veriyi açıkça taslak olarak işaretle.
- Bir testi geçirebilmek için beklenen sonucu değiştirme veya testi gevşetme.
- Hata, test sayısı, kapsam, mutasyon ve CI başarısı yalnızca gerçek kanıtla raporlanır.
- Sentetik veri kullan. Gerçek müşteri verisi, gizli anahtar ve `.env` Git'e girmez.
- Küçük ve anlamlı commit'ler oluştur. Git kimliğini uydurma.
- Dış hizmette yapılan iş yereldeki yapılandırmayla karıştırılmaz. GitHub'da
  çalışmamış bir workflow için yeşil CI rozeti veya branch protection iddiası yazma.
- Bağlam devri için yerel `docs/DEVAM_NOTU.md` dosyasını güncelle; devam ederken
  bu notu, yerel işlem günlüğünü ve Git durumunu oku.

## Başlangıç kontrolleri

`uv sync --locked --extra dev`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run python manage.py check`,
`uv run python -m pytest`. Windows'ta console launcher engellenirse standart
Python modül çağrısını kullan; sistem güvenlik ayarlarını değiştirme.
