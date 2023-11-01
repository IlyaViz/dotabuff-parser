import requests
import copy
import math
from bs4 import BeautifulSoup
from enums import PerformanceType
from constants import (headers, 
                       SUP_BACKGROUND, CARRY_BACKGROUND, C_BG, HERO_BACKGROUND,
                       GOLD_FIRST_LIMIT, GOLD_SECOND_LIMIT,
                       EXP_FIRST_LIMIT, EXP_SECOND_LIMIT,
                       PARTICIPATION_FIRST_LIMIT, PARTICIPATION_SECOND_LIMIT,
                       GOLD_PUNISHMENT, GOLD_AWARD_COFFICIENT,
                       EXP_PUNISHMENT, EXP_AWARD_COFFICIENT,
                       DAMAGE_1_DIVIDER, DAMAGE_1_AWARD_COFFICIENT,
                       DAMAGE_2_DIVIDER, DAMAGE_2_AWARD_COFFICIENT,
                       DAMAGE_3_DIVIDER, DAMAGE_3_AWARD_COFFICIENT,
                       CARRY_LANE_LOSE_PUNISHMENT, CARRY_LANE_WIN_AWARD,
                       SUP_LANE_LOSE_PUNISHMENT, SUP_LANE_WIN_AWARD,
                       PARTICIPATION_AWARD_COFFICIENT, PARTICIPATION_PUNISHMENT
                       )
from exceptions import ServerException, OldGameException

class GameParser:
    def __init__(self, game_id):
        self.basic_link = "https://ru.dotabuff.com/matches/"
        self.game_id = game_id
        self.parse()

    def parse(self):
        response = requests.get(self.basic_link+self.game_id, headers=headers)
        if response.status_code != 200:
            raise ServerException("Чёт не работает сервак")
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def nums_array_from_bs4_tags(self, data, replace_k=True, delete_two_overall=True):
        result = []
        for x in data:
            text = x.text
            if replace_k and "k" in text:
                text = text.replace("k", "")
                text = text.replace(".", "")
                text += "00"
            if (text == '-'):
                result.append(0)
            else:
                try:
                    result.append(float(text))
                except:
                    pass
        if delete_two_overall:
            result.pop(5)
            result.pop(-1)
        return result

    def get_dict_of_info(self):
        heros = self.soup.select(".image-hero.image-icon.image-overlay")
        kdas = list(filter(lambda x: 'tf-25' not in x.attrs['class'] and 'tf-30' not in x.attrs['class'] and 'tf-50' not in x.attrs['class'] and not 'color-stat-gold' in x.attrs['class'], self.soup.select(".tf-r.r-tab.r-group-1")))
        kills = kdas[::3]
        deaths = kdas[1::3]
        assists = kdas[2::3]
        golds = list(filter(lambda x: x.attrs.get("title","") != "Эта статистика убийств не включает добивания крипами или башнями. Реальный счёт игры показан в заголовке.", self.soup.select("acronym")))
        killed_creeps = self.soup.select(".tf-r.r-tab.r-group-2")[::2]
        gpms = self.soup.select(".tf-r.r-tab.r-group-2")[1::2]
        denied_creeps = self.soup.select(".tf-pl.r-tab.r-group-2")[::2]
        epms = self.soup.select(".tf-pl.r-tab.r-group-2")[1::2]
        hero_damages = self.soup.select(".tf-r.r-tab.r-group-3")[::3]
        heals = self.soup.select(".tf-r.r-tab.r-group-3")[1::3]
        tower_damages = self.soup.select(".tf-r.r-tab.r-group-3")[2::3]
        lanes = self.soup.select(".lane-outcome")
        if len(lanes) != 10:
            raise OldGameException("Too old game")

        heros = [x.attrs['title'] for x in heros]
        kills = self.nums_array_from_bs4_tags(kills)
        deaths = self.nums_array_from_bs4_tags(deaths)
        assists = self.nums_array_from_bs4_tags(assists)
        golds = self.nums_array_from_bs4_tags(golds)
        killed_creeps = self.nums_array_from_bs4_tags(killed_creeps)
        gpms = self.nums_array_from_bs4_tags(gpms)
        denied_creeps = self.nums_array_from_bs4_tags(denied_creeps)
        epms = self.nums_array_from_bs4_tags(epms)
        hero_damages = self.nums_array_from_bs4_tags(hero_damages)
        heals = self.nums_array_from_bs4_tags(heals)
        tower_damages = self.nums_array_from_bs4_tags(tower_damages)
        lanes = [x.text for x in lanes]
        result = {
            PerformanceType.heros: heros,
            PerformanceType.kills: kills,
            PerformanceType.deaths: deaths,
            PerformanceType.assists: assists,
            PerformanceType.golds: golds,
            PerformanceType.killed_creeps: killed_creeps,
            PerformanceType.gpms: gpms,
            PerformanceType.denied_creeps: denied_creeps,
            PerformanceType.epms: epms,
            PerformanceType.hero_damages: hero_damages,
            PerformanceType.heals: heals,
            PerformanceType.tower_damages: tower_damages,
            PerformanceType.lanes: lanes
        }
        return result
    
    def get_specific_top_value(self, top, performance_array):
        array_copy = copy.deepcopy(performance_array)
        for _ in range(top):
            top_value = max(array_copy)
            array_copy.remove(top_value)
        return top_value

    def get_exercises(self):
        info = self.get_dict_of_info()

        total_damages=[info[PerformanceType.hero_damages][x] + info[PerformanceType.tower_damages][x] for x in range(10)]        
        for num, hero in enumerate(info[PerformanceType.heros]):
            print(f"{HERO_BACKGROUND}{hero}{C_BG}\n")
            sum_to_do_carry = 0
            sum_bonus_carry = 0
            sum_to_do_sup = 0
            sum_bonus_sup = 0
            cur_to_do = 0
            cur_bonus = 0
            hero_team = 0 if num <= 4 else 1
            hero_kills = info[PerformanceType.kills][num]
            hero_assists = info[PerformanceType.assists][num]
            hero_gpm = info[PerformanceType.gpms][num]
            hero_epm = info[PerformanceType.epms][num]
            hero_hero_damage = info[PerformanceType.hero_damages][num]
            hero_tower_damage = info[PerformanceType.tower_damages][num]
            hero_lane = info[PerformanceType.lanes][num]

            team_total_kills = sum(info[PerformanceType.kills][hero_team*5:hero_team*5+5])

            hero_total_damage = hero_hero_damage+hero_tower_damage
            hero_participation = hero_kills+hero_assists
            hero_participation_procent = hero_participation/team_total_kills*100
            hero_total_damage_diff = max(total_damages)-hero_total_damage

            #for 1, 2, 3
            #gold
            if hero_gpm < GOLD_FIRST_LIMIT:
                cur_to_do = GOLD_PUNISHMENT
                sum_to_do_carry += cur_to_do
            elif hero_gpm > GOLD_SECOND_LIMIT:
                cur_bonus = (hero_gpm-math.floor(GOLD_SECOND_LIMIT))/10
                sum_bonus_carry += cur_bonus
            print(f"{CARRY_BACKGROUND}Gold: {cur_to_do}, bonus={cur_bonus}{C_BG}\n")

            #epms
            cur_to_do = 0
            cur_bonus = 0
            if hero_epm < EXP_FIRST_LIMIT:
                cur_to_do = EXP_PUNISHMENT
                sum_to_do_carry += cur_to_do
            elif hero_epm > EXP_SECOND_LIMIT:
                cur_bonus = (hero_epm-math.floor(EXP_SECOND_LIMIT))/10
                sum_bonus_carry += cur_bonus
            print(f"{CARRY_BACKGROUND}Exp: {cur_to_do}, bonus={cur_bonus}{C_BG}\n") 
            
            #damage
            cur_to_do = 0
            cur_bonus = 0
            if hero_total_damage_diff == 0:
                top_two_map_total_damage = self.get_specific_top_value(2, total_damages)   
                cur_bonus = (hero_hero_damage-top_two_map_total_damage)/DAMAGE_1_DIVIDER*DAMAGE_1_AWARD_COFFICIENT
                sum_bonus_carry += cur_bonus
            else:
                cur_to_do = hero_total_damage_diff/DAMAGE_2_DIVIDER*DAMAGE_2_AWARD_COFFICIENT
                sum_to_do_carry += cur_to_do
                top_two_team_total_damage = self.get_specific_top_value(2, total_damages[hero_team*5:hero_team*5+5]) 
                if hero_total_damage > top_two_team_total_damage:
                    cur_bonus = (hero_total_damage-top_two_team_total_damage)/DAMAGE_3_DIVIDER*DAMAGE_3_AWARD_COFFICIENT
                    sum_bonus_carry += cur_bonus
            print(f"{CARRY_BACKGROUND}Total damage(hero+tower): {cur_to_do}, bonus={cur_bonus}{C_BG}\n")

            #lane
            cur_bonus = 0
            cur_to_do = 0
            if hero_lane == "проигрыш":
                cur_to_do = CARRY_LANE_LOSE_PUNISHMENT
                sum_to_do_carry += cur_to_do
            elif hero_lane == "выигрыш":
                cur_bonus = CARRY_LANE_WIN_AWARD
                sum_bonus_carry += cur_bonus
            print(f"{CARRY_BACKGROUND}Lane status: {cur_to_do}, bonus={cur_bonus}{C_BG}\n")

            #for 4,5
            #lane
            cur_bonus = 0
            cur_to_do = 0
            if hero_lane == "проигрыш":
                cur_to_do = SUP_LANE_LOSE_PUNISHMENT
                sum_to_do_sup += cur_to_do
            elif hero_lane == "выигрыш":
                cur_bonus = SUP_LANE_WIN_AWARD 
                sum_bonus_sup += cur_bonus
            print(f"{SUP_BACKGROUND}Lane status: {cur_to_do}, bonus={cur_bonus}{C_BG}\n")

            #participation
            cur_bonus = 0
            cur_to_do = 0
            if hero_participation_procent < PARTICIPATION_FIRST_LIMIT:
                cur_to_do = PARTICIPATION_PUNISHMENT
                sum_to_do_sup += cur_to_do
            elif hero_participation_procent > PARTICIPATION_SECOND_LIMIT:
                cur_bonus = (hero_participation_procent-PARTICIPATION_SECOND_LIMIT)*PARTICIPATION_AWARD_COFFICIENT
                sum_bonus_sup += cur_bonus
            print(f"{SUP_BACKGROUND}Participation: {cur_to_do}, bonus={cur_bonus}{C_BG}\n")

            print(f"\033[4mTOTAL(CARRY)\033[0m: {sum_to_do_carry}, bonus={sum_bonus_carry}")
            print(f"\033[4mTOTAL(SUPPORT)\033[0m: {sum_to_do_sup}, bonus={sum_bonus_sup}\n")
