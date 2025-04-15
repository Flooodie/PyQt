import os
import csv
import sqlite3
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PyQt6.QtWidgets import QWidget
from config import RAPOR_DIZINI, DATABASE_NAME
from database import DatabaseManager

class ReportGenerator:
    def __init__(self):
        if not os.path.exists(RAPOR_DIZINI):
            os.makedirs(RAPOR_DIZINI)
    
    def generate_csv_report(self, data, headers, filename):
        """CSV raporu oluşturur"""
        csv_path = os.path.join(RAPOR_DIZINI, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        return csv_path
    
    def generate_pdf_report(self, data, headers, title, filename):
        """PDF raporu oluşturur"""
        pdf_path = os.path.join(RAPOR_DIZINI, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        
        # Başlık stili
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        elements.append(Paragraph(title, title_style))
        
        # Tablo verilerini hazırla
        table_data = [headers]
        for row in data:
            table_data.append([str(item) for item in row])
        
        # Tablo oluştur
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        return pdf_path
    
    def hayvan_listesi_raporu(self, format='excel'):
        """Hayvan listesi raporu oluşturur"""
        query = '''
            SELECT 
                h.kulak_kupesi,
                h.dogum_tarihi,
                h.cinsiyet,
                h.irk,
                h.durum,
                (SELECT COUNT(*) FROM dogum d WHERE d.anne_id = h.id) as dogum_sayisi,
                (SELECT COUNT(*) FROM tohumlama t WHERE t.hayvan_id = h.id) as tohumlama_sayisi
            FROM hayvanlar h
        '''
        data = DatabaseManager.execute_query(query)
        
        headers = ['Kulak Küpesi', 'Doğum Tarihi', 'Cinsiyet', 'Irk', 'Durum', 'Doğum Sayısı', 'Tohumlama Sayısı']
        
        if format == 'excel':
            return self.generate_csv_report(data, headers, 'hayvan_listesi')
        else:
            return self.generate_pdf_report(data, headers, 'Hayvan Listesi Raporu', 'hayvan_listesi')
    
    def saglik_raporu(self, baslangic_tarihi, bitis_tarihi, format='excel'):
        """Sağlık işlemleri raporu oluşturur"""
        query = '''
            SELECT 
                h.kulak_kupesi,
                s.islem_tarihi,
                s.islem_turu,
                s.islem_adi,
                s.veteriner,
                s.ilac_bilgisi,
                s.maliyet
            FROM saglik s
            JOIN hayvanlar h ON s.hayvan_id = h.id
            WHERE s.islem_tarihi BETWEEN ? AND ?
            ORDER BY s.islem_tarihi DESC
        '''
        data = DatabaseManager.execute_query(query, (baslangic_tarihi, bitis_tarihi))
        
        headers = ['Kulak Küpesi', 'İşlem Tarihi', 'İşlem Türü', 'İşlem Adı', 'Veteriner', 'İlaç Bilgisi', 'Maliyet']
        
        if format == 'excel':
            return self.generate_csv_report(data, headers, 'saglik_raporu')
        else:
            return self.generate_pdf_report(data, headers, 'Sağlık İşlemleri Raporu', 'saglik_raporu')
    
    def maliyet_raporu(self, baslangic_tarihi, bitis_tarihi, format='excel'):
        """Maliyet raporu oluşturur"""
        query = '''
            SELECT 
                h.kulak_kupesi,
                COALESCE(SUM(s.maliyet), 0) as saglik_maliyeti,
                COALESCE(SUM(y.maliyet), 0) as yem_maliyeti,
                COALESCE(SUM(s.maliyet), 0) + COALESCE(SUM(y.maliyet), 0) as toplam_maliyet
            FROM hayvanlar h
            LEFT JOIN saglik s ON h.id = s.hayvan_id AND s.islem_tarihi BETWEEN ? AND ?
            LEFT JOIN yem_tuketim y ON h.id = y.hayvan_id AND y.tarih BETWEEN ? AND ?
            GROUP BY h.id, h.kulak_kupesi
        '''
        data = DatabaseManager.execute_query(query, (baslangic_tarihi, bitis_tarihi, baslangic_tarihi, bitis_tarihi))
        
        headers = ['Kulak Küpesi', 'Sağlık Maliyeti', 'Yem Maliyeti', 'Toplam Maliyet']
        
        if format == 'excel':
            return self.generate_csv_report(data, headers, 'maliyet_raporu')
        else:
            return self.generate_pdf_report(data, headers, 'Maliyet Raporu', 'maliyet_raporu')

class RaporlarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.report_generator = ReportGenerator()
        self.init_ui()
    
    def init_ui(self):
        from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                                   QLabel, QComboBox, QDateEdit, QGroupBox,
                                   QRadioButton, QMessageBox, QSpacerItem,
                                   QSizePolicy)
        from PyQt6.QtCore import Qt, QDate
        from PyQt6.QtGui import QFont
        
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Raporlar")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(baslik)
        
        # Rapor tipleri için üst grup kutusu
        rapor_tipleri_grup = QGroupBox("Rapor Tipi")
        rapor_tipleri_layout = QVBoxLayout()
        
        # Rapor tipleri
        self.rapor_tipi_combo = QComboBox()
        self.rapor_tipi_combo.addItems([
            "Hayvan Listesi", 
            "Sağlık Raporu", 
            "Maliyet Raporu"
        ])
        rapor_tipleri_layout.addWidget(self.rapor_tipi_combo)
        
        rapor_tipleri_grup.setLayout(rapor_tipleri_layout)
        layout.addWidget(rapor_tipleri_grup)
        
        # Tarih aralığı grup kutusu
        self.tarih_grup = QGroupBox("Tarih Aralığı")
        tarih_layout = QHBoxLayout()
        
        # Başlangıç tarihi
        baslangic_label = QLabel("Başlangıç:")
        self.baslangic_date = QDateEdit()
        self.baslangic_date.setDate(QDate.currentDate().addMonths(-1))
        self.baslangic_date.setCalendarPopup(True)
        
        # Bitiş tarihi
        bitis_label = QLabel("Bitiş:")
        self.bitis_date = QDateEdit()
        self.bitis_date.setDate(QDate.currentDate())
        self.bitis_date.setCalendarPopup(True)
        
        tarih_layout.addWidget(baslangic_label)
        tarih_layout.addWidget(self.baslangic_date)
        tarih_layout.addWidget(bitis_label)
        tarih_layout.addWidget(self.bitis_date)
        
        self.tarih_grup.setLayout(tarih_layout)
        layout.addWidget(self.tarih_grup)
        
        # Format seçim grup kutusu
        format_grup = QGroupBox("Rapor Formatı")
        format_layout = QHBoxLayout()
        
        self.excel_radio = QRadioButton("Excel")
        self.excel_radio.setChecked(True)
        self.pdf_radio = QRadioButton("PDF")
        
        format_layout.addWidget(self.excel_radio)
        format_layout.addWidget(self.pdf_radio)
        
        format_grup.setLayout(format_layout)
        layout.addWidget(format_grup)
        
        # Butonlar
        butonlar_layout = QHBoxLayout()
        
        geri_btn = QPushButton("Anasayfaya Dön")
        geri_btn.clicked.connect(self.parent.anasayfaya_don)
        
        rapor_btn = QPushButton("Rapor Oluştur")
        rapor_btn.clicked.connect(self.rapor_olustur)
        
        butonlar_layout.addWidget(geri_btn)
        butonlar_layout.addWidget(rapor_btn)
        
        layout.addLayout(butonlar_layout)
        
        # Alt boşluk
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.rapor_tipi_combo.currentIndexChanged.connect(self.rapor_tipi_degisti)
        self.rapor_tipi_degisti()  # İlk durum ayarı
        
        self.setLayout(layout)
    
    def rapor_tipi_degisti(self):
        rapor_tipi = self.rapor_tipi_combo.currentText()
        
        # Hayvan listesi raporu için tarihe gerek yok
        if rapor_tipi == "Hayvan Listesi":
            self.tarih_grup.setEnabled(False)
        else:
            self.tarih_grup.setEnabled(True)
    
    def rapor_olustur(self):
        try:
            from PyQt6.QtWidgets import QMessageBox
            import os
            
            rapor_tipi = self.rapor_tipi_combo.currentText()
            format_tipi = 'excel' if self.excel_radio.isChecked() else 'pdf'
            
            rapor_dosyasi = None
            
            if rapor_tipi == "Hayvan Listesi":
                rapor_dosyasi = self.report_generator.hayvan_listesi_raporu(format=format_tipi)
            else:
                baslangic = self.baslangic_date.date().toString("yyyy-MM-dd")
                bitis = self.bitis_date.date().toString("yyyy-MM-dd")
                
                if rapor_tipi == "Sağlık Raporu":
                    rapor_dosyasi = self.report_generator.saglik_raporu(baslangic, bitis, format=format_tipi)
                elif rapor_tipi == "Maliyet Raporu":
                    rapor_dosyasi = self.report_generator.maliyet_raporu(baslangic, bitis, format=format_tipi)
            
            if rapor_dosyasi:
                QMessageBox.information(
                    self,
                    "Rapor Oluşturuldu",
                    f"Rapor başarıyla oluşturuldu:\n{rapor_dosyasi}",
                    QMessageBox.StandardButton.Ok
                )
                # Dosyayı aç
                if os.name == 'nt':  # Windows
                    os.startfile(rapor_dosyasi)
                elif os.name == 'posix':  # macOS ve Linux
                    import subprocess
                    subprocess.call(('open' if os.name == 'darwin' else 'xdg-open', rapor_dosyasi))
            else:
                QMessageBox.warning(
                    self,
                    "Hata",
                    "Rapor oluşturulurken bir hata oluştu.",
                    QMessageBox.StandardButton.Ok
                )
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Hata",
                f"Rapor oluşturulurken bir hata oluştu:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            ) 