import sqlite3, atexit
import datetime, math

class DataLog:
    def __init__ (self):
        self.database = sqlite3.connect('data.db')
        self.cursor = self.database.cursor()
        atexit.register(self.database.close)
    def logData(self, cur_time, values):
        # 0: soil moisture, 1: humidity, 2: temperature, 3: luminosity, 4: ecg
        ambientInterval = 600
        soilInterval = 3600
        if int(cur_time) % ambientInterval == 0:
            with self.database:
                self.cursor.execute("INSERT INTO ambient VALUES (:datetime, :humidity, :temperature, :luminosity)", {'datetime': cur_time, 'humidity': values[1], 'temperature': values[2], 'luminosity': values[3]})
                print("Logged ambient data")
        if int(cur_time) % soilInterval == 0:
            with self.database:
                self.cursor.execute("INSERT INTO soil VALUES (:datetime, :soil_moisture)", {'datetime': cur_time, 'soil_moisture': values[0]})
                print("Logged soil data")
    def logInteraction(self, cur_time):
        with self.database:
            self.cursor.execute("INSERT INTO interaction VALUES (:datetime)", {'datetime': cur_time})
            print("Logged interaction")
    def getSoil(self):
        # get mean values and lowest value over the past week and translate into mood between 0 and 1
        with self.database:
            self.cursor.execute("SELECT soil_moisture FROM soil WHERE datetime >= strftime('%s', 'now', '-7 days')")
            all_values = self.cursor.fetchall()
            sum = 0
            lowest = 100
            for val in all_values:
                for i in val:
                    sum = sum + i
                    if (i < lowest):
                        lowest = i
            lowest_pc = lowest / 100 # mapped between 0 and 1
            mean = sum / len(all_values) / 100 # mapped between 0 and 1
            return calculateMood(mean, "soil_moisture", soilLowest(lowest_pc))
    def getHumidityAndTemperature(self):
        # get mean values over the past 48 hours and translate into mood between 0 and 1
        with self.database:
            self.cursor.execute("SELECT humidity, temperature FROM ambient WHERE datetime >= strftime('%s', 'now', '-2 days')")
            all_values = self.cursor.fetchall()
            means = [sum(ele) / len(all_values) / 100 for ele in zip(*all_values)] # mapped between 0 and 1
            humidityMood = calculateMood(means[0], "humidity")
            temperatureMood = calculateMood(means[1], "temperature")
            return humidityMood, temperatureMood
    def getLuminosity(self):
        # get all values that satisfy optimum light conditions over past 2 calendar days
        with self.database:
            midnight = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
            unix_mn = midnight.strftime("%s")
            unix_pmn = (midnight - datetime.timedelta(days=2)).strftime("%s")
            self.cursor.execute("SELECT luminosity FROM ambient WHERE datetime BETWEEN ? and ? AND luminosity >= 11000", (unix_pmn, unix_mn,))
            all_values = float(len(self.cursor.fetchall()))
            num_hours = round(all_values / 6, 4)
            return calculateLuminosityMood(num_hours)
    def getInteraction(self):
        # get number of interactions in the past week
        with self.database:
            self.cursor.execute("SELECT datetime FROM interaction WHERE datetime >= strftime('%s', 'now', '-7 days')")
            all_values = float(len(self.cursor.fetchall()))
            mood = round(math.sqrt(all_values) / 5, 4)
            if mood > 1:
                mood = 1
            return mood
    def getMood(self):
        soil = self.getSoil()
        humidity, temperature = self.getHumidityAndTemperature()
        luminosity = self.getLuminosity()
        interaction = self.getInteraction()
        mean = round((soil + humidity + temperature + luminosity + interaction) / 5, 4)
        return mean


def calculateMood(x, data_type, lowest_val=0): 
    if data_type == "humidity":
        c = 89.1
        alpha = 5
        beta = 3.67
    elif data_type == "temperature" :
        c = 559.35
        alpha = 3.8
        beta = 9.5
    elif data_type == "soil_moisture":
        c = 259.67
        alpha = 3.6
        beta = 7.85
    return round(c * pow(x,(alpha-1)) * pow((1 - x), (beta - 1)) + lowest_val, 4)

def soilLowest(val):
    if val < 0.09847:
        val = 0.09847
    elif val > 0.22666:
        val = 0.22666
    y = round(1/((200*val)-12) - 0.03,4)
    return y

def calculateLuminosityMood(val):
    return round(1 / (1 + pow(math.e, -(val-6))), 4)