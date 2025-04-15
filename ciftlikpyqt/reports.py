import os
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from config import RAPOR_DIZINI
from database import DatabaseManager

class ReportGenerator:
    def __init__(self):
        if not os.path.exists(RAPOR_DIZINI):
            os.makedirs(RAPOR_DIZINI)
    
    def generate_excel_report(self, data, filename):
        """Excel raporu oluşturur"""
        df = pd.DataFrame(data)
        excel_path = os.path.join(RAPOR_DIZINI, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        df.to_excel(excel_path, index=False)
        return excel_path
    
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
        
        if format == 'excel':
            return self.generate_excel_report(data, 'hayvan_listesi')
        else:
            headers = ['Kulak Küpesi', 'Doğum Tarihi', 'Cinsiyet', 'Irk', 'Durum', 'Doğum Sayısı', 'Tohumlama Sayısı']
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
        
        if format == 'excel':
            return self.generate_excel_report(data, 'saglik_raporu')
        else:
            headers = ['Kulak Küpesi', 'İşlem Tarihi', 'İşlem Türü', 'İşlem Adı', 'Veteriner', 'İlaç Bilgisi', 'Maliyet']
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
        
        if format == 'excel':
            return self.generate_excel_report(data, 'maliyet_raporu')
        else:
            headers = ['Kulak Küpesi', 'Sağlık Maliyeti', 'Yem Maliyeti', 'Toplam Maliyet']
            return self.generate_pdf_report(data, headers, 'Maliyet Raporu', 'maliyet_raporu') 