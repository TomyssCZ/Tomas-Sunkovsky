# -*- coding: utf-8 -*-
import sys
import calendar
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QGridLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
                             QDialog, QLineEdit, QTextEdit, QComboBox, QTimeEdit,
                             QColorDialog, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, QTime, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QFont, QCursor, QColor

# ============================================================================
# DATABÁZE - Správa Událostí
# ============================================================================

class EventManager:
    """Správce událostí s SQLite databází"""
    
    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path  # Ulož jako string, ne jako Path
        self.init_db()
    
    def init_db(self):
        """Inicializace databáze a vytvoření tabulky"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    category TEXT,
                    color TEXT DEFAULT '#2563eb',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Chyba při otevírání databáze: {e}")
            print(f"Cesta: {self.db_path}")
    
    def add_event(self, title: str, description: str, date: str, 
                  start_time: str, end_time: str, category: str = "Personal", 
                  color: str = "#2563eb") -> int:
        """Přidání nové události. Vrací ID nové události."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO events (title, description, date, start_time, end_time, category, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, date, start_time, end_time, category, color))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def get_events_by_date(self, date_str: str) -> list:
        """Získá všechny události pro konkrétní den (format: YYYY-MM-DD)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, description, start_time, end_time, category, color
            FROM events
            WHERE date = ?
            ORDER BY start_time
        """, (date_str,))
        
        events = cursor.fetchall()
        conn.close()
        
        return events
    
    def get_events_by_month(self, year: int, month: int) -> dict:
        """Získá všechny události pro konkrétní měsíc. Vrací dict {date_str: [events]}"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_pattern = f"{year:04d}-{month:02d}%"
        
        cursor.execute("""
            SELECT date, id, title, description, start_time, end_time, category, color
            FROM events
            WHERE date LIKE ?
            ORDER BY date, start_time
        """, (date_pattern,))
        
        events_dict = {}
        for row in cursor.fetchall():
            date = row[0]
            event_data = row[1:]
            
            if date not in events_dict:
                events_dict[date] = []
            
            events_dict[date].append({
                'id': event_data[0],
                'title': event_data[1],
                'description': event_data[2],
                'start_time': event_data[3],
                'end_time': event_data[4],
                'category': event_data[5],
                'color': event_data[6]
            })
        
        conn.close()
        return events_dict
    
    def update_event(self, event_id: int, **kwargs) -> bool:
        """Aktualizace existující události"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        allowed_fields = {'title', 'description', 'date', 'start_time', 'end_time', 'category', 'color'}
        fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields_to_update:
            conn.close()
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in fields_to_update.keys()])
        values = list(fields_to_update.values()) + [event_id]
        
        cursor.execute(f"UPDATE events SET {set_clause} WHERE id = ?", values)
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def delete_event(self, event_id: int) -> bool:
        """Smazání události"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0

# ============================================================================
# EVENT DIALOG - Elegantní dialog pro přidání/editaci události
# ============================================================================

class EventDialog(QDialog):
    """Elegantní dialog pro přidání/editaci události"""
    
    def __init__(self, parent=None, event_manager=None, date_str=None, event_data=None):
        super().__init__(parent)
        self.event_manager = event_manager
        self.date_str = date_str
        self.event_data = event_data or {}
        self.event_id = event_data.get('id') if event_data else None
        self.on_save_callback = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializace UI dialogu"""
        self.setWindowTitle("Nová Událost" if not self.event_id else "Editace Události")
        self.setGeometry(100, 100, 500, 450)
        
        # Styly
        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QLineEdit, QTextEdit, QTimeEdit, QComboBox {
                background-color: #0f172a;
                border: 2px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #f8fafc;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QTimeEdit:focus, QComboBox:focus {
                border: 2px solid #2563eb;
            }
            QLabel { color: #94a3b8; font-weight: bold; font-size: 11px; }
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:pressed { background-color: #1e40af; }
        """)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setSpacing(12)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== Název Události ==========
        title_label = QLabel("Název Události:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Zadej název (např. Jednání, Schůzka)")
        self.title_input.setText(self.event_data.get('title', ''))
        self.title_input.setMinimumHeight(35)
        dialog_layout.addWidget(title_label)
        dialog_layout.addWidget(self.title_input)
        
        # ========== Popis Události ==========
        desc_label = QLabel("Popis:")
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Volitelný popis...")
        self.desc_input.setText(self.event_data.get('description', ''))
        self.desc_input.setMaximumHeight(80)
        dialog_layout.addWidget(desc_label)
        dialog_layout.addWidget(self.desc_input)
        
        # ========== Čas Od-Do ==========
        time_layout = QHBoxLayout()
        
        time_from_label = QLabel("Čas Od:")
        self.time_from = QTimeEdit()
        self.time_from.setTime(QTime.fromString(self.event_data.get('start_time', '09:00'), "hh:mm"))
        self.time_from.setDisplayFormat("hh:mm")
        time_layout.addWidget(time_from_label)
        time_layout.addWidget(self.time_from)
        
        time_to_label = QLabel("Čas Do:")
        self.time_to = QTimeEdit()
        self.time_to.setTime(QTime.fromString(self.event_data.get('end_time', '10:00'), "hh:mm"))
        self.time_to.setDisplayFormat("hh:mm")
        time_layout.addWidget(time_to_label)
        time_layout.addWidget(self.time_to)
        
        dialog_layout.addLayout(time_layout)
        
        # ========== Kategorie ==========
        category_label = QLabel("Kategorie:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Personal", "Work", "Birthday", "Holiday", "Other"])
        self.category_combo.setCurrentText(self.event_data.get('category', 'Personal'))
        dialog_layout.addWidget(category_label)
        dialog_layout.addWidget(self.category_combo)
        
        # ========== Barva ==========
        color_layout = QHBoxLayout()
        
        color_label = QLabel("Barva:")
        self.color_button = QPushButton()
        self.color_hex = self.event_data.get('color', '#2563eb')
        self.update_color_button()
        self.color_button.clicked.connect(self.open_color_picker)
        self.color_button.setMaximumWidth(60)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        dialog_layout.addLayout(color_layout)
        
        # ========== Tlačítka ==========
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("💾 Uložit")
        save_button.clicked.connect(self.save_event)
        
        delete_button = QPushButton("🗑️ Smazat")
        delete_button.setStyleSheet("""
            QPushButton { background-color: #dc2626; }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        delete_button.clicked.connect(self.delete_event)
        delete_button.setVisible(bool(self.event_id))
        
        cancel_button = QPushButton("❌ Zrušit")
        cancel_button.setStyleSheet("""
            QPushButton { background-color: #475569; }
            QPushButton:hover { background-color: #64748b; }
        """)
        cancel_button.clicked.connect(self.close)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        if self.event_id:
            buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(cancel_button)
        dialog_layout.addLayout(buttons_layout)
    
    def open_color_picker(self):
        """Otevření výběru barvy"""
        color = QColorDialog.getColor(QColor(self.color_hex), self, "Vyber barvu")
        if color.isValid():
            self.color_hex = color.name()
            self.update_color_button()
    
    def update_color_button(self):
        """Aktualizace vzhledu tlačítka barvy"""
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_hex};
                border: 2px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{ border: 2px solid #60a5fa; }}
        """)
    
    def save_event(self):
        """Uložení nebo aktualizace události"""
        title = self.title_input.text().strip()
        
        if not title:
            QMessageBox.warning(self, "Chyba", "Zadej název události!")
            return
        
        description = self.desc_input.toPlainText().strip()
        start_time = self.time_from.time().toString("hh:mm")
        end_time = self.time_to.time().toString("hh:mm")
        category = self.category_combo.currentText()
        color = self.color_hex
        
        if self.event_id:
            # Aktualizace existující události
            self.event_manager.update_event(
                self.event_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                category=category,
                color=color
            )
        else:
            # Vytvoření nové události
            self.event_manager.add_event(
                title=title,
                description=description,
                date=self.date_str,
                start_time=start_time,
                end_time=end_time,
                category=category,
                color=color
            )
        
        self.close()
        if self.on_save_callback:
            self.on_save_callback()
    
    def delete_event(self):
        """Smazání události"""
        reply = QMessageBox.question(self, "Potvrzení", "Opravdu chceš smazat tuto událost?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.event_manager.delete_event(self.event_id)
            self.close()
            if self.on_save_callback:
                self.on_save_callback()

# ============================================================================
# HLAVNÍ APLIKACE - Moderní Kalendář
# ============================================================================

class ModernCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📅 Moderní Kalendář")
        self.resize(1200, 800)
        
        # Aktuální datum pro zobrazení
        self.current_date = datetime.now()
        self.display_year = self.current_date.year
        self.display_month = self.current_date.month
        self.display_date = self.current_date
        
        # ✨ KROK 4: Režim zobrazení
        self.view_mode = "month"  # "month" nebo "week"
        
        # Inicializace správce událostí
        # Použij dočasnou složku nebo lokální adresář
        import tempfile
        import os
        db_path = os.path.join(tempfile.gettempdir(), "events.db")
        self.event_manager = EventManager(db_path)

        self.init_ui()

    def init_ui(self):
        # Hlavní widget a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Globální styly (Dark Mode, moderní vzhled)
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QWidget { color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif; }
            QPushButton {
                background-color: #334155; border: none; border-radius: 6px;
                padding: 8px 16px; font-weight: bold; color: white;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #1e293b; }
            #HeaderLabel { font-size: 24px; font-weight: bold; }
            #DayHeader { font-size: 14px; font-weight: bold; color: #94a3b8; }
            .DayCell {
                background-color: #1e293b; border-radius: 8px; padding: 10px;
            }
            .DayCell:hover { background-color: #334155; }
            .TodayCell {
                background-color: #2563eb; border-radius: 8px; padding: 10px;
            }
            .OtherMonthCell {
                background-color: #0f172a; color: #475569; border-radius: 8px;
            }
        """)

        # --- HLAVIČKA (Navigace) ---
        header_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("◀ Předchozí")
        self.btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_prev.clicked.connect(self.prev_period)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #334155; border: none; border-radius: 6px;
                padding: 8px 16px; font-weight: bold; color: white;
            }
            QPushButton:hover { 
                background-color: #475569; 
                border: 2px solid #2563eb;
            }
            QPushButton:pressed { background-color: #1e293b; }
        """)
        
        self.month_year_label = QLabel()
        self.month_year_label.setObjectName("HeaderLabel")
        self.month_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_next = QPushButton("Další ▶")
        self.btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_next.clicked.connect(self.next_period)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: #334155; border: none; border-radius: 6px;
                padding: 8px 16px; font-weight: bold; color: white;
            }
            QPushButton:hover { 
                background-color: #475569; 
                border: 2px solid #2563eb;
            }
            QPushButton:pressed { background-color: #1e293b; }
        """)
        
        self.btn_today = QPushButton("Dnes 📍")
        self.btn_today.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_today.clicked.connect(self.goto_today)
        self.btn_today.setStyleSheet("""
            QPushButton {
                background-color: #334155; border: none; border-radius: 6px;
                padding: 8px 16px; font-weight: bold; color: white;
            }
            QPushButton:hover { 
                background-color: #059669; 
                border: 2px solid #10b981;
            }
            QPushButton:pressed { background-color: #047857; }
        """)
        
        # ✨ KROK 4: Tlačítka pro přepínání pohledu
        self.btn_month_view = QPushButton("📅 Měsíc")
        self.btn_month_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_month_view.clicked.connect(self.set_month_view)
        self.btn_month_view.setStyleSheet("""
            QPushButton { background-color: #2563eb; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        
        self.btn_week_view = QPushButton("📋 Týden")
        self.btn_week_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_week_view.clicked.connect(self.set_week_view)

        header_layout.addWidget(self.btn_prev)
        header_layout.addStretch()
        header_layout.addWidget(self.month_year_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_today)
        header_layout.addWidget(self.btn_month_view)
        header_layout.addWidget(self.btn_week_view)
        header_layout.addWidget(self.btn_next)

        main_layout.addLayout(header_layout)

        # --- MŘÍŽKA KALENDÁŘE ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        main_layout.addLayout(self.grid_layout)

        self.update_view()

    def update_calendar(self):
        # Vyčištění předchozí mřížky
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Nastavení textu hlavičky
        month_names = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
                       "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]
        self.month_year_label.setText(f"{month_names[self.display_month - 1]} {self.display_year}")

        # Dny v týdnu
        days_of_week = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
        for col, day in enumerate(days_of_week):
            lbl = QLabel(day)
            lbl.setObjectName("DayHeader")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(lbl, 0, col)

        # Načtení všech událostí pro měsíc
        events_by_date = self.event_manager.get_events_by_month(self.display_year, self.display_month)

        # Generování dnů pomocí modulu calendar
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(self.display_year, self.display_month)

        row = 1
        for week in month_days:
            for col, date_obj in enumerate(week):
                day_frame = QFrame()
                day_frame.setMinimumHeight(120)
                day_frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                day_layout = QVBoxLayout(day_frame)
                day_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                day_layout.setContentsMargins(5, 5, 5, 5)
                day_layout.setSpacing(3)
                
                day_label = QLabel(str(date_obj.day))
                day_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                day_layout.addWidget(day_label)
                
                # ✨ KROK 3: Zobrazení barevných bloků s názvy událostí
                date_str = date_obj.strftime("%Y-%m-%d")
                if date_str in events_by_date:
                    events = events_by_date[date_str]
                    
                    # Zobraz max. 3 události
                    for event in events[:3]:
                        event_label = QLabel()
                        event_label.setText(f"🕐 {event['start_time']} - {event['title'][:20]}")
                        event_label.setFont(QFont("Arial", 8))
                        event_label.setStyleSheet(f"""
                            background-color: {event['color']};
                            color: white;
                            padding: 4px 6px;
                            border-radius: 3px;
                            margin-bottom: 2px;
                        """)
                        event_label.setWordWrap(True)
                        event_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                        
                        # Přidej hover efekt
                        self._add_event_hover_effect(event_label, event['color'])
                        
                        # ✨ KROK 3: Kliknutí na event pro editaci
                        event_label.mousePressEvent = lambda e, ev=event: self.on_event_clicked(ev, date_str)
                        
                        day_layout.addWidget(event_label)
                    
                    # Pokud je více než 3 události
                    if len(events) > 3:
                        more_label = QLabel(f"+{len(events) - 3} více")
                        more_label.setFont(QFont("Arial", 7))
                        more_label.setStyleSheet("color: #60a5fa; padding: 2px;")
                        day_layout.addWidget(more_label)
                
                day_layout.addStretch()
                
                # Zjištění, o jaký den jde a nastavení příslušné CSS třídy
                if date_obj.month != self.display_month:
                    day_frame.setProperty("class", "OtherMonthCell")
                elif date_obj == self.current_date.date():
                    day_frame.setProperty("class", "TodayCell")
                else:
                    day_frame.setProperty("class", "DayCell")
                
                # Aplikování dynamických properties
                day_frame.style().unpolish(day_frame)
                day_frame.style().polish(day_frame)
                
                # Přidej hover efekt na day frame
                self._add_day_cell_hover_effect(day_frame)
                
                # Kliknutí na den pro přidání nové události
                day_frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                day_frame.mousePressEvent = lambda event, d=date_str: self.on_day_clicked(d)
                
                self.grid_layout.addWidget(day_frame, row, col)
            row += 1

    def prev_month(self):
        if self.display_month == 1:
            self.display_month = 12
            self.display_year -= 1
        else:
            self.display_month -= 1
        self.update_calendar()

    def next_month(self):
        if self.display_month == 12:
            self.display_month = 1
            self.display_year += 1
        else:
            self.display_month += 1
        self.update_calendar()
    
    # ✨ KROK 4: Nové metody pro přepínání pohledu
    def update_view(self):
        """Aktualizuje pohled v závislosti na view_mode"""
        # Přidej animaci přechodu
        self.start_view_transition()
        
        if self.view_mode == "month":
            self.update_calendar()
        else:
            self.update_week_calendar()
    
    def prev_period(self):
        """Jde na předchozí období (měsíc/týden)"""
        if self.view_mode == "month":
            self.prev_month()
        else:
            self.display_date -= timedelta(days=7)
            self.update_view()
    
    def next_period(self):
        """Jde na další období (měsíc/týden)"""
        if self.view_mode == "month":
            self.next_month()
        else:
            self.display_date += timedelta(days=7)
            self.update_view()
    
    def set_month_view(self):
        """Přepne na měsíční pohled"""
        self.view_mode = "month"
        self.btn_month_view.setStyleSheet("""
            QPushButton { background-color: #2563eb; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_week_view.setStyleSheet("""
            QPushButton { background-color: #334155; }
            QPushButton:hover { background-color: #475569; }
        """)
        self.update_view()
    
    def set_week_view(self):
        """Přepne na týdenní pohled"""
        self.view_mode = "week"
        self.btn_week_view.setStyleSheet("""
            QPushButton { background-color: #2563eb; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_month_view.setStyleSheet("""
            QPushButton { background-color: #334155; }
            QPushButton:hover { background-color: #475569; }
        """)
        self.update_view()
    
    def update_week_calendar(self):
        """Vykreslí týdenní pohled"""
        # Vyčištění předchozí mřížky
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
        
        # Zjistení počátku týdne (pondělí)
        days_since_monday = self.display_date.weekday()
        week_start = self.display_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        # Aktualizace hlavičky
        month_names = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
                       "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]
        header_text = f"Týden {week_start.strftime('%d.%m.')} - {week_end.strftime('%d.%m.%Y')}"
        self.month_year_label.setText(header_text)
        
        # Dny v týdnu
        days_of_week = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        
        # Hora jako řádky (0-23)
        hours = list(range(24))
        
        # Prvý sloupec - hodiny
        hour_label = QLabel("Čas")
        hour_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hour_label.setStyleSheet("font-weight: bold; color: #94a3b8;")
        self.grid_layout.addWidget(hour_label, 0, 0)
        
        # Hlavička s dny týdne
        for col, day_name in enumerate(days_of_week, start=1):
            day_date = week_start + timedelta(days=col-1)
            day_header = QLabel(f"{day_name}\n{day_date.strftime('%d.%m.')}")
            day_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_header.setStyleSheet(f"""
                font-weight: bold;
                color: {'#2563eb' if day_date == self.current_date.date() else '#94a3b8'};
                padding: 8px;
            """)
            self.grid_layout.addWidget(day_header, 0, col)
        
        # Načtení všech událostí na tento týden
        events_by_date = {}
        for i in range(7):
            date = week_start + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            events = self.event_manager.get_events_by_date(date_str)
            events_by_date[date_str] = events
        
        # Vykreslení hodinové mřížky
        for hour in hours:
            # Hodina v prvním sloupci
            hour_label = QLabel(f"{hour:02d}:00")
            hour_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hour_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
            self.grid_layout.addWidget(hour_label, hour + 1, 0)
            
            # Buňky pro každý den
            for day_idx in range(7):
                day_date = week_start + timedelta(days=day_idx)
                date_str = day_date.strftime("%Y-%m-%d")
                
                cell = QFrame()
                cell.setMinimumHeight(40)
                cell.setStyleSheet("""
                    background-color: #1e293b;
                    border: 1px solid #334155;
                """)
                
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(1)
                
                # Zjistíme, které eventi patří do této hodiny
                events = events_by_date.get(date_str, [])
                for event in events:
                    try:
                        # event je tuple: (id, title, description, start_time, end_time, category, color)
                        event_start_hour = int(event[3].split(":")[0])
                        if event_start_hour == hour:
                            event_label = QLabel(event[1][:15])  # Zkrácený název
                            event_label.setFont(QFont("Arial", 7))
                            event_label.setStyleSheet(f"""
                                background-color: {event[6]};
                                color: white;
                                padding: 2px;
                                border-radius: 2px;
                                transition: all 0.3s ease;
                            """)
                            event_label.setWordWrap(True)
                            event_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                            
                            # Přidej hover efekt
                            self._add_event_hover_effect(event_label, event[6])
                            
                            # Kliknutí pro editaci
                            event_label.mousePressEvent = lambda e, ev=event, d=date_str: self.on_event_clicked(ev, d)
                            
                            cell_layout.addWidget(event_label)
                    except (IndexError, ValueError):
                        # Při chybě v parsování času přeskočit
                        pass
                
                cell_layout.addStretch()
                self.grid_layout.addWidget(cell, hour + 1, day_idx + 1)
    
    def goto_today(self):
        """Jdi na dnešní den"""
        self.current_date = datetime.now()
        self.display_year = self.current_date.year
        self.display_month = self.current_date.month
        self.display_date = self.current_date
        self.update_view()
    
    def on_day_clicked(self, date_str: str):
        """Otevření dialogu pro přidání nové události"""
        dialog = EventDialog(
            parent=self,
            event_manager=self.event_manager,
            date_str=date_str
        )
        dialog.on_save_callback = self.update_view
        dialog.exec()
    
    def on_event_clicked(self, event: dict, date_str: str):
        """Otevření dialogu pro editaci existující události"""
        event_with_id = event.copy() if isinstance(event, dict) else {
            'id': event[0],
            'title': event[1],
            'description': event[2],
            'start_time': event[3],
            'end_time': event[4],
            'category': event[5],
            'color': event[6]
        }
        dialog = EventDialog(
            parent=self,
            event_manager=self.event_manager,
            date_str=date_str,
            event_data=event_with_id
        )
        dialog.on_save_callback = self.update_view
        dialog.exec()
    
    def _add_event_hover_effect(self, label, color):
        """Přidání hover animace na event label"""
        original_style = f"""
            background-color: {color};
            color: white;
            padding: 4px 6px;
            border-radius: 3px;
            margin-bottom: 2px;
        """
        
        hover_style = f"""
            background-color: {color};
            color: white;
            padding: 4px 6px;
            border-radius: 3px;
            margin-bottom: 2px;
            border: 2px solid white;
        """
        
        def on_enter(event):
            label.setStyleSheet(hover_style)
        
        def on_leave(event):
            label.setStyleSheet(original_style)
        
        label.enterEvent = on_enter
        label.leaveEvent = on_leave
    
    def _add_day_cell_hover_effect(self, frame):
        """Přidání hover animace na den ve měsíčním pohledu"""
        original_style = frame.styleSheet()
        
        def on_enter(event):
            frame.setStyleSheet(original_style + """
                background-color: #334155;
                border: 2px solid #2563eb;
            """)
        
        def on_leave(event):
            frame.setStyleSheet(original_style)
        
        frame.enterEvent = on_enter
        frame.leaveEvent = on_leave
    
    def animate_widget_fade_in(self, widget, duration=300):
        """Fade-in animace pro widget"""
        widget.setStyleSheet(widget.styleSheet() + "\nopacity: 0;")
        
        def update_opacity(value):
            opacity = value / 100.0
            widget.setWindowOpacity(opacity)
        
        QTimer.singleShot(0, lambda: self._fade_in_effect(widget, duration))
    
    def _fade_in_effect(self, widget, duration):
        """Interní efekt pro fade-in"""
        start_value = 0
        end_value = 100
        
        timer = QTimer()
        timer.timeout.connect(lambda: self._update_fade(widget, timer, start_value, end_value, duration))
        timer.start(16)  # ~60 FPS
    
    def _update_fade(self, widget, timer, start, end, duration):
        """Aktualizace fade efektu"""
        elapsed = getattr(widget, '_fade_elapsed', 0) + 16
        setattr(widget, '_fade_elapsed', elapsed)
        
        if elapsed >= duration:
            widget.setStyleSheet(widget.styleSheet().replace("opacity: 0;", ""))
            timer.stop()
        else:
            progress = elapsed / duration
            widget.setWindowOpacity(progress)
    
    def animate_button_hover(self, button):
        """Přidání hover animace s zoomem"""
        original_style = button.styleSheet()
        
        def on_hover():
            button.setStyleSheet(original_style + """
                border: 2px solid #2563eb;
                transform: scale(1.05);
            """)
        
        def on_leave():
            button.setStyleSheet(original_style)
        
        button.enterEvent = lambda e: on_hover()
        button.leaveEvent = lambda e: on_leave()
    
    def create_pulse_animation(self, widget):
        """Vytvoří pulse animaci pro widget"""
        animation = QPropertyAnimation(widget, b"styleSheet")
        animation.setDuration(1000)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        base_style = widget.styleSheet()
        start_style = base_style.replace("background-color:", "background-color: rgba(37, 99, 235, 0.5);")
        end_style = base_style.replace("background-color:", "background-color: rgba(37, 99, 235, 1);")
        
        animation.setStartValue(start_style)
        animation.setEndValue(end_style)
        
        return animation
    
    def start_view_transition(self):
        """Animace přechodu mezi pohledy"""
        # Krátká animace při přechodu
        pass  # Transitionanimace se provádí automaticky
    
    def _complete_view_transition(self):
        """Dokončení přechodu"""
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernCalendar()
    window.show()
    sys.exit(app.exec())
