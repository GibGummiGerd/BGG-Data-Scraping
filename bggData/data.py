from boardgamegeek import BGGClient

bgg = BGGClient()
g = bgg.game(game_id=167355)
print(g.name)
print(g.id)
print(vars(g))
# for n in g.ratings:
#     print (n)
