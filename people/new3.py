#!/usr/bin/python3
"""

python3 core8/pwb.py people/new3
python3 core8/pwb.py people/new3 -job:rules_footballer ask
python3 core8/pwb.py people/new3 -nat:Yemeni ask
python3 core8/pwb.py people/new3 -nat:American limit:200

SELECT *
WHERE {
  values ?lowerdesc { "yemeni footballer"@en }
  values ?ddes { "Yemeni footballer"@en }
  {SELECT * WHERE {
    ?item wdt:P31 wd:Q5;
          wdt:P21 wd:Q6581097.
    ?item schema:description ?ddes
          bind(lcase(?ddes) as ?lowerdesc)
          # FILTER(!(BOUND(?de)))
  }
  }
}


بوت إضافة الوصوف عن الأشخاص في ويكي بيانات


SELECT * WHERE {
    values (?lowerdesc) { ("yemeni footballer"@en) }
    ?item wdt:P31 wd:Q5;
          wdt:P21 wd:Q6581097.
    ?item schema:description ?ddes
          FILTER(LANG(?ddes) = "en")
          bind(lcase(?ddes) as ?lowerdesc)
          # FILTER(!(BOUND(?de)))
  }

"""

#
# (C) Ibrahem Qasim, 2022
#
#
import re
import time
import random
import sys
# ---
from people.Nationalities import translationsNationalities
import people.occupationsall as oc
from wd_api import wd_bot
from newapi import printe
from wd_api import wd_desc

# ---

# ---
# ---
Testing = {1: False}
# ---
genders = {
    'Q6581097': 'male',
    'Q2449503': 'male',  # transgender male
    'Q6581072': 'female',
    'Q1052281': 'female',  # transgender female
}
genders_list = sorted([[x, y] for x, y in genders.items()])
# ---
# ---
Tab = {
    "Nationalities": translationsNationalities,
    "Occupations": oc.translationsOccupations,
}
# ---
printe.output(f'len of Nationalities = {len(translationsNationalities.keys())}')
printe.output(f'len of Occupations = {len(oc.translationsOccupations.keys())}')
time.sleep(1)
# ---
qualimit = {1: 20}
limit = {1: ""}
offset = {1: 0}
# ---
# python3 core8/pwb.py people/new3 occnew
# python3 core8/pwb.py people/new3 -job:researcher
# python3 core8/pwb.py people/new3 -nat:Yemeni -job:footballer
# python3 core8/pwb.py people/new3 -nat:American occnew
# python3 core8/pwb.py people/new3 -nat:American
for arg in sys.argv:
    # ---
    arg, _, value = arg.partition(':')
    # ---
    if arg in ['limit', '-limit']:
        limit[1] = value
    # ---
    if arg in ['qualimit', '-qualimit']:
        qualimit[1] = int(value)
    # ---
    if arg in ['off', '-off']:
        offset[1] = int(value)
    # ---
    if arg == 'occnew':
        Tab["Occupations"] = oc.translationsOccupations_new
    # ---
    if arg in ['nat', '-nat']:
        value = value.replace("_", " ")
        if value in translationsNationalities:
            Tab["Nationalities"] = {value: translationsNationalities[value]}
        else:
            print(f"nat value:({value}) not in translationsNationalities")
    # ---
    if arg in ['job', '-job']:
        value = "~ " + value.replace("_", " ")
        if value in oc.translationsOccupations:
            Tab["Occupations"] = {value: oc.translationsOccupations[value]}
        else:
            print(f"job value:({value}) not in oc.translationsOccupations")
# ---
targetlangs2 = ['ar']
targetlangs = ['ar', 'bn', 'ca', 'es', 'fr', 'gl', 'he']
# ---
W_check = {1: True}


def check_quarry_new(tab):
    # ---
    printe.output(f'check quarry_new: {len(tab)} jobs')
    # printe.output( tab  )
    # ---
    tabe = {}
    d = 0
    # ---
    # en_list = [ tab[x].get("en",{}).get("male") for x in tab if tab[x].get("en",{}).get("male") ]
    en_list = []
    # ---
    for x in tab:
        en_m = tab[x].get("en", {}).get("male")
        if en_m:
            en_list.append(en_m)
        en_f = tab[x].get("en", {}).get("female")
        if en_m and en_f and en_f != en_m:
            en_list.append(en_f)
    # ---
    if en_list != [] and en_list[0].lower().startswith("american"):
        qualimit[1] = 5
    # ---
    for x in en_list:
        if d not in tabe:
            tabe[d] = []
        # ---
        # python3 core8/pwb.py people/new3 -nat:Algerian limit:500 qualimit:15
        # python3 core8/pwb.py people/new3 -nat:American limit:50 qualimit:10
        if len(tabe[d]) < qualimit[1]:
            tabe[d].append(x)
        else:
            d += 1
            tabe[d] = [x]
    # ---
    New_Json = []
    # ---
    for numb, value in tabe.items():
        # ---
        # printe.output( en_list )
        # printe.output( "@@".join( tabe[numb] ) )
        printe.output(f"find qua for {len(value)} description.")
        # ---
        qua = '''SELECT
    (concat(strafter(str(?item),"/entity/")) as ?q)#?item
    (GROUP_CONCAT(DISTINCT(LANG(?des2)); separator=",") as ?deskey)
    (GROUP_CONCAT(DISTINCT(?des); separator=",") as ?desc)
    (GROUP_CONCAT(DISTINCT(strafter(str(?p211),"/entity/")); separator=",") as ?p21)
    WHERE {
        values ?des { %s }
        ?item wdt:P31 wd:Q5 .
        ?item wdt:P21 ?p211.
        ?item schema:description ?des.
        ?item schema:description ?des2.
    }
    group by ?item
    #limit 1000
    ''' % " ".join(
            f'"{f}"@en "{f.lower()}"@en' for f in tabe[numb]
        )
        # ---
        if limit[1]:
            qua += f"\n limit {limit[1]}"
        # ---
        if "printcheck" in sys.argv or numb == 0:
            print('qua :.')
            print(qua)
            print('qua .')
        # ---
        json = wd_bot.sparql_generator_url(qua)
        # ---
        New_Json.extend(iter(json))
        # ---
    # ---
    return New_Json


# ---
translations_o = {1: {}, 2: {}}
translations_for_nat = {1: {}}


def make_Tabs(tabs):
    # من هذا البوت
    # TraOc = translationsOccupations
    TraNat = tabs["Nationalities"]
    # ---
    # من البوتات الأخرى
    TraOc = tabs["Occupations"]
    # ---
    # skipnatkey = 'american'.lower()
    skipnatkey = ''
    # ---
    translations_o[1] = {}
    translations_o[2] = {}
    translations_for_nat[1] = {}
    # ---
    allnewkeys = 0
    # ---
    for natkey, natdic in TraNat.items():  # الجنسيات
        # ---
        if natkey.lower() == skipnatkey.lower():
            continue
        # ---
        # if natkey.lower() == 'american': print('american')
        # ---
        translations_for_nat[1][natkey] = {}
        newkeys = 0
        # ---
        for occupkey, occupdic in TraOc.items():  # المهن
            kkkk = re.sub(r'~', natkey, occupkey)
            translations_o[1][kkkk] = {}
            # ---
            male_k = ""
            female_k = ""
            # ---
            for translang, occ_dict in occupdic.items():  # المهن حسب اللغة
                if translang in natdic:
                    # printe.output(occupkey + '\t' + natkey + '\t' + translang)
                    # ---
                    nat_ln = natdic[translang]
                    # ---
                    femalee = ''
                    malee = ''
                    # ---
                    if nat_ln['male'] and occ_dict['male']:
                        malee = occ_dict['male'].replace('~', nat_ln['male'])
                    # ---
                    if nat_ln['female'] and occ_dict['female']:
                        femalee = occ_dict['female'].replace('~', nat_ln['female'])
                    # ---
                    if translang == "en":
                        male_k = malee
                        female_k = femalee
                    # ---
                    if malee or femalee:
                        translations_o[1][kkkk][translang] = {'male': malee, 'female': femalee}
                    # ---
            # ---
            if translations_o[1][kkkk] != {}:
                # if natkey.lower() == 'american' and occupkey == "~ physicist":
                # print(kkkk)
                # print(translations_o[1][kkkk])
                translations_o[2][kkkk.lower()] = translations_o[1][kkkk]
            else:
                del translations_o[1][kkkk]
            # ---
            if female_k and male_k:
                if female_k != male_k:
                    if female_k.lower() not in translations_o[2]:
                        translations_o[2][female_k.lower()] = translations_o[1][kkkk]
                        # printe.output( '<<lightpurple>> new way adding key: %s' % female_k )
                        allnewkeys += 1
                        newkeys += 1
            # ---
            translations_for_nat[1][natkey][kkkk] = translations_o[1][kkkk]
        # ---
        # printe.output( '<<lightpurple>> new way adding %d keys for lang %s' % (newkeys,natkey) )
    # ---
    printe.output('<<lightpurple>> people/new3.py adding %d keys for langs.' % allnewkeys)
    printe.output('<<lightpurple>> people/new3.py adding %d keys for langs.' % allnewkeys)
    printe.output('<<lightpurple>> people/new3.py adding %d keys for langs.' % allnewkeys)
    # ---
    for occupkey, occupdic in TraOc.items():  # المهن
        kkkk = occupkey.replace('~', '').strip()
        # ---
        # print(kkkk)
        # ---
        if 'ar' in occupdic.keys():
            # ---
            malee = occupdic['ar']['male'].replace('~', '').strip()
            femalee = occupdic['ar']['female'].replace('~', '').strip()
            # ---
            if kkkk.lower() not in translations_o[2]:
                translations_o[2][kkkk.lower()] = {}
            translations_o[2][kkkk.lower()]["ar"] = {'male': malee, 'female': femalee}


# ---
make_Tabs(Tab)
translations_o_lower = translations_o[2]
# ---
q_dones = []


def start_one_nat(nat_tab):
    # ---
    check = check_quarry_new(nat_tab)
    # ---
    total_nat = len(check)
    # ---
    printe.output(' find %d qid in check quarry new.' % total_nat)
    # ---
    c = 0
    # ---
    for x in check:  # q = 'Q30342921' #female
        # ---
        c += 1
        q = x["q"]
        p21 = x["p21"]
        endesc = x["desc"]
        # ---
        if q in q_dones:
            printe.output(f'<<lightpurple>>*q {q} in q_dones')
            continue
        # ---
        q_dones.append(q)
        # ---
        if "printx" in sys.argv:
            print(x)
        # ---
        printe.output('<<lightpurple>>*Action %d from %d; q:%s,endesc:%s.==' % (c, total_nat, q.ljust(10), endesc))
        # ---
        x_table = translations_o_lower.get(endesc.lower())
        # ---
        genderlabel = genders.get(p21, "male")
        # ---
        descriptions_keys = sorted(x["deskey"].split(","))
        NewDesc = {lang: {"language": lang, "value": x_table[lang][genderlabel]} for lang in x_table.keys() if lang not in descriptions_keys}
        # ---
        if NewDesc != {}:
            wd_desc.work_api_desc(NewDesc, q)


def mainnat(Tabs):  # translations_for_nat
    # ---
    # python pwb.py people/new3 mainnat -nat:American
    #
    # ---
    printe.output('<<lightpurple>>------------\n mainnat :')
    # ---
    if Tabs != {}:
        make_Tabs(Tabs)
    # ---
    Queries = 0
    # ---
    list_na = sorted(translations_for_nat[1].keys())
    # ---
    if len(list_na) > 100:
        new_len = len(list_na) // 2
        list_na = random.sample(list_na, new_len)
    # ---
    # 1 -  بدء العمل في  الاستعلامات
    for nat in list_na:
        # ---
        nat_tab = translations_for_nat[1][nat]
        # ---
        Queries += 1
        printe.output('<<lightyellow>>  *nat %d from %d; nat:%s.==' % (Queries, len(list_na), nat))
        # ---
        if Queries < offset[1]:
            continue
        # ---
        start_one_nat(nat_tab)
        # ---
    printe.output("انتهت بنجاح")


def Main_Test():
    qua = 'SELECT ?item WHERE { ?item wdt:P31 wd:Q5 . ?item wdt:P21 wd:Q6581097' + ' . ?item schema:description "Argentinian actor"@en.  '
    qua += 'OPTIONAL { ?item schema:description ?de. FILTER(LANG(?de) = "fr"). } FILTER (!BOUND(?de)) }'
    # ---

    # ---
    wd_bot.sparql_generator_url(qua)


# ---
if __name__ == "__main__":
    if "test" in sys.argv:
        Main_Test()
    else:
        mainnat({})
# ---
