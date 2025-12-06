import pickle
import csv
import numpy as np
import os

def pkl_to_csv(pkl_file_path, csv_file_path=None):
    """
    Đọc file pickle và xuất sang CSV
    
    Args:
        pkl_file_path: Đường dẫn đến file .pkl
        csv_file_path: Đường dẫn file CSV đầu ra (tùy chọn)
    """
    # Nếu không chỉ định đường dẫn CSV, tạo từ tên file pkl
    if csv_file_path is None:
        csv_file_path = pkl_file_path.replace('.pkl', '.csv')
    
    try:
        # Đọc file pickle
        print(f"Đang đọc file: {pkl_file_path}")
        with open(pkl_file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Kiểu dữ liệu: {type(data)}")
        
        # Xử lý dựa trên kiểu dữ liệu
        if isinstance(data, dict):
            print(f"Số lượng entries trong dictionary: {len(data)}")
            
            # Mở file CSV để ghi
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Kiểm tra cấu trúc của giá trị đầu tiên
                first_key = list(data.keys())[0] if data else None
                if first_key:
                    first_value = data[first_key]
                    print(f"Ví dụ key: {first_key}")
                    print(f"Kiểu giá trị: {type(first_value)}")
                    
                    if isinstance(first_value, (list, np.ndarray)):
                        # Nếu giá trị là array/list (embeddings)
                        embedding_size = len(first_value)
                        print(f"Kích thước embedding: {embedding_size}")
                        
                        # Header: user_id/name + các cột cho mỗi dimension của embedding
                        header = ['user_id'] + [f'dim_{i}' for i in range(embedding_size)]
                        writer.writerow(header)
                        
                        # Ghi dữ liệu
                        for key, value in data.items():
                            # Convert numpy array to list nếu cần
                            if isinstance(value, np.ndarray):
                                value = value.tolist()
                            row = [key] + value
                            writer.writerow(row)
                    else:
                        # Nếu giá trị là scalar hoặc kiểu khác
                        writer.writerow(['key', 'value'])
                        for key, value in data.items():
                            writer.writerow([key, value])
        
        elif isinstance(data, (list, np.ndarray)):
            print(f"Số lượng items trong list: {len(data)}")
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Kiểm tra item đầu tiên
                if len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, (list, np.ndarray)):
                        # Nếu là list of arrays
                        embedding_size = len(first_item)
                        header = ['index'] + [f'dim_{i}' for i in range(embedding_size)]
                        writer.writerow(header)
                        
                        for idx, item in enumerate(data):
                            if isinstance(item, np.ndarray):
                                item = item.tolist()
                            row = [idx] + item
                            writer.writerow(row)
                    else:
                        # List of scalars
                        writer.writerow(['index', 'value'])
                        for idx, item in enumerate(data):
                            writer.writerow([idx, item])
        
        else:
            print(f"Kiểu dữ liệu không được hỗ trợ: {type(data)}")
            return
        
        print(f"\n✓ Đã xuất thành công sang: {csv_file_path}")
        print(f"Kích thước file CSV: {os.path.getsize(csv_file_path)} bytes")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Đường dẫn file pickle
    pkl_file = r"d:\HUTECH\DACN\dataset\face_embeddings.pkl"
    
    # Đường dẫn file CSV output (tùy chọn)
    csv_file = r"d:\HUTECH\DACN\dataset\face_embeddings.csv"
    
    # Chuyển đổi
    pkl_to_csv(pkl_file, csv_file)
