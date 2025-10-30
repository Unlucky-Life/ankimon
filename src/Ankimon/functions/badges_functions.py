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
    milestones = {
        100: 1,
        200: 2,
        300: 3,
        500: 4,
    }
    badge_to_award = milestones.get(review_count)
    if badge_to_award and not check_for_badge(achievements, badge_to_award):
        achievements = receive_badge(badge_to_award, achievements)

    return achievements