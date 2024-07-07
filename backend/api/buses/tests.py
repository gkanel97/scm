from datetime import datetime
import pandas as pd
from django.test import TestCase
from unittest.mock import patch
from .monitor import BusDelayMonitor
from .timetables import TimetableOptimizer
import numpy as np

class TestBusDelayMonitor(TestCase):
    def setUp(self):
        start_time = datetime(2024, 1, 1, 6, 0)  # 6:00 AM
        end_time = datetime(2024, 1, 1, 10, 0)   # 10:00 AM
        self.monitor = BusDelayMonitor(start_time, end_time)

    def test_initialization(self):
        self.assertEqual(self.monitor.start_time, datetime(2024, 1, 1, 6, 0))
        self.assertEqual(self.monitor.end_time, datetime(2024, 1, 1, 10, 0))
        self.assertIsInstance(self.monitor.delay_quartiles, list)
        self.assertEqual(len(self.monitor.delay_quartiles), 0)

    @patch('buses.monitor.BusTrip.objects.filter')
    def test_get_trips_df(self, mock_filter):
        mock_filter.return_value.values.return_value = [
            {'trip_id': 1, 'start_datetime': self.monitor.start_time, 'schedule_relationship': 'OnTime', 'route_id': 101, 'direction_id': 1, 'delay': 5}
        ]
        df = self.monitor.get_trips_df()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)

    @patch('buses.monitor.BusRouteShape.objects.all')
    def test_get_route_names(self, mock_all):
        mock_all.return_value.values.return_value = [
            {'route_id': 101, 'route_short_name': 'Route 101', 'sequence': 1}
        ]
        df = self.monitor.get_route_names()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)

    @patch('buses.monitor.BusDelayMonitor.get_trips_df')
    @patch('buses.monitor.BusDelayMonitor.get_route_names')
    def test_calculate_delays(self, mock_get_route_names, mock_get_trips_df):
        mock_get_trips_df.return_value = pd.DataFrame({
            'trip_id': [1],
            'delay': [10],
            'route_id': [101]
        })
        mock_get_route_names.return_value = pd.DataFrame({
            'route_id': [101],
            'route_short_name': ['Route 101']
        }).set_index('route_id')
        df = self.monitor.calculate_delays()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue('delay' in df.columns)

    def test_calculate_delay_quartiles_with_positive_delays(self):
        delays = np.array([5, 15, 20, 35, 50, 60])
        self.monitor.calculate_delay_quartiles(delays)
        # Expected percentiles for the provided delays
        expected_quartiles = np.percentile(delays[delays >= 0], [33, 66])
        self.assertTrue(np.array_equal(self.monitor.delay_quartiles, expected_quartiles))

    def test_calculate_delay_quartiles_with_negative_delays(self):
        delays = np.array([-10, -5, 0, 10, 20, 30])
        self.monitor.calculate_delay_quartiles(delays)
        # Calculate only from non-negative delays
        expected_quartiles = np.percentile(delays[delays >= 0], [33, 66])
        self.assertTrue(np.array_equal(self.monitor.delay_quartiles, expected_quartiles))

    def test_calculate_delay_quartiles_with_all_negative(self):
        delays = np.array([-50, -40, -30])
        self.monitor.calculate_delay_quartiles(delays)
        # Expecting an empty array because all delays are negative
        self.assertEqual(len(self.monitor.delay_quartiles), 0)  # This checks if the array is indeed empty



    def test_classify_delays(self):
        # Set quartiles manually for predictable outcomes
        self.monitor.delay_quartiles = np.array([10, 20])
        # Test each category
        self.assertEqual(self.monitor.classify_delays(-1), 'Early')
        self.assertEqual(self.monitor.classify_delays(0), 'On time')
        self.assertEqual(self.monitor.classify_delays(5), 'Short delay')
        self.assertEqual(self.monitor.classify_delays(15), 'Medium delay')
        self.assertEqual(self.monitor.classify_delays(25), 'Long delay')

    def test_classify_delays_no_quartiles(self):
        self.monitor.delay_quartiles = np.array([])
        self.assertIsNone(self.monitor.classify_delays(10))

class TestTimetableOptimizer(TestCase):
    def setUp(self):
        self.first_bus = datetime(2024, 1, 1, 5, 0)
        self.last_bus = datetime(2024, 1, 1, 23, 0)
        self.target_services = 10
        self.optimizer = TimetableOptimizer(self.first_bus, self.last_bus, self.target_services)

    def test_initialization(self):
        self.assertEqual(self.optimizer.first_bus, self.first_bus)
        self.assertEqual(self.optimizer.last_bus, self.last_bus)
        self.assertEqual(self.optimizer.target_services, self.target_services)
        self.assertEqual(self.optimizer.population_size, 100)
        self.assertEqual(self.optimizer.genes, 20)

    def test_generate_population(self):
        population = self.optimizer.generate_population()
        self.assertEqual(len(population), self.optimizer.population_size - 2)
        for individual in population:
            self.assertEqual(len(individual['chromosome']), self.optimizer.genes)

    def test_fitness_calculation(self):
        chromosome = np.array([0, 10, 20, 30, 40, 50])
        f1, f2 = self.optimizer.fitness(chromosome)
        self.assertEqual(f1, len(chromosome))
        self.assertTrue(isinstance(f2, float)) 

    def test_crossover(self):
        chromosome1 = np.array([0, 20, 40, 60, 80])
        chromosome2 = np.array([0, 30, 50, 70, 90])
        offspring = self.optimizer.crossover(chromosome1, chromosome2)
        for child in offspring:
            self.assertTrue(all(np.diff(child) >= 0))



    def test_genetic_algorithm(self):
        results = self.optimizer.genetic_algorithm()
        self.assertTrue(isinstance(results, list))
        self.assertTrue(all(isinstance(x, dict) for x in results))

    def test_f1_calculation(self):
        chromosome1 = [0, 10, 20, 30, 40, 50]
        chromosome2 = [0, 15, 30, 45]
        chromosome3 = [5, 25, 45, 65, 85, 105, 125]

        expected_lengths = [len(chromosome1), len(chromosome2), len(chromosome3)]

        f1_result1 = self.optimizer.f1(chromosome1)
        f1_result2 = self.optimizer.f1(chromosome2)
        f1_result3 = self.optimizer.f1(chromosome3)

        self.assertEqual(f1_result1, expected_lengths[0], "f1 calculation for chromosome1 is incorrect")
        self.assertEqual(f1_result2, expected_lengths[1], "f1 calculation for chromosome2 is incorrect")
        self.assertEqual(f1_result3, expected_lengths[2], "f1 calculation for chromosome3 is incorrect")


    def test_f2_calculation(self):
        chromosome1 = np.array([0, 10, 20, 30, 40, 50])
        chromosome2 = np.array([50, 10, 30, 20, 40, 0])
        chromosome3 = np.array([10, 20, 20, 30, 40, 50])

        expected_f2_result1 = (10 + 10 + 10 + 10 + 10) / 2
        expected_f2_result2 = expected_f2_result1 
        expected_f2_result3 = (10 + 10 + 10 + 10) / 2

        f2_result1 = self.optimizer.f2(chromosome1)
        f2_result2 = self.optimizer.f2(chromosome2)
        f2_result3 = self.optimizer.f2(chromosome3)

        self.assertEqual(f2_result1, expected_f2_result1, "f2 calculation for chromosome1 is incorrect")
        self.assertEqual(f2_result2, expected_f2_result2, "f2 calculation for chromosome2 is incorrect")
        self.assertEqual(f2_result3, expected_f2_result3, "f2 calculation for chromosome3 is incorrect due to duplicates")
 
    def test_elitism(self):
        population = [{'chromosome': f'Individual{i}', 'f1': i % 50, 'f2': i % 20, 'rank': i % 5 + 1} for i in range(self.optimizer.population_size)]
        elite = self.optimizer.elitism(population)
        self.assertEqual(len(elite), self.optimizer.population_size)

    def test_check_target(self):
        population = [
            {'chromosome': 'A', 'f1': 5},
            {'chromosome': 'B', 'f1': 5},
            {'chromosome': 'C', 'f1': 5},
            {'chromosome': 'D', 'f1': 20}
        ]
        self.optimizer.f1_target = 10
        result = self.optimizer.check_target(population)
        self.assertTrue(result)



