# -*- coding: utf-8 -*-

# Helper class for updating/retrieving Inventory data
# Initially designed by https://github.com/aeckert

import json
import os
from datetime import datetime


class _BaseInventoryComponent(object):
    TYPE = None
    ID_FIELD = None
    STATIC_DATA_FILE = None

    def __init__(self):
        self._data = {}
        if self.STATIC_DATA_FILE is not None:
            self.init_static_data()

    @classmethod
    def init_static_data(cls):
        if not hasattr(cls, 'STATIC_DATA') or cls.STATIC_DATA is None:
            cls.STATIC_DATA = json.load(open(cls.STATIC_DATA_FILE))

    def parse(self, item):
        return item

    def retrieve_data(self, inventory):
        assert self.TYPE is not None
        assert self.ID_FIELD is not None
        ret = {}
        for item in inventory:
            data = item['inventory_item_data']
            if self.TYPE in data:
                item = data[self.TYPE]
                key = item[self.ID_FIELD]
                ret[key] = self.parse(item)
        return ret

    def refresh(self, inventory):
        self._data = self.retrieve_data(inventory)

    def get(self, item_id):
        return self._data(item_id)

    def all(self):
        return list(self._data.values())


class Candy(object):
    def __init__(self, family_id, quantity):
        self.type = Pokemons.name_for(family_id)
        self.quantity = quantity

    def consume(self, amount):
        if self.quantity < amount:
            raise Exception(
                'Tried to consume more {} candy than you have'.format(
                    self.type
                )
            )
        self.quantity -= amount

    def add(self, amount):
        if amount < 0:
            raise Exception('Must add positive amount of candy')
        self.quantity += amount


class Candies(_BaseInventoryComponent):
    TYPE = 'candy'
    ID_FIELD = 'family_id'

    @classmethod
    def family_id_for(self, pokemon_id):
        return Pokemons.first_evolution_id_for(pokemon_id)

    def get(self, pokemon_id):
        family_id = self.family_id_for(pokemon_id)
        return self._data.setdefault(family_id, Candy(family_id, 0))

    def parse(self, item):
        candy = item['candy'] if 'candy' in item else 0
        return Candy(item['family_id'], candy)


class Pokedex(_BaseInventoryComponent):
    TYPE = 'pokedex_entry'
    ID_FIELD = 'pokemon_id'

    def total_seen(self):
        return len(self._data)

    def total_captured(self):
        return len([
            p for p in self._data
            if self._data[p].get('times_captured', 0) > 0
        ])

    def seen(self, pokemon_id):
        return pokemon_id in self._data

    def captured(self, pokemon_id):
        if not self.seen(pokemon_id):
            return False
        return self._data[pokemon_id]['times_captured'] > 0


class Player(_BaseInventoryComponent):
    TYPE = 'player_stats'
    ID_FIELD = 'level'

    def refresh(self, inventory):
        _BaseInventoryComponent.refresh(self, inventory)
        self._player = self._data.values()[0]

    @property
    def pokemons_captured(self):
        return self._player.get('pokemons_captured', 0)

    @property
    def km_walked(self):
        return self._player.get('km_walked', 0.0)

    @property
    def level(self):
        return self._player.get('level')

    @property
    def big_magikarp_caught(self):
        return self._player.get('big_magikarp_caught', 0)

    @property
    def experience(self):
        return self._player.get('experience', 0)

    @property
    def pokemons_encountered(self):
        return self._player.get('pokemons_encountered', 0)

    @property
    def pokeballs_thrown(self):
        return self._player.get('pokeballs_thrown', 0)

    @property
    def eggs_hatched(self):
        return self._player.get('eggs_hatched', 0)

    @property
    def small_rattata_caught(self):
        return self._player.get('small_rattata_caught', 0)

    @property
    def unique_pokedex_entries(self):
        return self._player.get('unique_pokedex_entries')

    @property
    def prev_level_xp(self):
        return self._player.get('prev_level_xp', 0)

    @property
    def next_level_xp(self):
        return self._player.get('next_level_xp', 0)

    @property
    def poke_stop_visits(self):
        return self._player.get('poke_stop_visits', 0)


class Items(_BaseInventoryComponent):
    TYPE = 'item'
    ID_FIELD = 'item_id'
    STATIC_DATA_FILE = os.path.join('data', 'items.json')

    @classmethod
    def name_for(cls, item_id):
        return cls.STATIC_DATA[item_id]

    def parse(self, item):
        return Item(item)

    def total_count(self):
        return sum(self._data[i].count for i in self._data)

    def count_for(self, item_id):
        return self._data[item_id]['count']


class Item(object):
    def __init__(self, data):
        self._data = data
        self.item_id = data['item_id']
        self.name = Items.name_for(str(self.item_id))
        self.count = data.get('count', 0)


class Pokemons(_BaseInventoryComponent):
    TYPE = 'pokemon_data'
    ID_FIELD = 'id'
    STATIC_DATA_FILE = os.path.join('data', 'pokemon.json')

    def parse(self, item):
        if 'is_egg' in item:
            return Egg(item)
        return Pokemon(item)

    @classmethod
    def data_for(cls, pokemon_id):
        return cls.STATIC_DATA[pokemon_id - 1]

    @classmethod
    def name_for(cls, pokemon_id):
        return cls.data_for(pokemon_id)['Name']

    @classmethod
    def first_evolution_id_for(cls, pokemon_id):
        data = cls.data_for(pokemon_id)
        if 'Previous evolution(s)' in data:
            return int(data['Previous evolution(s)'][0]['Number'])
        return pokemon_id

    @classmethod
    def next_evolution_id_for(cls, pokemon_id):
        try:
            return int(
                cls.data_for(pokemon_id)
                   .get('Next evolution(s)')[0]
                   .get('Number')
            )
        except KeyError:
            return None

    @classmethod
    def evolution_cost_for(cls, pokemon_id):
        try:
            return int(
                cls.data_for(pokemon_id)
                   .get('Next Evolution Requirements')
                   .get('Amount')
            )
        except KeyError:
            return

    def total_count(self):
        return len(self._data)

    def all(self):
        # by default don't include eggs in all pokemon (usually just
        # makes caller's lives more difficult)
        return [
            p for p in super(Pokemons, self).all()
            if not isinstance(p, Egg)
        ]


class Egg(object):
    def __init__(self, data):
        self._data = data

    def has_next_evolution(self):
        return False


class Pokemon(object):
    def __init__(self, data):
        self._data = data
        self.id = data['id']
        self.pokemon_id = data['pokemon_id']
        self.cp = data['cp']
        self._static_data = Pokemons.data_for(self.pokemon_id)
        self.name = Pokemons.name_for(self.pokemon_id)
        self.iv_attack = data.get('individual_attack', 0)
        self.iv_defense = data.get('individual_defense', 0)
        self.iv_stamina = data.get('individual_stamina', 0)
        self.iv = self._compute_iv()
        self.nickname = data.get('nickname', u'–')
        self.caught_at = datetime.fromtimestamp(
            data.get('creation_time_ms') / 1000
        )

    def can_evolve_now(self):
        return self.has_next_evolution \
            and self.candy_quantity > self.evolution_cost

    def has_next_evolution(self):
        return 'Next Evolution Requirements' in self._static_data

    @property
    def next_evolution_id(self):
        return Pokemons.next_evolution_id_for(self.pokemon_id)

    @property
    def first_evolution_id(self):
        return Pokemons.first_evolution_id_for(self.pokemon_id)

    @property
    def evolution_cost(self):
        return self._static_data['Next Evolution Requirements']['Amount']

    def _compute_iv(self):
        total_iv = self.iv_attack + self.iv_defense + self.iv_stamina
        pokemon_potential = round((total_iv / 45.0), 3)
        return pokemon_potential


class Inventory(object):
    def __init__(self, raw):
        self.pokedex = Pokedex()
        self.candy = Candies()
        self.items = Items()
        self.pokemons = Pokemons()
        self.player = Player()
        self.refresh(raw)

    def refresh(self, raw):
        for i in (
            self.pokedex,
            self.candy,
            self.items,
            self.pokemons,
            self.player
        ):
            i.refresh(raw)
