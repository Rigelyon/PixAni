import cv2
import numpy as np


# converts text to bits
def text_to_bits(text):
    return ''.join([bin(ord(c))[2:].zfill(8) for c in text]) + '00000000'  # null terminator

# converts bits to text
def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if byte == '00000000':
            break
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

# resizes the image to a multiple of 8
def resize_image_to_multiple_of_8(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = img.shape
    new_h = h + (8 - h % 8) if h % 8 != 0 else h
    new_w = w + (8 - w % 8) if w % 8 != 0 else w
    padded = np.zeros((new_h, new_w), dtype=np.uint8)
    padded[:h, :w] = img
    return padded

def embed_to_image(img, message):
    bits = text_to_bits(message)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = resize_image_to_multiple_of_8(img)
    img = np.float32(img)
    h, w = img.shape
    bit_idx = 0

    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = img[i:i+8, j:j+8]
            dct = cv2.dct(block)

            coeff = int(dct[4, 3])
            if bit_idx < len(bits):
                bin_coeff = list(bin(abs(coeff))[2:].zfill(8))
                bin_coeff[-1] = bits[bit_idx]
                new_coeff = int(''.join(bin_coeff), 2)
                new_coeff = -new_coeff if coeff < 0 else new_coeff
                dct[4, 3] = new_coeff
                bit_idx += 1

            img[i:i+8, j:j+8] = cv2.idct(dct)

            if bit_idx >= len(bits):
                break
        if bit_idx >= len(bits):
            break

    return np.uint8(np.clip(img, 0, 255))

def extract_message(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = np.float32(img)
    h, w = img.shape
    bits = ''

    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = img[i:i+8, j:j+8]
            dct = cv2.dct(block)
            coeff = int(dct[4, 3])
            bin_coeff = bin(abs(coeff))[2:].zfill(8)
            bits += bin_coeff[-1]

            # Berhenti saat menemukan null terminator
            if bits.endswith('00000000'):
                return bits_to_text(bits)

    return bits_to_text(bits)
