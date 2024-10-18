import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt

# Veritabanına bağlan veya yeni bir tane oluştur
try:
    con = sqlite3.connect("tablo.db")
    imlec = con.cursor()
except sqlite3.Error as e:
    print(f"Veritabanına bağlanırken hata oluştu: {e}")


# Tabloyu oluştur
try:
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS kisiler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            yas INTEGER,
            meslek TEXT,
            gelir INTEGER
        )
    """)
except sqlite3.Error as e:
    print(f"Tablo oluşturulurken hata oluştu: {e}")


# Tabloya örnek veri ekleme
try:
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)", 
                  ("Ayşe", 26, "Mühendis",20000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)", 
                  ("Sercan", 29, "Ressam",15000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Mehmet",24,"Temizlik Görevlisi",30000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Betül",32,"Pilot",32000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Canan",21,"stajyer",10000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Akif",35,"Mühendis",45000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Leyla",42,"Ressam",19000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Sinan",40,"Doktor",70000))
    imlec.execute("INSERT INTO kisiler (isim, yas, meslek, gelir) VALUES (?, ?, ?, ?)",
                  ("Selim",38,"Doktor",68000))
    con.commit()  # Değişiklikleri kaydet

except sqlite3.Error as e:
    print(f"Veri eklenirken hata oluştu: {e}")


# Tabloya yeni sütun ekleme
# 'gelir' sütununun var olup olmadığını kontrol et
imlec.execute("PRAGMA table_info(kisiler)")
columns = imlec.fetchall()
maas_var = any(column[1] == "gelir" for column in columns)

if not maas_var:
    try:
        imlec.execute("ALTER TABLE kisiler ADD COLUMN gelir INTEGER")  # Yeni 'gelir' sütunu ekleniyor
        con.commit()  # Değişiklikleri kaydet
        print("'gelir' sütunu başarıyla eklendi.")
    except sqlite3.Error as e:
        print(f"Sütun eklenirken hata oluştu: {e}")
else:
    print("'gelir' sütunu zaten mevcut.")



# Yeni sütuna veri ekleme
imlec.execute("UPDATE kisiler SET gelir = ? WHERE id = ?", (20000,1))
con.commit()


# Tekrarlanan kayıtları silmek için sorgu
imlec.execute("""
    DELETE FROM kisiler
    WHERE id NOT IN(
        SELECT MIN(id)
        FROM kisiler
        GROUP BY isim, yas, meslek, gelir
    );
""")



# VERİTABANINI TABLO OLARAK GÖSTERME
# Veritabanına bağlan ve veriyi çek
imlec=con.cursor()

# Kisiler tablosunadaki tüm veriyi al
imlec.execute("SELECT * FROM kisiler")
veri = imlec.fetchall()

# Veriyi pandas DataFrame'e dönüştür
df = pd.DataFrame(veri, columns=["id","isim","yas","meslek","gelir"])

# Tabloyu terminale yazdır
print("Veritabanı Tablosu: ")
print(df)


# Tablo bilgilerini görmek için
#imlec.execute("PRAGMA table_info(kisiler)")
#print(imlec.fetchall())


# Veritabanını kapatma
con.close()
print("Veritabanı bağlantısı kapatıldı.")


# Tkinter arayüzünü oluşturma
root = tk.Tk()
root.title("Veritabanı Tablosu")

# DataFrame'i Tkinter table (ttk.Treeview) kullanarak gösterme
tree = ttk.Treeview(root, columns=columns, show= 'headings')

# Sütun başlıklarını ekle
for col in columns:
    tree.heading(col, text=col)

# Verileri tabloya ekle
for row in veri:
    tree.insert('','end', values= row)

tree.pack(expand=True, fill= 'both')

# Pencereyi göster
root.mainloop()


# VERİLERİ GRAFİK OLARAK GÖSTERME
# Yaş gruplarını tanımlama
def yas_gruplari(yas):
    if yas < 30:
        return "20'li Yaşlar"
    elif 30 <= yas < 40:
        return "30'lu Yaşlar"
    else:
        return "40 ve Üstü"

# Yeni bir sütun ekleyerek yaş gruplarını ata
df['yas_grubu'] = df['yas'].apply(yas_gruplari)

# Yaş gruplarına göre sayıları hesapla
yas_grup_sayilari = df['yas_grubu'].value_counts()

# Grafik çizimi
fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # 1 satır, 2 sütun

# Pasta grafiği
axs[0].pie(yas_grup_sayilari, labels=yas_grup_sayilari.index, autopct='%1.1f%%', startangle=140)
axs[0].set_title('Yaş Gruplarına Göre Dağılım')

# Bar grafiği
df.groupby('meslek')['gelir'].mean().plot(kind='bar', color='pink', alpha=0.8, ax=axs[1])
axs[1].set_title('Mesleklere Göre Ortalama Gelir')
axs[1].set_xlabel('Meslek')
axs[1].set_ylabel('Ortalama Gelir')

# Grafikleri göster
plt.tight_layout()
plt.show()
