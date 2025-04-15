import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from database import DatabaseManager

class NotificationManager:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
    async def send_telegram_message(self, message):
        """Telegram üzerinden mesaj gönderir"""
        try:
            await self.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            return True
        except Exception as e:
            print(f"Telegram mesajı gönderilirken hata oluştu: {str(e)}")
            return False
    
    def create_notification(self, hayvan_id, bildirim_turu, bildirim_tarihi, mesaj):
        """Veritabanına bildirim ekler"""
        data = {
            'hayvan_id': hayvan_id,
            'bildirim_turu': bildirim_turu,
            'bildirim_tarihi': bildirim_tarihi,
            'mesaj': mesaj
        }
        return DatabaseManager.insert_data('bildirimler', data)
    
    def check_notifications(self):
        """Bekleyen bildirimleri kontrol eder ve gönderir"""
        today = datetime.now().date()
        query = '''
            SELECT b.*, h.kulak_kupesi 
            FROM bildirimler b
            JOIN hayvanlar h ON b.hayvan_id = h.id
            WHERE b.bildirim_tarihi <= ? AND b.durum = 'Beklemede'
        '''
        notifications = DatabaseManager.execute_query(query, (today,))
        
        if notifications:
            for notification in notifications:
                message = f"🔔 Bildirim: {notification['kulak_kupesi']} numaralı hayvan için {notification['bildirim_turu']}\n\n{notification['mesaj']}"
                
                # Telegram mesajını gönder
                asyncio.run(self.send_telegram_message(message))
                
                # Bildirim durumunu güncelle
                DatabaseManager.update_data(
                    'bildirimler',
                    {'durum': 'Gönderildi'},
                    {'id': notification['id']}
                )
    
    def check_gebelik_bildirimleri(self):
        """Gebelik durumlarını kontrol eder ve bildirim oluşturur"""
        query = '''
            SELECT g.*, h.kulak_kupesi 
            FROM gebelik g
            JOIN hayvanlar h ON g.hayvan_id = h.id
            WHERE g.durum = 'Devam Ediyor'
        '''
        gebelikler = DatabaseManager.execute_query(query)
        
        if gebelikler:
            today = datetime.now().date()
            for gebelik in gebelikler:
                tahmini_dogum = datetime.strptime(gebelik['tahmini_dogum_tarihi'], '%Y-%m-%d').date()
                kalan_gun = (tahmini_dogum - today).days
                
                if kalan_gun <= 7:
                    mesaj = f"⚠️ {gebelik['kulak_kupesi']} numaralı hayvanın tahmini doğum tarihine {kalan_gun} gün kaldı!"
                    self.create_notification(
                        gebelik['hayvan_id'],
                        'Gebelik Uyarısı',
                        today,
                        mesaj
                    )
    
    def check_asi_bildirimleri(self):
        """Aşı tekrarlarını kontrol eder ve bildirim oluşturur"""
        query = '''
            SELECT s.*, h.kulak_kupesi 
            FROM saglik s
            JOIN hayvanlar h ON s.hayvan_id = h.id
            WHERE s.tekrar_tarihi IS NOT NULL
        '''
        asilar = DatabaseManager.execute_query(query)
        
        if asilar:
            today = datetime.now().date()
            for asi in asilar:
                tekrar_tarihi = datetime.strptime(asi['tekrar_tarihi'], '%Y-%m-%d').date()
                kalan_gun = (tekrar_tarihi - today).days
                
                if kalan_gun <= 7:
                    mesaj = f"💉 {asi['kulak_kupesi']} numaralı hayvanın {asi['islem_adi']} tekrarına {kalan_gun} gün kaldı!"
                    self.create_notification(
                        asi['hayvan_id'],
                        'Aşı Hatırlatma',
                        today,
                        mesaj
                    )
    
    def run_daily_checks(self):
        """Günlük kontrolleri gerçekleştirir"""
        self.check_gebelik_bildirimleri()
        self.check_asi_bildirimleri()
        self.check_notifications() 