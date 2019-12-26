import functools
import random
import time
import pygame


class Ship:
    min_ship = 1
    max_ship = 4
    avail_conditions = {
        0: "Живой",
        1: "Ранен",
        2: "Убит",
    }

    def __init__(self, name="", list_coords=None, board_len=10, screen=None):
        self.screen = screen
        self.name = name
        self.board_len = board_len
        self.valid = False
        self.coord_status = dict()
        self.coords = list_coords
        self.krest = pygame.image.load('krest.png')

    def draw(self, board_xy, vid=0, cellsize=30):
        out = set()
        for xy in self.coords:
            out.add(xy)
            if vid==1:
                if self.condition == 1:
                    # ранен желтй
                    sc = (255, 255, 0)
                elif self.condition == 0:
                    # здоров зеленый
                    sc = (102, 255, 51)
                else:
                    sc = (153, 0, 77)

                if self.coord_status[xy] is False:
                    self.screen.blit(self.krest, (board_xy[0] + xy[0]*cellsize+2 ,   board_xy[1] + xy[1]*cellsize+2  ) )

                else:
                    pygame.draw.circle(self.screen,
                                   sc,
                                   (board_xy[0] + xy[0]*cellsize+cellsize//2,board_xy[1] + xy[1]*cellsize+cellsize//2), (cellsize//2-2), 3 )

            else:
                if self.condition == 2 or self.coord_status[xy] is False:
                    self.screen.blit(self.krest, (board_xy[0] + xy[0]*cellsize+2 ,   board_xy[1] + xy[1]*cellsize+2  ) )

    @property
    def mask_ship(self):
        ret = []
        for x, y in self.coords:
            ret += [(x,y), (x + 1, y + 1), (x - 1, y - 1), (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y), (x + 1, y - 1), (x - 1, y + 1)]
        out = []
        for x,y in ret:
            if x>=0 and y>=0 and x<=self.board_len and y<=self.board_len:
                out.append((x,y))

        return set(  out )

    @property
    def hitted_coords(self):
        ret = set()
        for xy, i in self.coord_status.items():
            if not i:
                ret.add(xy)
        return ret

    @property
    def size(self):
        return len(self.coords)

    @property
    def condition(self):
        try:
            if functools.reduce(lambda x,y: x==y==True, self.coord_status.values()):
                return 0
            if not functools.reduce(lambda x,y: False if x==y==False else True, self.coord_status.values()):
                return 2
            return 1
        except:
            return 4

    def __str__(self):
        return self.name

    @property
    def coords(self):
        if self._coords:
            return self._coords
        else:
            return None

    @coords.setter
    def coords(self, coordlist):
        for x,y in coordlist:
            if x not in range(0,self.board_len) or y not in range(0, self.board_len):
                return
        else:
            cl = list(set(coordlist))
            if len(cl)!=len(coordlist) or len(cl) > Ship.max_ship or len(cl) < Ship.min_ship:
                print("Неверно!")
                return
            x = set()
            y = set()
            for i,j in coordlist:
                x.add(i)
                y.add(j)
            if len(x)>1 and len(y)>1:
                print("Неверно!")
                return
            rst = list(x) if len(y)==1 else list(y)
            rst.sort()
            if len(rst)-1 == (rst[-1] - rst[0]):
                self._coords = cl
                self.valid = True
                for xy in cl:
                    self.coord_status.update({xy: True})

    def hit(self, xy):
        if xy in self.coords:
            print("Подюита ", xy)
            self.coord_status[xy] = False
            return True
        return False

class Board:
    def __init__(self,uname="playername", screen=None, size=10, avail_ships=None):
        self.name = uname
        self.ships = []
        self.size = size
        self.screen = screen
        self._cellsize = 30
        self.avail_ship = avail_ships
        self.all_hit = []
        self.mimoimg = pygame.image.load('mimo.png')

    @property
    def cellsize(self):
        return self._cellsize

    def draw(self, coord, vid=1):
        #todo: дописать буквы наверху и цифры в столбик.
        a_k = ["a", "b", "v", "g", "d", "e", "j", "z", "i", "k"]
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        count = 0
        for elem in a_k:
            img = pygame.image.load('{}.png'. format(elem))
            self.screen.blit(img, (coord[0] + count * self._cellsize + 2, coord[1]-30))
            count += 1
        count = 0
        for elem in numbers:
            img = pygame.image.load('{}.png'. format(elem))
            self.screen.blit(img, (coord[0] -30, coord[1] + count * self._cellsize +2))
            count += 1
        for i in range(self.size):
            for j in range(self.size):
                pygame.draw.rect(self.screen,
                                 (64, 128, 255),
                                 ( coord[0]+i*self._cellsize , coord[1]+j*self._cellsize , self._cellsize,self._cellsize), 2 )

        all_ship_coords = set()
        for s in self.ships:
            for xy in s.coords:
                all_ship_coords.add(xy)

        for s in self.ships:
            s.draw(coord, vid,  self._cellsize)

        for xy in self.all_hit:
            if xy not in all_ship_coords:
                self.screen.blit(self.mimoimg,  (coord[0] + xy[0]*self._cellsize+2 ,   coord[1] + xy[1]*self._cellsize+2  )  )

    @property
    def avail_to_shot(self):
        all_cells = set( (a,b) for a in range(self.size) for b in range(self.size) )
        return all_cells - set(self.all_hit)

    @property
    def ret_all_cells(self):
        '''Возвращает все игровое поле а точнее словарь где ключ это координата а значение - соостояние клетки.
        по этим данным можно строить таблицу с весами для выстрела от имени противника'''
        #todo: допишите возвращение словаря
        dict_for_game = {}
        if not dict_for_game:
            for i in range(self.size):
                for j in range(self.size):
                    dict_for_game[i, j] = False
        for elem in self.ships:
            for val in elem.coord_status.items():
                dict_for_game[str(val[0])] = val[1]
        return dict_for_game


    def add(self, sh):
        '''Добавление корабля'''
        if sh.valid:
            for s0 in self.ships:
                for elem in sh.coords:
                    if elem in s0.mask_ship:
                        return False
                # if (sh.mask_ship & s0.mask_ship) != set(): # !!!!!!!!!
                #     return False
            # проверка палубности
            kvo = 0
            for s in self.ships:
                if s.size == sh.size:
                    kvo += 1

            if self.avail_ship[sh.size] > kvo:
                print("Добавили")
                self.ships.append(sh)
                return True
            else:
                print("Не добавляем!!")
        return False

    @property
    def can_start_game(self):
        '''Проверка что расставлены ВСЕ корабли'''
        for palubi, kvo in self.avail_ships.items():
            p = 0
            for s in self.ships:
                if s.size == palubi:
                    p += 1

            if p != kvo:
                return False

        return True

    @property
    def alldead(self):
        '''Все корабли потоплены'''
        # todo: дописать возврат тру фалс
        for elem in self.ships:
            if elem.condition != 2:
                return False
        return True


    def hit(self, target_xy):
        if target_xy[0]>=0 and target_xy[1]>=0 and target_xy[0]<=self.size-1 and target_xy[1]<=self.size-1:
            self.all_hit.append(target_xy)
            for s in self.ships:
                ok = s.hit(target_xy)
                if s.condition == 2:
                    self.all_hit += list(s.mask_ship)
                if ok:
                    return ok
        return False

class Game:
    def __init__(self, b1, b2):
        self.boards = [b1, b2]
        self.who = 0 #random.randint(0, 1)
        self.bot_desk = self.boards[self.who].ret_all_cells
        self.bot_ship = False
        self.bot_ship_mask = []

    @property
    def opponent(self):
        return abs(self.who - 1)

    def hit(self, player, xy):
        if player == self.who:
            popal = self.boards[self.opponent].hit(xy)
            if not popal:
                self.who = self.opponent
            return popal

    def bot_hit(self, player):
        '''Походить за этого игрока.'''
        #todo: тут должно получить доступное для доски противника, расставить веса, выбрать с учетом весов и вызвать self.hit
        if not self.bot_ship or True not in self.bot_ship.coord_status:
            bot_xy = random.choice(list(self.boards[self.opponent].avail_to_shot))
            bot_popal = self.boards[self.opponent].hit(bot_xy)
            for elem in self.boards[self.opponent].ships:
                for elems in elem.coords:
                    if bot_xy in elems:
                        self.bot_ship = elem
                        self.bot_ship_mask = elem.mask_ship
            if not bot_popal:
                self.who = self.opponent
            return bot_popal
        else:
            while self.who == 1:
                avail = self.boards[self.opponent].avail_to_shot & self.bot_ship_mask
                print(avail)
                bot_xy = random.choice(list(avail))
                bot_popal = self.boards[self.opponent].hit(bot_xy)
                if not bot_popal:
                    self.who = self.opponent
                return bot_popal


    def draw(self,):
        self.boards[0].draw((50, 40,), 1)
        self.boards[1].draw((400, 40,), 2)

        self.boards[1].draw((50, 440,), 1)
        self.boards[0].draw((400, 440,), 2)

    @property
    def check_done(self):
        if self.boards[0].alldead:
            return True, self.boards[1]
        if self.boards[1].alldead:
            return True, self.boards[0]

        return False, None


def generateShip(board, size, scr):
    ''' Переделать дома. Корабль или вертикальный или горизонтальный и потом уже рандомно достраиваете его в ту сторону.  '''
    rules = {
        4: 1,
        3: 2,
        2: 3,
        1: 4
    }
    possible_variants = []
    for i in range(size):
        for j in range(size):
            possible_variants.append((i, j))
    size = size-1

    def inside_build(len_of_ship, size, scr):
        while True:
            if len_of_ship == 1:
                num = random.randint(0, len(possible_variants) - 1)
                sh = Ship("some name", [possible_variants[num]], size, scr)
                if sh.valid:
                    return sh
            else:
                num = random.randint(0, len(possible_variants)-1)
                shipsbegin = list(possible_variants[num])
                cho1 = random.choice(shipsbegin)
                newship = []
                if cho1 == shipsbegin[0]:
                    cho2 = random.choice(["-", "+"])
                    if cho2 == "-":
                        for i in range(len_of_ship):
                            newship.append((shipsbegin[0]-i, shipsbegin[1]))
                        sh = Ship("some name", newship, size, scr)
                        if sh.valid:
                            return sh
                    if cho2 == "+":
                        for i in range(len_of_ship):
                            newship.append((shipsbegin[0] + i, shipsbegin[1]))
                        sh = Ship("some name", newship, size, scr)
                        if sh.valid:
                            return sh
                if cho1 == shipsbegin[1]:
                    cho3 = random.choice(["-", "+"])
                    if cho3 == "-":
                        for i in range(len_of_ship):
                            newship.append((shipsbegin[0], shipsbegin[1] - i))
                        sh = Ship("some name", newship, size, scr)
                        if sh.valid:
                            return sh
                    if cho3 == "+":
                        for i in range(len_of_ship):
                            newship.append((shipsbegin[0], shipsbegin[1] + i))
                        sh = Ship("some name", newship, size, scr)
                        if sh.valid:
                            return sh

    for vid_korablya, dopustimoe_kolichestvo in rules.items():
        for i in range(dopustimoe_kolichestvo):
            dobavili = False
            while not dobavili:
                ship = inside_build(vid_korablya, size, scr)
                dobavili = board.add(ship)
                if dobavili:
                    for elem in ship.mask_ship:
                        if elem in possible_variants:
                            possible_variants.remove(elem)
    return True


WHITE = (255, 255, 255)
X = 750
Y = 780
pygame.init()
screen = pygame.display.set_mode((X, Y))
rules =  {
    4: 1,
    3: 2,
    2: 3,
    1: 4
}

b1 = Board("Уася", screen, 10,rules)
generateShip(b1, b1.size, screen)

b2 = Board("Мыша", screen, 10,rules)
generateShip(b2, b2.size, screen)

game = Game(b1, b2)



hiitedlist = []
j = 0
pos = None

currplayer = game.who


while True:
    screen.fill(WHITE)
    gamedone, winner = game.check_done
    bot_xy = None
    if gamedone:
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(f'{winner.name} победил!', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (X // 2, Y // 2)
        screen.blit(text, textRect)
        pygame.display.update()
        time.sleep(3)
        exit(0)
    else:
        if currplayer == 0 and pos:
            x = (pos[0] - 400) // b2.cellsize
            y = (pos[1] - 40) // b2.cellsize
            pos = None
            xy = (x, y)
            if xy not in b2.all_hit:
                ok = game.hit(currplayer, xy)
                if not ok:
                    currplayer = abs(currplayer - 1)
        if currplayer == 1:
            ok = game.bot_hit(currplayer)
            if not ok:
                currplayer = abs(currplayer - 1)
            # if bot_xy is None:
            #     bot_xy = random.choice(list(b1.avail_to_shot))
            # else:
            #     bot_xy  = random.choice(list( b1.avail_to_shot & {(bot_xy[0]-1, bot_xy[1]), (bot_xy[0]+1, bot_xy[1]), (bot_xy[0], bot_xy[1]+1),(bot_xy[0], bot_xy[1]-1), }  ))
            # ok = game.hit(currplayer, bot_xy)
            # if not ok:
            #     currplayer = abs(currplayer - 1)
            #     bot_xy = None

        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()
            if i.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

        game.draw()

    pygame.display.update()
    time.sleep(0.01)

pygame.quit()

