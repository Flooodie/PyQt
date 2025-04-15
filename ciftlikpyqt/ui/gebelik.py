from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDateEdit, QComboBox, QFormLayout)
from PyQt6.QtCore import Qt, QDate
from database import DatabaseManager
from datetime import datetime, timedelta

class Gebelik(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Gebelik Takibi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(baslik)
        
        # Form
        form_layout = QFormLayout()
        
        # Tohumlama Seçimi
        self.tohumlama_input = QComboBox()
        self.load_tohumlama_kayitlari()
        form_layout.addRow("Tohumlama Kaydı:", self.tohumlama_input)
        
        # Tespit Tarihi
        self.tespit_tarihi_input = QDateEdit()
        self.tespit_tarihi_input.setCalendarPopup(True)
        self.tespit_tarihi_input.setDate(QDate.currentDate())
        form_layout.addRow("Tespit Tarihi:", self.tespit_tarihi_input)
        
        # Tahmini Doğum Tarihi (otomatik hesaplanır)
        self.tahmini_dogum_tarihi = QLabel()
        form_layout.addRow("Tahmini Doğum:", self.tahmini_dogum_tarihi)
        
        # Tespit tarihini değiştirince tahmini doğum tarihini güncelle
        self.tespit_tarihi_input.dateChanged.connect(self.hesapla_tahmini_dogum)
        
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
            "ID", "Hayvan", "Tohumlama Tarihi", "Tespit Tarihi",
            "Tahmini Doğum", "Durum", "Notlar"
        ])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # İlk tahmini doğum tarihini hesapla
        self.hesapla_tahmini_dogum()
    
    def load_tohumlama_kayitlari(self):
        """Beklemedeki tohumlama kayıtlarını combobox'a yükler"""
        query = '''
            SELECT t.id, t.tohumlama_tarihi, h.kulak_kupesi
            FROM tohumlama t
            JOIN hayvanlar h ON t.hayvan_id = h.id
            WHERE t.basari_durumu = 'Beklemede'
            AND NOT EXISTS (
                SELECT 1 FROM gebelik g WHERE g.tohumlama_id = t.id
            )
            ORDER BY t.tohumlama_tarihi DESC
        '''
        tohumlamalar = DatabaseManager.execute_query(query)
        
        self.tohumlama_input.clear()
        for t in tohumlamalar:
            self.tohumlama_input.addItem(
                f"{t['kulak_kupesi']} - {t['tohumlama_tarihi']} (ID: {t['id']})",
                t['id']
            )
    
    def hesapla_tahmini_dogum(self):
        """Tespit tarihine göre tahmini doğum tarihini hesaplar"""
        tespit_tarihi = self.tespit_tarihi_input.date().toPyDate()
        tahmini_dogum = tespit_tarihi + timedelta(days=280)  # Yaklaşık 280 gün
        self.tahmini_dogum_tarihi.setText(tahmini_dogum.strftime("%Y-%m-%d"))
    
    def kaydet(self):
        """Yeni gebelik kaydı oluşturur"""
        try:
            tohumlama_id = self.tohumlama_input.currentData()
            if not tohumlama_id:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir tohumlama kaydı seçin!")
                return
            
            # Tohumlama kaydından hayvan ID'sini al
            query = "SELECT hayvan_id FROM tohumlama WHERE id = ?"
            result = DatabaseManager.execute_query(query, (tohumlama_id,))
            if not result:
                QMessageBox.warning(self, "Uyarı", "Tohumlama kaydı bulunamadı!")
                return
            
            hayvan_id = result[0]['hayvan_id']
            
            # Form verilerini al
            data = {
                'hayvan_id': hayvan_id,
                'tohumlama_id': tohumlama_id,
                'tespit_tarihi': self.tespit_tarihi_input.date().toString("yyyy-MM-dd"),
                'tahmini_dogum_tarihi': self.tahmini_dogum_tarihi.text(),
                'durum': 'Devam Ediyor',
                'notlar': self.notlar_input.text()
            }
            
            # Veritabanına kaydet
            gebelik_id = DatabaseManager.insert_data('gebelik', data)
            
            if gebelik_id:
                # Tohumlama kaydının durumunu güncelle
                DatabaseManager.update_data(
                    'tohumlama',
                    {'basari_durumu': 'Başarılı'},
                    {'id': tohumlama_id}
                )
                
                QMessageBox.information(self, "Başarılı", "Gebelik kaydı başarıyla oluşturuldu!")
                self.load_data()  # Tabloyu güncelle
                self.load_tohumlama_kayitlari()  # Tohumlama listesini güncelle
                self.temizle_form()  # Formu temizle
            else:
                QMessageBox.critical(self, "Hata", "Kayıt oluşturulurken bir hata oluştu!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")
    
    def load_data(self):
        """Mevcut gebelik kayıtlarını tabloya yükler"""
        try:
            query = '''
                SELECT g.*, h.kulak_kupesi, t.tohumlama_tarihi
                FROM gebelik g
                JOIN hayvanlar h ON g.hayvan_id = h.id
                JOIN tohumlama t ON g.tohumlama_id = t.id
                ORDER BY g.tespit_tarihi DESC
            '''
            data = DatabaseManager.execute_query(query)
            
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(row['kulak_kupesi']))
                self.table.setItem(i, 2, QTableWidgetItem(row['tohumlama_tarihi']))
                self.table.setItem(i, 3, QTableWidgetItem(row['tespit_tarihi']))
                self.table.setItem(i, 4, QTableWidgetItem(row['tahmini_dogum_tarihi']))
                self.table.setItem(i, 5, QTableWidgetItem(row['durum']))
                self.table.setItem(i, 6, QTableWidgetItem(row['notlar'] or ''))
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu: {str(e)}")
    
    def temizle_form(self):
        """Form alanlarını temizler"""
        self.tespit_tarihi_input.setDate(QDate.currentDate())
        self.notlar_input.clear() 