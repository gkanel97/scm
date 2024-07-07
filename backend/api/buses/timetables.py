import random
import numpy as np
from datetime import timedelta

class TimetableOptimizer():

    def __init__(self, first_bus, last_bus, target_services):
        """
        Initializes an instance of the class with parameters for bus service optimization using a genetic algorithm.
        This setup involves specifying the first and last bus times, the number of target services, and various 
        parameters for the genetic algorithm itself.

        :param first_bus: The datetime representing the first bus departure.
        :type first_bus: datetime.datetime
        :param last_bus: The datetime representing the last bus departure.
        :type last_bus: datetime.datetime
        :param target_services: The number of services to target for optimization.
        :type target_services: int
        """

        # Initialize parameters from user input
        self.first_bus = first_bus
        self.last_bus = last_bus
        self.target_services = target_services

        # Initialize genetic algorithm parameters
        self.population_size = 100
        self.genes = 2 * target_services
        self.mutation_rate = 0.1
        self.n_generations = 100
        self.tournament_size = 5
        self.f1_target = target_services

        # max_value is the difference between the last bus and the first bus in minutes
        self.max_value = (self.last_bus - self.first_bus).seconds // 60

        # max_diff and min_diff are the maximum and minimum differences between consecutive services in minutes
        self.max_diff = 20
        self.min_diff = 2


    def f1(self, chromosome):
        """
        Calculates the actual number of services (bus trips) represented by a chromosome in the genetic algorithm.
        This method simply returns the length of the chromosome, which represents the total number of services.

        :param chromosome: A list or similar structure representing a chromosome in the genetic algorithm, where
                        each gene represents a bus service.
        :type chromosome: list or any sequence type

        :returns: The number of services (genes) in the given chromosome.
        :rtype: int
        """
        return len(chromosome)

    def f2(self, chromosome):
        """
        This method estimates the total expected waiting time for all passengers based on the assumption 
        of uniformly distributed arrivals between services. It computes half the sum of the differences 
        between consecutive service times.

        :param chromosome: A sequence representing a chromosome in the genetic algorithm, where each element 
                        is a service time.
        :type chromosome: array-like

        :returns: The sum of half of the differences between consecutive service times, representing the
                expected waiting time.
        :rtype: float
        """
        chromosome = np.unique(chromosome)
        return np.sum(np.diff(chromosome)) / 2

    def fitness(self, chromosome):
        """
        Computes the overall fitness score of a chromosome in the genetic algorithm based on its individual 
        fitness components. This method combines the results from the `f1` and `f2` fitness functions to 
        produce a single fitness value.

        :param chromosome: A sequence representing a chromosome in the genetic algorithm, where each element 
                        is a service time.
        :type chromosome: array-like

        :returns: A tuple containing the fitness scores computed by the `f1` and `f2` fitness functions, respectively.
        :rtype: tuple
        """
        return self.f1(chromosome), self.f2(chromosome)


    def generate_population(self):
        """
        Generates a population of chromosomes, each represented by a sorted array of gene values.

        :return: A list of dictionaries, each containing a sorted chromosome array.
        :rtype: list
        """
        population = []
        for i in range(self.population_size-2):
            chromosome = np.random.choice(range(1, self.max_value), self.genes-2, replace=False)
            chromosome = np.append(chromosome, [0, self.max_value])
            chromosome = np.unique(chromosome)
            population.append({'chromosome': chromosome})
        return population


    def non_dominated_ranking(self, population):
        """
        Applies non-dominated sorting to rank a population based on multiple objectives (f1 and f2).

        :param population: The list of chromosomes, each containing attributes 'f1' and 'f2' representing 
                           their fitness scores for the respective objectives.
        :type population: list
        :return: A list of chromosomes sorted by non-dominance rank, with added 'rank' attributes.
        :rtype: list
        """
        ranked_population = []
        curr_rank_idx = 1
        curr_values = population.copy()
        next_round_values = []
        while len(curr_values) > 0:
            for i, chromosome in enumerate(curr_values):
                dominated = False
                for j, chromosome_ in enumerate(curr_values):
                    if i == j:
                        continue
                    if (chromosome['f1'] > chromosome_['f1'] and chromosome['f2'] >= chromosome_['f2']) or (chromosome['f1'] >= chromosome_['f1'] and chromosome['f2'] > chromosome_['f2']):
                        dominated = True
                        break
                if dominated:
                    next_round_values.append(chromosome)
                else:
                    chromosome['rank'] = curr_rank_idx
                    ranked_population.append(chromosome)
            curr_rank_idx += 1
            curr_values = next_round_values.copy()
            next_round_values = []
        return ranked_population
    
    def tournament_selection(self, population):
        """
        Selects two best chromosomes from a population based on their rank after performing a tournament selection.

        :param population: The list of all chromosomes, each with a 'rank' attribute.
        :type population: list
        :param tournament_size: The number of chromosomes to include in each tournament.
        :type tournament_size: int
        :return: A tuple containing the two best chromosomes from the tournament.
        :rtype: tuple
        """
        tournament = random.choices(population, k=self.tournament_size)
        ranked_tournament = sorted(tournament, key=lambda x: x['rank'], reverse=True)
        return ranked_tournament[0], ranked_tournament[1]
    
    def crossover(self, chromosome1, chromosome2):
        """
        Performs a crossover operation between two chromosomes and ensures the resulting chromosomes meet a specified condition.

        :param chromosome1: The first parent chromosome.
        :type chromosome1: numpy.array
        :param chromosome2: The second parent chromosome.
        :type chromosome2: numpy.array
        :param max_diff: The maximum allowed difference between consecutive genes in a chromosome.
        :type max_diff: int
        :return: A list of new chromosomes that have been checked for gene difference constraints.
        :rtype: list
        """
        crossover_point = random.randint(1, min(len(chromosome1), len(chromosome2))-1)
        new_chromosome1 = np.concatenate((chromosome1[:crossover_point], chromosome2[crossover_point:]))
        new_chromosome2 = np.concatenate((chromosome2[:crossover_point], chromosome1[crossover_point:]))

        new_chromosomes = []
        for c in [new_chromosome1, new_chromosome2]:
            overlap_flag = np.any(np.diff(c) < 0)
            if overlap_flag:
                overlap_start_idx = np.where(np.diff(c) < 0)[0][0]
                if c[overlap_start_idx] == np.max(c):
                    overlap_end_idx = overlap_start_idx
                else:
                    overlap_end_idx = np.where(c - c[overlap_start_idx] > 0)[0][0]
                new_chromosome = np.concatenate((c[:overlap_start_idx], c[overlap_end_idx:]))
                new_chromosomes.append(new_chromosome)
            else:
                if np.max(np.diff(c)) < self.max_diff:
                    new_chromosomes.append(c)
                    
        return new_chromosomes
    
    def mutation(self, chromosome):
        """
        Applies mutation to a chromosome based on a given mutation rate and ensures the resulting chromosome meets a specified maximum difference constraint.

        :param chromosome: The chromosome to be mutated.
        :type chromosome: numpy.array
        :param mutation_rate: The probability of each gene undergoing mutation.
        :type mutation_rate: float
        :param max_value: The maximum possible value for any gene in the chromosome.
        :type max_value: int
        :param max_diff: The maximum allowed difference between consecutive genes in a chromosome after mutation.
        :type max_diff: int
        :return: The mutated chromosome that meets the max difference constraint.
        :rtype: numpy.array
        """
        for i in range(1, len(chromosome)-1): # Do not mutate first and last routes
            if random.random() < self.mutation_rate:
                chromosome[i] = random.randint(0, self.max_value)
        chromosome = np.unique(chromosome)
        return chromosome
    
    def elitism(self, population):
        """
        Selects the top-performing individuals from the population based on their rank and secondary fitness criteria.

        :param population: The list of all chromosomes in the current generation, each with attributes 'rank' and 'f2'.
        :type population: list
        :param elite_size: The number of top individuals to preserve as the elite.
        :type elite_size: int
        :return: A list of the elite individuals.
        :rtype: list
        """
        elite = sorted(population, key=lambda x: (x['rank'], x['f2']))[:self.population_size]
        return elite
    
    def check_target(self, population):
        """
        Checks if more than half of the population's individuals meet or are below a specified fitness target for the 'f1' attribute.

        :param population: The list of all chromosomes in the current generation, each with an 'f1' attribute.
        :type population: list
        :param f1_target: The target value for the 'f1' fitness attribute that individuals need to meet or be below.
        :type f1_target: float
        :return: True if more than half of the population meets or is below the f1 target; otherwise, False.
        :rtype: bool
        """
        f1_values = [x['f1'] for x in population]
        values_below_target = [x for x in f1_values if x <= self.f1_target]
        return len(values_below_target) > len(population) / 2
    
    def convert_chromosome_to_timetable(self, chromosome):
        """
        Converts a chromosome representing bus departure times into a list of bus departure times.

        :param chromosome: The chromosome, a list of gene values where each gene represents minutes past the first bus departure.
        :type chromosome: list
        :return: A list of bus departure times, starting with the first bus and ending with the last bus.
        :rtype: list of datetime.datetime
        """
        timetable = [self.first_bus]
        for c in chromosome[1:]:
            route_timedelta = timedelta(minutes=int(c))
            timetable.append(timetable[0] + route_timedelta)
        return timetable
    
    def genetic_algorithm(self):
        """
        Executes a genetic algorithm to find optimal solutions based on fitness functions 'f1' and 'f2'.

        :return: A list of dictionaries, each containing the optimal timetable, number of services, and average waiting time.
        :rtype: list of dict
        """
        population = self.generate_population()
        generation = 0
        pareto_solutions = [population]
        while generation < self.n_generations:
            for chromosome in population:
                chromosome['f1'], chromosome['f2'] = self.fitness(chromosome['chromosome'])
            parent_population = self.non_dominated_ranking(population)
            offspring_population = []
            while len(offspring_population) < self.population_size:
                parent1, parent2 = self.tournament_selection(parent_population)
                children = self.crossover(parent1['chromosome'], parent2['chromosome'])
                for child in children:
                    child = self.mutation(child)
                    offspring_population.append({'chromosome': child})
            for chromosome in offspring_population:
                chromosome['f1'], chromosome['f2'] = self.fitness(chromosome['chromosome'])
            offspring_population = self.non_dominated_ranking(offspring_population)
            new_population = self.elitism(parent_population + offspring_population)
            pareto_solutions.append(new_population)
            population = new_population
            generation += 1
            if self.check_target(population):
                break
        optimal_timetables = []
        for x in population:
            if x['rank'] == 1:
                optimal_timetables.append({
                    'timetable': self.convert_chromosome_to_timetable(x['chromosome']),
                    'num_services': x['f1'],
                    'waiting_time': x['f2'] / x['f1']
                })
        return optimal_timetables