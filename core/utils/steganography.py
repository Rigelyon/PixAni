import os
import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct 
import json 


def text_to_binary(text):
    binary = ''.join(format(ord(char), '08b') for char in text)

    # Tambahkan penanda awal dan panjang pesan (16 bit penanda + 16 bit panjang)
    marker = '1111000011110000'  # Penanda unik
    length_prefix = format(len(binary), '016b')  # 16-bit untuk panjang
    return marker + length_prefix + binary

def binary_to_text(binary):
    # Cari penanda awal
    marker = '1111000011110000'
    marker_pos = binary.find(marker)
    
    if marker_pos == -1:
        return ""
    
    binary = binary[marker_pos + len(marker):]  # Lewati penanda
    
    # Baca 16 bit berikutnya sebagai panjang pesan
    if len(binary) < 16:
        return ""
    
    length = int(binary[:16], 2)
    binary = binary[16:]
    
    # Pastikan panjang binary cukup
    if len(binary) < length:
        return ""
    
    binary = binary[:length]
    try:
        text = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
        return text
    except:
        return ""

def calculate_capacity(img_width, img_height, block_size=8):
    blocks_x = img_width // block_size
    blocks_y = img_height // block_size
    return blocks_x * blocks_y

def get_frequency_position():
    return (4, 3)  # Posisi tetap untuk memudahkan ekstraksi

def embed_message(image, message, filename):
    output_dir = "media/embedded_images"
    output_path = os.path.join(output_dir, filename)
    strength = 2.0

    try:
        # Buka gambar dan konversi ke numpy array
        img = image
        
        # Konversi ke RGB jika mode gambar berbeda
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img_array = np.array(img)
        
        # Konversi pesan ke binary dengan penanda
        binary_message = text_to_binary(message)
        
        # Hitung kapasitas maksimum
        capacity = calculate_capacity(img_array.shape[1], img_array.shape[0])
        required = len(binary_message)
        
        if required > capacity:
            raise ValueError(f"Pesan terlalu besar. Kapasitas: {capacity} bit, Dibutuhkan: {required} bit")
        
        # Proses setiap channel (hanya menggunakan channel merah untuk penyisipan)
        channel = 0  # 0: merah
        data = img_array[:, :, channel].astype(float)
        
        message_index = 0
        block_size = 8
        freq_pos = get_frequency_position()
        
        for i in range(0, data.shape[0] - block_size + 1, block_size):
            for j in range(0, data.shape[1] - block_size + 1, block_size):
                if message_index >= len(binary_message):
                    break
                
                # Ambil blok 8x8
                block = data[i:i+block_size, j:j+block_size]
                
                # Lakukan DCT 2D
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                # Sisipkan bit pesan pada koefisien frekuensi
                x, y = freq_pos
                current_val = dct_block[x, y]
                bit = int(binary_message[message_index])
                
                # Modifikasi koefisien DCT dengan cara yang lebih robust
                if bit == 1:
                    new_val = abs(current_val) + strength
                else:
                    new_val = -abs(current_val) - strength
                
                dct_block[x, y] = new_val
                
                # Inverse DCT
                idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                
                # Kembalikan ke gambar dengan clipping
                data[i:i+block_size, j:j+block_size] = np.clip(idct_block, 0, 255)
                
                message_index += 1
        
        # Simpan gambar hasil
        img_array[:, :, channel] = data.astype(np.uint8)
        result_img = Image.fromarray(img_array)
        
        # Simpan sebagai PNG untuk menghindari kompresi lossy
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            print("Peringatan: Format JPG mungkin menyebabkan kehilangan data. Disarankan menggunakan PNG.")

        os.makedirs(output_dir, exist_ok=True)
        result_img.save(output_path)
        return json.dumps({ "output_path": output_path })
    
    except Exception as e:
        print(f"Error saat embedding: {str(e)}")
        return False

def extract_message(image):
    strength=2.0

    try:
        img = image
        
        # Konversi ke RGB jika mode gambar berbeda
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img_array = np.array(img)
        
        # Gunakan channel yang sama dengan embedding
        channel = 0
        data = img_array[:, :, channel].astype(float)
        
        binary_message = ""
        block_size = 8
        freq_pos = get_frequency_position()
        
        # Variabel untuk penanda dan panjang pesan
        marker = '1111000011110000'
        found_marker = False
        length_binary = ""
        message_length = 0
        bits_collected = 0
        
        for i in range(0, data.shape[0] - block_size + 1, block_size):
            for j in range(0, data.shape[1] - block_size + 1, block_size):
                block = data[i:i+block_size, j:j+block_size]
                
                # Lakukan DCT
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                # Ekstrak bit dari koefisien frekuensi
                x, y = freq_pos
                threshold = strength / 2  # Threshold untuk menentukan bit
                bit = '1' if dct_block[x, y] > threshold else '0'
                
                binary_message += bit
                bits_collected += 1
                
                # Cari penanda jika belum ditemukan
                if not found_marker and len(binary_message) >= len(marker):
                    if marker in binary_message:
                        found_marker = True
                        marker_pos = binary_message.find(marker)
                        binary_message = binary_message[marker_pos + len(marker):]
                        bits_collected = len(binary_message)
                
                # Jika penanda ditemukan, baca panjang pesan
                if found_marker and len(length_binary) < 16 and bits_collected >= 16:
                    length_binary = binary_message[:16]
                    message_length = int(length_binary, 2)
                    binary_message = binary_message[16:]
                    bits_collected = len(binary_message)
                
                # Jika sudah memiliki panjang pesan, cek apakah sudah cukup
                if message_length > 0 and bits_collected >= message_length:
                    binary_message = binary_message[:message_length]
                    return binary_to_text(marker + length_binary + binary_message)
        result = binary_to_text(marker + length_binary + binary_message)
        return json.dumps(result)
    
    except Exception as e:
        print(f"Error saat ekstraksi: {str(e)}")
        return ""
    

def test_extract_data():
    try:
        # Use the correct directory routing
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_file_path = os.path.join(base_dir, 'data.json')
        
        with open(data_file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise ValueError(f"The file 'data.json' was not found at {data_file_path}.")
    except json.JSONDecodeError:
        raise ValueError(f"Failed to decode JSON from 'data.json' at {data_file_path}.")