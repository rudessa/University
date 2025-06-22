import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import time
import argparse
import math
from datetime import datetime


class PushUpCounter:
    def __init__(self, video_source=0, elbow_angle_threshold=120, height_threshold_ratio=0.1):
        """
        Initialize the push-up counter using MoveNet.

        Args:
            video_source: Camera index or video file path
            elbow_angle_threshold: Angle threshold for elbow bend (degrees)
            height_threshold_ratio: Ratio of height change to determine up/down positions
        """
        # Загружаем модель MoveNet
        self.model = hub.load(
            'https://tfhub.dev/google/movenet/singlepose/lightning/4')
        self.movenet = self.model.signatures['serving_default']

        self.video_source = video_source
        self.elbow_angle_threshold = elbow_angle_threshold
        self.height_threshold_ratio = height_threshold_ratio

        self.push_up_count = 0  # Счетчик отжиманий
        # Последняя обнаруженная позиция (вверх/вниз)
        self.last_position = None
        self.rep_stage = None  # Текущая стадия отжимания

        # Параметры для отслеживания времени
        self.start_time = None
        self.last_rep_time = None
        self.rep_times = []

        # Для отслеживания начальной высоты и текущей высоты тела
        self.initial_height = None
        self.min_height = None
        self.max_height = None

        # Метод обнаружения положения
        self.detection_method = None

        # Индексы ключевых точек модели MoveNet
        self.keypoint_dict = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 3,
            'right_ear': 4,
            'left_shoulder': 5,
            'right_shoulder': 6,
            'left_elbow': 7,
            'right_elbow': 8,
            'left_wrist': 9,
            'right_wrist': 10,
            'left_hip': 11,
            'right_hip': 12,
            'left_knee': 13,
            'right_knee': 14,
            'left_ankle': 15,
            'right_ankle': 16
        }

    def calculate_angle(self, a, b, c):
        """
        Вычисление угла между тремя точками (в градусах).

        Аргументы:
            a: первая точка [x, y]
            b: средняя точка [x, y] (вершина угла)
            c: конечная точка [x, y]

        Возвращает:
            угол в градусах
        """
        # Преобразование точек в массивы numpy
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        # Вычисление векторов
        ba = a - b
        bc = c - b

        # Вычисление угла с использованием скалярного произведения
        cosine_angle = np.dot(ba, bc) / \
            (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.arccos(cosine_angle) * 180.0 / np.pi

        return angle

    def distance_calculate(self, p1, p2):
        """Вычисление евклидова расстояния между двумя точками."""
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

    def preprocess_image(self, image):
        """Предобработка изображения для модели MoveNet."""
        input_image = tf.convert_to_tensor(image)
        input_image = tf.cast(input_image, dtype=tf.int32)
        input_image = tf.image.resize_with_pad(input_image, 192, 192)
        input_image = tf.cast(input_image, dtype=tf.int32)
        return input_image

    def run_movenet(self, input_image):
        """Запуск модели MoveNet на предобработанном изображении."""
        model_output = self.movenet(input_image)
        keypoints_with_scores = model_output['output_0'].numpy()
        return keypoints_with_scores

    def extract_landmarks(self, keypoints_with_scores, image_width, image_height):
        """Извлечение ключевых точек из результатов обнаружения MoveNet."""
        keypoints = keypoints_with_scores[0, 0, :, :]
        landmarks = {}

        if keypoints[self.keypoint_dict['nose']][2] < 0.2:
            return None

        landmarks["full_landmarks"] = keypoints

        for name, idx in self.keypoint_dict.items():
            y, x, confidence = keypoints[idx]

            if confidence > 0.2:
                landmarks[name] = (
                    int(x * image_width),
                    int(y * image_height)
                )

                landmarks[name + "_3d"] = (x, y, confidence)

        # Проверка наличия минимально необходимых ключевых точек для обнаружения отжимания
        required_keypoints = ['left_shoulder', 'right_shoulder', 'left_elbow',
                              'right_elbow', 'left_wrist', 'right_wrist']

        if not all(kp in landmarks for kp in required_keypoints):
            return None

        return landmarks

    def determine_best_detection_method(self, landmarks):
        """Автоматическое определение лучшего метода для обнаружения отжиманий."""
        if not landmarks:
            return None

        # Проверка, находится ли человек в профильном ракурсе (вид сбоку)
        # Вычисление расстояния между плечами - если небольшое, человек, вероятно, обращен к камере
        if "left_shoulder" not in landmarks or "right_shoulder" not in landmarks:
            return "frontal"  # По умолчанию фронтальный вид, если точки плеч отсутствуют

        left_shoulder = landmarks["left_shoulder"]
        right_shoulder = landmarks["right_shoulder"]
        shoulder_distance = self.distance_calculate(
            left_shoulder, right_shoulder)

        # Проверка относительного положения плеч и бедер
        left_hip = landmarks.get("left_hip")
        right_hip = landmarks.get("right_hip")

        if not left_hip or not right_hip:
            # Если точки бедер не обнаружены, используем расстояние между плечами как прокси
            image_width = max(left_shoulder[0], right_shoulder[0]) * 2
        else:
            # Если плечи далеко друг от друга относительно ширины кадра, человек, вероятно, обращен к камере
            image_width = max(
                left_shoulder[0], right_shoulder[0], left_hip[0], right_hip[0]) * 2

        facing_threshold = 0.2  # 20% ширины кадра

        if shoulder_distance / image_width > facing_threshold:
            # Человек обращен к камере - используем метод высоты и угла локтя
            return "frontal"
        else:
            # Человек в профильном ракурсе - используем метод расстояния между плечом и запястьем
            return "profile"

    def analyze_push_up(self, landmarks, image_width, image_height):
        """
        Анализ позы для обнаружения отжиманий с использованием нескольких методов.
        Возвращает: стадию (down, up или None) и количество отжиманий
        """

        if not landmarks:
            return None, self.push_up_count

        # Если метод обнаружения не установлен, определяем его
        if self.detection_method is None:
            self.detection_method = self.determine_best_detection_method(
                landmarks)
            print(f"Selected detection method: {self.detection_method}")

        # Отслеживание текущего положения
        current_position = None

        # Метод 1: Угол локтя (работает как для фронтального, так и для профильного ракурса)
        if all(key in landmarks for key in ["left_shoulder", "left_elbow", "left_wrist"]):
            left_elbow_angle = self.calculate_angle(
                landmarks["left_shoulder"],
                landmarks["left_elbow"],
                landmarks["left_wrist"]
            )
        else:
            left_elbow_angle = 180   # По умолчанию прямая рука, если точки отсутствуют

        if all(key in landmarks for key in ["right_shoulder", "right_elbow", "right_wrist"]):
            right_elbow_angle = self.calculate_angle(
                landmarks["right_shoulder"],
                landmarks["right_elbow"],
                landmarks["right_wrist"]
            )
        else:
            right_elbow_angle = 180   # По умолчанию прямая рука, если точки отсутствуют

         # Используем средний угол локтя
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2

        # Метод 2: Высота тела (работает для фронтального ракурса)
        # Для расчета высоты нам нужны плечи и лодыжки
        has_shoulders = "left_shoulder" in landmarks and "right_shoulder" in landmarks
        has_ankles = "left_ankle" in landmarks and "right_ankle" in landmarks

        if has_shoulders and has_ankles:
            # Вычисление высоты тела на основе плеч и лодыжек
            left_shoulder_y = landmarks["left_shoulder"][1]
            right_shoulder_y = landmarks["right_shoulder"][1]
            left_ankle_y = landmarks["left_ankle"][1]
            right_ankle_y = landmarks["right_ankle"][1]

            # Средняя высота плеч
            avg_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
            # Средняя высота лодыжек
            avg_ankle_y = (left_ankle_y + right_ankle_y) / 2

            # Текущая высота тела от плеч до лодыжек
            current_height = avg_shoulder_y - avg_ankle_y

            current_height = image_height - current_height

            if self.min_height is None:
                self.min_height = current_height
            if self.max_height is None:
                self.max_height = current_height

            self.min_height = min(self.min_height, current_height)
            self.max_height = max(self.max_height, current_height)

            # Пороговое значение диапазона высоты для счета отжимания
            height_range = self.max_height - self.min_height
            height_threshold = height_range * self.height_threshold_ratio
        else:
            # Если у нас нет нужных точек, полагаемся только на угол локтя
            current_height = 0
            height_threshold = 0
            self.detection_method = "profile"

        if self.detection_method == "frontal" and has_shoulders and has_ankles:
            # Для фронтального ракурса используем комбинацию угла локтя и высоты
            if avg_elbow_angle < self.elbow_angle_threshold and current_height < self.max_height - height_threshold:
                current_position = "down"
            elif avg_elbow_angle > self.elbow_angle_threshold and current_height > self.min_height + height_threshold:
                current_position = "up"
        else:
            # Для профильного ракурса в основном используем угол локтя
            if avg_elbow_angle < self.elbow_angle_threshold:
                current_position = "down"
            elif avg_elbow_angle > self.elbow_angle_threshold:
                current_position = "up"

        # Обнаружение полного отжимания
        if self.last_position == "down" and current_position == "up":
            self.push_up_count += 1

            # Запись информации о времени
            current_time = time.time()
            if self.last_rep_time is not None:
                rep_duration = current_time - self.last_rep_time
                self.rep_times.append(rep_duration)
            self.last_rep_time = current_time

        if current_position:
            self.last_position = current_position

        return current_position, self.push_up_count

    def get_statistics(self):
        """ Расчет статистики """
        stats = {}

        if self.start_time is not None:
            stats["total_duration"] = time.time() - self.start_time
        else:
            stats["total_duration"] = 0

        if self.rep_times:
            stats["avg_rep_time"] = sum(self.rep_times) / len(self.rep_times)
            stats["fastest_rep"] = min(self.rep_times)
            stats["slowest_rep"] = max(self.rep_times)
        else:
            stats["avg_rep_time"] = 0
            stats["fastest_rep"] = 0
            stats["slowest_rep"] = 0

        return stats

    def draw_statistics(self, image, stats):
        """ Отображение статистики """
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255)
        thickness = 2
        line_spacing = 30

        overlay = image.copy()
        cv2.rectangle(overlay, (10, 150), (300, 300), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)

        def format_time(seconds):
            return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

        y_pos = 180
        stats_text = [
            f"Duration: {format_time(stats['total_duration'])}",
            f"Avg Rep: {stats['avg_rep_time']:.2f}s",
            f"Fastest: {stats['fastest_rep']:.2f}s" if stats['fastest_rep'] else "Fastest: --",
            f"Slowest: {stats['slowest_rep']:.2f}s" if stats['slowest_rep'] else "Slowest: --",
            f"Method: {self.detection_method or 'detecting...'}"
        ]

        for text in stats_text:
            cv2.putText(image, text, (20, y_pos), font,
                        font_scale, color, thickness, cv2.LINE_AA)
            y_pos += line_spacing

        return image

    def draw_status_bar(self, image, stage):
        h, w, _ = image.shape
        bar_height = 30
        y_pos = h - bar_height - 10

        cv2.rectangle(image, (10, y_pos), (w - 10, y_pos +
                      bar_height), (100, 100, 100), -1)

        if stage == "down":
            completion = 0.5
            color = (0, 0, 255)
        elif stage == "up":
            completion = 1.0
            color = (0, 255, 0)
        else:
            completion = 0.0
            color = (150, 150, 150)

        bar_width = int((w - 20) * completion)
        cv2.rectangle(image, (10, y_pos), (10 + bar_width,
                      y_pos + bar_height), color, -1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        if stage:
            cv2.putText(image, f"Stage: {stage.upper()}", (20, y_pos + 20),
                        font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            cv2.putText(image, "Position not detected", (20, y_pos + 20),
                        font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        return image

    def draw_pose(self, image, landmarks):
        """ Отрисовка ключевых точек позы и связей между ними """
        if not landmarks or "full_landmarks" not in landmarks:
            return image

        POSE_CONNECTIONS = [
            (self.keypoint_dict['left_shoulder'],
             self.keypoint_dict['right_shoulder']),
            (self.keypoint_dict['left_shoulder'],
             self.keypoint_dict['left_elbow']),
            (self.keypoint_dict['right_shoulder'],
             self.keypoint_dict['right_elbow']),
            (self.keypoint_dict['left_elbow'],
             self.keypoint_dict['left_wrist']),
            (self.keypoint_dict['right_elbow'],
             self.keypoint_dict['right_wrist']),
            (self.keypoint_dict['left_shoulder'],
             self.keypoint_dict['left_hip']),
            (self.keypoint_dict['right_shoulder'],
             self.keypoint_dict['right_hip']),
            (self.keypoint_dict['left_hip'], self.keypoint_dict['right_hip']),
            (self.keypoint_dict['left_hip'], self.keypoint_dict['left_knee']),
            (self.keypoint_dict['right_hip'],
             self.keypoint_dict['right_knee']),
            (self.keypoint_dict['left_knee'],
             self.keypoint_dict['left_ankle']),
            (self.keypoint_dict['right_knee'],
             self.keypoint_dict['right_ankle'])
        ]

        keypoints = landmarks["full_landmarks"]
        h, w, _ = image.shape

        # Отрисовка всех ключевых точек
        for i, (y, x, confidence) in enumerate(keypoints):
            if confidence > 0.2:
                cx, cy = int(x * w), int(y * h)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)

        # Отрисовка связей между точками
        for connection in POSE_CONNECTIONS:
            start_idx, end_idx = connection
            if keypoints[start_idx][2] > 0.2 and keypoints[end_idx][2] > 0.2:
                start_point = (
                    int(keypoints[start_idx][1] * w), int(keypoints[start_idx][0] * h))
                end_point = (int(keypoints[end_idx][1] * w),
                             int(keypoints[end_idx][0] * h))
                cv2.line(image, start_point, end_point, (0, 255, 0), 2)

        return image

    def draw_angles(self, image, landmarks):
        """ Отображение углов локтей на изображении """
        if not landmarks:
            return image

        if all(key in landmarks for key in ["left_shoulder", "left_elbow", "left_wrist"]):
            left_elbow_angle = self.calculate_angle(
                landmarks["left_shoulder"],
                landmarks["left_elbow"],
                landmarks["left_wrist"]
            )

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 255, 255)
            thickness = 2

            cv2.putText(
                image,
                f"{int(left_elbow_angle)}°",
                landmarks["left_elbow"],
                font,
                font_scale,
                color,
                thickness,
                cv2.LINE_AA
            )

        if all(key in landmarks for key in ["right_shoulder", "right_elbow", "right_wrist"]):
            right_elbow_angle = self.calculate_angle(
                landmarks["right_shoulder"],
                landmarks["right_elbow"],
                landmarks["right_wrist"]
            )

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 255, 255)
            thickness = 2

            cv2.putText(
                image,
                f"{int(right_elbow_angle)}°",
                landmarks["right_elbow"],
                font,
                font_scale,
                color,
                thickness,
                cv2.LINE_AA
            )

        return image

    def run(self):
        """ Основная функция для запуска счетчика """

        try:
            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened():
                raise ValueError(
                    f"Could not open video source {self.video_source}")

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Создание объекта записи выходного видео
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"pushup_movenet_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

            self.start_time = time.time()

            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("End of video stream.")
                    break

                display_image = image.copy()
                input_image = self.preprocess_image(image)

                # Запуск обнаружения позы
                keypoints_with_scores = self.run_movenet(
                    tf.expand_dims(input_image, axis=0))

                # Извлечение ключевых точек
                image_height, image_width, _ = image.shape
                landmarks = self.extract_landmarks(
                    keypoints_with_scores, image_width, image_height)

                # Анализ движения отжимания
                stage, count = self.analyze_push_up(
                    landmarks, image_width, image_height)

                # Отрисовка
                display_image = self.draw_pose(display_image, landmarks)
                display_image = self.draw_angles(display_image, landmarks)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(
                    display_image, f"Push-up count: {count}", (50, 100), font, 2, (255, 0, 0), 3, cv2.LINE_AA)
                display_image = self.draw_status_bar(display_image, stage)
                stats = self.get_statistics()
                display_image = self.draw_statistics(display_image, stats)

                # Запись кадра в выходное видео
                out.write(display_image)

                cv2.imshow('MoveNet Push-up Counter', display_image)

                if cv2.waitKey(5) & 0xFF == 27:
                    break

            cap.release()
            out.release()
            cv2.destroyAllWindows()

            print(f"Workout complete! {count} push-ups performed.")
            print(f"Total duration: {stats['total_duration']:.2f} seconds")
            if stats['avg_rep_time'] > 0:
                print(f"Average rep time: {stats['avg_rep_time']:.2f} seconds")
            print(f"Output saved to {output_file}")

        except Exception as e:
            print(f"Error: {e}")
            return False

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Push-up counter using MoveNet')
    parser.add_argument('--video', type=str, default='0',
                        help='Path to video file or camera index (default: 0 for webcam)')
    parser.add_argument('--elbow-angle-threshold', type=float, default=120,
                        help='Angle threshold for elbow bend (default: 120 degrees)')
    parser.add_argument('--height-threshold-ratio', type=float, default=0.1,
                        help='Ratio of height change to determine up/down positions (default: 0.1)')

    args = parser.parse_args()

    # Преобразование строки '0' в целое число 0 для веб-камеры
    if args.video.isdigit():
        args.video = int(args.video)

    # Создание и запуск счетчика отжиманий
    counter = PushUpCounter(
        video_source=args.video,
        elbow_angle_threshold=args.elbow_angle_threshold,
        height_threshold_ratio=args.height_threshold_ratio
    )
    counter.run()


if __name__ == "__main__":
    main()
