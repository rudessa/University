import cv2
import mediapipe as mp
import numpy as np
import time
import argparse


class RunningSpeedCalculator:
    def __init__(self, video_path, output_path='output_speed.mp4', scaling_factor=1.0, reference_height=1.7):
        """
        Инициализация калькулятора скорости бега.

        Args:
            video_path (str): Путь к видеофайлу
            output_path (str): Путь для сохранения обработанного видео
            scaling_factor (float): Масштабный коэффициент для преобразования пикселей в метры
            reference_height (float): Рост человека в метрах для калибровки (по умолчанию 1.7 м)
        """
        self.video_path = video_path
        self.output_path = output_path
        self.scaling_factor = scaling_factor
        self.reference_height = reference_height

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Не удалось открыть видео: {video_path}")

        # Получение параметров видео
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"FPS: {self.fps}")
        print(f"Разрешение: {self.frame_width}x{self.frame_height}")
        print(f"Всего кадров: {self.total_frames}")

        # Переменные для отслеживания
        self.prev_position = None
        self.current_frame = 0
        self.distances = []
        self.speeds = []
        self.times = []
        self.calibrated = False
        self.pixel_to_meter_ratio = None

    def calibrate_from_height(self, landmarks):
        """
        Калибровка масштаба на основе высоты человека
        Используем расстояние между плечом и голеностопом как приблизительную высоту
        """
        if landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility > 0.7 and \
           landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE].visibility > 0.7:

            shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            ankle = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE]

            shoulder_y = shoulder.y * self.frame_height
            ankle_y = ankle.y * self.frame_height

            pixel_height = abs(ankle_y - shoulder_y)
            # Предполагаем, что расстояние плечо-голеностоп составляет примерно 70% роста
            self.pixel_to_meter_ratio = self.reference_height * 0.7 / pixel_height
            self.calibrated = True

            print(
                f"Калибровка: {pixel_height} пикселей = {self.reference_height * 0.7} метров")
            print(
                f"Коэффициент пересчета: {self.pixel_to_meter_ratio} м/пиксель")

            return True
        return False

    def get_person_position(self, landmarks):
        """
        Получение позиции человека (центр тяжести) на основе ключевых точек
        Используем бедра как центр масс для отслеживания горизонтального перемещения
        """
        if landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].visibility > 0.5 and \
           landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility > 0.5:

            left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]

            center_x = (left_hip.x + right_hip.x) / 2 * self.frame_width
            center_y = (left_hip.y + right_hip.y) / 2 * self.frame_height

            return (center_x, center_y)

        # Если бедра не видны, попробуем использовать другие ключевые точки
        visible_landmarks = [
            (idx, landmark) for idx, landmark in enumerate(landmarks.landmark)
            if landmark.visibility > 0.5
        ]

        if visible_landmarks:
            avg_x = sum(landmark.x for _,
                        landmark in visible_landmarks) / len(visible_landmarks)
            avg_y = sum(landmark.y for _,
                        landmark in visible_landmarks) / len(visible_landmarks)
            return (avg_x * self.frame_width, avg_y * self.frame_height)

        return None

    def calculate_speed(self, position, timestamp):
        """
        Расчет скорости на основе текущей и предыдущей позиции
        """
        if self.prev_position is None or not self.calibrated:
            self.prev_position = position
            return None

        # Расчет перемещения в пикселях
        displacement_pixels = abs(position[0] - self.prev_position[0])

        # Преобразование пикселей в метры
        displacement_meters = displacement_pixels * self.pixel_to_meter_ratio

        # Расчет времени с предыдущего кадра в секундах
        time_diff = 1.0 / self.fps

        # Расчет скорости в м/с
        speed = displacement_meters / time_diff

        # Сохраняем текущее положение как предыдущее для следующего кадра
        self.prev_position = position

        # Данные для графика
        self.distances.append(displacement_meters)
        self.speeds.append(speed)
        self.times.append(timestamp)

        return speed

    def process_video(self):
        """
        Обработка видео и расчет скорости бега
        """
        start_time = time.time()
        frame_count = 0

        # Для сохранения обработанного видео
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_count += 1
            timestamp = frame_count / self.fps

            # Преобразование BGR в RGB для MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Обработка кадра с помощью MediaPipe Pose
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Если не откалибровано, пытаемся калибровать
                if not self.calibrated:
                    self.calibrate_from_height(results.pose_landmarks)

                # Получение позиции человека
                position = self.get_person_position(results.pose_landmarks)

                if position:
                    # Рисуем точку в центре масс
                    cv2.circle(frame, (int(position[0]), int(
                        position[1])), 5, (0, 255, 0), -1)

                    # Расчет скорости
                    speed = self.calculate_speed(position, timestamp)

                    # Отображение данных на кадре
                    if speed is not None:
                        speed_kmh = speed * 3.6  # Конвертация м/с в км/ч
                        cv2.putText(
                            frame,
                            f"Speed: {speed_kmh:.2f} km/h ({speed:.2f} m/s)",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )

                # Рисуем скелет
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(245, 117, 66), thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(245, 66, 230), thickness=2)
                )

            # Отображение прогресса
            progress = (frame_count / self.total_frames) * 100
            cv2.putText(
                frame,
                f"Progress: {progress:.1f}%",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # Записываем кадр в выходное видео
            output_video.write(frame)

            # Показываем кадр
            cv2.imshow('Running Speed Analysis', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Время обработки: {processing_time:.2f} секунд")
        print(f"Результат сохранен в файл: {self.output_path}")

        self.cap.release()
        output_video.release()
        cv2.destroyAllWindows()

        self.analyze_results()

    def analyze_results(self):
        """
        Анализ собранных данных о скорости
        """
        if not self.speeds:
            print("Не удалось получить данные о скорости")
            return

        avg_speed = np.mean(self.speeds)
        max_speed = np.max(self.speeds)

        print(
            f"Средняя скорость: {avg_speed * 3.6:.2f} км/ч ({avg_speed:.2f} м/с)")
        print(
            f"Максимальная скорость: {max_speed * 3.6:.2f} км/ч ({max_speed:.2f} м/с)")

        # Можно также построить график скорости по времени
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(12, 6))
            plt.plot(self.times, [s * 3.6 for s in self.speeds], 'b-')
            plt.title('Скорость бега')
            plt.xlabel('Время (с)')
            plt.ylabel('Скорость (км/ч)')
            plt.grid(True)
            plt.savefig('speed_graph.png')
            plt.show()
        except ImportError:
            print("Для построения графика необходимо установить библиотеку matplotlib")


def main():
    parser = argparse.ArgumentParser(
        description='Калькулятор скорости бега по видео')
    parser.add_argument('--video', type=str, required=True,
                        help='Путь к видеофайлу')
    parser.add_argument('--output', type=str, default='output_speed.mp4',
                        help='Путь для сохранения обработанного видео')
    parser.add_argument('--height', type=float, default=1.7,
                        help='Рост бегущего человека в метрах (для калибровки)')
    parser.add_argument('--scale', type=float, default=1.0,
                        help='Масштабный коэффициент (если известен)')

    args = parser.parse_args()

    calculator = RunningSpeedCalculator(
        video_path=args.video,
        output_path=args.output,
        scaling_factor=args.scale,
        reference_height=args.height
    )

    calculator.process_video()


if __name__ == "__main__":
    main()
