# data_generator.py
# Генератор тестовых данных GNSS для тестирования программы

import csv
import random
from datetime import datetime, timedelta

def generate_test_data(file_path, num_points=100):
    """Generate synthetic GNSS tracking data for testing"""
    
    # Starting point (approximately Moscow, Russia)
    lat = 55.7558
    lon = 37.6173
    alt = 144.0  # meters
    
    # Starting time (current time)
    current_time = datetime.now().replace(microsecond=0)
    
    # Open file for writing
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['timestamp', 'latitude', 'longitude', 'altitude', 'speed', 'satellites'])
        
        # Generate points along a random walk
        for i in range(num_points):
            # Add some random movement (realistic for walking/driving)
            lat += random.uniform(-0.001, 0.001)  # ~100m in latitude
            lon += random.uniform(-0.001, 0.001)  # ~100m in longitude
            alt += random.uniform(-2, 2)  # Change in altitude
            
            # Calculate a somewhat realistic speed (0-60 km/h)
            speed = random.uniform(0, 60)
            
            # Variable number of satellites (between 4 and 12)
            satellites = random.randint(4, 12)
            
            # Increment time (1 minute between points)
            current_time += timedelta(minutes=1)
            
            # Write the data point
            writer.writerow([
                current_time.strftime('%Y-%m-%d %H:%M:%S'),
                f"{lat:.6f}",
                f"{lon:.6f}",
                f"{alt:.1f}",
                f"{speed:.1f}",
                satellites
            ])
    
    print(f"Generated {num_points} test data points and saved to {file_path}")

if __name__ == "__main__":
    generate_test_data("test_data.csv", 120)  