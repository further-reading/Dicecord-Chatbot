import patreon
from utils.patreon_info import (
    CREATOR_ID, TIER_IDS, CAMPAIGN_ID, PAGE_SIZE,
)


def get_arcane_name(pledge, pledges_response):
    reward = pledge.relationship('reward')
    if reward.id() in TIER_IDS:
        patron = pledge.relationship('patron')
        patron_id = patron.id()
        user = pledges_response.find_resource_by_type_and_id('user', patron_id)
        return user.attribute('full_name')


def get_credits():
    api_client = patreon.API(CREATOR_ID)
    arcane_pledges = []
    cursor = None
    while True:
        pledges_response = api_client.fetch_page_of_pledges(
            CAMPAIGN_ID,
            PAGE_SIZE,
            cursor=cursor,
            )
        all_pledges = pledges_response.data()
        all_pledges = [get_arcane_name(p, pledges_response) for p in all_pledges]
        arcane_pledges += [name for name in all_pledges if name]
        cursor = api_client.extract_cursor(pledges_response)
        if not cursor:
            break
    return '\n'.join(arcane_pledges)
