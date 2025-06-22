import cv2
import os
import numpy as np
import time
from matplotlib import pyplot as plt

class FaceDetector:
    """
    Класс для обнаружения лиц на изображениях с использованием нескольких методов
    """
    
    def __init__(self, dataset_path="FaceDataset"):
        """
        Инициализация детектора лиц
        
        Args:
            dataset_path (str): Путь к папке с изображениями
        """
        self.dataset_path = dataset_path
        
        # Загружаем каскады Хаара для лица (основной метод)
        haar_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(haar_cascade_path)
        
        # Загружаем дополнительные каскады для повышения точности
        alt_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'
        self.alt_face_cascade = cv2.CascadeClassifier(alt_cascade_path)
        
        alt2_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        self.alt2_face_cascade = cv2.CascadeClassifier(alt2_cascade_path)
        
        # Профильный детектор для лиц в профиль
        profile_cascade_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
        self.profile_cascade = cv2.CascadeClassifier(profile_cascade_path)
        
        # Параметры для настройки DNN детектора (более современный метод)
        self.dnn_model_file = "models/opencv_face_detector_uint8.pb"
        self.dnn_config_file = "models/opencv_face_detector.pbtxt"
        
        # Проверяем наличие моделей для DNN детектора
        self.use_dnn = os.path.exists(self.dnn_model_file) and os.path.exists(self.dnn_config_file)
        
        if self.use_dnn:
            self.net = cv2.dnn.readNetFromTensorflow(self.dnn_model_file, self.dnn_config_file)
    
    def detect_faces_dnn(self, image):
        """
        Обнаружение лиц с использованием DNN (более точный современный метод)
        
        Args:
            image: Исходное изображение
            
        Returns:
            list: Список обнаруженных лиц в формате (x, y, w, h)
        """
        if not self.use_dnn:
            return []
            
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], False, False)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Порог уверенности
                x1 = int(detections[0, 0, i, 3] * width)
                y1 = int(detections[0, 0, i, 4] * height)
                x2 = int(detections[0, 0, i, 5] * width)
                y2 = int(detections[0, 0, i, 6] * height)
                
                # Проверяем границы изображения
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)
                
                # Преобразуем в формат (x, y, w, h)
                w = x2 - x1
                h = y2 - y1
                faces.append((x1, y1, w, h))
        
        return faces
    
    def detect_faces_cascade(self, gray_image):
        """
        Обнаружение лиц с использованием каскадов Хаара
        
        Args:
            gray_image: Изображение в оттенках серого
            
        Returns:
            list: Список обнаруженных лиц
        """
        # Используем все доступные каскады для повышения точности
        faces1 = self.face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )
        
        faces2 = self.alt_face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.08,
            minNeighbors=4,
            minSize=(20, 20)
        )
        
        faces3 = self.alt2_face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.09,
            minNeighbors=4,
            minSize=(20, 20)
        )
        
        # Ищем профильные лица (лица в профиль)
        faces4 = self.profile_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(20, 20)
        )
        
        # Переворачиваем изображение и снова ищем профильные лица
        flipped = cv2.flip(gray_image, 1)
        faces5 = self.profile_cascade.detectMultiScale(
            flipped,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(20, 20)
        )
        
        # Корректируем координаты для перевернутого изображения
        width = gray_image.shape[1]
        corrected_faces5 = []
        for (x, y, w, h) in faces5:
            corrected_faces5.append((width - x - w, y, w, h))
        
        # Объединяем результаты всех детекторов
        all_faces = []
        if len(faces1) > 0:
            all_faces.extend(faces1)
        if len(faces2) > 0:
            all_faces.extend(faces2)
        if len(faces3) > 0:
            all_faces.extend(faces3)
        if len(faces4) > 0:
            all_faces.extend(faces4)
        if len(corrected_faces5) > 0:
            all_faces.extend(corrected_faces5)
            
        return all_faces
        
    def non_max_suppression(self, boxes, overlap_thresh=0.3):
        """
        Применение алгоритма подавления немаксимумов для устранения дублирования лиц
        
        Args:
            boxes: Список прямоугольников (x, y, w, h)
            overlap_thresh: Порог перекрытия
            
        Returns:
            list: Отфильтрованный список прямоугольников
        """
        if len(boxes) == 0:
            return []
            
        # Преобразуем формат из (x, y, w, h) в (x1, y1, x2, y2)
        boxes_array = []
        for (x, y, w, h) in boxes:
            boxes_array.append([x, y, x + w, y + h])
        
        boxes_array = np.array(boxes_array)
        
        # Если прямоугольники в формате float, преобразуем их в int
        if boxes_array.dtype.kind == "f":
            boxes_array = boxes_array.astype("int")
            
        # Инициализируем список индексов выбранных прямоугольников
        pick = []
        
        # Извлекаем координаты
        x1 = boxes_array[:, 0]
        y1 = boxes_array[:, 1]
        x2 = boxes_array[:, 2]
        y2 = boxes_array[:, 3]
        
        # Вычисляем площадь каждого прямоугольника
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        
        # Сортируем индексы по y2 (нижние правые y-координаты)
        idxs = np.argsort(y2)
        
        # Основной цикл NMS
        while len(idxs) > 0:
            # Берем последний индекс из списка и добавляем в список выбранных
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            
            # Находим наибольшие координаты для начала прямоугольника
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            
            # Находим наименьшие координаты для конца прямоугольника
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            
            # Вычисляем ширину и высоту перекрытия
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)
            
            # Вычисляем процент перекрытия
            overlap = (w * h) / area[idxs[:last]]
            
            # Удаляем индексы с перекрытием больше порогового значения
            idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))
            
        # Возвращаем результат в формате (x, y, w, h)
        result = []
        for i in pick:
            x1_val, y1_val, x2_val, y2_val = boxes_array[i]
            result.append((x1_val, y1_val, x2_val - x1_val, y2_val - y1_val))
            
        return result
    
    def equalize_histogram(self, image):
        """
        Применяет выравнивание гистограммы для улучшения контраста
        
        Args:
            image: Исходное изображение
            
        Returns:
            Изображение с улучшенным контрастом
        """
        # Конвертируем в YUV для сохранения цвета
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            return cv2.equalizeHist(image)
    
    def process_image(self, image_path):
        """
        Обработка изображения для обнаружения лиц
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            tuple: (изображение с отмеченными лицами, количество обнаруженных лиц)
        """
        # Читаем изображение
        start_time = time.time()
        original_image = cv2.imread(image_path)
        
        if original_image is None:
            print(f"Ошибка: Не удалось загрузить изображение {image_path}")
            return None, 0
            
        # Создаем копию для отрисовки результатов
        result_image = original_image.copy()
        
        # Применяем улучшение контраста
        enhanced_image = self.equalize_histogram(original_image)
            
        # Конвертируем в оттенки серого
        gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
        
        # Применяем CLAHE (адаптивное выравнивание гистограммы) для улучшения качества
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_image = clahe.apply(gray_image)
            
        # Обнаружение лиц с использованием всех методов
        cascade_faces = self.detect_faces_cascade(gray_image)
        dnn_faces = self.detect_faces_dnn(enhanced_image) if self.use_dnn else []
            
        # Объединяем результаты
        all_faces = list(cascade_faces)
        all_faces.extend(dnn_faces)
            
        # Убираем дублирующиеся обнаружения с помощью NMS
        faces = self.non_max_suppression(all_faces)
        
        # Отрисовываем результаты
        for (x, y, w, h) in faces:
            # Рисуем синий прямоугольник
            cv2.rectangle(result_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
        processing_time = time.time() - start_time
        if processing_time < 0.5:  
            time.sleep(0.5 - processing_time) 
            
        return result_image, len(faces)
        
    def process_dataset(self):
        """
        Обработка всех изображений в датасете
        """
        # Создаем папку для результатов, если её нет
        results_dir = "FaceDetectionResults"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        # Проверяем наличие папки с датасетом
        if not os.path.exists(self.dataset_path):
            print(f"Ошибка: Папка {self.dataset_path} не найдена")
            return
            
        # Получаем список файлов в папке
        images = [f for f in os.listdir(self.dataset_path) if os.path.isfile(os.path.join(self.dataset_path, f))]
        supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
        
        valid_images = []
        for img in images:
            ext = os.path.splitext(img)[1].lower()
            if ext in supported_formats:
                valid_images.append(img)
                
        # Обрабатываем каждое изображение
        for i, image_name in enumerate(valid_images):
            image_path = os.path.join(self.dataset_path, image_name)
            
            print(f"Обработка изображения [{i+1}/{len(valid_images)}]: {image_name}")
            
            result_image, face_count = self.process_image(image_path)
            
            if result_image is not None:
                result_path = os.path.join(results_dir, f"result_{image_name}")
                cv2.imwrite(result_path, result_image)
                
                print(f"Найдено лиц: {face_count}")
                print(f"Результат сохранён: {result_path}")
                print("-" * 50)
                
                plt.figure(figsize=(10, 6))
                plt.subplot(121)
                plt.imshow(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB))
                plt.title('Исходное изображение')
                plt.axis('off')
                
                plt.subplot(122)
                plt.imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
                plt.title(f'Обнаружено лиц: {face_count}')
                plt.axis('off')
                
                plt.tight_layout()
                plt.savefig(os.path.join(results_dir, f"comparison_{image_name}"))
                plt.close()


if __name__ == "__main__":
    # Создаем экземпляр детектора
    detector = FaceDetector()
    
    # Обрабатываем все изображения в датасете
    detector.process_dataset()
    
    print("Обработка завершена. Результаты сохранены в папке 'FaceDetectionResults'")