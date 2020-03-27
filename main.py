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
NEW_COUPLES = []
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
        self.age = 0

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
            self.pM.__single_time__()
            self.pH.__single_time__()
            self.last_check = (self.last_check + 1) % 2
            return True, self.age
        NEW_COUPLES.append(self)
        self.last_check = (self.last_check + 1) % 2
        self.age += 1
        return False, self.age

    def death_broke(self):
        COUPLES.remove(self)
        self.pM.couple = None
        self.pH.couple = None

    def child(self):
        if self.pM.is_pregnant == 0 and self.pM.want_child() and self.pH.want_child() and self.pM.get_pregnant():
            p = random.uniform(0, 1)
            numb = 4
            if p < 0.9889:
                numb = 1
            elif p < 0.9989:
                numb = 2
            elif p < 0.9999:
                numb = 3
            self.pM.is_pregnant = 9
            self.pM.children = numb
            self.pM.father = self.pH


class Person:
    def __init__(self, name, age, is_woman):
        self.name = name
        self.age = age
        self.ageYear = age / 12
        self.single = 0
        self.couple = None
        self.is_woman = is_woman
        self.son_count = 0
        self.is_pregnant = 0
        self.children = 0

    def death(self):
        global WOMEN_COUNT, MEN_COUNT, NEW_PERSONS
        if self.ageYear < 1:
            p = 1 / 2724 if self.is_woman else 1 / 2124
        elif self.ageYear < 4:
            p = 1 / 64512 if self.is_woman else 1 / 52632
        elif self.ageYear < 14:
            p = 1 / 125004 if self.is_woman else 1 / 99996
        elif self.ageYear < 24:
            p = 1 / 49584 if self.is_woman else 1 / 22896
        elif self.ageYear < 34:
            p = 1 / 29856 if self.is_woman else 1 / 14580
        elif self.ageYear < 44:
            p = 1 / 13272 if self.is_woman else 1 / 7956
        elif self.ageYear < 54:
            p = 1 / 5052 if self.is_woman else 1 / 3348
        elif self.ageYear < 64:
            p = 1 / 2136 if self.is_woman else 1 / 1344
        elif self.ageYear < 74:
            p = 1 / 780 if self.is_woman else 1 / 504
        elif self.ageYear < 84:
            p = 1 / 252 if self.is_woman else 1 / 180
        else:
            p = 1 / 84 if self.is_woman else 1 / 72
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
        self.ageYear = self.age / 12
        return False

    def want_couple(self):
        if self.single != 0:
            self.single -= 1
            return False
        if 12 <= self.ageYear < 15:
            p = 0.6
        elif 15 <= self.ageYear < 21:
            p = 0.65
        elif 21 <= self.ageYear < 35:
            p = 0.8
        elif 35 <= self.ageYear < 45:
            p = 0.6
        elif 45 <= self.ageYear < 60:
            p = 0.5
        elif 60 <= self.ageYear < 125:
            p = 0.2
        else:
            p = 0
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
        diff = abs(self.ageYear - other_person.ageYear)
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
            NEW_COUPLES.append(self.couple)
            return True
        return False

    def check_couple(self):
        if self.couple is None:
            return
        ok, _ = self.couple.broke()
        if not ok:
            self.couple.child()

    def want_child(self):
        if self.son_count + 1 == 1:
            p = 0.9901
        elif self.son_count + 1 == 2:
            p = 0.4401
        elif self.son_count + 1 == 3:
            p = 0.0401
        elif self.son_count + 1 == 4:
            p = 0.0011
        else:
            p = 0.0099
        return random.uniform(0, 1) < p

    def check_child(self):
        global WOMEN_COUNT, MEN_COUNT
        if self.is_pregnant != 0:
            self.is_pregnant -= 1
            if self.is_pregnant == 0:
                for _ in range(self.children):
                    name, women = ("Women", True) if random.uniform(0, 1) < 0.5 else ("Men", False)
                    child = Person(name, 0, women)
                    NEW_PERSONS.append(child)
                    if child.is_woman:
                        WOMEN_COUNT += 1
                    else:
                        MEN_COUNT += 1
                self.son_count += self.children
                self.father.son_count += self.children
                self.father = None
                self.children = 0
            else:
                env.ob_pregnant[env.now] += 1

    def get_pregnant(self):
        if self.ageYear < 12:
            p = 0
        elif self.ageYear < 15:
            p = 0.2
        elif self.ageYear < 21:
            p = 0.85
        elif self.ageYear < 25:
            p = 0.9
        elif self.ageYear < 30:
            p = 0.8
        elif self.ageYear < 35:
            p = 0.75
        elif self.ageYear < 40:
            p = 0.55
        elif self.ageYear < 45:
            p = 0.38
        elif self.ageYear < 60:
            p = 0.05
        else:
            return False
        return random.uniform(0, 1) < p

    def __single_time__(self):
        if 12 <= self.ageYear < 15:
            self.single = int(random.expovariate(3))
        elif 15 <= self.ageYear < 35:
            self.single = int(random.expovariate(6))
        elif 35 <= self.ageYear < 45:
            self.single = int(random.expovariate(12))
        elif 45 <= self.ageYear < 60:
            self.single = int(random.expovariate(24))
        elif 60 <= self.ageYear < 125:
            self.single = int(random.expovariate(48))

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
            else:
                p.check_couple()
        i += 1


def month(env, months):
    global PERSONS, NEW_PERSONS, COUPLES, NEW_COUPLES

    env.ob_persons = [None] * MONTHS
    env.ob_women = [None] * MONTHS
    env.ob_men = [None] * MONTHS
    env.ob_couples = [None] * MONTHS
    env.ob_pregnant = [None] * MONTHS
    env.ob_timeline = [""] * MONTHS

    for _ in tqdm(range(months)):
        y = int(env.now / 12) + 1 + 2020
        m = int(env.now % 12) + 1
        env.ob_timeline[env.now] = f'{m}/{y}'
        env.ob_pregnant[env.now] = 0
        env.ob_persons[env.now] = len(PERSONS)
        env.ob_women[env.now] = WOMEN_COUNT
        env.ob_men[env.now] = MEN_COUNT
        env.ob_couples[env.now] = len(COUPLES)
        initialize_population()
        if len(PERSONS) == 0:
            break
        yield env.timeout(1)
        PERSONS = NEW_PERSONS
        COUPLES = NEW_COUPLES
        NEW_COUPLES = []
        NEW_PERSONS = []


env = simpy.Environment()
env.process(month(env, MONTHS))

job = Thread(target=env.run)
job.start()

fig = plt.figure()
ax_persons = fig.add_subplot(2, 1, 1)
ax_couples = fig.add_subplot(2, 1, 2)


def animate(i):
    # line.set_ydata(env.ob_persons)
    ax_persons.clear()
    ax_persons.plot(env.ob_persons, label="Persons")
    ax_persons.plot(env.ob_women, label="Women")
    ax_persons.plot(env.ob_men, label="Men")
    ax_persons.grid()
    ax_persons.legend()
    ax_persons.title.set_text("Population")
    ax_couples.clear()
    ax_couples.plot(env.ob_couples, label="Couples")
    ax_couples.plot(env.ob_pregnant, label="Pregnant")
    ax_couples.grid()
    ax_couples.legend()
    ax_couples.title.set_text("Couples")
    if len(PERSONS) == 0:
        plt.close()


ani = animation.FuncAnimation(fig, animate, interval=500, save_count=12)

plt.show()

print(f'{int(env.now % 12) + 1}/{int(env.now / 12) + 1 + 2020}')
if len(PERSONS) == 0:
    print('Your population died :(')

plt.plot([i + 1 for i in range(len(env.ob_persons))], env.ob_persons, label='Persons')
plt.plot([i + 1 for i in range(len(env.ob_women))], env.ob_women, label='Women')
plt.plot([i + 1 for i in range(len(env.ob_men))], env.ob_men, label='Men')
plt.grid()
plt.legend()
plt.xlabel("Month")
plt.show()

plt.plot([i + 1 for i in range(len(env.ob_couples))], env.ob_couples, label='Couples')
plt.plot([i + 1 for i in range(len(env.ob_pregnant))], env.ob_pregnant, label='Pregnant')
plt.grid()
plt.legend()
plt.xlabel("Month")
plt.show()
