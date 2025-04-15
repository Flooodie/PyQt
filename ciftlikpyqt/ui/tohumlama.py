from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDateEdit, QComboBox, QFormLayout)
from PyQt6.QtCore import Qt, QDate
from database import DatabaseManager

class Tohumlama(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Tohumlama Takibi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(baslik)
        
        # Form
        form_layout = QFormLayout()
        
        # Hayvan Seçimi
        self.hayvan_input = QComboBox()
        self.load_hayvanlar()
        form_layout.addRow("Hayvan:", self.hayvan_input)
        
        # Tohumlama Tarihi
        self.tarih_input = QDateEdit()
        self.tarih_input.setCalendarPopup(True)
        self.tarih_input.setDate(QDate.currentDate())
        form_layout.addRow("Tohumlama Tarihi:", self.tarih_input)
        
        # Boğa Bilgisi
        self.boga_input = QLineEdit()
        form_layout.addRow("Boğa Bilgisi:", self.boga_input)
        
        # Yöntem
        self.yontem_input = QComboBox()
        self.yontem_input.addItems(["Suni Tohumlama", "Doğal Aşım"])
        form_layout.addRow("Yöntem:", self.yontem_input)
        
        # Veteriner
        self.veteriner_input = QLineEdit()
        form_layout.addRow("Veteriner:", self.veteriner_input)
        
        # Notlar
        self.notlar_input = QLineEdit()
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Hayvan", "Tohumlama Tarihi", "Boğa Bilgisi",
            "Yöntem", "Veteriner", "Başarı Durumu"
        ])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_hayvanlar(self):
        """Dişi hayvanları combobox'a yükler"""
        query = "SELECT id, kulak_kupesi FROM hayvanlar WHERE cinsiyet = 'Dişi'"
        hayvanlar = DatabaseManager.execute_query(query)
        
        self.hayvan_input.clear()
        for hayvan in hayvanlar:
            self.hayvan_input.addItem(f"{hayvan['kulak_kupesi']} (ID: {hayvan['id']})", hayvan['id'])
    
    def kaydet(self):
        """Yeni tohumlama kaydı oluşturur"""
        try:
            # Form verilerini al
            data = {
                'hayvan_id': self.hayvan_input.currentData(),
                'tohumlama_tarihi': self.tarih_input.date().toString("yyyy-MM-dd"),
                'boga_bilgisi': self.boga_input.text(),
                'yontem': self.yontem_input.currentText(),
                'veteriner': self.veteriner_input.text(),
                'notlar': self.notlar_input.text(),
                'basari_durumu': 'Beklemede'
            }
            
            # Validasyon
            if not data['hayvan_id']:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir hayvan seçin!")
                return
            
            if not data['boga_bilgisi']:
                QMessageBox.warning(self, "Uyarı", "Lütfen boğa bilgisini girin!")
                return
            
            # Veritabanına kaydet
            tohumlama_id = DatabaseManager.insert_data('tohumlama', data)
            
            if tohumlama_id:
                QMessageBox.information(self, "Başarılı", "Tohumlama kaydı başarıyla oluşturuldu!")
                self.load_data()  # Tabloyu güncelle
                self.temizle_form()  # Formu temizle
            else:
                QMessageBox.critical(self, "Hata", "Kayıt oluşturulurken bir hata oluştu!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")
    
    def load_data(self):
        """Mevcut tohumlama kayıtlarını tabloya yükler"""
        try:
            query = '''
                SELECT t.*, h.kulak_kupesi
                FROM tohumlama t
                JOIN hayvanlar h ON t.hayvan_id = h.id
                ORDER BY t.tohumlama_tarihi DESC
            '''
            data = DatabaseManager.execute_query(query)
            
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(row['kulak_kupesi']))
                self.table.setItem(i, 2, QTableWidgetItem(row['tohumlama_tarihi']))
                self.table.setItem(i, 3, QTableWidgetItem(row['boga_bilgisi']))
                self.table.setItem(i, 4, QTableWidgetItem(row['yontem']))
                self.table.setItem(i, 5, QTableWidgetItem(row['veteriner'] or ''))
                self.table.setItem(i, 6, QTableWidgetItem(row['basari_durumu']))
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu: {str(e)}")
    
    def temizle_form(self):
        """Form alanlarını temizler"""
        self.tarih_input.setDate(QDate.currentDate())
        self.boga_input.clear()
        self.yontem_input.setCurrentIndex(0)
        self.veteriner_input.clear()
        self.notlar_input.clear() 