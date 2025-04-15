import sqlite3
from datetime import datetime
from config import DATABASE_NAME

def create_database():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Hayvanlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hayvanlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kulak_kupesi TEXT UNIQUE NOT NULL,
                dogum_tarihi DATE NOT NULL,
                cinsiyet TEXT NOT NULL,
                irk TEXT NOT NULL,
                anne_id INTEGER,
                baba_id INTEGER,
                durum TEXT DEFAULT 'Aktif',
                notlar TEXT,
                FOREIGN KEY (anne_id) REFERENCES hayvanlar (id),
                FOREIGN KEY (baba_id) REFERENCES hayvanlar (id)
            )
        ''')
        
        # Tohumlama tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tohumlama (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hayvan_id INTEGER NOT NULL,
                tohumlama_tarihi DATE NOT NULL,
                boga_bilgisi TEXT NOT NULL,
                yontem TEXT NOT NULL,
                veteriner TEXT,
                basari_durumu TEXT DEFAULT 'Beklemede',
                notlar TEXT,
                FOREIGN KEY (hayvan_id) REFERENCES hayvanlar (id)
            )
        ''')
        
        # Gebelik tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gebelik (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hayvan_id INTEGER NOT NULL,
                tohumlama_id INTEGER NOT NULL,
                tespit_tarihi DATE NOT NULL,
                tahmini_dogum_tarihi DATE NOT NULL,
                durum TEXT DEFAULT 'Devam Ediyor',
                notlar TEXT,
                FOREIGN KEY (hayvan_id) REFERENCES hayvanlar (id),
                FOREIGN KEY (tohumlama_id) REFERENCES tohumlama (id)
            )
        ''')
        
        # Doğum tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dogum (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gebelik_id INTEGER NOT NULL,
                dogum_tarihi DATE NOT NULL,
                yavru_id INTEGER NOT NULL,
                dogum_tipi TEXT NOT NULL,
                komplikasyonlar TEXT,
                notlar TEXT,
                FOREIGN KEY (gebelik_id) REFERENCES gebelik (id),
                FOREIGN KEY (yavru_id) REFERENCES hayvanlar (id)
            )
        ''')
        
        # Sağlık tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saglik (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hayvan_id INTEGER NOT NULL,
                islem_tarihi DATE NOT NULL,
                islem_turu TEXT NOT NULL,
                islem_adi TEXT NOT NULL,
                veteriner TEXT,
                ilac_bilgisi TEXT,
                doz TEXT,
                tekrar_tarihi DATE,
                maliyet REAL,
                notlar TEXT,
                FOREIGN KEY (hayvan_id) REFERENCES hayvanlar (id)
            )
        ''')
        
        # Bildirimler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bildirimler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hayvan_id INTEGER NOT NULL,
                bildirim_turu TEXT NOT NULL,
                bildirim_tarihi DATE NOT NULL,
                durum TEXT DEFAULT 'Beklemede',
                mesaj TEXT,
                FOREIGN KEY (hayvan_id) REFERENCES hayvanlar (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Veritabanı başarıyla oluşturuldu!")
        
    except sqlite3.Error as e:
        print(f"Veritabanı oluşturulurken hata oluştu: {str(e)}")

def get_db_connection():
    """Veritabanı bağlantısı oluşturur ve cursor döndürür"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Sütun isimlerine erişim için
    return conn

class DatabaseManager:
    @staticmethod
    def execute_query(query, parameters=None):
        """SQL sorgusu çalıştırır ve sonuçları döndürür"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
                
            conn.commit()
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"Sorgu hatası: {str(e)}")
            return None

    @staticmethod
    def insert_data(table, data):
        """Belirtilen tabloya veri ekler"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
            
            cursor.execute(query, list(data.values()))
            conn.commit()
            last_id = cursor.lastrowid
            
            cursor.close()
            conn.close()
            return last_id
        except sqlite3.Error as e:
            print(f"Veri ekleme hatası: {str(e)}")
            return None

    @staticmethod
    def update_data(table, data, condition):
        """Belirtilen tablodaki veriyi günceller"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
            where_clause = ' AND '.join([f'{k} = ?' for k in condition.keys()])
            query = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
            
            values = list(data.values()) + list(condition.values())
            cursor.execute(query, values)
            
            conn.commit()
            affected_rows = cursor.rowcount
            
            cursor.close()
            conn.close()
            return affected_rows
        except sqlite3.Error as e:
            print(f"Güncelleme hatası: {str(e)}")
            return 0 