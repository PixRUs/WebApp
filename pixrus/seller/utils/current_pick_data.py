from product.models import ApiRequest


def get_current_pick_data(active_picks):
    pick_list = []
    for pick in active_picks:
        sport_league = pick.sport_league
        home_team = pick.game_data['home_team']
        away_team = pick.game_data['away_team']
        book_maker = pick.pick_data['book_maker']
        target_winner = pick.pick_data['target_winner']
        type_of_pick = pick.type_of_pick
        vendor_req = ApiRequest.objects.filter(sport_league=sport_league,type_of_pick=type_of_pick).first().response_data
        found = False
        for game in vendor_req:
            if game['home_team'] == home_team and game['away_team'] == away_team:
                for book in game['bookmakers']:
                    if book['title']== book_maker:
                        odds = book['markets'][0]['outcomes']
                        for odd in odds:
                            if odd['name'] == target_winner:
                                pick_list.append((pick,odd['price']))
                                found = True
        if not found:
            pick_list.append((pick,"pick data currently not available"))

    return pick_list
