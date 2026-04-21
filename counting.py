import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def run_car_counting(image_path):
    # 1. Setup Folder
    output_dir = 'output'
    steps_dir = os.path.join(output_dir, 'steps')
    if not os.path.exists(steps_dir):
        os.makedirs(steps_dir)

    # 2. Load Image
    img = cv2.imread(image_path)
    if img is None:
        return print("Error: Pastikan file 'parking.jpg' ada di folder input/")
    
    output_img = img.copy()

    # 3. Step 1: Preprocessing (V-Channel & Top-Hat)
    # Gunakan channel Value untuk stabilitas cahaya
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    
    # Top-Hat Transform: Menonjolkan objek terang di atas background gelap
    kernel_top = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    tophat = cv2.morphologyEx(v_channel, cv2.MORPH_TOPHAT, kernel_top)
    cv2.imwrite(os.path.join(steps_dir, '1_v_channel.png'), tophat)

    # 4. Step 2: Thresholding
    # Gunakan OTSU pada hasil Top-Hat untuk memisahkan mobil dari aspal
    _, thresh = cv2.threshold(tophat, 50, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(os.path.join(steps_dir, '2_threshold.png'), thresh)

    # 5. Step 3: Morfologi Agresif
    # Menggunakan kernel besar untuk menyatukan komponen mobil menjadi satu kotak solid
    kernel_clean = np.ones((5, 5), np.uint8)
    # Closing untuk menyambung kaca, kap, dan atap
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_clean, iterations=4)
    # Dilasi sedikit agar kotak lebih pas membungkus bodi mobil
    dilated = cv2.dilate(closed, kernel_clean, iterations=1)
    cv2.imwrite(os.path.join(steps_dir, '3_morphology.png'), dilated)

    # 6. Deteksi Kontur & Filter Geometris
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    car_count = 0
    # PARAMETER TUNING
    MIN_AREA = 450 
    MAX_AREA = 10000
    MIN_ASPECT = 0.4
    MAX_ASPECT = 2.5

    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h
        
        # Validasi: Apakah ini berbentuk mobil?
        if MIN_AREA < area < MAX_AREA:
            if MIN_ASPECT < aspect_ratio < MAX_ASPECT:
                car_count += 1
                # Gambar Bounding Box Hijau (Kotak Mobil)
                cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(output_img, f"#{car_count}", (x, y - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 7. Simpan Hasil
    cv2.imwrite(os.path.join(output_dir, 'result.png'), output_img)
    
    print(f"\nSelesai! Berhasil mendeteksi {car_count} mobil.")
    print(f"Hasil disimpan di folder '{output_dir}'")

    # Show result
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB))
    plt.title(f"Final Count: {car_count} Cars")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    run_car_counting('input/parking.jpg')
