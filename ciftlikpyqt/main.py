#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, 
                            QVBoxLayout, QWidget)

from database import create_database
from ui.anasayfa import Anasayfa
from ui.hayvan_kayit import HayvanKayit
from ui.tohumlama import Tohumlama
from ui.gebelik import Gebelik
from ui.saglik import Saglik
from reports import RaporlarWidget

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çiftlik Yönetim Sistemi")
        self.resize(1024, 768)
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Sayfalar için StackedWidget
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)
        
        # Sayfaları oluştur ve ekle
        self.anasayfa = Anasayfa(self)
        self.hayvan_kayit = HayvanKayit(self)
        self.tohumlama = Tohumlama(self)
        self.gebelik = Gebelik(self)
        self.saglik = Saglik(self)
        self.raporlar = RaporlarWidget(self)
        
        # Sayfaları stack'e ekle
        self.stacked_widget.addWidget(self.anasayfa)  # Index 0
        self.stacked_widget.addWidget(self.hayvan_kayit)  # Index 1
        self.stacked_widget.addWidget(self.tohumlama)  # Index 2
        self.stacked_widget.addWidget(self.gebelik)  # Index 3
        self.stacked_widget.addWidget(self.saglik)  # Index 4
        self.stacked_widget.addWidget(self.raporlar)  # Index 5
        
        # Başlangıçta anasayfayı göster
        self.stacked_widget.setCurrentIndex(0)
    
    def sayfa_degistir(self, index):
        """Belirtilen indexteki sayfaya geçiş yapar"""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
    
    def anasayfaya_don(self):
        """Anasayfaya dönüş yapar"""
        self.stacked_widget.setCurrentIndex(0)

def main():
    # Veritabanını oluştur
    create_database()
    
    # Uygulamayı başlat
    app = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 