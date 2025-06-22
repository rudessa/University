# gnss_tracker.py
# Простой парсер и анализатор данных GNSS трекинга

import os, sys, csv, math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class processing:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {"time": [], "lat": [], "lon": [], "alt": [], "speed": [], "satellites": []}
        self.processing_done = False

    def load_data(self):
        try:
            with open(self.file_path, "r") as f:
                reader = csv.reader(f, delimiter=",")
                header = next(reader)  
                
                for row in reader:
                    if len(row) >= 6: # Базовая проверка
                        # Parse time
                        self.data["time"].append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                        # Parse position
                        self.data["lat"].append(float(row[1]))
                        self.data["lon"].append(float(row[2]))
                        self.data["alt"].append(float(row[3]))
                        # Parse speed
                        self.data["speed"].append(float(row[4]))
                        # Parse satellites count
                        self.data["satellites"].append(int(row[5]))
            
            print("Data loaded successfully!")
            return True
        except Exception as e:
            print("Error loading data:", e)
            return False

    def process(self):
        # Calculate some basic stats
        if len(self.data["lat"]) == 0:
            print("No data to process!")
            return False
        
        self.stats = {}
        self.stats["distance"] = self.calculate_distance()
        self.stats["avg_speed"] = sum(self.data["speed"]) / len(self.data["speed"])
        self.stats["max_speed"] = max(self.data["speed"])
        self.stats["duration"] = (self.data["time"][-1] - self.data["time"][0]).total_seconds() / 3600  # hours
        self.stats["avg_satellites"] = sum(self.data["satellites"]) / len(self.data["satellites"])
        
        self.processing_done = True
        print("Processing completed!")
        return True

    def calculate_distance(self):
        """Calculate total distance traveled using Haversine formula"""
        total_distance = 0
        
        for i in range(1, len(self.data["lat"])):
            lat1, lon1 = self.data["lat"][i-1], self.data["lon"][i-1]
            lat2, lon2 = self.data["lat"][i], self.data["lon"][i]
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Radius of Earth in kilometers
            distance = c * r
            
            total_distance += distance
        
        return total_distance

    def plot_track(self):
        if not self.processing_done:
            print("Please process data first!")
            return False
        
        plt.figure(figsize=(10, 8))
        plt.plot(self.data["lon"], self.data["lat"])
        plt.scatter(self.data["lon"][0], self.data["lat"][0], color='green', label='Start')
        plt.scatter(self.data["lon"][-1], self.data["lat"][-1], color='red', label='End')
        plt.title("GNSS Track")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.legend()
        plt.savefig("track.png")
        plt.close()
        
        print("Track plotted and saved as 'track.png'")
        return True
    
    def plot_speed(self):
        if not self.processing_done:
            print("Please process data first!")
            return False
        
        # Convert datetime to relative time in hours
        relative_time = [(t - self.data["time"][0]).total_seconds() / 3600 for t in self.data["time"]]
        
        plt.figure(figsize=(12, 6))
        plt.plot(relative_time, self.data["speed"])
        plt.title("Speed vs Time")
        plt.xlabel("Time (hours)")
        plt.ylabel("Speed (km/h)")
        plt.grid(True)
        plt.savefig("speed.png")
        plt.close()
        
        print("Speed plot saved as 'speed.png'")
        return True
    
    def plot_altitude(self):
        if not self.processing_done:
            print("Please process data first!")
            return False
        
        # Convert datetime to relative time in hours
        relative_time = [(t - self.data["time"][0]).total_seconds() / 3600 for t in self.data["time"]]
        
        plt.figure(figsize=(12, 6))
        plt.plot(relative_time, self.data["alt"])
        plt.title("Altitude vs Time")
        plt.xlabel("Time (hours)")
        plt.ylabel("Altitude (m)")
        plt.grid(True)
        plt.savefig("altitude.png")
        plt.close()
        
        print("Altitude plot saved as 'altitude.png'")
        return True
        
    def plot_satellites(self):
        if not self.processing_done:
            print("Please process data first!")
            return False
        
        # Convert datetime to relative time in hours
        relative_time = [(t - self.data["time"][0]).total_seconds() / 3600 for t in self.data["time"]]
        
        plt.figure(figsize=(12, 6))
        plt.plot(relative_time, self.data["satellites"])
        plt.title("Satellites Count vs Time")
        plt.xlabel("Time (hours)")
        plt.ylabel("Number of Satellites")
        plt.grid(True)
        plt.savefig("satellites.png")
        plt.close()
        
        print("Satellites plot saved as 'satellites.png'")
        return True
        
    def generate_report(self):
        if not self.processing_done:
            print("Please process data first!")
            return False
        
        with open("report.txt", "w") as f:
            f.write("GNSS Track Analysis Report\n")
            f.write("=========================\n\n")
            f.write(f"File analyzed: {self.file_path}\n")
            f.write(f"Track date: {self.data['time'][0].strftime('%Y-%m-%d')}\n")
            f.write(f"Start time: {self.data['time'][0].strftime('%H:%M:%S')}\n")
            f.write(f"End time: {self.data['time'][-1].strftime('%H:%M:%S')}\n")
            f.write(f"Duration: {self.stats['duration']:.2f} hours\n")
            f.write(f"Total distance: {self.stats['distance']:.2f} km\n")
            f.write(f"Average speed: {self.stats['avg_speed']:.2f} km/h\n")
            f.write(f"Maximum speed: {self.stats['max_speed']:.2f} km/h\n")
            f.write(f"Average satellite count: {self.stats['avg_satellites']:.1f}\n")
        
        print("Report generated and saved as 'report.txt'")
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python gnss_tracker.py <data_file.csv>")
        return
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return
    
    processor = processing(file_path)
    
    if processor.load_data() and processor.process():
        processor.plot_track()
        processor.plot_speed()
        processor.plot_altitude()
        processor.plot_satellites()
        processor.generate_report()
        
        print("All processing completed successfully!")

if __name__ == "__main__":
    main()
