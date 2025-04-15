# Çiftlik Yönetim Sistemi

Bu proje, çiftliklerde hayvan takibini kolaylaştırmak için geliştirilmiş bir PyQt6 uygulamasıdır.

## Özellikler

- Hayvan kaydı ve listeleme
- Tohumlama takibi
- Gebelik takibi
- Sağlık işlemleri takibi
- Detaylı raporlar

## Kurulum

1. Python 3.8 veya daha yeni bir sürüm yükleyin
2. Sanal ortam oluşturun (opsiyonel ama önerilir):
   ```bash
   python -m venv ciftlik_venv
   ```
3. Sanal ortamı aktifleştirin:
   - Windows:
     ```bash
     ciftlik_venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source ciftlik_venv/bin/activate
     ```
4. Gerekli paketleri yükleyin:
   ```bash
   pip install -r ciftlikpyqt/requirements.txt
   ```

## Kullanım

1. Ana dizinde aşağıdaki komutu çalıştırın:
   ```bash
   python ciftlikpyqt/main.py
   ```
2. Uygulama başlatıldığında ana menüden istediğiniz modülü seçin

## Veritabanı Yapısı

Uygulama SQLite veritabanı kullanır. İlk çalıştırma otomatik olarak aşağıdaki tabloları oluşturur:

- `hayvanlar`: Çiftlikteki hayvanların kayıtları
- `tohumlama`: Tohumlama işlemleri
- `gebelik`: Gebelik takibi
- `dogum`: Doğum kayıtları
- `saglik`: Sağlık işlemleri
- `bildirimler`: Sistem bildirimleri

## Sorun Giderme

### PyQt6 Kurulum Sorunu

Eğer PyQt6 ile ilgili bir kurulum veya çalıştırma sorunu yaşarsanız, alternatif olarak PySide6 paketini kullanmayı deneyebilirsiniz:

```bash
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PySide6
```

Ardından `main.py` dosyasındaki import ifadelerini PySide6 ile değiştirin:

```python
# Örnek: PyQt6 yerine PySide6 kullanımı
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget
```

### Platform Desteği

- Windows 10/11, macOS 10.14+, ve Linux'ta test edilmiştir
- macOS için Python'un sistem çapında yüklenmesi yerine, Homebrew veya Python.org adresinden indirilen Python sürümünü kullanmanız önerilir
