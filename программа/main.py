import numpy as np
import random
import pygame
import sys


class Model:
    def __init__(self, size):
        self.field = []
        self.field_change = []
        self.field_id = []

        self.quartet = []
        self.quartet_line = []

        self.quartet_energy = []
        self.quartet_energy_change = []

        self.size = size
        self.energy = 0
        self.energy_change = 0

        self.memory = {}

    def find_x_y(self, number):
        y = number // self.size
        x = number % self.size
        return x, y

    def return_number(self, x, y):
        return y * self.size + x

    def create_field(self):
        point = [-1, 1]
        dop = []
        field = []

        for i in range(self.size):
            for j in range(self.size):
                dop.append(random.choice(point))
            field.append(dop)
            dop = []

        self.field = np.array(field)
        self.field_change = self.field.copy()

    def create_field_id(self):
        dop = []
        field = []
        a = 0

        for i in range(self.size):
            for j in range(self.size):
                dop.append(a)
                a += 1
            field.append(dop)
            dop = []

        self.field_id = np.array(field)

    def find_quartet(self):
        quartet = []

        dop = []

        for number in range(self.size * self.size):
            x, y = self.find_x_y(number)

            if x < self.size - 1:
                dop.append(self.return_number(x + 1, y))
            if y < self.size - 1:
                dop.append(self.return_number(x + 1, y + 1))
                dop.append(self.return_number(x, y + 1))
            if len(dop) == 3:
                dop.append(self.return_number(x, y))

            if len(dop) == 4:
                quartet.append(dop)
            dop = []

        self.quartet = np.array(quartet)

    def check_frustration(self, one_quartet, field):
        minus_count = 0
        for i in one_quartet:
            x, y = self.find_x_y(i)
            if field[y][x] < 0:
                minus_count += 1
        if minus_count == 1 or minus_count == 3:
            return 1
        else:
            return 0

    def random_spin(self, field, one_quartet):
        for i in one_quartet:
            x, y = self.find_x_y(i)
            field[y][x] = field[y][x] * -1

    def check_energy(self, field):
        for i in self.quartet:
            if self.check_frustration(i, field) != 1:
                return 0
        return 1

    def spin(self, field, x, y):
        field[y][x] = field[y][x] * -1

    def make_line_quartet(self):
        dop = []
        array = []
        a = 0
        for i in self.quartet:
            dop.append(i)
            a += 1
            if a == self.size - 1:
                array.append(dop)
                a = 0
                dop = []
        self.quartet_line = array

    def find_combination(self):
        number = 0

        dop = []
        collector = []

        dop_extra = []
        collector_extra = []

        skip = 0

        for line in self.quartet_line:
            number = 0
            num_lin = 0
            for q in line:
                if number == 0 and self.check_frustration(line[0], self.field_change) == 0 and \
                        self.check_frustration(line[1], self.field_change) == 1:
                    if num_lin == 0:
                        x, y = self.find_x_y(line[0][3])
                        self.spin(self.field_change, x, y)
                        num_lin += 1
                        number += 1
                    else:
                        x, y = self.find_x_y(line[0][2])
                        self.spin(self.field_change, x, y)

                elif self.check_frustration(q, self.field_change) == 0:
                    dop.append(q)
                    # print("find - ", dop)

                elif self.check_frustration(q, self.field_change) == 1 and len(dop) > 0:
                    collector.append(dop)
                    dop = []
                    # print("collector - ", collector)

                elif number == self.size - 2:
                    if len(dop) > 0:
                        collector.append(dop)
                        dop = []
                        # print("collector - ", collector)

                number += 1
                num_lin = 2
            # print()

            for q_sort in collector:
                if len(q_sort) > 1:
                    counter = 1
                    for q in q_sort:
                        if counter % 2 == 0:
                            x, y = self.find_x_y(q[2])
                            self.spin(self.field_change, x, y)
                        counter += 1
            dop = []
            collector = []

        for line in self.quartet_line:
            dop_extra.append(line[-2])
            dop_extra.append(line[-1])
            collector_extra.append(dop_extra)
            dop_extra = []

        for q in collector_extra:
            if self.check_frustration(q[0], self.field_change) == 1 and \
                    self.check_frustration(q[1], self.field_change) == 0:

                x, y = self.find_x_y(q[1][1])
                self.spin(self.field_change, x, y)

        self.test_energy()

    def find_edges(self):

        collector_1 = []
        collector_2 = []
        dop_1 = []
        dop_2 = []

        counter = 0

        # y = [0, self.size - 2]
        # x = [0, self.size - 2]

        for line in self.quartet_line:
            q_1, q_2 = line[0], line[-1]
            if self.check_frustration(q_1, self.field_change) == 0:
                dop_1.append(q_1)
            else:
                if len(dop_1) > 0:
                    collector_1.append(dop_1)
                    dop_1 = []

            if self.check_frustration(q_2, self.field_change) == 0:
                dop_2.append(q_1)
            else:
                if len(dop_2) > 0:
                    collector_1.append(dop_2)
                    dop_2 = []
            counter += 1
            if counter + 2 >= self.size:
                if len(dop_2) > 0:
                    collector_2.append(dop_2)
                    dop_2 = []
                if len(dop_1) > 0:
                    collector_2.append(dop_1)
                    dop_1 = []

        for q in collector_1:
            number = 1
            if len(q) > 1:
                for q_sort in q:
                    if number % 2 == 0:
                        x, y = self.find_x_y(q_sort[3])
                        self.spin(self.field_change, x, y)
                        number += 1

        for q in collector_2:
            number = 1
            if len(q) > 1:
                for q_sort in q:
                    if number % 2 == 0:
                        x, y = self.find_x_y(q_sort[1])
                        self.spin(self.field_change, x, y)
                        number += 1

    def test_energy(self):
        e = 0
        for i in self.quartet:
            if self.check_frustration(i, self.field) != 1:
                e += 1
        self.energy = e

        e = 0
        for i in self.quartet:
            if self.check_frustration(i, self.field_change) != 1:
                e += 1
        self.energy_change = e

    def check_quartet_energy(self):
        dop = []
        for line in self.quartet_line:
            for q in line:
                if self.check_frustration(q, self.field) == 1:
                    dop.append(1)
                else:
                    dop.append(0)
            self.quartet_energy.append(dop)
            dop = []

        dop = []
        for line in self.quartet_line:
            for q in line:
                if self.check_frustration(q, self.field_change) == 1:
                    dop.append(1)
                else:
                    dop.append(0)
            self.quartet_energy_change.append(dop)
            dop = []

    def return_paremetrs(self):
        super_array = [self.field, self.field_change, self.quartet_energy, self.quartet_energy_change,
                       self.energy, self.energy_change]
        return super_array

    def start(self):
        self.quartet_energy = []
        self.quartet_energy_change = []
        self.memory = {}
        self.create_field()
        self.create_field_id()
        self.find_quartet()
        self.make_line_quartet()
        self.find_combination()
        self.check_quartet_energy()
        self.test_energy()

    def return_field_change(self):
        return self.field_change


pygame.init()


class Interface:
    def __init__(self, size, field, field_change, quartet_energy, quartet_energy_change, energy, energy_change):
        self.screen = pygame.display.set_mode((1800, 1000))
        self.screen.fill((240, 230, 220))

        self.blue = (30, 50, 240)
        self.red = (240, 10, 40)
        self.green = (150, 190, 120)
        self.dark_grey = (207, 215, 230)

        self.x = 5
        self.y = 5

        self.size = size

        self.radius = size * 40 + 6 * (size + 1)
        self.interval = 1800 - self.radius - 6

        self.surface = pygame.Surface((size * 40 + 6 * (size + 1), size * 40 + 6 * (size + 1)))
        self.surface_change = pygame.Surface((size * 40 + 6 * (size + 1), size * 40 + 6 * (size + 1)))
        self.surface.fill(self.blue)
        self.surface_change.fill(self.blue)

        self.marker = 1
        self.block = 1

        print(1000 - self.radius)

        ###############
        self.field = field
        self.field_change = field_change
        self.quartet_energy = quartet_energy
        self.quartet_energy_change = quartet_energy_change
        self.enegy = energy
        self.energy_change = energy_change

    def draw_spin(self, field, surface):
        x, y = 6, 6
        for a in field:
            for b in a:
                if b == 1:
                    pygame.draw.rect(surface, (244, 244, 244), (x, y, 40, 40))
                else:
                    pygame.draw.rect(surface, (3, 3, 3), (x, y, 40, 40))
                x += 46
            x = 6
            y += 46

    def draw_quartets(self, quartet_energy, surface):
        x, y = 4, 4
        for line in quartet_energy:
            for q in line:
                if q == 0:
                    pygame.draw.rect(surface, (255, 10, 10), (x, y, 90, 90), 4)

                x += 46
            y += 46
            x = 6

    def draw_surface(self, surface, field, quartet_energy, x, y):
        surface.fill(self.blue)
        self.draw_spin(field, surface)

        if self.marker == 1:
            self.draw_quartets(quartet_energy, surface)
            self.screen.blit(surface, (x, y))
        else:
            self.screen.blit(surface, (x, y))

    def draw_button(self):
        local_interval = (1000 - self.radius - 90) // 2
        color = ()
        x, y = 10, self.radius + local_interval

        if self.marker == 1:
            color = self.green
        elif self.marker == -1:
            color = self.red

        pygame.draw.rect(self.screen, color, (x, y, 150, 90))

    def change_marker(self, coordinates):
        local_interval = (1000 - self.radius - 90) // 2
        x, y = 10, self.radius + local_interval
        if x < coordinates[0] < 160 and y < coordinates[1] < y + 90:
            self.marker = self.marker * -1

    def draw_text(self):
        local_interval = (1000 - self.radius - 90) // 2
        x, y = 190, self.radius + local_interval
        f1 = pygame.font.Font(None, 36)
        text1 = f1.render(f'Start energy - {self.enegy}', True, (50, 50, 50))
        text2 = f1.render(f'Final energy - {self.energy_change}', True, (50, 50, 50))

        self.screen.blit(text1, (x, y + 30))
        self.screen.blit(text2, (x + 400, y + 30))

    def change_fields(self, field, field_change, quartet_energy, quartet_energy_change, energy, energy_change):
        self.field = field
        self.field_change = field_change
        self.quartet_energy = quartet_energy
        self.quartet_energy_change = quartet_energy_change
        self.enegy = energy
        self.energy_change = energy_change

    def change_spin(self):
        pass

    def start(self):

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.screen.fill((240, 230, 220))

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.change_marker(pygame.mouse.get_pos())

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        model.start()
                        self.change_fields(*model.return_paremetrs())

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        print('ok')
                        model.find_combination()
                        model.quartet_energy = []
                        model.quartet_energy_change = []
                        model.check_quartet_energy()
                        self.change_fields(*model.return_paremetrs())

                self.draw_surface(self.surface, self.field, self.quartet_energy, self.x, self.y)
                self.draw_surface(self.surface_change, self.field_change, self.quartet_energy_change, self.interval,
                                  self.y)

                self.draw_button()
                self.draw_text()

                pygame.display.flip()


# size = int(input('Please input size    '))
# while 2 > size > 19:
#     size = int(input('Please input size    '))
size = 19
model = Model(size)
model.start()

interface = Interface(size, *model.return_paremetrs())
interface.start()
