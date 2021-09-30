# MakeDB script

Creates SQLite table from CSV election results

- It copies all the data to a new table
- Name for the table and new names for all the columns are configured in a JSON file
- Additional columns are added:
    - `ballotsIssued` (int) number of all the ballots issued.
        - This field is calculated by summing a certain subset of the fields of the original data.
        The subset is configured in the JSON config file.
        - Usually it's configured to be the sum of fields such as: "issued for early voting", "issued for voting at home" and "issued on the polling station".
    - `ballotsFound` (int) number of all the ballots discovered in all the ballot boxes.
        - This field is calculated by summing a certain subset of the fields of the original data.
        The subset is configured in the JSON config file.
        - The sum of fields "valid ballots" and "invalid ballots"
    - `turnout` (float) - ratio between the number of issued ballots and the number of registered voters (number of voters in roll by the end of the elections)
        - not rounded
    - `<candidate_name>_res` (float) ratio between the number of votes
        received by the candidate and `ballotsFound`
        - not rounded

## Usage

`makedb.py --csv <path to CSV> --config <path to config file>`

Config file is a JSON file that maps CSV fields to short ASCII
names to use as column names in resulting SQL DB. Config also
defines how additional fields mentioned above are calculated.

Example:

Let's say CSV has following fields:

```
0 Регион
1 ТИК
2 УИК
3 Число избирателей, включенных в список избирателей
4 Число избирательных бюллетеней, полученных участковой избирательной комиссией
5 Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно
6 Число избирательных бюллетеней, выданных в помещении для голосования в день голосования
7 Число избирательных бюллетеней, выданных вне помещения для голосования в день голосования
8 Число погашенных избирательных бюллетеней
9 Число избирательных бюллетеней в переносных ящиках для голосования
10 Число бюллетеней в стационарных ящиках для голосования
11 Число недействительных избирательных бюллетеней
12 Число действительных избирательных бюллетеней
13 Число полученных открепительных  удостоверений
14 Число открепительных удостоверений, выданных избирателям на избирательном участке
15 Число избирателей, проголосовавших по открепительным удостоверениям
16 Число неиспользованных открепительных удостоверений
17 Число открепительных удостоверений, выданных избирателям ТИК
18 Число утраченных открепительных удостоверений
19 Число утраченных избирательных бюллетеней
20 Число избирательных бюллетеней, не учтенных при получении
21 Жириновский Владимир Вольфович
22 Зюганов Геннадий Андреевич
23 Миронов Сергей Михайлович
24 Прохоров Михаил Дмитриевич
25 Путин Владимир Владимирович
26 КОИБ (1) / КЭГ (2)
```

Here's how config might look like:

```json
{
    "table_name": "pres2024",
    "fields": [
        [0, "region"],
        [1, "tik"],
        [2, "uik"]
        [5, "ballotsIssuedEarly"]
        [6, "ballotsIssuedOnStation"]
        [7, "ballotsIssuedOutside"],
        [11, "invalidBallots"],
        [12, "validBallots"],
        [21, "ZHirinovskij", "cand"],
        [25, "Putin", "cand"]
    ],
    "additional_fields": {
        "ballotsIssued" : ["ballotsIssuedEarly", "ballotsIssuedOnStation", "ballotsIssuedOutside"],
        "ballotsFound" : ["invalidBallots", "validBallots"]
    }
}
```

This config results in the following SQLite table:
*TBD*


## Field name reference
Internal name                            | Name that could be seen in real protocols
-----------------------------------------|-------------------------------------------
region                                   | Субъект
tik                                      | ТИК
uik                                      | УИК
votersReg                                | Число избирателей, включенных в списки избирателей на момент окончания голосования
ballotsAllocated                         | Число избирательных бюллетеней, полученных участковыми избирательными комиссиями
ballotsIssuedEarly                       | Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно
ballotsCancelled                         | Число погашенных избирательных бюллетеней
ballotsIssuedOnStation                   | Число избирательных бюллетеней, выданных избирателям на избирательных участках в день голосования
ballotsIssuedOutside                     | Число избирательных бюллетеней, выданных избирателям, проголосовавшим вне помещений для голосования
ballotsInMobileBoxes                     | Число избирательных бюллетеней, содержащихся в переносных ящиках для голосования
ballotsInStationaryBoxes                 | Число избирательных бюллетеней, содержащихся в стационарных ящиках для голосования
validBallots                             | Число действительных избирательных бюллетеней
invalidBallots                           | Общее число недействительных избирательных бюллетеней
invalid1469                              | Число избирательных бюллетеней, признанных недействительными на основании пункта 14 статьи 69 Федерального закона "О выборах Президента Российской Федерации"
invalidBlank                             | Число недействительных избирательных бюллетеней, не содержащих отметок ни по одной из позиций
invalidDroppedCandidates                 | Число признанных недействительными избирательных бюллетеней, в которых голоса избирателей поданы в ходе досрочного голосования за выбывшего впоследствии зарегистрированного кандидата
absenteeCertificatesAllocated            | Число открепительных удостоверений, полученных участковыми избирательными комиссиями
absenteeCertificatesIssuedOnStationEarly | Число открепительных удостоверений, выданных участковыми избирательными комиссиями избирателям на избирательных участках до дня голосования
absenteeCertificatesIssuedByTer          | Число открепительных удостоверений, выданных избирателям в территориальных избирательных комиссиях
votesWithAbsenteeCertificates            | Число избирателей, проголосовавших по открепительным удостоверениям на избирательных участках
unusedAbsenteeCertificates               | Число неиспользованных открепительных удостоверений
absenteeCertificateTicketsCancelled      | Число погашенных в соответствии с пунктом 6 статьи 65 Федерального закона "О выборах Президента Российской Федерации" отрывных талонов открепительных удостоверений
lostBallots                              | Число бюллетений по актам об утрате" / "Число утраченных избирательных бюллетеней
lostAbsCertificates                      | Число открепит. удостов. по актам об утрате
unaccountedBallots                       | Число избирательных бюллетеней, не учтенных при получении
nota (None Of The Above, against all)    | Против всех
uik_name                                 | Полное название УИК
url                                      | Ссылка
ballotsIssued                            | Число бюллетеней, выданных участникам голосования
ballotsInAllBoxes                        | Число бюллетеней, содержащихся в ящиках для голосования
coib                                     | optical scanning voting machines (1,0)

Candidate names are transliterated, only lastnames are used, e.g.:

Internal name    | Name that could be seen in real protocols
-----------------|-------------------------------------------
Govoruhin        | ГОВОРУХИН Станислав Сергеевич
Dzhabrailov      | ДЖАБРАИЛОВ Умар Алиевич
Zhirinovskij     | ЖИРИНОВСКИЙ Владимир Вольфович
Zyuganov         | ЗЮГАНОВ Геннадий Андреевич
Pamfilova        | ПАМФИЛОВА Элла Александровна
