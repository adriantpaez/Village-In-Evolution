import random
import simpy
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm
from threading import Thread
from sys import argv


WOMEN_COUNT = int(argv[2])
MEN_COUNT = int(argv[3])
MONTHS = int(argv[1])
PERSONS = []
NEW_PERSONS = []
SINGLE_MEN_WONT = []
SINGLE_WOMEN_WONT = []
COUPLES = []
SONS = []
count = 0


class Couple:
    def __init__(self, pM, pH):
        self.pM = pM
        self.pH = pH
        self.last_check = 0

    def get_women(self):
        return self.pM

    def get_men(self):
        return self.pH

    def get_couple(self, p):
        if self.pM == p:
            return self.pH
        else:
            return self.pM

    def broke(self):
        if self.last_check == 0 and random.uniform(0, 1) < 0.2:
            COUPLES.remove(self)
            self.pM.couple = None
            self.pH.couple = None
            self.last_check = (self.last_check + 1) % 2
            return True
        self.last_check = (self.last_check + 1) % 2
        return False

    def death_broke(self):
        COUPLES.remove(self)
        self.pM.couple = None
        self.pH.couple = None

    def child(self):
        if self.pM.is_pregnant == 0 and self.pM.want_child() and self.pH.want_child() and self.pM.get_pregnant():
            p = random.uniform(0, 1)
            numb = 5
            if p < 0.7:
                numb = 1
            elif p < 0.88:
                numb = 2
            elif p < 0.96:
                numb = 3
            elif p < 0.99:
                numb = 4
            self.pM.is_pregnant = 9
            self.pM.children = numb


class Person:
    def __init__(self, name, age, is_woman):
        self.name = name
        self.age = age
        self.single = 0
        self.couple = None
        self.is_woman = is_woman
        self.son_count = 0
        self.is_pregnant = 0
        self.children = 0

    def death(self):
        global WOMEN_COUNT, MEN_COUNT, NEW_PERSONS
        p = 1
        if self.age < 12:
            p = 0.25 / (12 * 12)
        elif self.age < 45:
            p = 0.15 / (33 * 12) if self.is_woman else 0.1 / (33 * 12)
        elif self.age < 76:
            p = 0.35 / (31 * 12) if self.is_woman else 0.3 / (31 * 12)
        elif self.age < 125:
            p = 0.65 / (24 * 12) if self.is_woman else 0.7 / (24 * 12)
        if random.uniform(0, 1) < p:
            if self.is_woman:
                WOMEN_COUNT -= 1
            else:
                MEN_COUNT -= 1
            if self.couple is not None:
                self.couple.death_broke()
            return True
        NEW_PERSONS.append(self)
        if self.is_woman:
            self.check_child()
        self.age += 1
        return False

    def want_couple(self):
        p = 0
        if 12 <= self.age < 15:
            p = 0.6
        elif 15 <= self.age < 21:
            p = 0.65
        elif 21 <= self.age < 35:
            p = 0.8
        elif 35 <= self.age < 45:
            p = 0.6
        elif 45 <= self.age < 60:
            p = 0.5
        elif 60 <= self.age < 125:
            p = 0.2
        if random.uniform(0, 1) <= p:
            if self.is_woman:
                for i in range(len(SINGLE_MEN_WONT)):
                    if self.make_couple(SINGLE_MEN_WONT[i]):
                        SINGLE_MEN_WONT.pop(i)
                        break
                else:
                    SINGLE_WOMEN_WONT.append(self)
            else:
                for i in range(len(SINGLE_WOMEN_WONT)):
                    if self.make_couple(SINGLE_WOMEN_WONT[i]):
                        SINGLE_WOMEN_WONT.pop(i)
                        break
                else:
                    SINGLE_MEN_WONT.append(self)
            return True
        return False

    def make_couple(self, other_person):
        diff = abs(self.age - other_person.age)
        p = 0.15
        if diff < 5:
            p = 0.45
        elif diff < 10:
            p = 0.4
        elif diff < 15:
            p = 0.35
        elif diff < 20:
            p = 0.25
        if random.uniform(0, 1) <= p:
            self.couple = other_person.couple = Couple(self, other_person) if self.is_woman \
                else Couple(other_person, self)
            COUPLES.append(self.couple)
            return True
        return False

    def check_couple(self):
        if self.couple is None:
            return
        if not self.couple.broke():
            self.couple.child()

    def want_child(self):
        p = 0
        if self.son_count + 1 == 1:
            p = 0.6
        elif self.son_count + 1 == 2:
            p = 0.75
        elif self.son_count + 1 == 3:
            p = 0.35
        elif self.son_count + 1 == 4:
            p = 0.2
        elif self.son_count + 1 == 5:
            p = 0.1
        else:
            p = 0.05
        return random.uniform(0, 1) < p

    def check_child(self):
        if self.is_pregnant != 0:
            self.is_pregnant -= 1
            if self.is_pregnant == 0:
                for _ in range(self.children):
                    name, women = ("Women", True) if random.uniform(0, 1) < 0.5 else ("Men", False)
                    child = Person(name, 0, women)
                    NEW_PERSONS.append(child)
                self.children = 0
            else:
                env.ob_pregnant[env.now] += 1

    def get_pregnant(self):
        p = 0
        if self.age < 12:
            p = 0
        elif self.age < 15:
            p = 0.2
        elif self.age < 21:
            p = 0.45
        elif self.age < 35:
            p = 0.8
        elif self.age < 45:
            p = 0.4
        elif self.age < 60:
            p = 0.2
        elif self.age < 125:
            p = 0.05
        return random.uniform(0, 1) < p

    def __single_time__(self):
        if 12 <= self.age < 15:
            return random.expovariate(3)
        elif 15 <= self.age < 35:
            return random.expovariate(6)
        elif 35 <= self.age < 45:
            return random.expovariate(12)
        elif 45 <= self.age < 60:
            return random.expovariate(24)
        elif 60 <= self.age < 125:
            return random.expovariate(48)

    def __str__(self):
        return f'Mujer {id(self)}' if self.is_woman else f'Hombre {id(self)}'


print(f'Generating {WOMEN_COUNT} women')
for i in tqdm(range(WOMEN_COUNT)):
    age = random.randint(1, 100 * 12) - 1
    w = Person(f'Woman {i}', age, True)
    PERSONS.append(w)

print(f'Generating {MEN_COUNT} men')
for i in tqdm(range(MEN_COUNT)):
    age = random.randint(1, 100 * 12) - 1
    m = Person(f'Men {i}', age, False)
    PERSONS.append(m)


def initialize_population():
    global SINGLE_MEN_WONT, SINGLE_WOMEN_WONT
    i = 0
    SINGLE_WOMEN_WONT = []
    SINGLE_MEN_WONT = []
    while i < len(PERSONS):
        p = PERSONS[i]
        if not p.death():
            if p.couple is None:
                p.want_couple()
            elif p.couple is not None:
                p.check_couple()
        i += 1


def month(env, months):
    global PERSONS, NEW_PERSONS

    env.ob_persons = [None] * MONTHS
    env.ob_couples = [None] * MONTHS
    env.ob_pregnant = [None] * MONTHS
    env.ob_timeline = [""] * MONTHS

    for _ in tqdm(range(months)):
        y = int(env.now / 12) + 1 + 2020
        m = int(env.now % 12) + 1
        env.ob_timeline[env.now] = f'{m}/{y}'
        env.ob_pregnant[env.now] = 0
        initialize_population()
        env.ob_persons[env.now] = len(PERSONS)
        if len(PERSONS) == 0:
            break
        env.ob_couples[env.now] = len(COUPLES)
        yield env.timeout(1)
        PERSONS = NEW_PERSONS
        NEW_PERSONS = []


env = simpy.Environment()
env.process(month(env, MONTHS))

job = Thread(target=env.run)
job.start()

fig = plt.figure()
ax_persons = fig.add_subplot(2, 2, 1)
ax_couples = fig.add_subplot(2, 2, 2)


def animate(i):
    # line.set_ydata(env.ob_persons)
    ax_persons.clear()
    ax_persons.plot(env.ob_timeline[max(0, env.now - 12):env.now], env.ob_persons[max(0, env.now - 12):env.now])
    ax_persons.title.set_text("Population")
    ax_couples.clear()
    ax_couples.plot(env.ob_timeline[max(0, env.now - 12):env.now], env.ob_couples[max(0, env.now - 12):env.now])
    ax_couples.plot(env.ob_pregnant[max(0, env.now - 12):env.now])
    ax_couples.title.set_text("Couples")
    if len(PERSONS) == 0:
        plt.close()


ani = animation.FuncAnimation(fig, animate, interval=500, save_count=12)

plt.show()

print(f'{int(env.now % 12) + 1}/{int(env.now / 12) + 1 + 2020}')
if len(PERSONS) == 0:
    print('Your population died :(')

plt.plot(env.ob_timeline, env.ob_persons)
plt.xlabel("Month")
plt.ylabel("Population")
plt.show()

plt.plot(env.ob_timeline, env.ob_couples)
plt.xlabel("Month")
plt.ylabel("Couples")
plt.show()
