from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import TakeFirst

class ResultsItem(Item):

    tournament_url = Field(default='', output_processor=TakeFirst())

    home_team = Field(default='', output_processor=TakeFirst())
    away_team = Field(default='', output_processor=TakeFirst())
    datetime  = Field(default='', output_processor=TakeFirst())
    year      = Field(default='', output_processor=TakeFirst())
    league    = Field(default='', output_processor=TakeFirst())
    group     = Field(default='', output_processor=TakeFirst())

    event_id  = Field(default='', output_processor=TakeFirst())
    event_hash_01 = Field(default='', output_processor=TakeFirst())
    event_hash_02 = Field(default='', output_processor=TakeFirst())
    tournament_id = Field(default='', output_processor=TakeFirst())

    event_results   = Field(default='', output_processor=TakeFirst())

    ou_full_results = Field(default='', output_processor=TakeFirst())
    ou_frst_results = Field(default='', output_processor=TakeFirst())
    ou_scnd_results = Field(default='', output_processor=TakeFirst())

    hda_full_results = Field(default='', output_processor=TakeFirst())
    hda_frst_results = Field(default='', output_processor=TakeFirst())
    hda_scnd_results = Field(default='', output_processor=TakeFirst())

