import random
import matplotlib.pyplot as plt
import numpy as np


class CityGrid:
    def __init__(self, n=10, m=10, obstruct_coverage=30):
        if n < 0:
            self.n = 1
        else:
            self.n = n
        if m < 0:
            self.m = 1
        else:
            self.m = m
        if obstruct_coverage < 0:
            self.obstruct_coverage = 1
        else:
            self.obstruct_coverage = obstruct_coverage
        self.grid = [[0 for _ in range(self.m)] for _ in range(self.n)]
        self.random_obstruct()
        self.towers = {}
        self.visualization_grid = np.zeros((self.n, self.m))

    def print_grid(self):
        for i in self.grid:
            print(i)
        print()

    def random_obstruct(self):
        est_obs = int(self.n*self.m*self.obstruct_coverage/100)
        i = 0
        while i < est_obs:
            rand_n = random.randint(0, self.n-1)
            rand_m = random.randint(0, self.m-1)
            if self.grid[rand_n][rand_m] != 0:
                continue
            self.grid[rand_n][rand_m] = -1
            i += 1

    def place_tower(self, n, m, R):
        if n < 0 or n >= self.n:
            print(f'Place n in range 0, {self.n-1}')
            return
        if m < 0 or m >= self.m:
            print(f'Place m in range 0, {self.m-1}')
            return
        if R < 0:
            print('Radius must be non-negative')
            return
        if self.grid[n][m] != 0:
            print('Block is already used')
            return
        if len(self.towers) == 0:
            i = 1
        else:
            i = list(self.towers)[-1] + 1
        self.grid[n][m] = i
        self.towers[i] = R

    def find_tower_coordinates(self, tower_id):
        for i in range(self.n):
            for j in range(self.m):
                if self.grid[i][j] == tower_id:
                    return i, j

    def visualize_tower_coverage(self, tower_id):
        if tower_id not in self.towers:
            print(f'Tower with ID {tower_id} does not exist')
            return

        R = self.towers[tower_id]
        x, y = self.find_tower_coordinates(tower_id)

        grid = [x[:] for x in self.grid]
        if x is not None and y is not None:
            for i in range(self.n):
                for j in range(self.m):
                    if abs(i - x) <= R and abs(j - y) <= R:
                        grid[i][j] = tower_id

        for i in grid:
            print(i)
        print()

    def optimize_tower_placement(self):
        self.towers = {}
        non_obstructed = [(i, j) for i in range(self.n) for j in range(self.m) if self.grid[i][j] == 0]

        while non_obstructed:
            x, y = non_obstructed[0]
            region = self.find_connected_region(x, y)
            region_center = self.calculate_region_center(region)
            max_distance = max(self.calculate_distance(region_center, (i, j)) for i, j in region)
            self.place_tower(region_center[0], region_center[1], max_distance)
            non_obstructed = [(i, j) for i, j in non_obstructed if (i, j) not in region]

    def find_connected_region(self, x, y):
        stack = [(x, y)]
        region = set()

        while stack:
            x, y = stack.pop()
            if (x, y) in region:
                continue
            region.add((x, y))

            for i, j in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if 0 <= i < self.n and 0 <= j < self.m and self.grid[i][j] == 0:
                    stack.append((i, j))

        return region

    def calculate_region_center(self, region):
        x_values = [x for x, _ in region]
        y_values = [y for _, y in region]
        center_x = sum(x_values) // len(region)
        center_y = sum(y_values) // len(region)
        return center_x, center_y

    def find_reliable_path(self, source_id, target_id):
        if source_id not in self.towers or target_id not in self.towers:
            print("Source or target tower does not exist")
            return

        visited = set()
        queue = [(source_id, [source_id])]
        most_reliable_path = None

        while queue:
            current_id, path = queue.pop(0)
            visited.add(current_id)

            if current_id == target_id:
                if most_reliable_path is None or len(path) < len(most_reliable_path):
                    most_reliable_path = path
                continue

            for neighbor_id in self.get_connected_towers(current_id):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        return most_reliable_path

    def get_connected_towers(self, tower_id):
        connected_towers = set()
        for other_id, other_radius in self.towers.items():
            if other_id != tower_id:
                if self.can_communicate(tower_id, other_id):
                    connected_towers.add(other_id)
        return connected_towers

    def can_communicate(self, tower1_id, tower2_id):
        tower1_x, tower1_y = self.find_tower_coordinates(tower1_id)
        tower2_x, tower2_y = self.find_tower_coordinates(tower2_id)
        distance = self.calculate_distance(tower1_x, tower1_y, tower2_x, tower2_y)
        return distance <= self.towers[tower1_id]

    def calculate_distance(self, x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    def find_all_data_paths(self):
        all_paths = []
        for source_id in self.towers:
            for target_id in self.towers:
                if source_id != target_id:
                    paths = self.dfs_find_paths(source_id, target_id, [])
                    if paths:
                        all_paths.extend(paths)
        return all_paths

    def dfs_find_paths(self, current_id, target_id, path):
        path = path + [current_id]
        if current_id == target_id:
            return [path]
        if current_id not in self.towers:
            return []

        paths = []
        for neighbor_id in self.get_connected_towers(current_id):
            if neighbor_id not in path:
                new_paths = self.dfs_find_paths(neighbor_id, target_id, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def visualize_city(self):
        fig, ax = plt.subplots()

        for i in range(self.n):
            for j in range(self.m):
                if self.grid[i][j] == -1:
                    ax.add_patch(plt.Rectangle((j+0.5, i+0.5), 1, 1, color='gray'))

        for tower_id, R in self.towers.items():
            x, y = self.find_tower_coordinates(tower_id)
            circle = plt.Circle((y, x), R, color='red', fill=False)
            ax.add_artist(circle)
            ax.add_patch(plt.Rectangle((y - 0.5, x - 0.5), 1, 1, color='red'))

        for path in self.find_all_data_paths():
            path_coordinates = [self.find_tower_coordinates(tower_id) for tower_id in path]
            path_x, path_y = zip(*path_coordinates)
            ax.plot(path_y, path_x, marker='o', color='blue')

        ax.set_aspect('equal', adjustable='datalim')
        plt.xlim(0, self.m)
        plt.ylim(0, self.n)
        plt.gca().invert_yaxis()
        plt.show()


def main():
    print('Create city by typing n, m and obstruct_coverage separated by space')
    values = input()
    try:
        n, m, obstruct_coverage = [int(x) for x in values.split(' ')]
        city = CityGrid(n, m, obstruct_coverage)
    except ValueError:
        print('Values must be integers')
        return
    while True:
        print('1. Print city grid\n'
              '2. Place tower\n'
              '3. Visualize tower coverage\n'
              '4. Get most reliable path between two towers\n'
              '5. Visualize city grid\n'
              '6. Exit')
        i = input()
        if i == '1':
            city.print_grid()
        elif i == '2':
            print('Type x, y and R of tower separated by space')
            try:
                x, y, R = [int(x) for x in input().split(' ')]
            except ValueError:
                print('Values must be integers')
                continue
            city.place_tower(x, y, R)
        elif i == '3':
            print('Type tower ID')
            try:
                id = int(input())
            except ValueError:
                print('Values must be integers')
                continue
            city.visualize_tower_coverage(id)
        elif i == '4':
            print('Type two towers IDs separated by space')
            try:
                id1, id2 = [int(x) for x in input().split(' ')]
            except ValueError:
                print('Values must be integers')
                continue
            print("Most reliable path:", city.find_reliable_path(id1, id2))
        elif i == '5':
            city.visualize_city()
        elif i == '6':
            break
        else:
            print('Type correct value')


if __name__ == '__main__':
    main()
