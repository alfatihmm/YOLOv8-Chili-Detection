import os
import random
import glob
import time
import json
from datetime import datetime
from fpdf import FPDF
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import pkg_resources
from concurrent.futures import ThreadPoolExecutor

def create_pdf(data_file, output_directory='.', parent_directory_id='1pWwGZTkuX2091DVyIU2ufnFF_13jPRnQ', credentials_file='penyakitlombok-396692ec95bf.json'):
    def upload_file(pdf_file_path, parent_directory_id):
        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            pkg_resources.resource_filename(__name__, credentials_file),
            scopes=['https://www.googleapis.com/auth/drive'])

        drive = GoogleDrive(gauth)

        file_name = os.path.basename(pdf_file_path)

        file = drive.CreateFile({'parents': [{'id': parent_directory_id}], 'title': file_name})
        file.SetContentFile(pdf_file_path)
        file.Upload()
        print(f"\n--------- {file_name} is Uploaded ----------")

    def add_sample_frames(pdf, counts):
        # Add sample frames for each type
        for frame_type, count in counts.items():
            frame_files = glob.glob(os.path.join("output_frames", f"{frame_type}_*.png"))
            num_samples = min(2, len(frame_files), count)  # Take minimum of 2, available frames, and count of detections
            sampled_frames = random.sample(frame_files, num_samples)  # Take random samples

            if num_samples > 0:  # Only add section if there are samples available for this type
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"Sampel {frame_type.capitalize()} yang terdeteksi:", 0, 1)

                for i, frame_file in enumerate(sampled_frames):
                    if i % 2 == 0:
                        pdf.y += 10  # Add some vertical space if starting a new row

                    pdf.image(frame_file, x=10 + (i % 2) * 100, y=pdf.get_y(), w=75, h=50)  # Display images side by side

                    if i % 2 == 1 or i == num_samples - 1:  # Add a line break after every two images or if it's the last image
                        pdf.ln(60)  # Add a line break after every two images
                    else:
                        pdf.cell(50)  # Add some horizontal space if there's another image in the row

                pdf.ln(10)  # Add some vertical space after each frame type

    def add_estimated_positions(pdf, speed=6.7):
        # Get list of all frame files
        frame_files = glob.glob(os.path.join("output_frames", "*.png"))

        # Extract detection times and calculate positions
        positions = []
        for frame_file in frame_files:
            base_name = os.path.basename(frame_file)
            parts = base_name.split('_')
            if len(parts) == 2:
                time_str = parts[1].replace('.png', '')
                detection_time = datetime.strptime(time_str, "%H-%M-%S")
                start_time = datetime.strptime(json_data['start_time'], "%H:%M:%S")
                elapsed_time = (detection_time - start_time).total_seconds() / 60  # Convert to minutes
                position = elapsed_time * speed
                positions.append((base_name, position))

        # Sort positions by distance
        positions.sort(key=lambda x: x[1])

        # Add positions table to PDF
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Perkiraan Letak Penyakit yang Terdeteksi", 0, 1, 'C')

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(10, 10, "No", 1, 0, 'C')
        pdf.cell(80, 10, "Jenis Penyakit (Nama File)", 1, 0, 'C')
        pdf.cell(80, 10, "Jarak dari Posisi Start (meter)", 1, 1, 'C')

        pdf.set_font('Arial', '', 12)
        for i, (disease_type, position) in enumerate(positions, 1):
            pdf.cell(10, 10, str(i), 1, 0, 'C')
            pdf.cell(80, 10, disease_type, 1, 0, 'C')
            pdf.cell(80, 10, f"{position:.2f} meter", 1, 1, 'C')

    def indonesian_month_name(month_number):
        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        return months[month_number - 1]

    def format_date_indonesian(date_str):
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        day = date_obj.day
        month = indonesian_month_name(date_obj.month)
        year = date_obj.year
        return f"{day} {month} {year}"

    # Load data from JSON
    with open(data_file, 'r') as file:
        json_data = json.load(file)

    # Extract data from JSON
    counts = {
        'bercak': json_data['bercak'],
        'kuning': json_data['kuning'],
        'berlubang': json_data['berlubang']
    }

    start_time = json_data['start_time']
    end_time = json_data['end_time']
    duration = json_data['duration']
    date = json_data['date']

    # Get current date and time
    now = datetime.now()
    date_str = now.strftime("%d%m%y")
    time_str = now.strftime("%H:%M")

    # Create PDF filename
    output_filename = os.path.join(output_directory, f"Hasil_Deteksi_{date_str}_{time_str}.pdf")

    # Create PDF
    pdf = FPDF()
    pdf.alias_nb_pages()  # Set alias for total number of pages
    pdf.add_page()

    # Add title
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "LAPORAN HASIL DETEKSI PENYAKIT PADA DAUN CABAI ", 0, 1, align='C')
    pdf.cell(0, 10, "Tugas Akhir D4 Teknik Elektronika ", 0, 1, align='C')

    pdf.ln(5)  # Add some vertical space

    # Draw a line
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Adjust the coordinates according to your layout

    # Add start time, end time, duration, and date
    pdf.set_font('Arial', '', 11)

    pdf.cell(30, 10, "Durasi", 0, 0)
    pdf.cell(0, 10, ": " + duration, 0, 1)

    pdf.cell(30, 10, "Waktu Mulai ", 0, 0)
    pdf.cell(0, 10, ": " + start_time, 0, 1)

    pdf.cell(30, 10, "Waktu Selesai", 0, 0)
    pdf.cell(0, 10, ": " + end_time, 0, 1)

    formatted_date = format_date_indonesian(date)
    pdf.cell(30, 10, "Tanggal", 0, 0)
    pdf.cell(0, 10, ": " + formatted_date, 0, 1)

    pdf.ln(5)  # Add some vertical space

    # Add counts
    pdf.set_font('Arial', 'B', 12)

    cell_width = 40
    table_width = cell_width * 3 + 4

    page_width = pdf.w
    x_pos = (page_width - table_width) / 2

    pdf.set_x(x_pos)
    pdf.cell(cell_width, 10, "Jenis Penyakit", 1, 0, align='C')
    pdf.cell(cell_width, 10, "Jumlah", 1, 0, align='C')
    pdf.cell(cell_width, 10, "Persentase", 1, 1, align='C')

    total_count = sum(counts.values())

    for category, count in counts.items():
        pdf.set_x(x_pos)
        pdf.set_font('Arial', '', 12)
        pdf.cell(cell_width, 10, category.capitalize(), 1, 0, align='C')
        pdf.cell(cell_width, 10, str(count), 1, 0, align='C')
        percentage = (count / total_count) * 100
        pdf.cell(cell_width, 10, f"{percentage:.2f}%", 1, 1, align='C')

    pdf.ln(5)
    add_sample_frames(pdf, counts)

    pdf.ln(10)

    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, "Untuk contoh gambar deteksi selengkapnya dapat dibuka pada tautan berikut:")
    with open("folder_link.txt", "r") as link_file:
        link_url = link_file.read()
    pdf.set_font('Arial', 'U', 12)
    pdf.cell(0, 10, link_url, 0, 1, link=link_url)

    # Add estimated positions page
    add_estimated_positions(pdf)

    pdf.output(output_filename, 'F')

    # Upload PDF to Google Drive
    upload_file(output_filename, parent_directory_id)
