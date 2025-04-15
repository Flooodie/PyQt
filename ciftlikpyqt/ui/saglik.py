from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDateEdit, QComboBox, QFormLayout,
                             QSpinBox, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from database import DatabaseManager

class Saglik(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Sağlık Takibi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(baslik)
        
        # Form
        form_layout = QFormLayout()
        
        # Hayvan Seçimi
        self.hayvan_input = QComboBox()
        self.load_hayvanlar()
        form_layout.addRow("Hayvan:", self.hayvan_input)
        
        # İşlem Tarihi
        self.tarih_input = QDateEdit()
        self.tarih_input.setCalendarPopup(True)
        self.tarih_input.setDate(QDate.currentDate())
        form_layout.addRow("İşlem Tarihi:", self.tarih_input)
        
        # İşlem Türü
        self.islem_turu_input = QComboBox()
        self.islem_turu_input.addItems([
            "Aşı", "Tedavi", "Kontrol", "Doğum Sonrası Bakım",
            "Parazit İlacı", "Vitamin", "Diğer"
        ])
        form_layout.addRow("İşlem Türü:", self.islem_turu_input)
        
        # İşlem Adı
        self.islem_adi_input = QLineEdit()
        form_layout.addRow("İşlem Adı:", self.islem_adi_input)
        
        # Veteriner
        self.veteriner_input = QLineEdit()
        form_layout.addRow("Veteriner:", self.veteriner_input)
        
        # İlaç Bilgisi
        self.ilac_input = QLineEdit()
        form_layout.addRow("İlaç Bilgisi:", self.ilac_input)
        
        # Doz
        self.doz_input = QLineEdit()
        form_layout.addRow("Doz:", self.doz_input)
        
        # Tekrar Tarihi
        self.tekrar_tarihi_input = QDateEdit()
        self.tekrar_tarihi_input.setCalendarPopup(True)
        self.tekrar_tarihi_input.setDate(QDate.currentDate().addDays(30))
        form_layout.addRow("Tekrar Tarihi:", self.tekrar_tarihi_input)
        
        # Maliyet
        self.maliyet_input = QSpinBox()
        self.maliyet_input.setRange(0, 1000000)
        self.maliyet_input.setSuffix(" TL")
        form_layout.addRow("Maliyet:", self.maliyet_input)
        
        # Notlar
        self.notlar_input = QTextEdit()
        self.notlar_input.setMaximumHeight(100)
        form_layout.addRow("Notlar:", self.notlar_input)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        # Kaydet butonu
        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        kaydet_btn.clicked.connect(self.kaydet)
        button_layout.addWidget(kaydet_btn)
        
        # Ana sayfaya dön butonu
        don_btn = QPushButton("Ana Sayfaya Dön")
        don_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        don_btn.clicked.connect(lambda: self.parent.sayfa_degistir(0))
        button_layout.addWidget(don_btn)
        
        layout.addLayout(button_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Hayvan", "İşlem Tarihi", "İşlem Türü", "İşlem Adı",
            "Veteriner", "İlaç", "Tekrar Tarihi", "Maliyet"
        ])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_hayvanlar(self):
        """Aktif hayvanları combobox'a yükler"""
        query = "SELECT id, kulak_kupesi FROM hayvanlar WHERE durum = 'Aktif'"
        hayvanlar = DatabaseManager.execute_query(query)
        
        self.hayvan_input.clear()
        for hayvan in hayvanlar:
            self.hayvan_input.addItem(f"{hayvan['kulak_kupesi']} (ID: {hayvan['id']})", hayvan['id'])
    
    def kaydet(self):
        """Yeni sağlık kaydı oluşturur"""
        try:
            # Form verilerini al
            data = {
                'hayvan_id': self.hayvan_input.currentData(),
                'islem_tarihi': self.tarih_input.date().toString("yyyy-MM-dd"),
                'islem_turu': self.islem_turu_input.currentText(),
                'islem_adi': self.islem_adi_input.text(),
                'veteriner': self.veteriner_input.text(),
                'ilac_bilgisi': self.ilac_input.text(),
                'doz': self.doz_input.text(),
                'tekrar_tarihi': self.tekrar_tarihi_input.date().toString("yyyy-MM-dd"),
                'maliyet': self.maliyet_input.value(),
                'notlar': self.notlar_input.toPlainText()
            }
            
            # Validasyon
            if not data['hayvan_id']:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir hayvan seçin!")
                return
            
            if not data['islem_adi']:
                QMessageBox.warning(self, "Uyarı", "Lütfen işlem adını girin!")
                return
            
            # Veritabanına kaydet
            saglik_id = DatabaseManager.insert_data('saglik', data)
            
            if saglik_id:
                QMessageBox.information(self, "Başarılı", "Sağlık kaydı başarıyla oluşturuldu!")
                self.load_data()  # Tabloyu güncelle
                self.temizle_form()  # Formu temizle
            else:
                QMessageBox.critical(self, "Hata", "Kayıt oluşturulurken bir hata oluştu!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")
    
    def load_data(self):
        """Mevcut sağlık kayıtlarını tabloya yükler"""
        try:
            query = '''
                SELECT s.*, h.kulak_kupesi
                FROM saglik s
                JOIN hayvanlar h ON s.hayvan_id = h.id
                ORDER BY s.islem_tarihi DESC
            '''
            data = DatabaseManager.execute_query(query)
            
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(row['kulak_kupesi']))
                self.table.setItem(i, 2, QTableWidgetItem(row['islem_tarihi']))
                self.table.setItem(i, 3, QTableWidgetItem(row['islem_turu']))
                self.table.setItem(i, 4, QTableWidgetItem(row['islem_adi']))
                self.table.setItem(i, 5, QTableWidgetItem(row['veteriner'] or ''))
                self.table.setItem(i, 6, QTableWidgetItem(row['ilac_bilgisi'] or ''))
                self.table.setItem(i, 7, QTableWidgetItem(row['tekrar_tarihi'] or ''))
                self.table.setItem(i, 8, QTableWidgetItem(f"{row['maliyet']} TL" if row['maliyet'] else ''))
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu: {str(e)}")
    
    def temizle_form(self):
        """Form alanlarını temizler"""
        self.tarih_input.setDate(QDate.currentDate())
        self.islem_turu_input.setCurrentIndex(0)
        self.islem_adi_input.clear()
        self.veteriner_input.clear()
        self.ilac_input.clear()
        self.doz_input.clear()
        self.tekrar_tarihi_input.setDate(QDate.currentDate().addDays(30))
        self.maliyet_input.setValue(0)
        self.notlar_input.clear() 