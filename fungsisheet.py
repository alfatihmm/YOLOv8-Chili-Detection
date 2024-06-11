from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re
import time
from datetime import datetime



def update_sheet():
    # Konfigurasi otentikasi dengan file kredensial JSON untuk Google Drive
    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'penyakitlombok-396692ec95bf.json', 
        scopes=['https://www.googleapis.com/auth/drive'])
    drive = GoogleDrive(gauth)

    # ID folder Google Drive yang ingin Anda telusuri
    folder_id = '1pWwGZTkuX2091DVyIU2ufnFF_13jPRnQ'
    
    # Mendapatkan daftar file dalam folder
    files = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    # Mengakses Google Sheets
    gc = gspread.authorize(gauth.credentials)

    # Buka spreadsheet
    spreadsheet_id = '15Ci-7AqYHvzznvsXP46c7bCnfPKGR0usUSs622aNL6Q'
    sheet = gc.open_by_key(spreadsheet_id).sheet1

    # Menulis data ke Google Sheets
    values = [['Nama File', 'Tanggal', 'Waktu', 'Link']]

    # Format nama file yang dicari: Hasil_Deteksi_DDMMYY_jam:menit
    pattern = re.compile(r'Hasil_Deteksi_(\d{2})(\d{2})(\d{2})_(\d{2}):(\d{2})')

    for file in files:
        match = pattern.match(file['title'])
        if match:
            day, month, year, hour, minute = match.groups()
            try:
                # Konversi format tanggal dari DDMMYY menjadi YYYY-MM-DD
                date = datetime.strptime(f'{year}{month}{day}', '%y%m%d').strftime('%Y-%m-%d')
                values.append([file['title'], date, f'{hour}:{minute}', file['alternateLink']])
            except ValueError:
                # Lanjutkan ke file berikutnya jika format tanggal tidak valid
                continue

    # Clear data di dalam spreadsheet
    sheet.clear()

    # Update data baru ke spreadsheet
    sheet.update('A1', values)

    print('Data telah ditulis ke Google Sheets.')

# Panggil fungsi untuk menjalankannya
#update_sheet()

