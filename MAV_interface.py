#Projet Roguelike, par Nino Mulac, Ilane Pelletier et Arwen Duee-Moreau
from time import sleep
import random
from typing import *
from tkinter import *
import copy
import math

def sign(x) -> int:
    if x > 0:
        return 1
    return -1

def heal(creature) -> True:
    creature.hp+=3
    return True

def teleport(creature, unique : bool) -> bool:
    f=theGame().floor
    l=len(f)
    c=Coord(random.randint(0,l),random.randint(0,l))
    while f[c]!=Map.empty:
        c=f[Coord(random.randint(0,l),random.randint(0,l))]
    f.move(creature,c-f.pos(creature))
    return unique

def getch():
    """Single char input, only works only on mac/linux/windows OS terminals"""
    try:
        import termios
        # POSIX system. Create and return a getch that manipulates the tty.
        import sys, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch().decode('utf-8')

class Coord(object):
    "Vec2D"

    def __init__(self,x : int ,y : int ,angle=False):
        if not(angle):
            self.x=int(x)
            self.y=int(y)
        else:
            self.x=int(x*math.cos(y))
            self.y=int(x*math.sin(y))

    def __repr__(self) -> str:
        return "<"+str(self.x)+","+str(self.y)+">"

    def __eq__(self,other) -> bool:
        return self.x==other.x and self.y==other.y

    def __ne__(self,other) -> bool:
        return not(self==other)

    def __add__(self,other):
        if type(other) is Coord:
            return Coord(self.x+other.x,self.y+other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x+other,self.y+other)

    def __neg__(self):
        return Coord(-self.x,-self.y)

    def  __mul__(self,other):
        if type(other) is Coord:
            return Coord(self.x*other.x,self.y*other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x*other,self.y*other)

    def __sub__(self,other):
        if type(other) is Coord:
            return Coord(self.x-other.x,self.y-other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x-other,self.y-other)

    def __abs__(self):
        return Coord(abs(self.x),abs(self.y))

    def __floordiv__(self,other):
        if type(other) is Coord:
            return Coord(self.x/other.x,self.y/other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x/other,self.y/other)

    def __truediv__(self,other):
        if type(other) is Coord:
            return Coord(self.x/other.x,self.y/other.y)
        if (type(other) is int) or (type(other) is float):
            return Coord(self.x/other,self.y/other)

    def __len__(self) -> float:
        return math.sqrt(self.x**2+self.y**2)

    def __lt__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)<len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)<other

    def __gt__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)>len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)>other

    def __le__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)<=len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)<=other

    def __ge__(self,other) -> bool:
        if type(other) is Coord:
            return len(self)>=len(other)
        if (type(other) is int) or (type(other) is float):
            return len(self)>=other

    def distance(self,other) -> float:
        return (self-other).__len__()

    def dirtrig(self):
        if self==Coord(0,0):
            return Coord(0,0)
        cos=self.x/self.__len__()
        if cos>1/(math.sqrt(2)):
            return Coord(-1,0)
        if cos<-1/(math.sqrt(2)):
            return Coord(1,0)
        if self.y>0:
            return Coord(0,-1)
        return Coord(0,1)

    def direction(self,other):
        return (self-other).dirtrig()

    def inverse(self):
        return Coord(self.y,self.x)

    def coin1(self,other):
        return Coord(self.x,other.y)

    def coin2(self,other):
        return Coord(other.x,self.y)

    def middle(self,other):
        return (self+other)//2

class Element(object):
    "Élement de base pour la construction du roquelike"

    def __init__(self,name,abbrv=None,transparent=False):
        self.name=name
        self.transparent=transparent
        if abbrv==None:
            self.abbrv=name[0]
        else:
            self.abbrv=abbrv

    def __repr__(self) -> str:
        return self.abbrv

    def description(self) -> str:
        return "<{}>".format(self.name)

    def meet(self,hero):
        raise NotImplementedError("Not implemented yet")


class Creature(Element):
    "Élement possédant des pv et une force, pouvant se déplacer"

    def __init__(self,name,hp,abbrv=None,strength=1):
        Element.__init__(self,name,abbrv)
        self.hp=hp
        self.strength=strength

    def description(self) -> str:
        return Element.description(self)+"({})".format(self.hp)

    def meet(self,other) -> bool:
        self.hp-=other.strength
        theGame().addMessage(f"The {other.name} hits the {self.description()}")
        return False if self.hp>0 else True

class Pillules(Element):
    def __init__(self,name,abbvr=None,usage=None,transparent=True, valeur_pillule=0):
        Equipment.__init__(self,name,abbvr,usage,transparent)
        self.valeur_pillule=valeur_pillule

    def meet(self, creature : Creature):
        theGame().addMessage(f"You pick up a {self.name}")
        creature.bourse+=self.valeur_pillule
        return True

class Equipment(Element):
    "Élément ramassable et équipable par le héros"

    def __init__(self,name,abbvr=None,usage=None,transparent=False,bourse=0):
        Element.__init__(self,name,abbvr)
        self.usage=usage
        self.transparent=transparent

    def meet(self,hero) -> True:
        theGame().addMessage(f"You pick up a {self.name}")
        return Hero.take(hero,self)

    def use(self,creature) -> bool:
        if self.usage!=None:
            theGame().addMessage(f"The {creature.name} uses the {self.name}")
            return self.usage(creature)
        theGame().addMessage(f"The {self.name} is not usable")
        return False

class Hero(Creature):
    "Le héros, controllé par le joueur"

    def __init__(self, name="Hero", hp=10, abbrv="@", archer=None, strength=2,joie=50,tristesse=50,colere=50, peur=50, xp=0, bourse=0 , hunger = 100):
        Creature.__init__(self,name,hp,abbrv,strength)
        self._inventory=[]
        self.joie=joie
        self.tristesse=tristesse
        self.colere=colere
        self.bourse=bourse
        self.hunger = hunger

    def take(self,equip)-> True:
        if isinstance(equip,Equipment):
            self._inventory.append(equip)
            return True
        raise TypeError

    def description(self) -> str:
        return Creature.description(self)+"{}".format(self._inventory)

    def __repr__(self) -> str:
        return self.abbrv

    def fullDescription(self) -> str:
        a=self.__dict__
        res=""
        for i in a:
            if i[0]!="_":
                res+=f"> {i} : {a[i]}\n"
        res+="> INVENTORY : "+str([x.name for x in self._inventory])
        return res

    def kill(self) -> None:
        self.hp=0

    def use(self,item : Equipment) -> None:
        if not(type(item) is Equipment):
            raise TypeError("C'est pas un équipement!")
        if not(item in self._inventory):
            raise ValueError("Tu l'as pas, tu peux pas l'utiliser!")
        if item.use(self):
            self._inventory.remove(item)

class Arme(Equipment):

    def __init__(self, name, force, durabilite, abbrv="", usage=None):
        Equipment.__init__(self, name, abbrv)
        self.usage = usage
        self.force=force
        self.durabilite=durabilite

    def equiper(self,creature : Creature) -> None:
        creature.strength+=self.force

    def desequiper(self,creature : Creature) -> None:
        creature.strength-=self.force

    def casse(self , attaque):
        if attaque >= self.durabilite:
            print("l'arme a été détruite")
            Hero.inventory.remove(self)
            #mettre les changement emotionels

        elif attaque < (self.durabilite)/4 : #attaque faible
            self.durabilite = self.durabilite - attaque
            print("l'arme a été un peu abimée, la durabilié est de "+str(self.durabilite))
            #mettre les changements emotionels

        elif attaque < (self.durabilite)/2: #attaque moyenne
            self.durabilite = self.durabilite - attaque
            print("l'arme a été moyennement abimée, la durabilié est de "+str(self.durabilite))
            #mettre les changement emotionnels

        else: #attaque forte
            self.durabilite = self.durabilite - attaque
            print("l'arme a été beaucoup abimée, la durabilié est de "+str(self.durabilite))

class Armure(Equipment):

    def __init__(self, name, defense, durabilite, abbrv="", usage=None):
        Equipment.__init__(self, name, abbrv)
        self.usage = usage
        self.defense=defense
        self.durabilite=durabilite

    def equiper(self,creature : Creature) -> None:
        creature.hp+=self.defense

    def desequiper(self,creature : Creature) -> None:
        creature.hp-=self.defense

    def casse(self , attaque):
        if attaque >= self.durabilite:
            print("l'armure a été détruite")
            Hero.inventory.remove(self)
            #mettre les changement emotionels

        elif attaque < (self.durabilite)/4 : #attaque faible
            self.durabilite = self.durabilite - attaque
            print("l'armure a été un peu abimée, la durabilié est de "+str(self.durabilite))
            #mettre les changements emotionels

        elif attaque < (self.durabilite)/2: #attaque moyenne
            self.durabilite = self.durabilite - attaque
            print("l'armure a été moyennement abimée, la durabilié est de "+str(self.durabilite))
            #mettre les changement emotionnels

        else: #attaque forte
            self.durabilite = self.durabilite - attaque
            print("l'armure a été beaucoup abimée, la durabilié est de "+str(self.durabilite))
            #mettres les changement emotionnels

    """def casse(self, #attaque_subite=le nombre de fois d'attaque subite#):
        if attaque_subite < (self_durabilite)/2 :
            if attaque_subite < (self_durabilite)/4 :
                if attaque_subite > self_durabilite :
                    #l'armure est détruite donc disparait du héro et ne reapparait pas dans son inventaire
                    return
                #on montre l'armure est ++abimée
                return
            # on montre l'armure est +abimée
            #changement_emotion(1)   --> cause=1
            return"""

class Amulette(Equipment):

    def __init__(self,name,defense=0,force=0,courage=0,abbrv="",usage=None):
        Equipment.__init__(self, name, abbrv)
        self.usage = usage
        self.defense=defense
        self.force=force
        self.courage=courage

    def equiper (self,creature : Hero) -> None:
        creature.hp+=self.defense
        creature.strength+=self.force
        creature.courage+=self.courage

    def desequiper (self,creature : Hero) -> None:
        creature.hp-=self.defense
        creature.strength-=self.force
        creature.courage-=self.courage

class PNJ(Creature):

    def __init__(self, name, hp=100, abbrv="", strength=0, archer=None, actif=None):
        Creature.__init__(self, name, hp, abbrv, strength, archer)
        self.actif=actif

    def meet(self, other) -> None:
        if isinstance(other,Hero):
            if self.actif!=None:
                for i in self.actif:
                    theGame().addMessage(self.name+" : "+ i)

class Marchand(PNJ):

    def __init__(self, name, hp=100, abbrv="", strength=0, archer=None, actif=["Infiermière : Bonjour, mon loulou. Quel age as tu? Ah oui tu es jeune!","Et qu'as tu dans des poches? Si tu as trouvé des pillules bleus ou jaunes ne les mangent pas!","Vient plutot me les donner, en échange je te donnerai des cookies ou des sucreries.","C'est d'accord? Alors as tu trouvé ce style de médicament?"],dialoguenon=["Infiermière : Ce n'est pas grave loulou. reviens me voir si tu en trouve."],dialogueoui=["Infiermière : A oui effectivement, contre quoi veux tu me les échanger."]):
        PNJ.__init__(self, name, hp, abbrv, strength, archer, actif)
        self.dialoguenon=dialoguenon
        self.dialogueoui=dialogueoui
        self.chariot=[]
        for i in range(5):
            self.chariot.append(random.choice([Equipment("bonbon"),Equipment("cookie"),Equipment("sucette"),Arme("béquille"),Equipment("chewing-gum")]))

    def meet(self,creature) -> None:
        if isinstance(creature,Hero):
            [theGame().addMessage(i) for i in self.actif]
            theGame().fenetre.bind('b', self.fin_de_discussion())

    def reponse(self) -> None:
        [theGame().addMessage(i) for i in self.dialogueoui]

    def fin_de_discussion(self) -> None:
        [theGame().addMessage(i) for i in self.dialoguenon]

class Room(object):
    "Salle composant la Map, est définie par les coordonnées de ses coins"

    def __init__(self,c1:Coord,c2:Coord):
        self.c1=c1
        self.c2=c2

    def __contains__(self,coord:Coord)->bool:
        return self.c1.x<=coord.x<=self.c2.x and self.c1.y<=coord.y<=self.c2.y

    def __repr__(self) -> str:
        return f"[<{self.c1.x},{self.c1.y}>, <{self.c2.x},{self.c2.y}>]"

    def center(self) -> Coord:
        return self.c1.middle(self.c2)

    def coins(self) -> List[Coord]:
        return [self.c1,self.c2,self.c1.coin1(self.c2),self.c2.coin1(self.c1)]

    def intersect(self,other) -> bool:
        for i in self.coins():
            if i in other:
                return True
        for i in other.coins():
            if i in self:
                return True
        return False

    def randCoord(self) -> Coord:
        return Coord(random.randint(self.c1.x,self.c2.x),random.randint(self.c1.y,self.c2.y))

    def randEmptyCoord(self,map) -> Coord:
        coord=self.center()
        cc=self.center()
        while coord in map._elem.values() or coord==cc:
            coord=self.randCoord()
        return coord

    def decorate(self,map) -> None:
        map.put(self.randEmptyCoord(map),theGame().randEquipment())
        map.put(self.randEmptyCoord(map),theGame().randMonster())

class Map(object):
    "Carte du jeu dans lequel évoluent le héros et les créatures"
    ground1="."
    ground2="."
    ground3="`"
    ground4="´"
    listground=[ground1,ground2,ground3,ground4]

    empty=" "

    def __init__(self,size=10,hero=None,nbrooms=10):
        self.nbrooms=nbrooms
        self._rooms=[]
        self._roomsToReach=[]
        if hero==None:
            self.hero=theGame().hero
        else:
            self.hero=hero
        self._mat=[[self.empty for i in range(size)] for k in range(size)]
        self._elem={}
        self.generateRooms(self.nbrooms)
        self.reachAllRooms()
        self.blankmap=[[str(self._mat[j][i]) for i in range(len(self))] for j in range(len(self))]
        self.put(self._rooms[0].center(),self.hero)
        for i in self._elem.keys():
            self._mat[self._elem.get(i).y][self._elem.get(i).x]=i.abbrv
        for i in self._rooms:
            i.decorate(self)

    def __repr__(self) -> str:
        return "\n".join(["".join([str(self._mat[n][k]) for k in range(len(self))]) for n in range(len(self))])+"\n"

    def __len__(self) -> int:
        return len(self._mat)

    def __contains__(self,item) -> bool:
        if isinstance(item,Coord):
            return 0<=item.x<=len(self)-1 and 0<=item.y<=len(self)-1
        return item in self._elem.keys()

    def __getitem__(self,item) -> Any:
        if type(item) is Coord:
            return self.get(item)
        else:
            return self.pos(item)

    def __setitem__(self,cle,valeur)->None:
        if type(cle) is Coord:
            self.put(cle,valeur)
        else:
            if not cle in self:
                self.put(valeur,cle)
            else:
                self.tp(cle,valeur)

    def get(self,coord : Coord, testeroupas=True) -> Element:
        if testeroupas:
            self.checkCoord(coord)
        for i,j in self._elem.items():
            if j==coord:
                return i
        return self._mat[coord.y][coord.x]

    def pos(self,element : Element) -> Coord:
        self.checkElement(element)
        return self._elem.get(element)

    def groundize(self,coord : Coord) -> None:
        self._mat[coord.y][coord.x]=self.blankmap[coord.y][coord.x]

    def elementize(self,coord : Coord, abbrv : str) -> None:
        self._mat[coord.y][coord.x]=abbrv

    def put(self,coord : Coord,element : Element) -> None:
        self.checkCoord(coord)
        self.checkElement(element)
        if self[coord]==self.empty or isinstance(self[coord],Element):
            raise ValueError('Incorrect cell')
        if element in self:
            raise KeyError('Already placed')
        self._elem[element]=Coord(coord.x,coord.y)
        self.elementize(coord,element.abbrv)

    def rm(self,element : Element) -> None:
        if type(element) is Coord:
            self.checkCoord(element)
            self._elem = {key:val for key, val in self._elem.items() if not val == element}
            self.groundize(element)
        else:
            self.groundize(self.pos(self._elem.pop(element)))

    def move(self,element : Element,way : Coord) -> None:
        coordarr=self.pos(element)+way
        if coordarr in self:
            if not coordarr in self._elem.values() and self._mat[coordarr.y][coordarr.x] in Map.listground:
                self.groundize(self.pos(element))
                self._elem[element]=coordarr
                self.elementize(coordarr,element.abbrv)
            elif self._mat[coordarr.y][coordarr.x]!=Map.empty:
                if self.get(coordarr).meet(element):
                    self.rm(coordarr)

    def tp(self,element : Element,dest : Coord) -> None:
        self.move(element,self.pos(element)-dest)

    def remplirrectangle(self,c1:Coord,c2:Coord,thing=" ") -> None:
        if type(thing) is list:
            for i in range(c1.x,c2.x+1):
                for j in range(c1.y,c2.y+1):
                    self._mat[j][i]=random.choice(thing)
        else:
            for i in range(c1.x,c2.x+1):
                for j in range(c1.y,c2.y+1):
                    self._mat[j][i]=thing

    def addRoom(self,room:Room) -> None:
        self._roomsToReach.append(room)
        self.remplirrectangle(room.c1,room.c2,Map.listground)

    def findRoom(self,coord : Coord) -> Any:
        for i in self._roomsToReach:
            if coord in i:
                return i
        return False

    def intersectNone(self,room : Room) -> bool:
        for i in self._roomsToReach:
            if room.intersect(i):
                return False
        return True

    def dig(self,coord : Coord) -> None:
        self._mat[coord.y][coord.x]=random.choice(Map.listground)
        a=self.findRoom(coord)
        if a:
            self._rooms.append(a)
            self._roomsToReach.remove(a)

    def corridor(self,c1 : Coord,c2 : Coord) -> None:
        self.dig(c1)
        coord=Coord(c1.x,c1.y)
        while not(coord==c2):
            coord+=self.dircorridor(coord,c2)
            self.dig(coord)

    def dircorridor(self,c1 : Coord,c2 : Coord) -> Coord:
        if c1.y!=c2.y:
            return Coord(0,1) if c1.y<c2.y else Coord(0,-1)
        if c1.x!=c2.x:
            return Coord(1,0) if c1.x<c2.x else Coord(-1,0)

    def reach(self) -> None:
        r1=random.choice(self._rooms)
        r2=random.choice(self._roomsToReach)
        self.corridor(r1.center(),r2.center())

    def reachAllRooms(self) -> None:
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach)>0:
            self.reach()

    def randRoom(self) -> Room:
        x1=random.randint(0,len(self)-3)
        y1=random.randint(0,len(self)-3)
        largeur=random.randint(3,8)
        hauteur=random.randint(3,8)
        x2=min(len(self)-1,x1+largeur)
        y2=min(len(self)-1,y1+hauteur)
        return Room(Coord(x1,y1),Coord(x2,y2))

    def generateRooms(self,n) -> None:
        for i in range(n):
            r=self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)

    def checkCoord(self,coord) -> None:
        if not(type(coord) is Coord):
            raise TypeError('Not a Coord')
        if not coord in self:
            raise IndexError('Out of map coord')

    def checkElement(self,elem) -> None:
        if not(isinstance(elem,Element)):
            raise TypeError('Not a Element')

    def moveAllMonsters(self) -> None:
        def aleatoire(i,direction):
            chance = random.randint(1,4)
            if chance == 4:
                deplacement = random.choice(direction)
                self.move(i,deplacement)

        direction = [Coord(0,1),Coord(0,-1),Coord(1,0),Coord(-1,0),Coord(-1,1),Coord(-1,-1),Coord(1,1),Coord(1,-1)]

        for i in self._elem :
            if isinstance(i,Creature) and not (isinstance(i,Hero)):
                if self._elem[i].distance(self._elem[self.hero])<=1 :
                    self.hero.meet(i)

                elif self.get(self._elem[i]+self._elem[i].direction(self._elem[self.hero])) in Map.listground :
                    if self._elem[i].distance(self._elem[self.hero])<6 :
                        self.move(i,self._elem[i].direction(self._elem[self.hero]))
                    else:
                        aleatoire(i,direction)

                else:
                    if self._elem[i].distance(self._elem[self.hero])<6 :
                        posmonstre = self.pos(i)
                        poshero = self.pos(self.hero)
                        new = posmonstre - poshero #permet de savoir quelle direction donner si la premiere ne marche pas

                        if (self.pos(i).direction(self.pos(self.hero))).x != 0:
                            self.move(i,Coord(0,sign(new.x)))
                        else:
                            self.move(i,Coord(sign(new.y),0))
                    else:
                        aleatoire(i,direction)

class Escalier(Element):
    def __init__(self,name,abbrv=None,up=None):
        Element.__init__(self,name,abbrv="#")
        self.up=up

    def meet(self,hero):
        '''theGame().etages est la variables contenant les etages'''
        if isinstance(hero,Hero):
            if self.up==None:
                if theGame().stage==10:
                    return
                theGame().addMessage(f"{hero.name} prend les escaliers et monte.")
                self.floor=self.etages[theGame().stage]
                self.placescalier()
            else:
                if theGame().stage==0:
                    return
                theGame().addMessage(f"{hero.name} prend les escaliers et monte.")
                self.floor=self.etages[theGame().stage]
                self.placescalier()

    def placescalier(self,map: Map):
        map.put(self.center(),self)

class Game(object):
    "Jeu"
    _actions={"z" : lambda hero : theGame().floor.move(hero,Coord(0,-1)),
              "s" : lambda hero : theGame().floor.move(hero,Coord(0,1)),
              "q" : lambda hero : theGame().floor.move(hero,Coord(-1,0)),
              "d" : lambda hero : theGame().floor.move(hero,Coord(1,0)),
              "i" : lambda hero : theGame().addMessage(hero.fullDescription()),
              "k" : lambda hero : hero.kill(),
              "<space>" : lambda hero : theGame().tour(),
              "u" : lambda hero : hero.use(theGame().select(hero._inventory))
              }
    monsters = { 0: [ Creature("Goblin",4), Creature("Bat",2,"W") ],
                 1: [ Creature("Ork",6,strength=2), Creature("Blob",10) ],
                 5: [ Creature("Dragon",20,strength=3) ] }
    equipments = { 0: [ Equipment("potion","!",usage=lambda creature : heal(creature)),Pillules("or1","b",valeur_pillule=1)],
                   1: [ Equipment("sword","s"), Equipment("arc"),Equipment("potion","!",usage= lambda creature : teleport(creature,True)) ,Pillules("or2","j",valeur_pillule=2)],
                   2: [ Equipment("chainmail"), Pillules("or5","p",valeur_pillule=5) ],
                   3: [ Equipment("portoloin","w",usage= lambda creature : teleport(creature,False)), Pillules("or10","J", valeur_pillule=10)]}
    def __init__(self,hero=None,level=1,sizemap=20):
        self.hero=Hero()
        if hero!=None:
            self.hero=hero
        self.level=level
        self.floor=None
        self._message=[]
        self.mapvue=[[Map.empty for i in range(sizemap+2)] for k in range(sizemap+2)]
        self.sizemap=sizemap
        self.mapvisible=[[Map.empty for i in range(self.sizemap+2)] for k in range(self.sizemap+2)]

    def buildFloor(self,size=20) -> None:
        self.floor=Map(hero=self.hero,size=size)

    def addMessage(self,msg) -> None:
        self._message.append(msg)

    def readMessages(self) -> str:
        if self._message!=[]:
            a=". ".join(self._message)+". "
            self._message=[]
            return a
        return ""

    def randElement(self,collection : dict) -> Element:
        x=random.expovariate(1/self.level)
        n=int(x)
        while not(n in collection):
            n-=1
        return copy.copy(random.choice(collection[n]))

    def randEquipment(self) -> Equipment:
        return self.randElement(self.equipments)

    def randMonster(self) -> Creature:
        return self.randElement(self.monsters)

    def select(self,l : List[Equipment]) -> Equipment:
        print("Choose item>",[f"{i}: {l[i].name}" for i in range(len(l))])
        a=getch()
        if a in [str(i) for i in range(len(l))]:
            return l[int(a)]

    def playthegame(self) -> None:
        self.canvas=Canvas(self.fenetre,width=1200,height=800,background="black")
        self.canvas.place(x=0,y=0)
        bouton_quitter = Button(self.fenetre, text='Quitter', command=self.fenetre.destroy)
        bouton_quitter.place(x=1200,y=800)
        self.initgraph()
        self.fenetre.mainloop()

    def initgraph(self)-> None:
        imgPATH="images/"
        hero_f=PhotoImage(file=imgPATH+"hero_de_face.png")
        sol_img1=PhotoImage(file=imgPATH+"sol_1.png")
        sol_img2=PhotoImage(file=imgPATH+"sol_2.png")
        sol_img3=PhotoImage(file=imgPATH+"sol_3.png")
        sol_img4=PhotoImage(file=imgPATH+"sol_4.png")
        pot_img1=PhotoImage(file=imgPATH+"fiole_1.png")
        pot_img3=PhotoImage(file=imgPATH+"fiole_3.png")
        bequille_img=PhotoImage(file=imgPATH+"bequille.png")
        ted_img=PhotoImage(file=imgPATH+"ourson_1.png")
        sad_img=PhotoImage(file=imgPATH+"tristesse_1.png")
        or1_img=PhotoImage(file=imgPATH+"or1.png")
        or2_img=PhotoImage(file=imgPATH+"or2.png")
        or5_img=PhotoImage(file=imgPATH+"or5.png")
        or10_img=PhotoImage(file=imgPATH+"or10.png")
        marchand_f=PhotoImage(file=imgPATH+"marchand_de_face.png")
        marchand_f=PhotoImage(file=imgPATH+"marchand_de_face2.png")
        marchand_d=PhotoImage(file=imgPATH+"marchand_vers_droite.png")
        marchand_g=PhotoImage(file=imgPATH+"marchand_vers_gauche.png")
        marchand_sf=PhotoImage(file=imgPATH+"marchand_sucette_de_face.png")

        #barre d'inventaire
        hotbar = PhotoImage(file=imgPATH+"hotbar.png").zoom(2)
        #niveaux satiete
        faim100 = PhotoImage(file=imgPATH+"faim100.png").zoom(2)
        faim75 = PhotoImage(file=imgPATH+"faim75.png").zoom(2)
        faim50 = PhotoImage(file=imgPATH+"faim50.png").zoom(2)
        faim25 = PhotoImage(file=imgPATH+"faim25.png").zoom(2)
        faim0 = PhotoImage(file=imgPATH+"faim0.png").zoom(2)

        self.dicimages={"." : sol_img1,"," : sol_img2,"`" : sol_img3,"´" : sol_img4,"@" : hero_f,"!" : pot_img3,"G" : ted_img,"W":ted_img,"O":sad_img,"B":ted_img,"D":ted_img,"s":bequille_img,"!":pot_img1,"c":pot_img3,"b":or1_img,"j":or2_img,"p":or5_img,"P":or10_img,"M":marchand_f,'inventory':hotbar, 'faim100' : faim100 , 'faim75' : faim75 , 'faim50' : faim50 , 'faim25' : faim25 , 'faim0': faim0}
        self.canvas.config(width=1000,height=800)
        self.voirMap()
        self.updategraph()
        [self.fenetre.bind(i,self.turn) for i in self._actions]
        self.canvas.pack()
        self.fenetre.mainloop()

    def turn(self,event) -> None:
        if event.char in self._actions:
            self._actions[event.char](self.floor.hero)
        self.floor.moveAllMonsters()
        self.voirMap()
        self.updategraph()

    def updategraph(self) -> None:
        y=0
        self.canvas.delete("all")
        #print(self.floor,"\n".join(["".join([str(self.mapvisible[n][k]) for k in range(self.sizemap)]) for n in range(self.sizemap)])+"\n") -> debug
        for i in self.mapvisible:
            x=0
            for k in i:
                if k!=Map.empty:
                    self.canvas.create_image(x,y,image=self.dicimages.get(self.floor.blankmap[int(y/32)][int(x/32)]))
                if k in self.dicimages:
                    self.canvas.create_image(x,y,image=self.dicimages.get(k))
                else:
                    self.canvas.create_text(x,y,text=str(k),font="Arial 16")
                x+=32
            y+=32
        self.canvas.create_text(85,120,text=self.readMessages(),font="Arial 16 italic",fill="blue")
        self.canvas.create_text(85,60,text=self.floor.hero.description(),font="Arial 16 italic",fill="blue")

        #truc pour l'interface
        if theGame().floor.hero.hp>=1:
            self.canvas.create_image(50 , 400 , image = self.dicimages['inventory'])

            satiete = theGame().floor.hero.hunger
            if satiete >= 100:
                self.canvas.create_image(600,20,image = self.dicimages['faim100'])
            elif satiete >= 75:
                self.canvas.create_image(600,20,image = self.dicimages['faim75'])
            elif satiete >= 50:
                self.canvas.create_image(600,20,image = self.dicimages['faim50'])
            elif satiete >= 25:
                self.canvas.create_image(600,20,image = self.dicimages['faim25'])
            elif satiete > 0:
                self.canvas.create_image(600,20,image = self.dicimages['faim0'])
                #mettre un message comme quoi le niveau de nourriture est bas
            else:
                None
                #mettre un message comme quoi le joueur doit manger

        self.canvas.pack()
        if theGame().floor.hero.hp<1:
            self.endgame()

    def begingame(self):
        self.buildFloor(20)
        self.fenetre=Tk()
        self.fenetre.title('DG')
        #self.fenetre.attributes("-toolwindow",True)  #-fullscreen  #-toolwindow
        self.fenetre.configure(background="pink")
        self.canvas=Canvas(self.fenetre,width=1200,height=800,background="black")
        #time.sleep(5)
        self.canvas.place(x=0,y=0)
        self.canvas.create_text(85,120,text="NEW GAME",font="Arial 16 italic",fill="blue")
        self.bouton_quitter = Button(self.fenetre, text='Quitter', command=self.fenetre.destroy) #util pour le fullscreen
        self.bouton_quitter.place(x=1200,y=800)
        self.canvas.delete("all")
        self.canvas.destroy()
        #bouton_jouer = Button(self.fenetre,text='Jouer',command=self.playthegame)
        #bouton_jouer.place(x=1500,y=800)
        self.playthegame()

    def endgame(self) -> None:
        self.canvas.delete("all")
        self.canvas=Canvas(self.fenetre,width=1200,height=800,background="black")
        self.canvas.place(x=0,y=0)
        self.canvas.create_text(85,120,text="GAME OVER",font="Arial 16 italic",fill="blue")
        #self.canvas-self.canvas

    def voirMap(self):
        theta=0
        self.mapvisible=[[" " for i in range(self.sizemap+2)] for k in range(self.sizemap+2)]
        ch=self.floor[self.floor.hero]
        while theta<=2*math.pi:
            r=0
            cv=Coord(0,0)
            while r<=6 and (ch+cv in self.floor) and (self.floor[ch+cv] in Map.listground or self.floor[self.floor.hero]==ch+cv):
                self.mapvue[(cv+ch).y][(cv+ch).x]=str(self.floor[cv+ch])
                self.mapvisible[(cv+ch).y][(cv+ch).x]=str(self.floor[cv+ch])
                r+=0.2
                cv=Coord(r,theta,True)
            cv=Coord(r+0.5,theta,True)
            if r<6 and ch+cv in self.floor:
                self.mapvue[(cv+ch).y][(cv+ch).x]=str(self.floor[cv+ch])
                self.mapvisible[(cv+ch).y][(cv+ch).x]=str(self.floor[cv+ch])
            theta+=0.1

def theGame(game = Game()) -> Game:
    return game

theGame().begingame()