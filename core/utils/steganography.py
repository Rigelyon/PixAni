import numpy as np
import pywt
from PIL import Image
from scipy.fftpack import dct, idct
import json
import base64
import os

def dct_steganography_embed(image_array, data):
    """
    Embed data into image using DCT (Discrete Cosine Transform) method
    """
    # Convert data to binary
    binary_data = ''.join(format(ord(i), '08b') for i in data)
    binary_data += '00000000'  # Add terminator
    
    # Check if the image can hold the data
    max_bytes = (image_array.shape[0] * image_array.shape[1]) // 64
    if len(binary_data) > max_bytes * 8:
        raise ValueError("Data is too large for the cover image")
    
    # Reshape image array for 8x8 blocks
    height, width = image_array.shape
    h_blocks = height // 8
    w_blocks = width // 8
    
    # Process each 8x8 block
    data_index = 0
    for i in range(h_blocks):
        for j in range(w_blocks):
            if data_index < len(binary_data):
                # Extract block
                block = image_array[i*8:(i+1)*8, j*8:(j+1)*8]
                
                # Apply DCT
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                # Modify DCT coefficients
                bit = int(binary_data[data_index])
                if bit == 1:
                    # Make coefficient odd
                    if dct_block[7, 7] % 2 == 0:
                        dct_block[7, 7] += 1
                else:
                    # Make coefficient even
                    if dct_block[7, 7] % 2 == 1:
                        dct_block[7, 7] += 1
                
                # Apply inverse DCT
                idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                
                # Update image array
                image_array[i*8:(i+1)*8, j*8:(j+1)*8] = idct_block
                
                data_index += 1
            else:
                break
    
    return image_array

def dwt_steganography_embed(image_array, data):
    """
    Embed data into image using DWT (Discrete Wavelet Transform) method
    """
    # Convert data to binary
    binary_data = ''.join(format(ord(i), '08b') for i in data)
    binary_data += '00000000'  # Add terminator
    
    # Apply Haar wavelet transform
    coeffs = pywt.dwt2(image_array, 'haar')
    cA, (cH, cV, cD) = coeffs
    
    # Check if the image can hold the data
    max_bytes = cD.size // 8
    if len(binary_data) > max_bytes:
        raise ValueError("Data is too large for the cover image")
    
    # Flatten the cD coefficient array
    flat_cD = cD.flatten()
    
    # Embed data
    for i in range(len(binary_data)):
        if i < len(flat_cD):
            bit = int(binary_data[i])
            # Modify LSB of coefficient
            if bit == 1:
                flat_cD[i] = np.ceil(flat_cD[i])
                if flat_cD[i] % 2 == 0:
                    flat_cD[i] += 1
            else:
                flat_cD[i] = np.floor(flat_cD[i])
                if flat_cD[i] % 2 == 1:
                    flat_cD[i] -= 1
    
    # Reshape cD
    cD = flat_cD.reshape(cD.shape)
    
    # Apply inverse DWT
    embedded_array = pywt.idwt2((cA, (cH, cV, cD)), 'haar')
    
    # Clip values to valid range
    embedded_array = np.clip(embedded_array, 0, 255)
    
    return embedded_array

def embed_data_in_image(image, data_str):
    """
    Main function to embed data in the image using a combination of DCT and DWT
    """
    # Convert image to grayscale and get numpy array
    if image.mode != 'L':
        gray_image = image.convert('L')
    else:
        gray_image = image
    
    # Convert image to numpy array
    image_array = np.array(gray_image)
    
    # Encode data as base64 to make it more compact
    data_bytes = data_str.encode('utf-8')
    encoded_data = base64.b64encode(data_bytes).decode('utf-8')
    
    # Add a signature and data length
    signature = "PIXANI_DATA:"
    data_with_sig = signature + encoded_data
    
    # Compress data if needed (implementation omitted for simplicity)
    
    try:
        # Try DCT steganography first
        dct_embedded_array = dct_steganography_embed(image_array.copy(), data_with_sig)
        embedded_image = Image.fromarray(dct_embedded_array.astype(np.uint8))
    except ValueError:
        # If DCT fails due to size, try DWT
        try:
            dwt_embedded_array = dwt_steganography_embed(image_array, data_with_sig)
            embedded_image = Image.fromarray(dwt_embedded_array.astype(np.uint8))
        except ValueError:
            raise ValueError("Data is too large for the cover image using both DCT and DWT methods")
    
    # Convert back to original mode if needed
    if image.mode != 'L':
        # Copy the color from the original image
        original_array = np.array(image)
        embedded_array = np.array(embedded_image)
        
        # Create a new color image
        new_image = image.copy()
        # Replace luminance with the embedded data
        if image.mode == 'RGB':
            # Simple approach - just use the embedded grayscale for all channels
            # A more sophisticated approach would be to convert to YCbCr, modify Y and convert back
            r, g, b = original_array[:, :, 0], original_array[:, :, 1], original_array[:, :, 2]
            factor = 0.8  # Balance between preserving color and hiding data
            r_new = np.clip((r * factor + embedded_array * (1 - factor)), 0, 255).astype(np.uint8)
            g_new = np.clip((g * factor + embedded_array * (1 - factor)), 0, 255).astype(np.uint8)
            b_new = np.clip((b * factor + embedded_array * (1 - factor)), 0, 255).astype(np.uint8)
            
            new_array = np.stack((r_new, g_new, b_new), axis=2)
            new_image = Image.fromarray(new_array)
        else:
            # For other modes, convert back to original mode
            new_image = embedded_image.convert(image.mode)
    else:
        new_image = embedded_image
    
    return new_image

def decode_data_from_image(image):
    """
    Decode data from an image using a combination of DCT and DWT
    """
    def extract_dct_data(image_array):
        """
        Extract data from image using DCT method
        """
        height, width = image_array.shape
        h_blocks = height // 8
        w_blocks = width // 8
        binary_data = ''

        for i in range(h_blocks):
            for j in range(w_blocks):
                block = image_array[i*8:(i+1)*8, j*8:(j+1)*8]
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                bit = int(dct_block[7, 7]) % 2
                binary_data += str(bit)
                if binary_data.endswith('00000000'):
                    break
            if binary_data.endswith('00000000'):
                break

        return binary_data

    def extract_dwt_data(image_array):
        """
        Extract data from image using DWT method
        """
        coeffs = pywt.dwt2(image_array, 'haar')
        _, (_, _, cD) = coeffs
        flat_cD = cD.flatten()
        binary_data = ''

        for coeff in flat_cD:
            bit = int(coeff) % 2
            binary_data += str(bit)
            if binary_data.endswith('00000000'):
                break

        return binary_data

    # Convert image to grayscale and get numpy array
    if image.mode != 'L':
        gray_image = image.convert('L')
    else:
        gray_image = image

    image_array = np.array(gray_image)

    try:
        # Try extracting data using DCT
        binary_data = extract_dct_data(image_array)
    except Exception:
        # If DCT fails, try DWT
        binary_data = extract_dwt_data(image_array)

    # Convert binary data to string
    byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = ''.join([chr(int(byte, 2)) for byte in byte_data if byte != '00000000'])

    # Verify and extract the signature
    if decoded_data.startswith("PIXANI_DATA:"):
        encoded_data = decoded_data[len("PIXANI_DATA:"):]
        data_str = base64.b64decode(encoded_data).decode('utf-8')
        return json.loads(data_str)
    else:
        raise ValueError("No valid embedded data found in the image")
    

def placeholder_extract_data():
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