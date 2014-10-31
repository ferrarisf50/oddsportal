# -*- coding: utf-8 -*-
import sys, os
sys.dont_write_bytecode = True

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import ItemLoader
from soccer.items import ResultsItem
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request

from flask import session, request, url_for, flash
import re, json, time, urllib2, requests
from soccer import models
from soccer.settings import session


crawlers_path = os.path.abspath(__name__).split('crawlers')[0]
links = open(crawlers_path + '/crawlers/soccer/soccer/spiders/links.txt').readlines()


from soccer.settings import logger_present, logger_absent


class Cron_crawler(CrawlSpider):

    name            = "soccer_cron"
    allowed_domains = ["oddsportal.com"]
    start_urls      = links

    def parse(self, response):

        hxs    = HtmlXPathSelector(response)
        years  = hxs.select("//div[@class='main-menu2 main-menu-gray']/ul//a").extract()
        league = hxs.select("//div[@id='breadcrumb']/a/text()").extract()[2]
        group  = hxs.select("//div[@id='breadcrumb']/a/text()").extract()[3]
        
        year_url = re.findall(re.compile('\"(.+?)\"'),  years[0])[0]
        year_num = re.findall(re.compile('>(.+?)</a>'), years[0])[0]
        year_for_database = re.sub('/', '-', year_num)
        new_url  = urljoin_rfc(get_base_url(response),  year_url)

        yield Request((new_url), meta = {'year':   year_num,
                                         'group':  group,
                                         'league': league}, callback=self.parse_category)


    def parse_category(self, response):

        hxs = HtmlXPathSelector(response)
        tournament_links = hxs.select("//table[@id='tournamentTable']//a[not(@class)]/@href").extract()
        
        for i, link in enumerate(tournament_links[1:]):
            new_url = urljoin_rfc(get_base_url(response), link)

            checker = session.query(models.Result).filter_by(tournament_url = new_url).all()
            if checker:
                logger_present.info(new_url)
            else:
                logger_absent.info(new_url)
                yield Request(new_url, meta={'url':    response.url,
                                             'year':   response.meta['year'],
                                             'group':  response.meta['group'],
                                             'league': response.meta['league']}, callback=self.parse_item)


    def parse_item(self, response):

        print '='*30
        print 'Start working on tournament'

        hxs = HtmlXPathSelector(response)
        html_data  = response.body
        event_id   = re.findall(re.compile('"id":"(.+?)"'),             html_data)[0]
        
        #-- If there is no xhash tag on the page, we are on the wrong page, let's skip it
        try:
            event_hash_01  = re.findall(re.compile('"xhash":"(.+?)"'),      html_data)[0]
        except:
            return
        event_hash_02  = re.findall(re.compile('"xhashf":"(.+?)"'),     html_data)[0]
        tournament_id  = re.findall(re.compile('tournamentId\":(\d*)'), html_data)[0]
        tournament_url = response.url

        event_hash = event_hash_01
        

        #-- We want to ignore live events and wait for results --#
        live_tag = hxs.select("//p[@class='result-live']/text()").extract()
        if live_tag:
            return

        home_team = hxs.select("//div[@id='col-content']/h1/text()").extract()[0].split(' - ')[0]
        away_team = hxs.select("//div[@id='col-content']/h1/text()").extract()[0].split(' - ')[1]

        #-- Datetime gonna be in Unix format like "1410112800" for 07'Sep 2014 --#
        event_datetime = hxs.select("//p[contains(@class, 'datet')]/@class").extract()[0]
        event_datetime = re.findall(re.compile('datet t(.+?)-'), event_datetime)[0]

        #-- Results are written this way: "1:1 (1:1, 0:0)" --#
        #-- final results, then 1st half and then 2nd half --#
        try:
            halfs_results = hxs.select("//p[@class='result']/text()").extract()[0]
            first_half_results  = re.findall(re.compile('\((.+?)\)'), halfs_results)[0].split(', ')[0]
            second_half_results = re.findall(re.compile('\((.+?)\)'), halfs_results)[0].split(', ')[1]
        except:
            first_half_results, second_half_results = '', ''

        try:
            final_results = hxs.select("//p[@class='result']/strong/text()").extract()[0]
            final_results = re.findall(re.compile('(\d:\d)'), final_results)[0]
            results       = {'full': final_results, 'frst': first_half_results, 'scnd': second_half_results}
        except:
            #TODO: send to empty tournament constructor
            return
        #-- To extract odds, GET requests are used; they include event_id, event_hash and request code --#
        #-- Codes: over/under fulltime - "2-2"; 1st half - "2-3"; 2nd half - "2-4" --#
        #-- For Home-Draw-Away (hda) odds we use 1-2, 1-3, 1-4 codes respectively --#
        ou_full_request = 'http://fb.oddsportal.com/feed/match/1-1-{}-2-2-{}.dat?_=100'
        ou_full_request = ou_full_request.format(event_id, event_hash)
        
        ou_frst_request = 'http://fb.oddsportal.com/feed/match/1-1-{}-2-3-{}.dat?_=100'
        ou_frst_request = ou_frst_request.format(event_id, event_hash)

        ou_scnd_request = 'http://fb.oddsportal.com/feed/match/1-1-{}-2-4-{}.dat?_=100'
        ou_scnd_request = ou_scnd_request.format(event_id, event_hash)

        hda_full_request = 'http://fb.oddsportal.com/feed/match/1-1-{}-1-2-{}.dat?_=100'
        hda_full_request = hda_full_request.format(event_id, event_hash)

        hda_frst_request = 'http://fb.oddsportal.com/feed/match/1-1-{}-1-3-{}.dat?_=100'
        hda_frst_request = hda_frst_request.format(event_id, event_hash)

        hda_scnd_request = 'http://fb.oddsportal.com/feed/match/1-1-{}-1-4-{}.dat?_=100'
        hda_scnd_request = hda_scnd_request.format(event_id, event_hash)

        get_requests = {'ou_full_request':  ou_full_request,
                        'ou_frst_request':  ou_frst_request,
                        'ou_scnd_request':  ou_scnd_request,
                        'hda_full_request': hda_full_request,
                        'hda_frst_request': hda_frst_request,
                        'hda_scnd_request': hda_scnd_request}

        l = ItemLoader(item = ResultsItem(), response = response)
        l.add_value('home_team',  home_team)
        l.add_value('away_team',  away_team)
        l.add_value('datetime', event_datetime)
        l.add_value('event_results',  json.dumps(results))
        l.add_value('year',     response.meta['year'])
        l.add_value('league',   response.meta['league'])
        l.add_value('group',    response.meta['group'])
        l.add_value('event_id', event_id)
        l.add_value('event_hash_01', event_hash_01)
        l.add_value('event_hash_02', event_hash_02)
        l.add_value('tournament_id', tournament_id)
        l.add_value('tournament_url', tournament_url)


        
        yield Request(url  = get_requests['ou_full_request'], 
                      meta = {'item': l, 'requests': get_requests}, 
                      callback = self.parse_ou_full)

    
    def parse_ou_full(self, response):
        from json_analysers import over_under

        response.meta['item'].add_value('ou_full_results', over_under(response.body))

        yield Request(url      = response.meta['requests']['ou_frst_request'],
                      meta     = {'item':     response.meta['item'], 
                                  'requests': response.meta['requests']},
                      callback = self.parse_ou_frst)

    def parse_ou_frst(self, response):
        from json_analysers import over_under

        response.meta['item'].add_value('ou_frst_results', over_under(response.body))

        yield Request(url      = response.meta['requests']['ou_scnd_request'],
                      meta     = {'item':     response.meta['item'], 
                                  'requests': response.meta['requests']},
                      callback = self.parse_ou_scnd)

    def parse_ou_scnd(self, response):
        from json_analysers import over_under

        response.meta['item'].add_value('ou_scnd_results', over_under(response.body))

        yield Request(url      = response.meta['requests']['hda_full_request'],
                      meta     = {'item':     response.meta['item'], 
                                  'requests': response.meta['requests']},
                      callback = self.parse_hda_full)

    def parse_hda_full(self, response):
        from json_analysers import home_draw_away

        response.meta['item'].add_value('hda_full_results', home_draw_away(response.body))

        yield Request(url      = response.meta['requests']['hda_frst_request'],
                      meta     = {'item':     response.meta['item'], 
                                  'requests': response.meta['requests']},
                      callback = self.parse_hda_frst)

    def parse_hda_frst(self, response):
        from json_analysers import home_draw_away

        response.meta['item'].add_value('hda_frst_results', home_draw_away(response.body))

        yield Request(url      = response.meta['requests']['hda_scnd_request'],
                      meta     = {'item':     response.meta['item'], 
                                  'requests': response.meta['requests']},
                      callback = self.parse_hda_scnd)

    def parse_hda_scnd(self, response):
        from json_analysers import home_draw_away

        response.meta['item'].add_value('hda_scnd_results', home_draw_away(response.body))

        logger_absent.info('Saved: ' + str(response.meta['item'].__dict__))
        yield response.meta['item'].load_item()