from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class Anasayfa(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Çiftlik Takip Sistemi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(baslik)
        
        # Buton container
        button_container = QVBoxLayout()
        button_container.setSpacing(20)
        
        # Butonlar ve açıklamaları
        butonlar = [
            ("Hayvan Kayıt", "Yeni hayvan kaydı ve hayvan listesi", 1),
            ("Tohumlama Takibi", "Tohumlama kayıtları ve takibi", 2),
            ("Gebelik Takibi", "Gebelik durumu ve doğum takibi", 3),
            ("Sağlık Takibi", "Aşı, tedavi ve sağlık kayıtları", 4),
            ("Raporlar", "Detaylı raporlar ve analizler", 5)
        ]
        
        for text, desc, page_index in butonlar:
            # Her buton için container
            btn_container = QHBoxLayout()
            
            # Buton
            btn = QPushButton(text)
            btn.setMinimumSize(200, 60)
            btn.setFont(QFont('Arial', 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #2574a9;
                }
            """)
            btn.clicked.connect(lambda checked, index=page_index: self.parent.sayfa_degistir(index))
            
            # Açıklama
            desc_label = QLabel(desc)
            desc_label.setFont(QFont('Arial', 10))
            desc_label.setStyleSheet("color: #7f8c8d;")
            
            btn_container.addWidget(btn)
            btn_container.addWidget(desc_label)
            btn_container.addStretch()
            
            button_container.addLayout(btn_container)
        
        # Butonları ana layout'a ekle
        layout.addLayout(button_container)
        
        # Alt boşluk
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.setLayout(layout) 