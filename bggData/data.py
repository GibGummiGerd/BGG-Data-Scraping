from boardgamegeek import BGGClient
bgg = BGGClient()
g = bgg.game(game_id=167355)
print (g.name)
print (g.id)
for n in g.alternative_names: 
    print (n)