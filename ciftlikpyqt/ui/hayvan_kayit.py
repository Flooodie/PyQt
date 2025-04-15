from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDateEdit, QComboBox, QFormLayout)
from PyQt6.QtCore import Qt, QDate
from database import DatabaseManager

class HayvanKayit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Hayvan Kayıt")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(baslik)
        
        # Form
        form_layout = QFormLayout()
        
        # Kulak Küpesi
        self.kulak_kupesi_input = QLineEdit()
        form_layout.addRow("Kulak Küpesi:", self.kulak_kupesi_input)
        
        # Doğum Tarihi
        self.dogum_tarihi_input = QDateEdit()
        self.dogum_tarihi_input.setCalendarPopup(True)
        self.dogum_tarihi_input.setDate(QDate.currentDate())
        form_layout.addRow("Doğum Tarihi:", self.dogum_tarihi_input)
        
        # Cinsiyet
        self.cinsiyet_input = QComboBox()
        self.cinsiyet_input.addItems(["Dişi", "Erkek"])
        form_layout.addRow("Cinsiyet:", self.cinsiyet_input)
        
        # Irk
        self.irk_input = QComboBox()
        self.irk_input.addItems(["Holstein", "Simental", "Montofon", "Jersey", "Diğer"])
        form_layout.addRow("Irk:", self.irk_input)
        
        # Anne ID
        self.anne_id_input = QComboBox()
        self.anne_id_input.setEditable(True)
        self.load_anne_adaylari()
        form_layout.addRow("Anne:", self.anne_id_input)
        
        # Baba ID
        self.baba_id_input = QComboBox()
        self.baba_id_input.setEditable(True)
        self.load_baba_adaylari()
        form_layout.addRow("Baba:", self.baba_id_input)
        
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Kulak Küpesi", "Doğum Tarihi", "Cinsiyet", "Irk", 
            "Anne ID", "Baba ID", "Notlar"
        ])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_anne_adaylari(self):
        """Dişi hayvanları anne adayı olarak yükler"""
        query = "SELECT id, kulak_kupesi FROM hayvanlar WHERE cinsiyet = 'Dişi'"
        anneler = DatabaseManager.execute_query(query)
        
        self.anne_id_input.clear()
        self.anne_id_input.addItem("", None)  # Boş seçenek
        for anne in anneler:
            self.anne_id_input.addItem(f"{anne['kulak_kupesi']} (ID: {anne['id']})", anne['id'])
    
    def load_baba_adaylari(self):
        """Erkek hayvanları baba adayı olarak yükler"""
        query = "SELECT id, kulak_kupesi FROM hayvanlar WHERE cinsiyet = 'Erkek'"
        babalar = DatabaseManager.execute_query(query)
        
        self.baba_id_input.clear()
        self.baba_id_input.addItem("", None)  # Boş seçenek
        for baba in babalar:
            self.baba_id_input.addItem(f"{baba['kulak_kupesi']} (ID: {baba['id']})", baba['id'])
    
    def kaydet(self):
        """Yeni hayvan kaydı oluşturur"""
        try:
            # Form verilerini al
            data = {
                'kulak_kupesi': self.kulak_kupesi_input.text(),
                'dogum_tarihi': self.dogum_tarihi_input.date().toString("yyyy-MM-dd"),
                'cinsiyet': self.cinsiyet_input.currentText(),
                'irk': self.irk_input.currentText(),
                'anne_id': self.anne_id_input.currentData(),
                'baba_id': self.baba_id_input.currentData(),
                'notlar': self.notlar_input.text(),
                'durum': 'Aktif'
            }
            
            # Validasyon
            if not data['kulak_kupesi']:
                QMessageBox.warning(self, "Uyarı", "Lütfen kulak küpesi numarasını girin!")
                return
            
            # Veritabanına kaydet
            hayvan_id = DatabaseManager.insert_data('hayvanlar', data)
            
            if hayvan_id:
                QMessageBox.information(self, "Başarılı", "Hayvan kaydı başarıyla oluşturuldu!")
                self.load_data()  # Tabloyu güncelle
                self.temizle_form()  # Formu temizle
                
                # Anne/baba listelerini güncelle
                self.load_anne_adaylari()
                self.load_baba_adaylari()
            else:
                QMessageBox.critical(self, "Hata", "Kayıt oluşturulurken bir hata oluştu!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")
    
    def load_data(self):
        """Mevcut hayvan kayıtlarını tabloya yükler"""
        try:
            query = '''
                SELECT h.*, 
                    a.kulak_kupesi as anne_kupesi,
                    b.kulak_kupesi as baba_kupesi
                FROM hayvanlar h
                LEFT JOIN hayvanlar a ON h.anne_id = a.id
                LEFT JOIN hayvanlar b ON h.baba_id = b.id
            '''
            data = DatabaseManager.execute_query(query)
            
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(row['kulak_kupesi']))
                self.table.setItem(i, 2, QTableWidgetItem(row['dogum_tarihi']))
                self.table.setItem(i, 3, QTableWidgetItem(row['cinsiyet']))
                self.table.setItem(i, 4, QTableWidgetItem(row['irk']))
                self.table.setItem(i, 5, QTableWidgetItem(row['anne_kupesi'] or ''))
                self.table.setItem(i, 6, QTableWidgetItem(row['baba_kupesi'] or ''))
                self.table.setItem(i, 7, QTableWidgetItem(row['notlar'] or ''))
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu: {str(e)}")
    
    def temizle_form(self):
        """Form alanlarını temizler"""
        self.kulak_kupesi_input.clear()
        self.dogum_tarihi_input.setDate(QDate.currentDate())
        self.cinsiyet_input.setCurrentIndex(0)
        self.irk_input.setCurrentIndex(0)
        self.anne_id_input.setCurrentIndex(0)
        self.baba_id_input.setCurrentIndex(0)
        self.notlar_input.clear() 