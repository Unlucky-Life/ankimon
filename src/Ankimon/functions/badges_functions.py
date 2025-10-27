import json

from ..resources import badgebag_path

def check_badges(achievements):
    with open(badgebag_path, "r", encoding="utf-8") as json_file:
        badge_list = json.load(json_file)
        for badge_num in badge_list:
            achievements[str(badge_num)] = True
    return achievements

def check_for_badge(achievements, rec_badge_num):
    achievements = check_badges(achievements)
    if achievements[str(rec_badge_num)] is False:
        got_badge = False
    else:
        got_badge = True
    return got_badge

def save_badges(badges_collection):
    with open(badgebag_path, 'w') as json_file:
        json.dump(badges_collection, json_file)

def receive_badge(badge_num,achievements):
    achievements = check_badges(achievements)
    #for badges in badge_list:
    achievements[str(badge_num)] = True
    badges_collection = []
    for num in range(1,69):
        if achievements[str(num)] is True:
            badges_collection.append(int(num))
    save_badges(badges_collection)
    return achievements

def handle_review_count_achievement(review_count, achievements):
    if review_count == 100:
        check = check_for_badge(achievements,1)
        if check is False:
            achievements = receive_badge(1,achievements)
    elif review_count == 200:
        check = check_for_badge(achievements,2)
        if check is False:
            achievements = receive_badge(2,achievements)
    elif review_count == 300:
        check = check_for_badge(achievements,3)
        if check is False:
            achievements = receive_badge(3,achievements)
    elif review_count == 500:
        check = check_for_badge(achievements,4)
        if check is False:
            receive_badge(4,achievements)
    return achievements