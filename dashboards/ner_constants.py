# import string
# import re
# import pandas as pd
# import numpy as np
# from collections import defaultdict

# import spacy
# from spacy import displacy
# from spacy.matcher import Matcher
# from spacy.lemmatizer import Lemmatizer
# from spacy.lookups import Lookups


# Tag colours
colors = ["#67E568","#257F27","#08420D","#FFF000","#FFB62B","#E56124","#E53E30","#7F2353","#F911FF","#9F8CA6"]

POS = {
       # Openness
       'CREATED': colors[1],
       'IMPROVED': colors[1],
       'CHANGED': colors[1],
       'RESEARCHED': colors[1],

       # Conscientiousness
       'MANAGED': colors[3],
       'ACHIEVED': colors[3],
       'SOLVED': colors[3],
       'SAVED': colors[3],
       'REGULATED': colors[3],
       'TECH_STACK': colors[3],
       'SKILLS': colors[3],

       # Extraversion
       'LED': colors[6],
       'COMMUNICATED': colors[6],
       'NETWORKED': colors[6],
       'BUZZ': colors[6],

       # Agreeability
       'COLLABORATED': colors[4],
       'SUPPORTED': colors[4],

       # Neurotism
       'STRESSED': colors[5],

       # Neurotism
       'HEADERS': colors[7],
       'AVOID': colors[7],

       'SELF': colors[9],
       }

POS_2 = {'SELF': colors[0],
       'TEAMWORK': colors[1],
       'COLLABORATED': colors[1],
       'SUPPORTED': colors[1],
       'NETWORKED': colors[1],
       'COMMUNICATED': colors[1],
       'COMMUNICATION': colors[1],
       'RESEARCHED': colors[2],
       'REGULATED': colors[2],
       'LEADERSHIP': colors[7],
       'LED': colors[7],
       'MANAGED': colors[7],
       'RESULT_DRIVEN': colors[3],
       'ACHIEVED': colors[3],
       'SOLVED': colors[3],
       'SAVED': colors[3],
       'ANALYTICAL': colors[4],
       'CREATED': colors[4],
       'IMPROVED': colors[4],
       'CHANGED': colors[4],
       'NEGATIVE': colors[5],
       'WEAK_WORDS': colors[5],
       'TECH_STACK': colors[6],
       'BUZZ': colors[8],
       'AVOID': colors[8],
       }


SKILLS = {
    'led': """
                    Led,
                    Chaired,
                    Controlled,
                    Coordinated,
                    Guided,
                    Headed,
                    Hired,
                    Instructed,
                    Operated,
                    Orchestrated,
                    Organised,
                    Organized,
                    Oversaw,
                    Planned,
                    Produced,
                    Programmed
                    """.replace(' ', '').replace('\n', '').split(','),
    'created': """
                    Created,
                    Administered,
                    Built,
                    Brainstormed,
                    Charted,
                    Created,
                    Conceptualized,
                    Defined,
                    Designed,
                    Developed,
                    Devised,
                    Founded,
                    Engineered,
                    Established,
                    Formalised,
                    Formalized,
                    Formed,
                    Formulated,
                    Implemented,
                    Incorporated,
                    Initiated,
                    Innovated,
                    Instituted,
                    Introduced,
                    Launched,
                    Modelled,
                    Opened,
                    Originated,
                    Pioneered,
                    Set up,
                    Shaped,
                    Spearheaded,
                    Started
                    """.replace(' ', '').replace('\n', '').split(','),
    'saved': """
                    Saved,
                    Conserved,
                    Consolidated,
                    Decreased,
                    Deducted,
                    Diagnosed,
                    Lessened,
                    Lowered,
                    Reconciled,
                    Reduced,
                    Slashed,
                    Yielded
                    """.replace(' ', '').replace('\n', '').split(','),
    'improved': """
                    Improved,
                    Accelerated,
                    Advanced,
                    Amplified,
                    Boosted,
                    Capitalised,
                    Capitalized,
                    Cut,
                    Delivered,
                    Enhanced,
                    Elevated,
                    Expanded,
                    Expedited,
                    Furthered,
                    Gained,
                    Generated,
                    Grew,
                    Improved,
                    Increased,
                    Lifted,
                    Maximized,
                    Outpaced,
                    Raised,
                    Sped,
                    Stimulated,
                    Strengthened,
                    Sustained
                    """.replace(' ', '').replace('\n', '').split(','),
    'changed': """
                    Adjusted,
                    Changed,
                    Centralised,
                    Centralized,
                    Clarified,
                    Converted,
                    Customised,
                    Customized,
                    Influenced,
                    Integrated,
                    Modified,
                    Moderated,
                    Modernised,
                    Modernized,
                    Overhauled,
                    Ordered,
                    Redesigned,
                    Refined,
                    Refocused,
                    Rehabilitated,
                    Reinforced,
                    Remodeled,
                    Reorganized,
                    Replaced,
                    Restructured,
                    Revamped,
                    Revitalised,
                    Revitalized,
                    Simplified,
                    Standardised,
                    Standardized,
                    Systemised,
                    Systemized,
                    Structured,
                    Streamlined,
                    Updated,
                    Upgraded,
                    Transformed
                    """.replace(' ', '').replace('\n', '').split(','),
    'solved': """
                    Solved,
                    Altered,
                    Assigned,
                    Balanced,
                    Catalogued,
                    Corrected,
                    Contracted,
                    Computed,
                    Crafted,
                    Determined,
                    Drafted,
                    Filed,
                    Eliminated,
                    Extracted,
                    Fashioned,
                    Fixed,
                    Invented,
                    Patched,
                    Piloted,
                    Purchased,
                    Rebuilt,
                    Recorded,
                    Resolved,
                    Released,
                    Tabulated,
                    Traced
                    """.replace(' ', '').replace('\n', '').split(','),
    'managed': """
                    Managed,
                    Managing,
                    Aligned,
                    Appraised,
                    Arranged,
                    Budgetted,
                    Cultivated,
                    Directed,
                    Executed,
                    Enabled,
                    Facilitated,
                    Fostered,
                    Inspired,
                    Mentored,
                    Mobilised,
                    Mobilized,
                    Motivated,
                    Multi-task,
                    Prioritise,
                    Prioritize,
                    Recruited,
                    Supervised,
                    Supervized,
                    Scheduled,
                    Taught,
                    Trained,
                    Unified
                    """.replace(' ', '').replace('\n', '').split(','),
    'networked': """
                    Networked,
                    Acquired,
                    Forged,
                    Navigated,
                    Negotiated,
                    Partnered,
                    Secured
                    """.replace(' ', '').replace('\n', '').split(','),
    'supported': """
                    Supported,
                    Advised,
                    Advocated,
                    Arbitrated,
                    Coached,
                    Consulted,
                    Educated,
                    Fielded,
                    Informed,
                    Shared
                    """.replace(' ', '').replace('\n', '').split(','),
    'researched': """
                    Researched,
                    Analyzed,
                    Analysed,
                    Assembled,
                    Assessed,
                    Audited,
                    Budgeted,
                    Calculated,
                    Collected,
                    Compiled,
                    Concieved,
                    Discovered,
                    Evaluated,
                    Examined,
                    Explored,
                    Forecasted,
                    Identified,
                    Inspected,
                    Interpreted,
                    Investigated,
                    Judged,
                    Mapped,
                    Measured,
                    Probed,
                    Proved,
                    Qualified,
                    Quantified,
                    Queried,
                    Studied,
                    Surveyed,
                    Summarised,
                    Summarized,
                    Tested,
                    Tracked,
                    Uncovered
                    """.replace(' ', '').replace('\n', '').split(','),
    'communicated': """
                    Communicated,
                    Addressed,
                    Authored,
                    Adviced,
                    Briefed,
                    Campaigned,
                    Co-authored,
                    Composed,
                    Conveyed,
                    Convinced,
                    Corresponded,
                    Counseled,
                    Critiqued,
                    Documented,
                    Edited,
                    Illustrated,
                    Interviewed,
                    Lobbied,
                    Outlined,
                    Persuaded,
                    Presented,
                    Promoted,
                    Proposed,
                    Publicised,
                    Publicized,
                    Presented,
                    Recommended,
                    Referred,
                    Represented,
                    Specified,
                    Spoke,
                    Translated,
                    Reviewed,
                    Wrote
                    """.replace(' ', '').replace('\n', '').split(','),
    'regulated': """
                    Authorised,
                    Authorized,
                    Blocked,
                    Classified,
                    Delegated,
                    Dispatched,
                    Enforced,
                    Ensured,
                    Itemised,
                    Itemized,
                    Monitored,
                    Regulated,
                    Screened,
                    Scrutinised,
                    Scrutinized,
                    Validated,
                    Verified
                    """.replace(' ', '').replace('\n', '').split(','),
    'achieved': """
                    Achieved,
                    Accomplished,
                    Attained,
                    Awarded,
                    Completed,
                    Demonstrated,
                    Earned,
                    Exceeded,
                    Outperformed,
                    Performed,
                    Reached,
                    Retrieved,
                    Showcased,
                    Succeeded,
                    Surpassed,
                    Thrived,
                    Targeted,
                    Won
                    """.replace(' ', '').replace('\n', '').split(','),
    'collaborated': """
                    Acknowledged,
                    Assimilated,
                    Adapted,
                    Blended,
                    Coalesced,
                    Collaborated,
                    Cooperated,
                    Conducted,
                    Contributed,
                    Diversified,
                    Embraced,
                    Encouraged,
                    Energized,
                    Explained,
                    Gathered,
                    Harmonised,
                    Harmonized,
                    Helped,
                    Ignited,
                    Involved,
                    Joined,
                    Lectured,
                    Melded,
                    Merged,
                    Participated,
                    Prepared,
                    Provided,
                    Served,
                    Teamed,
                    United,
                    Volunteered
                    """.replace(' ', '').replace('\n', '').split(','),
    'stressed': """
                    Worried,
                    Stressed,
                    Irritated,
                    Anger,
                    Upset,
                    Down,
                    Anxious,
                    Threatened,
                    Frustrated,
                    Depressed
                    """.replace(' ', '').replace('\n', '').split(','),
    'avoid': """
                    Assisted,
                    Attempted,
                    Familiarised,
                    Familiarized,
                    Tried,
                    Enjoyed,
                    Liked,
                    Loved,
                    Did,
                    Got,
                    Had,
                    Handled,
                    Made,
                    Worked,
                    Utilised,
                    Utilized,
                    Because,
                    He,
                    She,
                    Me,
                    Him,
                    Her,
                    Our
                    """.replace(' ', '').replace('\n', '').split(','),
    'buzz': """
                    Specialised,
                    Specialized,
                    Experienced,
                    Skilled,
                    Leadership,
                    Passionate,
                    Expert,
                    Expertise,
                    Excellence,
                    Excellent,
                    Strategic,
                    Focused
                    """.replace(' ', '').replace('\n', '').split(','),
}

MEASURABLE_RESULTS = {
    'metrics': [
        '$',
        '€',
        'Euro',
        'USD',
        '%',
        'percent',
        'fundraised',
        'millions',
        'thousands',
        'hundreds',
        'expenses',
        'profits',
        'growth',
        'sales',
        'volume',
        'revenue',
        'page views',
        'engagement',
        'donations',
        'closed',
        'customer ratings',
        'retention',
        'response',
        'average',
        'complaints',
        'budget'
        'numeric_value'
    ],
    'metrics': [
        'approximately',
        'little',
        'bit',
        ''
    ]
}

# http://datasciencestack.liip.ch/download.json
null = None
tech_stack = {"Data Sources":
              {"Scraping":[
                {"name":"Scrapy Cluster","link":"https://github.com/istresearch/scrapy-cluster","description":"Scrapy as a cluster","license":"Opensource"},
                {"name":"X-ray","link":"https://github.com/kichooo/x-ray","description":"Very fast and simple scraper","license":"Lib"},
                {"name":"Portia","link":"https://github.com/scrapinghub/portia","description":"Visual scraping for scrapy","license":""},{"name":"Scrapy","link":"https://scrapy.org","description":"Powerfull Python Scraping Framework","license":"Opensource"},{"name":"Nutch","link":"https://nutch.apache.org","description":"High Scalability Crawler","license":"Opensource"},{"name":"PhantomJS","link":"http://phantomjs.org","description":"Headless Browser perfect for scraping","license":"Lib"},{"name":"ImportIO","link":"https://www.import.io","description":"Webscraping as a Service","license":"Saas"},{"name":"Morph","link":"https://morph.io","description":"Multi Lang Scraper Platform","license":"Saas"}],"Social Media":[{"name":"Quintly","link":"https://www.quintly.com","description":"Cross-platform social media analytics","license":""},{"name":"Buffer","link":"https://bufferapp.com/","description":"Content planning + analytics","license":""},{"name":"HootSuite","link":"https://hootsuite.com/de/","description":"Content curation + analytics","license":""},{"name":"BrandWatch","link":"https://www.brandwatch.com","description":"Campaign monitoring in social media","license":""},{"name":"Klout","link":"https://klout.com/home","description":"User rating platform","license":""},{"name":"Falcon","link":"https://www.falcon.io","description":"Analytics + content for campaigns","license":""},{"name":"Kred","link":"http://home.kred","description":"Influence user scoring","license":""},{"name":"SocialBlade","link":"https://socialblade.com","description":"Focus on video on social media ","license":""},{"name":"Sprout Social","link":"https://sproutsocial.com","description":"Social media meanagement","license":""},{"name":"Gnip","link":"https://gnip.com","description":"Raw Social Media Data","license":"Saas"},{"name":"Datasift","link":"http://datasift.com","description":"Raw Social Media Data","license":"Saas"},{"name":"Spinn3r","link":"https://www.spinn3r.com","description":"Social Media Crawler","license":"Saas"}],"Website Analytics":[{"name":"Ahoy","link":"https://github.com/ankane/ahoy.js","description":"Simple JS tracker","license":"Opensource"},{"name":"Matomo","link":"https://matomo.org","description":"On Premise alternative with Saas option","license":"Opensource/Saas"},{"name":"Countly","link":"https://count.ly/community-edition/","description":"Selfhosted analytics ","license":"Opensource/Saas"},{"name":"Awstats","link":"http://www.awstats.org","description":"Perl based","license":"Opensource"},{"name":"Openweb Analytics","link":"http://www.openwebanalytics.com/","description":"Similar to Piwik runs on PHP","license":"Opensource"},{"name":"Sitespect","link":"https://www.sitespect.com","description":"Analytics with focus on A/B testing.","license":""},{"name":"Loggr","link":"http://loggr.net","description":"Website + App analytics","license":""},{"name":"Parse.ly","link":"https://www.parse.ly","description":"Tiny but cute analytics","license":""},{"name":"Chartbeat","link":"https://chartbeat.com/","description":"Beautiful realtime analytics with dashboards.","license":""},{"name":"Going Up","link":"http://www.goingup.com/","description":"SEO and analytics in one tool. ","license":""},{"name":"Mint","link":"http://haveamint.com/","description":"Self hosted analytics solution","license":""},{"name":"Clicky","link":"http://clicky.com/","description":"Track users, audio, video analytics.","license":""},{"name":"Clicktale","link":"http://www.clicktale.com/","description":"Record users on website.","license":""},{"name":"Foxmetrics","link":"http://foxmetrics.com","description":"Track users, plain vanilla.","license":""},{"name":"Opentracker","link":"http://www.opentracker.net/","description":"Realtime, Geo and User Tracking","license":""},{"name":"Webtrends","link":"https://www.webtrends.com","description":null,"license":"Saas"},{"name":"Calq","link":"https://calq.io/","description":"Custom Analytics for mobile and web.","license":""},{"name":"Heap Analytics","link":"https://heapanalytics.com","description":"Enterprise oriented","license":"Saas"},{"name":"Analytics Suite 2","link":"http://www.atinternet.com/de/","description":"Enterprise oriented","license":"Proprietary"},{"name":"Statcounter","link":"http://statcounter.com/product/","description":"Free and paid version","license":"Saas"},{"name":"Luckyorange","link":"http://www.luckyorange.com","description":"Saas solution","license":"Saas"},{"name":"Sawmill","link":"http://sawmill.net","description":"Saas with plugins","license":"Proprietary"},{"name":"ClickMeter","link":"http://clickmeter.com","description":"Website analytics with focus on campaigns","license":""},{"name":"Segment.io","link":"http://segment.io/","description":"Integrate multiple tracking solutions in one js code","license":""},{"name":"Indicative","link":"http://www.indicative.com/","description":"Web + mobile analytics.","license":""},{"name":"Adjust","link":"https://www.adjust.com","description":"Campaign tracking","license":""},{"name":"Popcorn Metrics","link":"http://www.popcornmetrics.com/","description":"Capture events integration","license":""},{"name":"Gauges","link":"http://get.gaug.es/","description":"Realtime analytics tool.","license":""},{"name":"Onthe","link":"https://t.onthe.io/media","description":"Website tracker with focus on editorial staff","license":"Saas"},{"name":"Google Analytics","link":"http://analytics.google.com","description":"General purpose analytics ","license":"Saas"},{"name":"Kissmetrics","link":"https://www.kissmetrics.com","description":"Ecommerce oriented","license":"Saas"},{"name":"Woopra","link":"https://www.woopra.com","description":"Ecommerce oriented","license":"Saas"},{"name":"Adobe Analytics","link":"http://www.adobe.com/marketing-cloud/web-analytics.html","description":"Enterprise level","license":"Saas"},{"name":"Fox Metrics","link":"http://www.foxmetrics.com","description":"Ecommerce oriented","license":"Saas"},{"name":"GoSquared","link":"https://www.gosquared.com","description":"Focus on CRM","license":"Saas"},{"name":"Google Marketing Platform","link":"https://www.google.com/analytics/360-suite/","description":"Enterprise level Analytics","license":"Saas"},{"name":"Siteimprove Analytics","link":"https://siteimprove.com/de-ch/product/analytics/","description":"Dutch Saas solution","license":"Saas"},{"name":"Fathon Analytics","link":"https://usefathom.com","description":"Privacy first","license":""},{"name":"Simple Analytics","link":"https://simpleanalytics.io","description":"Simple, Clean, Friendly analytics","license":""},{"name":"VWO","link":"https://vwo.com/","description":"Visual website Analyzer","license":""}],"Tag Management":[{"name":"7Tag","link":"https://7tag.org","description":"From the people that developed Piwik","license":"Lib"},{"name":"Google Tag Manager","link":"https://www.google.com/analytics/tag-manager/","description":"Google Tag Manager","license":"Saas Free"},{"name":"Tealium Tag Manager","link":"http://tealium.com/products/tealium-iq-tag-management-system/","description":"Enterprise Level Tag Manager","license":"Saas"},{"name":"Tag Commander","link":"https://www.commandersact.com/en/","description":"Tag Manager","license":"Saas"},{"name":"Qubit Tag manager","link":"http://www.qubit.com/solutions/tag-management","description":"Tag Manager with containers","license":"Saas"},{"name":"Supertag","link":"https://www.datalicious.com/supertag-agile-tag-management","description":"Tag Management with A/B Testing","license":"Saas"},{"name":"Matomo Tag Manager","link":"https://matomo.org/docs/tag-manager/","description":"Tag Manager from Matomo","license":""},{"name":"Ensighten Tag Mgmt","link":"https://www.ensighten.com/products/enterprise-tag-management/","description":"Tag manager from IBM","license":""},{"name":"Adobe DTM ","link":"https://dtm.adobe.com","description":"Tag management by adobe","license":""}],"IoT":[{"name":"Raspberry Pi","link":"http://raspberrypi.org","description":"Standard","license":"$"},{"name":"Photon","link":"https://www.particle.io","description":"IoT with Wifi","license":"$"},{"name":"NodeRed","link":"https://nodered.org","description":"Flow based programming for IoT","license":"Saas"},{"name":"Flowhub","link":"https://flowhub.io","description":"Flow based programming for the full stack","license":"Saas"},{"name":"UbiDots","link":"https://ubidots.com","description":"Data Collection and Analysis","license":"Saas"},{"name":"Thingspeak","link":"https://thingspeak.com","description":"Data Collection and Analysis","license":"Saas"},{"name":"Xively","link":"https://www.xively.com","description":"Data Collection and Analysis","license":"Saas"},{"name":"Bragi","link":"http://www.bragi.net/intelligent-edge/","description":"AI for small IoT devices","license":""}],"Heatmaps":[{"name":"CrazyEgg","link":"https://www.crazyegg.com","description":"Heatmap Analytics","license":""},{"name":"Inspectlet","link":"https://www.inspectlet.com/","description":"Analytics with focus on heatmaps","license":""},{"name":"Session Cam","link":"https://sessioncam.com","description":"Focus on heatmaps integration","license":""},{"name":"Hotjar","link":"https://www.hotjar.com/","description":"Focus on visual analytics. New approach.","license":""},{"name":"Mouseflow","link":"https://mouseflow.com","description":"Live heatmap analytics","license":""}],"Mobile Analytics":[{"name":"Upsight","link":"http://www.upsight.com","description":"Omnichannel marketing tracking","license":""},{"name":"AppsFlyer","link":"https://www.appsflyer.com","description":"Mobile Analytics","license":""},{"name":"Tapstream","link":"https://tapstream.com","description":"App analytics","license":""},{"name":"Appcelerator","link":"http://www.appcelerator.com/mobile-app-development-products/","description":"Native apps analytics","license":""},{"name":"Amazon Pinpoint","link":"https://aws.amazon.com/de/pinpoint/","description":"Mobile Analytics with Multi-Channel-Messaging","license":""},{"name":"Apsalar","link":"https://apsalar.com","description":"App shop analytics","license":""},{"name":"Flurry Analytics","link":"https://developer.yahoo.com/analytics/","description":"Yahoo mobile analytics","license":""},{"name":"AppSee","link":"https://www.appsee.com","description":"Mobile analytics for ecommerce","license":""},{"name":"Localytics","link":"https://www.localytics.com","description":"Modern mobile analytics","license":""},{"name":"Appfigures","link":"http://appfigures.com/","description":"Mobile + Store analytics","license":""},{"name":"App Annie","link":"https://www.appannie.com/de/","description":"Mobile + store analytics","license":""},{"name":"PrioriData","link":"https://prioridata.com","description":"Mobile + app shop analytics","license":""},{"name":"App Trace","link":"http://www.apptrace.com","description":"App store analytics","license":""},{"name":"Playtomic","link":"http://playtomic.org","description":"Tiny open source analytics for games","license":""},{"name":"GameAnalytics","link":"http://www.gameanalytics.com/","description":"Leading mobile game analytics ","license":""},{"name":"Asking Point","link":"https://www.askingpoint.com/mobile-app-rating-widget/","description":"Mobile user ratings analytics","license":""},{"name":"Amplitude","link":"https://amplitude.com/","description":"Redshift mobile analytics","license":""},{"name":"Mixpanel","link":"http://mixpanel.com","description":"Crossdevice","license":"Saas"},{"name":"Firebase","link":"https://firebase.google.com/products/analytics","description":"Analytics for Firebase by Google","license":""}]},"Data Processing":{"ETL":[{"name":"Genie","link":"https://netflix.github.io/genie/","description":"Orchestrate Jobs","license":""},{"name":"luigi","link":"https://github.com/spotify/luigi","description":"Build complex pipelines of batch jobs","license":""},{"name":"Aminator","link":"https://github.com/Netflix/aminator","description":"Automated AMI creation","license":""},{"name":"RubyETL","link":"https://github.com/square/ETL","description":"ETL for Ruby","license":"Lib"},{"name":"xarray","link":"https://github.com/pydata/xarray","description":"pandas for netCDF files","license":""},{"name":"SQOOP","link":"http://sqoop.apache.org","description":"Data scooping","license":"Opensource"},{"name":"Drill","link":"https://drill.apache.org","description":"Transform on the fly","license":"Opensource"},{"name":"Airflow","link":"http://airbnb.io/projects/airflow/","description":"Data job workflow manager ","license":"Opensource"},{"name":"Nifi","link":"https://nifi.apache.org","description":"Process and Distribute Data","license":"Opensource"},{"name":"Kettle","link":"http://community.pentaho.com/projects/data-integration/","description":"ETL from Pentaho","license":"Opensource"},{"name":"TalenD","link":"https://www.talend.com","description":"ETL","license":"Saas"},{"name":"Keboola","link":"https://www.keboola.com","description":"SQL based ETL ","license":"Saas"},{"name":"Kiba","link":"http://www.kiba-etl.org","description":"ETL for Ruby","license":"Lib"},{"name":"Datanitro","link":"https://datanitro.com","description":"Use python to script Excel macros ","license":"$"},{"name":"Tabula","link":"http://tabula.technology","description":"Extract Tables from PDFs","license":""},{"name":"Mathematica","link":"http://www.wolfram.com/mathematica/","description":"It does it all. ETL, visualizations, analysis. Links R, Python etc.","license":""}],"Datacleaning":[{"name":"Openrefine","link":"http://openrefine.org","description":"Easy data cleansing","license":"Opensource"},{"name":"Wrangler","link":"http://vis.stanford.edu/wrangler/","description":"Open soure version of data wrangler","license":"Opensource"},{"name":"Trifacta","link":"http://trifacta.com","description":"Commercial version of wrangler","license":"Saas"},{"name":"Pappa Parse","link":"https://www.papaparse.com","description":"CSV importer for huge files","license":""}],"Alerting/Logging":[{"name":"Graylog","link":"http://graylog.org","description":"Opensource Logging Service","license":"Opensource"},{"name":"Logstash","link":"http://logstash.net","description":"From ELK Stack","license":"Opensource"},{"name":"Fluentd","link":"http://www.fluentd.org","description":"Open Source Data collector","license":"Opensource"},{"name":"Goaccess","link":"https://goaccess.io","description":"Realtime weblog analyzer","license":"Opensource"},{"name":"Loggly","link":"http://loggly.com","description":"Like Graylog but paid","license":"Saas"},{"name":"Splunk","link":"http://www.splunk.com","description":"Industry strength log analysis ","license":"Saas"},{"name":"Sumologic","link":"https://www.sumologic.com","description":"Cloud hosted log analysis","license":"Saas"}],"MessageQueue":[{"name":"Heron","link":"https://github.com/apache/incubator-heron","description":"Realitme Stream processing from Twitter","license":"OpenSource"},{"name":"Streamalert","link":"https://github.com/airbnb/streamalert","description":"Serverless, realtime data analysis framework ","license":"Opensource"},{"name":"Celery","link":"http://www.celeryproject.org","description":"Distributed Task Queue","license":"Opensource"},{"name":"Impala","link":"http://impala.apache.org","description":"Realtime Stream Query","license":"Opensource"},{"name":"Nats","link":"https://nats.io","description":"Opensource for Cloud and Realtime","license":"Opensource"},{"name":"Druid","link":"http://druid.io","description":"Streams and Column DB","license":"Opensource/Saas"},{"name":"NSQ","link":"http://nsq.io","description":"Distributed Messaging Platform","license":"Opensource"},{"name":"ActiveMQ","link":"http://activemq.apache.org","description":"Popular Message Queue","license":"Opensource"},{"name":"RocketMQ","link":"https://rocketmq.incubator.apache.org","description":"Distributed Message Queue","license":"OpenSource"},{"name":"Kafka","link":"https://kafka.apache.org","description":"PubSub Stream","license":"Opensource"},{"name":"RabbitMQ","link":"https://www.rabbitmq.com","description":"Message Queue","license":"Opensource"},{"name":"Flink","link":"http://flink.apache.org","description":"Stream Analytics","license":"Opensource"},{"name":"Storm","link":"http://storm.apache.org","description":"Distributed realtime computation system.","license":"Opensource"},{"name":"Flume","link":"https://flume.apache.org","description":"Log Data Streams","license":"Opensource"},{"name":"Google","link":"https://cloud.google.com/pubsub/","description":"PubSub Stream","license":"Saas"},{"name":"Kinesis","link":"https://aws.amazon.com/de/kinesis/streams/","description":"PubSub Stream","license":"Saas"},{"name":"Dataflow","link":"https://cloud.google.com/dataflow/","description":"Orchestration","license":"Saas"},{"name":"MQTT","link":"http://mqtt.org/","description":"Erlang from Basel.. used by swiscomm/iot","license":"Opensouce/Sass"},{"name":"Amazon SQS","link":"https://aws.amazon.com/de/sqs/","description":"Simple Queue Service in a Cloud","license":"Saas"},{"name":"Scaledrone","link":"https://www.scaledrone.com/","description":"Crossbrowser Realtime Messagequeue","license":"Saas"}]},"Database":{"Open Data":[{"name":"DKAN","link":"https://www.drupal.org/project/dkan","description":"Open data for drupal","license":""},{"name":"Opendatasoft","link":"https://www.opendatasoft.com","description":"Commercial Open Data Portal Solution","license":""},{"name":"JKAN","link":"https://jkan.io","description":"Backend-free open data portal, powered by Jekyll","license":""},{"name":"CKAN","link":"https://ckan.org","description":"Open Source data portal platform","license":""}],"Database":[{"name":"LevelDB","link":"https://github.com/google/leveldb","description":"Key/Value","license":"Opensource"},{"name":"Beringei","link":"https://github.com/facebookincubator/beringei","description":"Inmem Timeseries DB from Facebook","license":"Opensource"},{"name":"TimescaleDB","link":"https://github.com/timescale/timescaledb","description":"Build ontop of postgres","license":"Opensource"},{"name":"SQLITE","link":"https://www.sqlite.org","description":"Filebased/Prototype DB","license":"Opensource"},{"name":"Postgres","link":"http://postgresapp.com","description":"SQL","license":"Opensource"},{"name":"MariaDB","link":"http://mariadb.org","description":"SQL","license":"Opensource"},{"name":"Neo4j","link":"https://neo4j.com","description":"Graph / NoSQL","license":"Opensource"},{"name":"Tinkerpop","link":"http://tinkerpop.apache.org","description":"Graph / NoSQL","license":"Opensource"},{"name":"Graphengine","link":"https://www.graphengine.io","description":"RAM Store+Model+Engine from Microsoft","license":"Opensource"},{"name":"RocksDb","link":"http://rocksdb.org","description":"Key/Value","license":"Opensource"},{"name":"Redis","link":"https://redis.io","description":"Key/Value","license":"Opensource"},{"name":"MongoDB","link":"http://mongoid.org","description":"NoSQL","license":"Opensource"},{"name":"CouchDB","link":"http://couchdb.apache.org","description":"NoSQL","license":"Opensource"},{"name":"Couchbase","link":"http://couchbase.com","description":"NoSQL","license":"Opensource"},{"name":"Aerospike","link":"http://www.aerospike.com","description":"NoSQL","license":"Opensource"},{"name":"LucidDb","link":"http://luciddb.sourceforge.net","description":"DWH","license":"Opensource"},{"name":"MonetDB","link":"https://www.monetdb.org/Home","description":"Column Oriented","license":"Opensource"},{"name":"Hypertable","link":"http://www.hypertable.org","description":"Column Oriented","license":"Opensource"},{"name":"MLDB","link":"https://www.mldb.ai","description":"DB with ML in it","license":"Opensource"},{"name":"Pytables","link":"http://www.pytables.org","description":"Hierarchical Data","license":"Opensource"},{"name":"BlinkDB","link":"http://blinkdb.org","description":"Sampling DB","license":"Opensource"},{"name":"HDF5 Data Format","link":"http://www.h5py.org","description":"High density format for data","license":"Opensource"},{"name":"Avro","link":"http://avro.apache.org/docs/current/","description":"Filesystem for Serialization of Data (like CSV)","license":"Opensource"},{"name":"KX DB","link":"https://kx.com","description":"Fast Column oriented with own query language","license":"Opensource"},{"name":"Axibase","link":"http://axibase.com","description":"Time Series Database with Viz","license":"Opensource"},{"name":"PumpkinDB","link":"http://pumpkindb.org/","description":"Database focusing on Events","license":"Opensource"},{"name":"Clickhouse","link":"https://clickhouse.yandex","description":"Column Oriented from Yandex","license":"Opensource"},{"name":"Coackroach DB","link":"https://www.cockroachlabs.com/product/cockroachdb/","description":"Massive DB without giving up SQL","license":""},{"name":"DVC","link":"https://dvc.org","description":"Data Version Control for ML","license":""},{"name":"MYSQL","link":"https://www.mysql.com","description":"SQL","license":"Saas/GPL"},{"name":"OracleDB","link":"https://en.wikipedia.org/wiki/Oracle_Database","description":"SQL","license":"Saas"},{"name":"Riak","link":"http://basho.com/products/","description":"NoSQL","license":"Saas/GPL"},{"name":"Google Bigtable","link":"https://cloud.google.com/bigtable/","description":"NoSQL","license":"Saas"},{"name":"Presto","link":"https://prestodb.io","description":"MPP","license":"Saas/GPL"},{"name":"Teradata","link":"https://en.wikipedia.org/wiki/Teradata","description":"MPP","license":"SaasSaas"},{"name":"Snowflake","link":"https://www.snowflake.net","description":"DWH","license":"Saas"},{"name":"SAP Hana","link":"https://de.wikipedia.org/wiki/SAP_HANA","description":"Column Oriented","license":"Saas"},{"name":"FoundationDB","link":"https://www.foundationdb.org","description":"Prod muliti-model key-value db","license":""},{"name":"Grakn","link":"http://grakn.ai","description":"Graph based knowledge db","license":""},{"name":"HP Vertica","link":"https://en.wikipedia.org/wiki/Vertica","description":"MPP column oriented db","license":"Saas/Hosted"},{"name":"Mapd","link":"https://www.mapd.com","description":"GPU Database","license":"Saas"},{"name":"Datomic","link":"http://www.datomic.com","description":"Cloud Distributed Database","license":"Saas"},{"name":"Cloud Spanner","link":"https://cloud.google.com/spanner/","description":"MPP from Google","license":"Saas"},{"name":"Graqn","link":"https://grakn.ai","description":"Graph DB for ML","license":""}],"In Memory/Search":[{"name":"Elastic","link":"http://elastic.co","description":"General flexible fast solution","license":"Opensource"},{"name":"Lucene","link":"http://lucene.apache.org/","description":"Mature Search engine","license":"Opensource"},{"name":"Solr","link":"http://lucene.apache.org/solr/","description":"Builds on Lucene","license":"Opensource"},{"name":"Lunar","link":"http://lunrjs.com/","description":"Inbrowser search engine","license":"Opensource"},{"name":"Compass","link":"http://www.compass-project.org","description":"Java search engine","license":"Opensource"},{"name":"Sphinx","link":"http://sphinxsearch.com","description":"Java search engine","license":"Opensource"},{"name":"Xapian","link":"https://xapian.org","description":"C search engine","license":"Opensource"},{"name":"VoltDB","link":"https://www.voltdb.com","description":"Fast inmem column db","license":"Opensource"},{"name":"Lemur/Indri","link":"https://www.lemurproject.org/indri.php","description":"Java Search Engine ","license":"Opensource"},{"name":"Fusion","link":"https://lucidworks.com/products/","description":"Lucidworks search solution.","license":""},{"name":"Websolr","link":"https://websolr.com","description":"Hosted Solr","license":"Saas"},{"name":"Searchify","link":"http://www.searchify.com","description":"Hosted Search","license":"Saas"},{"name":"Searchblox","link":"http://www.searchblox.com","description":"Hosted Search","license":"Saas"},{"name":"Site Search 360","link":"https://sitesearch360.com/","description":"Hosted Search. Affordable, based in Germany. Features both pushed content and website crawling ","license":"SaaS"},{"name":"Bonsai","link":"https://bonsai.io","description":"Elastic Saas","license":"Saas"},{"name":"Searchly","link":"http://www.searchly.com","description":"Elastic Saas","license":"Saas"},{"name":"Azure Search","link":"https://azure.microsoft.com/en-in/services/search/","description":"Microsoft Saas search","license":"Saas"},{"name":"Cloudsearch","link":"https://aws.amazon.com/de/cloudsearch/","description":"Amazon Saas search","license":"Saas"},{"name":"Exasol","link":"http://www.exasol.com","description":"Industry strength fast inmem db","license":"Saas"},{"name":"Algolia","link":"https://www.algolia.com","description":"Hosted Search with focus on integration","license":"Saas"},{"name":"Memsql","link":"https://www.memsql.com","description":"Inmem sql","license":""}],"Hadoop Ecosystem":[{"name":"Hbase","link":"https://hbase.apache.org","description":"Distributed Database/Filesystem","license":"Opensource"},{"name":"Cassandra","link":"http://cassandra.apache.org","description":"Distributed database","license":"Opensource"},{"name":"Hive","link":"http://hive.apache.org","description":"Data Warehouse","license":"Opensource"},{"name":"Oozie","link":"http://oozie.apache.org","description":"workflow Scheduler","license":"Opensource"},{"name":"Openstack","link":"https://www.openstack.org","description":"Open source software for creating private and public clouds.","license":"Opensource"},{"name":"Mahout","link":"http://mahout.apache.org","description":"Distributed realtime computation system.","license":"Opensource"},{"name":"Spark","link":"http://spark.apache.org","description":"General engine for large-scale data processing.","license":"Opensource"},{"name":"Hadoop","link":"http://hadoop.apache.org","description":"Distributed Storage and Computation / Map Reduce","license":"Opensource"},{"name":"Redshift","link":"https://aws.amazon.com/de/redshift/","description":"Amazon DWH Solution","license":"Saas"},{"name":"S3","link":"https://aws.amazon.com/de/s3/pricing/","description":"Distributed Storage","license":"Saas"},{"name":"Cloudera","link":"http://www.cloudera.com","description":"Haddop Ecosystem","license":"Saas"},{"name":"Hortonworks","link":"http://hortonworks.com/products/sandbox/","description":"Hadoop on premise or cloud","license":"Saas"}]},"Analysis / ML":{"Deep Learning":[{"name":"Paddle","link":"https://github.com/PaddlePaddle/Paddle","description":"Baidu DL framework","license":""},{"name":"TFLearn","link":"https://github.com/tflearn/tflearn","description":"Highlevel Deeplearning (now part of tensorflow)","license":"Lib"},{"name":"Brainstorm","link":"https://github.com/IDSIA/brainstorm","description":"Sucessor of pybrain","license":"Lib"},{"name":"NeuroJS","link":"https://github.com/janhuenermann/neurojs","description":"JS Deep learning library","license":"Lib"},{"name":"Tensor2Tensor","link":"https://github.com/tensorflow/tensor2tensor","description":"Open-source system for training deep learning models in TensorFlow","license":"Opensource"},{"name":"MobileNet","link":"https://github.com/hollance/MobileNet-CoreML","description":"ML on apple devices","license":"Opensource"},{"name":"Ludwig","link":"https://github.com/uber/ludwig","description":"DL without coding","license":""},{"name":"Nauta","link":"https://github.com/IntelAI/nauta","description":"DL experiment monitoring","license":""},{"name":"Analytics Zoo","link":"https://github.com/intel-analytics/analytics-zoo","description":"DL on Spark","license":""},{"name":"Leaf","link":"https://github.com/autumnai/leaf","description":"Open Machine Intelligence Framework","license":"Opensource"},{"name":"Deep Neuroevolution","link":"https://github.com/uber-common/deep-neuroevolution/tree/master/gpu_implementation","description":"Train deep networks much faster ","license":""},{"name":"Magenta","link":"https://github.com/tensorflow/magenta","description":"Deep Learning lib for audio","license":""},{"name":"Pandas-Summary","link":"https://github.com/mouradmourafiq/pandas-summary","description":"An extension to pandas dataframes describe function","license":""},{"name":"Caffee2","link":"https://caffe2.ai","description":"Crossplatform Deeplearning Framework from Facebook","license":"Opensource"},{"name":"Cogntive Kit","link":"https://www.microsoft.com/en-us/cognitive-toolkit/","description":"Deep learning Kit from Microsoft","license":"Opensource"},{"name":"Tensorflow","link":"https://www.tensorflow.org","description":"Googles Lowlevel Deeplearning framework","license":"Opensource"},{"name":"Deeplearning4J","link":"https://deeplearning4j.org","description":"Highlevel Deeplearning Java","license":"Opensource"},{"name":"Torch","link":"http://torch.ch","description":"General Deeplearn lua","license":"Opensource"},{"name":"Theano","link":"http://www.deeplearning.net/software/theano/","description":"Lowlevel Deeplearning on GPUs","license":"Opensource"},{"name":"MXNet","link":"http://mxnet.io","description":"Lightweight deep learning framework","license":"Opensource"},{"name":"Keras","link":"https://keras.io","description":"Highlevel Deeplearning","license":"Lib"},{"name":"Caffee","link":"http://caffe.berkeleyvision.org","description":"Highlevel Deeplearning","license":"Lib"},{"name":"Pybrain","link":"http://pybrain.org","description":"Python Machine Learning Library with focus on NN","license":"Lib"},{"name":"Google ML","link":"https://cloud.google.com/ml/","description":"Hosted Deeplearning Infrastructure ","license":"Saas"},{"name":"Gym","link":"https://gym.openai.com","description":"Reinforcement Learning Framework","license":"Saas"},{"name":"Tensorflow js","link":"https://js.tensorflow.org/","description":"Tensorflow in your browser","license":""},{"name":"Weights \u0026 Biases","link":"https://www.wandb.com","description":"Tracking DL experiments","license":""},{"name":" Verta.ai","link":"https://www.verta.ai","description":"DL model management","license":""},{"name":"MLflow","link":"https://mlflow.org","description":"ML lifecycle","license":""},{"name":"Determined AI","link":"https://determined.ai","description":"DL Platform","license":""},{"name":"Universe","link":"https://universe.openai.com","description":"Benchmark general AI agents","license":"Saas"},{"name":"Wekinator","link":"http://www.wekinator.org","description":"Simply train a DNN for artsy projects","license":""},{"name":"Nanonets","link":"https://nanonets.com/","description":"Pre-trained Models Saas","license":""},{"name":"Epoq","link":"https://www.epoq.de/en/","description":"Recommender as a Service for ecommerce","license":""},{"name":"pytorch","link":"Pytorch","description":"python production DL ","license":null},{"name":"Fastai","link":"https://www.fast.ai","description":"Keras for pytorch","license":null},{"name":"Snorkel","link":"https://www.snorkel.org","description":"Weak supervised learning","license":null}],"Stats Software":[{"name":"Ipython","link":"http://ipython.org","description":"Ipython Notebooks","license":"Opensource"},{"name":"RMarkdown","link":"http://rmarkdown.rstudio.com","description":"Like Ipython Notebooks for R","license":"Opensource"},{"name":"Rattle","link":"http://rattle.togaware.com","description":"Graphical UI for R models","license":"Opensource"},{"name":"Weka","link":"http://www.cs.waikato.ac.nz/ml/weka/","description":"ML industry strength toolkit in java","license":"Opensource"},{"name":"R","link":"https://www.r-project.org","description":"Big opensource stats framefork mainly used in academia","license":"Opensource"},{"name":"Julia","link":"http://julialang.org","description":"Lang for Scientific Comp.","license":"Opensource"},{"name":"Octave","link":"https://www.gnu.org/software/octave/","description":"Like matlab but open source","license":"Opensource"},{"name":"SPSS","link":"https://en.wikipedia.org/wiki/SPSS","description":"IBMs industrial strength stats in java","license":"Saas"},{"name":"SAS","link":"https://en.wikipedia.org/wiki/SAS_(software)","description":"Proprietary stats modeling ","license":"Saas"},{"name":"Matlab","link":"https://www.mathworks.com/products/matlab.html","description":"Industrial strength numerical computing environment ","license":"Saas"},{"name":"Pandas","link":"http://pandas.pydata.org","description":"Easy-to-use data structures and data analysis tools in python","license":"Lib"}],"General (focus python)":[{"name":"Lore","link":"https://github.com/instacart/lore","description":"Maintainable ML approachable for Software Engineers.","license":""},{"name":"Tuber","link":"https://github.com/soodoku/tuber","description":"Youtube Analytics in R","license":"Library"},{"name":"DMTK","link":"https://github.com/microsoft/dmtk","description":"Distributed Machine Learning Toolkit from Microsoft","license":"Lib"},{"name":"Sklearn-Pandas","link":"https://github.com/paulgb/sklearn-pandas","description":"Scikit-Learn for pandas data frames","license":"Lib"},{"name":"Dask-learn","link":"https://github.com/dask/dask-learn","description":"Scikit-Learn parallel computing","license":"Lib"},{"name":"PhpML","link":"https://github.com/php-ai/php-ml","description":"Machine Learning in PHP","license":"Lib"},{"name":"REP","link":"https://github.com/yandex/rep","description":"Ipython Scikit Extension","license":"Lib"},{"name":"XBoost","link":"https://github.com/dmlc/xgboost","description":"Python bindings for eXtreme Gradient Boosting (Tree) Librar","license":"Lib"},{"name":"Nteract","link":"https://github.com/nteract/nteract","description":"Best of jupyter notebooks ","license":""},{"name":"Scrapbook","link":"https://github.com/nteract/scrapbook","description":"Save Jupyter notebook outputs","license":""},{"name":"AutoML","link":"https://github.com/ClimbsRocks/auto_ml","description":"Automated machine learning pipelines for analytics and production","license":"Lib"},{"name":"Hyperopt","link":"https://github.com/hyperopt/hyperopt-sklearn","description":"Automatic Hyperparameter optimization","license":"Lib"},{"name":"Pandas Profiling","link":"https://github.com/JosPolfliet/pandas-profiling","description":"Have a first look at your data in seconds","license":"Lib"},{"name":"NetworkX","link":"https://networkx.github.io","description":"A high-productivity software for complex networks","license":"Lib"},{"name":"Prophet","link":"https://facebookincubator.github.io/prophet/","description":"Time Series forecasting from Facebook","license":"Lib"},{"name":"PyMc3","link":"http://pymc-devs.github.io/pymc3/index.html","description":"Machine Learning Bayesian Modeling","license":"Opensource"},{"name":"automl-gs","link":"https://github.com/minimaxir/automl-gs","description":"CSV to ML","license":null},{"name":"Catboost","link":"https://github.com/catboost/catboost","description":"Open Source gradient boosting machine from Yandex","license":""},{"name":"Lightgbm","link":"https://github.com/Microsoft/LightGBM","description":"Light gradient boosting machine from Microsoft","license":""},{"name":"TPOT","link":"https://github.com/EpistasisLab/tpot","description":"AutoML for Python","license":""},{"name":"Pandas-Overview","link":"https://github.com/conradoqg/pandas-overview","description":"An extension to pandas dataframes describe function","license":""},{"name":"Pandas-Profiling","link":"https://github.com/pandas-profiling/pandas-profiling","description":"Create HTML profiling reports from pandas DataFrame objects","license":""},{"name":"LIME","link":"https://github.com/marcotcr/lime","description":"Explaining the predictions of any machine learning classifier","license":""},{"name":"SHAP","link":"https://github.com/slundberg/shap","description":"A unified approach to explain the output of any machine learning model","license":""},{"name":"Automl-gs","link":"https://github.com/minimaxir/automl-gs","description":"Easy AutoML ","license":""},{"name":"eli5","link":"https://github.com/TeamHG-Memex/eli5","description":"ML Explainer","license":null},{"name":"Lightning","link":"https://github.com/scikit-learn-contrib/lightning","description":"Large-scale linear classification","license":null},{"name":"py-earth","link":"https://github.com/scikit-learn-contrib/py-earth","description":"Piecewise linear ML","license":null},{"name":"imbalanced-learn","link":"https://github.com/scikit-learn-contrib/imbalanced-learn","description":"Imbalanced Learn techniques","license":null},{"name":"Nbdime","link":"https://github.com/jupyter/nbdime","description":"Git Merge Jupyter notebooks","license":null},{"name":"Aerosolve","link":"http://airbnb.io/projects/aerosolve/","description":"A human friendly machine learning library by Airbnb.","license":"Opensource"},{"name":"Unplugg","link":"http://unplu.gg/","description":"Time Series Prediction","license":"Opensource"},{"name":"Shogun","link":"http://shogun.ml/examples/latest/index.html#","description":"Machine Learning for C++","license":"Opensource"},{"name":"Anodot","link":"https://www.anodot.com/","description":"Anomaly detection","license":""},{"name":"Papermill","link":"https://papermill.readthedocs.io/en/latest/","description":"Parametrize jupyter notebooks","license":""},{"name":"Scikit Learn","link":"http://scikit-learn.org/stable/","description":" A Python module for machine learning built on top of SciPy.","license":"Lib"},{"name":"Dlib","link":"http://dlib.net","description":"Like Scikit Learn but for C","license":"Lib"},{"name":"Dask","link":"http://dask.pydata.org/en/latest/","description":"Parallel Computing for Python","license":"Lib"},{"name":"Scipy","link":"https://www.scipy.org","description":"Python framework for mathematics, science, and engineering.","license":"Lib"},{"name":"Numpy","link":"http://www.numpy.org","description":"A fundamental package for scientific computing with Python.","license":"Lib"},{"name":"Statsmodels","link":"http://statsmodels.sourceforge.net/devel/","description":"Statistical modeling and econometrics in Python.","license":"Lib"},{"name":"Algorithmia","link":"https://algorithmia.com/algorithms","description":"ML Algorithms as a marketplace","license":"Saas"},{"name":"xgboost","link":"https://xgboost.readthedocs.io/en/latest/","description":"Fast optimized ML","license":null},{"name":"JS-Recommender","link":"https://www.npmjs.com/package/js-recommender","description":"Recommender in JS","license":""},{"name":"Featuretools","link":"https://www.featuretools.com","description":"Automated Feature Generation for Pandas","license":""}],"Assistant":[{"name":"Lyrebird","link":"http://lyrebird.ai","description":"Voice synth from samples ","license":""},{"name":"Tada","link":"https://tada.ai","description":"AI Assistant for Google Analytics","license":"Saas"},{"name":"Statsbot","link":"http://statsbot.co","description":"AI Assistant for Google Analytics","license":"Saas"},{"name":"Kitt.ai","link":"http://kitt.ai","description":"NLU / Chatflow ","license":""}],"Computer Vision":[{"name":"Openface","link":"http://cmusatyalab.github.io/openface/","description":"State of the art open source face detection","license":""},{"name":"Facenet","link":"https://github.com/davidsandberg/facenet","description":"Deep Learning face detection","license":""},{"name":"VOTT","link":"https://github.com/Microsoft/VoTT/blob/master/README.md","description":"Visual Tagging for CV","license":""},{"name":"Video Intelligence","link":"https://cloud.google.com/video-intelligence/","description":"Video Intelligence","license":"Saas"},{"name":"SciKit Image","link":"http://scikit-image.org","description":"A collection of algorithms for image processing in Python","license":"Lib"},{"name":"Google Computer Vision","link":"https://cloud.google.com/vision/","description":"Saas for Image recognition","license":"Saas"},{"name":"IBM CV","link":"http://www.ibm.com/watson/developercloud/visual-recognition.html","description":"CV from IBM","license":"Saas"},{"name":"SimpleCV","link":"http://simplecv.org","description":"Framework that gives access to OpenCV. ","license":"Lib"},{"name":"Clarifai","link":"https://www.clarifai.com","description":"Saas for Image recognition","license":"Saas"},{"name":"Microsoft Computer Vision","link":"https://www.microsoft.com/cognitive-services/en-us/computer-vision-api","description":"Saas for Image recognition","license":"Saas"},{"name":"Diffbot","link":"https://www.diffbot.com","description":"Saas for Image recognition","license":"Saas"},{"name":"Kairos","link":"https://www.kairos.com/features","description":"Saas for Image recognition","license":"Saas"}],"NLP":[{"name":"CoreNLP","link":"http://stanfordnlp.github.io/CoreNLP/","description":"Integrated NLP Toolkit","license":"Lib "},{"name":"SAGA","link":"https://github.com/gsi-upm/SAGA","description":"GATE Sentiment plugin","license":""},{"name":"SEAS","link":"https://github.com/gsi-upm/SEAS/tree/master/gate.sa.modules","description":"GATE Sentiment plugin","license":""},{"name":"LDAjs","link":"https://github.com/primaryobjects/lda","description":"Topic Modeling","license":"Lib "},{"name":"FuzzyWuzzy","link":"https://github.com/seatgeek/fuzzywuzzy","description":"Fuzzy Stringmatching in Ruby","license":"Lib "},{"name":"Natural.js","link":"https://github.com/NaturalNode/natural","description":"General Language utilities for node","license":"Lib "},{"name":"Thinc","link":"https://github.com/explosion/thinc","description":null,"license":"Lib "},{"name":"DeepSpeech","link":"https://github.com/mozilla/DeepSpeech","description":"Voice Recognition without the Middle Man","license":"Lib"},{"name":"Vader","link":"https://github.com/cjhutto/vaderSentiment","description":"Sentiment analyzer","license":null},{"name":"OpenNLP","link":"https://opennlp.apache.org","description":"Open NLP Toolkit from Apache with bindings","license":"Opensource"},{"name":"Python NLTK","link":"http://www.nltk.org","description":"Lib for text processing in Python ","license":"Lib "},{"name":"Spacy","link":"https://spacy.io","description":"Industrial strength NLP with Python ","license":"Saas"},{"name":"Pattern","link":"http://www.clips.ua.ac.be/pattern","description":"Pattern recognition package in Go lang","license":"Lib "},{"name":"Lexalitics","link":"https://www.lexalytics.com","description":"NLP as  a Service","license":"Saas/Lib "},{"name":"OpenCalais","link":"http://opencalais.com","description":"Named Entities from Text","license":"Saas"},{"name":"Cortical","link":"http://www.cortical.io","description":"Retina: an Saas performing complex NLP operations ","license":"Saas"},{"name":"Monkeylearn","link":"http://monkeylearn.com","description":"NLP as a Service","license":"Saas"},{"name":"GATE","link":"https://gate.ac.uk/sentiment/","description":"General architecture for text engineering","license":""},{"name":"Comprehend","link":"https://aws.amazon.com/de/comprehend/","description":"NLP from Amazon Saas","license":""},{"name":"Azure Text Analytics","link":"https://azure.microsoft.com/en-us/services/cognitive-services/text-analytics/","description":"Microsoft Text Analytics","license":""},{"name":"TextBlob","link":"http://textblob.readthedocs.io/en/dev/","description":"Simplified text processing","license":""},{"name":"Prodigy","link":"https://prodi.gy/docs/video-insults-classifier","description":"Make training and anotation super simple for texts","license":"Lib "},{"name":"Texacy","link":"http://textacy.readthedocs.io/en/latest/","description":"Highlevel Spacy","license":"Lib "},{"name":"Gensim","link":"http://radimrehurek.com/gensim/","description":"Topic Modeling","license":"Lib "},{"name":"TM","link":"http://tm.r-forge.r-project.org","description":"Text mining for R","license":"Lib "},{"name":"Google NLP","link":"https://cloud.google.com/natural-language/","description":"NLP Deep learning Models from google","license":"Saas"},{"name":"Aylen","link":"http://aylien.com","description":"Full Service NLP ","license":"Saas"},{"name":"AssemblyAI","link":"https://www.assemblyai.com/","description":"Customizable Speech recognition","license":"Lib "},{"name":"Arria","link":"https://www.arria.com","description":"Natural Language Generation","license":"Saas"},{"name":"Spark NLP","link":"https://nlp.johnsnowlabs.com","description":"Production ready NLP","license":""},{"name":"Tone","link":"https://www.ibm.com/watson/services/tone-analyzer/","description":"IMBs tone analyzer","license":""},{"name":"Einstein","link":"https://elements.heroku.com/addons/einstein-vision","description":"NLP and image recognition on heroku","license":""},{"name":"Dandelion","link":"https://dandelion.eu/","description":"NLP Saas","license":null}],"ChatBots Framework":[{"name":"Rasa","link":"https://github.com/RasaHQ/rasa_nlu","description":"Turn natural language into structured data ","license":""},{"name":"P-Brain","link":"https://github.com/patrickjquinn/P-Brain.ai","description":"Natural Language for Bots","license":"Lib"},{"name":"Botpress","link":"http://botpress.io","description":"Open Source Framwork for Bots","license":"Opensource"},{"name":"Telegram Bot","link":"https://telegram.org/blog/bot-revolution","description":"Bot Framework for Telegram","license":"Opensource"},{"name":"Botframework","link":"https://dev.botframework.com","description":"Microsoft Bot Framework","license":"Saas"},{"name":"Snowbotty","link":"https://snowboy.kitt.ai","description":"Voice recognition that runs on raspberry pi.","license":"Saas"},{"name":"Recast","link":"https://recast.ai","description":"Collaborative Bot creation","license":"Saas"},{"name":"Howdy","link":"https://howdy.ai/botkit/","description":"Open Source Bot Kit","license":"Lib"},{"name":"Chatfuel","link":"https://chatfuel.com","description":"Build Chatbots without Coding for Facebook","license":"Saas"},{"name":"Lex","link":"https://stackshare.io/amazon-lex","description":"Amazon Echo Lex Library","license":"Saas"},{"name":"Aiva","link":"http://kengz.me/aiva/","description":"General-purpose virtual assistant for developers","license":"Lib"},{"name":"WitAI","link":"https://wit.ai","description":"Natural Language for Bots","license":"Saas"},{"name":"Api.ai","link":"https://api.ai","description":"Natural Language for Bots","license":"Saas"},{"name":"Dialogflow","link":"https://dialogflow.com","description":"Google's Conversational Modeling Engine","license":""},{"name":"Stealth","link":"https://hellostealth.org","description":"Open Source ruby framework","license":""},{"name":"Pandorabots","link":"https://home.pandorabots.com/home.html","description":"Chatbots Saas","license":""},{"name":"botkit","link":"https://botkit.ai","description":"Building Blocks for Chatbots","license":""}],"Speech":[{"name":"Jasper","link":"https://jasperproject.github.io","description":"Opensource voice lib","license":""},{"name":"Speech-Recognition-Tensorflow","link":"https://github.com/thomasschmied/Speech_Recognition_with_Tensorflow","description":"Open Source Listen-Attend-Spell implementation","license":""},{"name":"ESpeak-NG","link":"https://github.com/espeak-ng/espeak-ng/","description":"Open Source speech synthesis for 102 languages","license":""},{"name":"Spitch","link":"https://www.spitch.ch","description":"Swiss ASR provider","license":""},{"name":"Snowboy","link":"https://snowboy.kitt.ai","description":"Custom Wakeup word","license":""},{"name":"OpenSTT","link":"https://openstt.org","description":"Initiative for opensource STT","license":""},{"name":"Speech Recognition","link":"https://pypi.org/project/SpeechRecognition/","description":"Meta-lib for python","license":""},{"name":"Amazon Polly","link":"https://console.aws.amazon.com/polly/home/SynthesizeSpeech","description":"TTS from Amazon","license":""},{"name":"Bing Speech ","link":"https://azure.microsoft.com/en-us/services/cognitive-services/speech/","description":"Speech API from Bing","license":""},{"name":"Google TTS","link":"https://cloud.google.com/text-to-speech/","description":"Deep learning TTS from Google","license":""},{"name":"FreeTTs","link":"https://freetts.sourceforge.io/docs/index.php","description":"Open source speech synthesis in Java","license":""},{"name":"Slowsoft","link":"https://slowsoft.ch/deu/","description":"Speech synthetisis for swiss german","license":""}]},"Visualization / Dashboard":{"General":[{"name":"Datamaps","link":"http://datamaps.github.io","description":"SVG Map visualization","license":"Lib"},{"name":"Glue","link":"https://github.com/glue-viz/glue","description":"Linked Data viz in python","license":"Lib"},{"name":"Altair","link":"https://altair-viz.github.io","description":"Vegalite for Python","license":"Lib"},{"name":"Britecharts","link":"https://eventbrite.github.io/britecharts/","description":"Charting Lib from Eventbrite","license":"Lib"},{"name":"Folium","link":"https://github.com/python-visualization/folium","description":"Python Map visualization with leafletjs","license":"Opensource"},{"name":"Bqplot","link":"https://github.com/bloomberg/bqplot","description":"Plotting library for Jupyter Notebooks","license":null},{"name":"Deck.gl","link":"http://uber.github.io/deck.gl/#/","description":"WebGL visualization for big data","license":""},{"name":"SQL Pad","link":"http://rickbergfalk.github.io/sqlpad/","description":"Visualize SQL in your browser","license":""},{"name":"Gephi","link":"http://gephi.org","description":"Network Visualization","license":"Opensource"},{"name":"Knitr","link":"https://yihui.name/knitr/","description":"Reports for R","license":"Opensource"},{"name":"Datawrapper","link":"https://www.datawrapper.de","description":"Focus on embedding and responsiveness in js","license":"Saas/Opensource"},{"name":"Anychart","link":"http://www.anychart.com","description":"Robust js lib","license":"Saas/Opensource"},{"name":"Chartblocks","link":"http://www.chartblocks.com/en/","description":"Simple chart creator ","license":"Saas/Opensource"},{"name":"Zeppelin","link":"http://zeppelin.apache.org","description":"Crosslanguage Interactive Viz Notebook","license":"Opensource"},{"name":"Shiny","link":"http://shiny.rstudio.com/","description":"Visualization of R models","license":"Saas/Opensource"},{"name":"Stratifyd","link":"http://stratifyd.com","description":"Dashboards with AI","license":""},{"name":"GGPlot","link":"http://ggplot2.org","description":"For R","license":"Lib"},{"name":"Matplotlib","link":"http://matplotlib.org","description":"General Purpose Lib","license":"Lib"},{"name":"Bookeh","link":"http://bokeh.pydata.org/en/latest/","description":"Sophisticated python lib","license":"Lib"},{"name":"Seaborn","link":"http://seaborn.pydata.org","description":"Sophisticated python lib","license":"Lib"},{"name":"Bokeh","link":"http://bokeh.pydata.org","description":"Visualization Lib for Python","license":""},{"name":"Linkurious","link":"http://linkurio.us","description":"Visualize Network Data online","license":"Saas"},{"name":"Fnordmetric","link":"http://fnordmetric.io","description":"Charts from SQL","license":"Lib"},{"name":"DataShader","link":"http://datashader.readthedocs.io/en/latest/","description":"Visualization for big data","license":"Lib"},{"name":"Mapbox","link":"https://www.mapbox.com","description":"Maps Visualization online","license":"Saas"},{"name":"Visage","link":"https://visage.co","description":"Proprietary vis Saas","license":""},{"name":"Processing","link":"https://processing.org","description":"Procedural visuals","license":""},{"name":"I want hue","link":"http://tools.medialab.sciences-po.fr/iwanthue/","description":"Color Selector","license":""},{"name":"Google Fusion Tables","link":"https://support.google.com/fusiontables/answer/2571232","description":"Combine GTables into one viz","license":""},{"name":"Data Graph","link":"http://www.visualdatatools.com/DataGraph/","description":"Proprietary for mac ","license":""},{"name":"Google Charts","link":"https://developers.google.com/chart/interactive/docs/gallery","description":"Golden classic","license":"Saas"},{"name":"Raw","link":"http://app.raw.densitydesign.org/#/","description":"Rather esoteric stuff but cool","license":"Saas"},{"name":"Nodebox","link":"https://www.nodebox.net","description":"Procedural visuals","license":""},{"name":"Cytoscape","link":"http://www.cytoscape.org","description":"Network visualization tool","license":""},{"name":"Carto","link":"https://carto.com","description":"Map based platform","license":""},{"name":"Circos ","link":"http://circos.ca","description":"Circle based visualisations","license":""},{"name":"QTools","link":"https://q.tools","description":"Easy suite to create viz without programming","license":""},{"name":"Panopticon","link":"http://www.panopticon.com","description":"Viz for traders","license":""},{"name":"Flourish Studio","link":"https://flourish.studio/pricing/","description":"Great animated visualisations","license":""},{"name":"iNZight","link":"https://www.stat.auckland.ac.nz/~wild/iNZight/index.php","description":"Open source tool for automatic visualisation","license":""},{"name":"DataWrapper","link":"https://www.datawrapper.de","description":"Viz without coding","license":""},{"name":"Pylustrator","link":"https://pylustrator.readthedocs.io/en/latest/","description":"Matplotlib gui","license":null}],"Dashboards":[{"name":"JsonDash","link":"https://github.com/christabor/flask_jsondash","description":"Make Dashboards with Flask and JSON","license":"Lib"},{"name":"ReDash","link":"https://redash.io","description":"Dashboard with Analytics","license":"Opensource/Saas"},{"name":"Vida","link":"https://vida.io","description":"Flexible dashboard","license":"Opensource/Saas"},{"name":"Screenly","link":"https://www.screenly.io","description":"Manage multiple dashboards","license":"Opensource/Saas"},{"name":"Plotly","link":"https://plot.ly","description":"Dashboards wit a lot of Bindings","license":"Opensource/Saas"},{"name":"Grafana","link":"http://grafana.org","description":"Good greping support, ELK stack competitor","license":"Opensource"},{"name":"Mozaik","link":"http://mozaik.rocks","description":"Modular modern dashboard","license":""},{"name":"Dashing","link":"http://dashing.io","description":"Sinatra based framework with realtime","license":"Lib"},{"name":"Freeboard","link":"http://freeboard.io","description":"Dashboard for IoT","license":"Saas"},{"name":"Keen","link":"https://keen.io","description":"Dashboard and Analytics","license":"Saas"},{"name":"Geckoboard","link":"https://www.geckoboard.com","description":"Dashboards for TVs","license":"Saas"},{"name":"Telemetry","link":"https://www.telemetrytv.com/dashboards/","description":"Dashboards for TVs","license":"Saas"},{"name":"Klipfolio","link":"https://www.klipfolio.com","description":"Easy to use dashboard","license":"Saas"},{"name":"Supermetrics","link":"https://supermetrics.com/product/supermetrics-for-google-drive/","description":"Metrics on Google Drive","license":"Saas"},{"name":"DisplayR","link":"https://www.displayr.com/pricing/","description":"R Dashboards","license":"Saas"},{"name":"Quadrigram","link":"http://www.quadrigram.com","description":"Visualizations without coding","license":""},{"name":"Tableau Public","link":"https://public.tableau.com/s/","description":"Build dashboards with Tableau for web","license":""},{"name":"Infogram","link":"https://infogram.com/","description":"Create easy visualisations online","license":""}],"Javascript":[{"name":"Cubism","link":"http://square.github.io/cubism/","description":"Time series viz in js","license":"Lib"},{"name":"Vega","link":"https://vega.github.io/vega-lite/","description":"Declarative Viz in js","license":"Lib"},{"name":"Odyssey","link":"http://cartodb.github.io/odyssey.js/","description":"Stories visualization in js","license":"Lib"},{"name":"DC.js","link":"https://dc-js.github.io/dc.js/","description":"Multi Dimensional Charting","license":"Opensource"},{"name":"Crossfilter","link":"http://crossfilter.github.io/crossfilter/","description":"Multi Dimensional Filtering","license":"Opensource"},{"name":"Peity","link":"http://benpickles.github.io/peity/","description":"Sparklines for the web","license":""},{"name":"InfoVis","link":"https://github.com/philogb/jit","description":"Older js vis framework","license":""},{"name":"Candela","link":"https://github.com/Kitware/candela","description":"Framework for interoperable, reusable visualization","license":""},{"name":"Chartist","link":"https://gionkunz.github.io/chartist-js/","description":"Responsive js viz","license":""},{"name":"Leafletjs","link":"http://leafletjs.com","description":"js lib for map visualization","license":"Opensource"},{"name":"Variancecharts","link":"http://variancecharts.com","description":"Like GGplot for js","license":"Saas/Opensource"},{"name":"Amcharts","link":"https://www.amcharts.com","description":"Fancy js viz","license":"Saas/Opensource"},{"name":"Timeline","link":"http://timeline.knightlab.com","description":"Timeline viz in js","license":"Saas/Opensource"},{"name":"Cytoscape js","link":"http://js.cytoscape.org","description":"Like Cytoscape but in js","license":""},{"name":"Fancygrid","link":"https://fancygrid.com","description":"Like Datatables","license":""},{"name":"D3","link":"https://d3js.org","description":"General very exensible JS lib","license":"Lib"},{"name":"NVD3","link":"http://nvd3.org","description":"Highlevel D3","license":"Lib"},{"name":"Chartjs","link":"http://www.chartjs.org","description":"Easy to use js lib","license":"Lib"},{"name":"Sigma","link":"http://sigmajs.org","description":"Network Viz in js","license":"Lib"},{"name":"Gatherplot","link":"http://www.gatherplot.org","description":"Gatherplots in js","license":"Lib"},{"name":"HighCharts","link":"http://www.highcharts.com","description":"Industry strength js viz","license":"Lib"},{"name":"Gojs","link":"http://gojs.net/latest/index.html","description":"Interactive JS visualizations","license":"Lib"},{"name":"Tangle","link":"http://worrydream.com/Tangle/","description":"Interactive HTML exploration","license":""},{"name":"Paperjs","link":"http://paperjs.org/examples/","description":"Experimental js vis","license":""},{"name":"Kartograph","link":"http://kartograph.org","description":"Lightweight beautiful maps","license":""},{"name":"Arbor.js","link":"http://arborjs.org","description":"Graph layout with jquery","license":""},{"name":"Cola.js","link":"http://ialab.it.monash.edu/webcola/","description":"Constrained-based layout for web","license":""},{"name":"Processing.js","link":"http://processingjs.org","description":"Procedural vis for js","license":""},{"name":"Zingchart","link":"https://www.zingchart.com","description":"Lib for multiple charts","license":""},{"name":"Rickshaw","link":"http://code.shutterstock.com/rickshaw/","description":"Interactive time series with js","license":""},{"name":"Recline","link":"http://okfnlabs.org/recline/","description":"Data vis with D3 made easy","license":""},{"name":"Polymaps","link":"http://polymaps.org","description":"Older js map vis","license":""},{"name":"Envision.js","link":"http://www.humblesoftware.com/envision","description":"Fast dynamic HTML charting","license":""},{"name":"Kitware","link":"https://www.kitware.com","description":"3D Elevation platform","license":""},{"name":"Highcharts Cloud","link":"https://cloud.highcharts.com/","description":"Highcharts viz without installation","license":""},{"name":"dygraphs","link":"http://dygraphs.com","description":"Fast, flexible open source JavaScript charting library","license":""},{"name":"Charted","link":"https://www.charted.co","description":"Simplest viz ever","license":""},{"name":"Observablehq","link":"https://observablehq.com","description":"D3 and Notebooks in One","license":""},{"name":"eCharts","link":"https://echarts.apache.org/en/index.html","description":"An open-sourced JavaScript visualization tool developed by Baidu.","license":null}]},"Business Intelligence":{"Business Intelligence":[{"name":"OpenMining","link":"https://github.com/mining/mining","description":"BI in Python Notebooks","license":"Opensource"},{"name":"Blazer","link":"https://github.com/ankane/blazer","description":"Simple SQL to Graph ","license":"Opensource"},{"name":"Bdash","link":"https://github.com/bdash-app/bdash","description":"Simple Mac BI application","license":"Opensource"},{"name":"Kibana","link":"https://www.elastic.co/products/kibana","description":"Fast Moving BI on top of elastic","license":"Opensource"},{"name":"Airpal","link":"http://airbnb.io/projects/airpal/","description":"BI from airbnb","license":"Opensource"},{"name":"Metabase","link":"http://www.metabase.com","description":"Easy to fork and extend","license":"Saas/Opensource"},{"name":"Qlik","link":"http://qlik.com","description":"Highly customizatble BI","license":"Saas/Opensource"},{"name":"Superset","link":"http://airbnb.io/projects/superset/","description":"Data Exploration Platform","license":"Opensource"},{"name":"Roambi","link":"https://www.sap.com/products/roambi.html","description":"SAP Mobile BI ","license":""},{"name":"Tamr","link":"http://www.tamr.com","description":"AI for BI ","license":"Saas"},{"name":"IBM Cognos","link":"https://en.wikipedia.org/wiki/Cognos","description":"BI by IBM","license":"Saas"},{"name":"Oracle BI","link":"https://www.oracle.com/solutions/business-analytics/business-intelligence/index.html","description":"Integrated BI","license":"Saas"},{"name":"SAP BI","link":"http://www.sap.com/solution/platform-technology/analytics/business-intelligence-bi.html","description":"Integrated BI","license":"Saas"},{"name":"PowerBI","link":"https://powerbi.microsoft.com/de-de/","description":"Highly Integrated BI","license":"Saas"},{"name":"Tableau","link":"http://www.tableau.com","description":"Industry standard visualization/analytics","license":"Saas"},{"name":"ChartIO","link":"https://chartio.com","description":"Easy to use BI","license":"Saas"},{"name":"Sisense","link":"http://sisense.com","description":"Easy to use inmem BI ","license":"Saas"},{"name":"Pentaho","link":"http://community.pentaho.com","description":"Integrated BI","license":"Saas"},{"name":"Looker","link":"https://looker.com","description":"Fancy BI platform","license":"Saas"},{"name":"Spotfire","link":"http://spotfire.tibco.com","description":"Data Viz and Analytics","license":"Saas"},{"name":"Micro Stratetegy","link":"http://microstrategy.com","description":"Integrated BI","license":"Saas"},{"name":"SAS Visual Analytics","link":"http://www.sas.com/en_us/software/business-intelligence/visual-analytics.html","description":"Like Tableau from SAS","license":"Saas"},{"name":"Interana","link":"https://www.interana.com","description":"Interactive Behavior analytics","license":"Saas"},{"name":"Cluvio","link":"https://www.cluvio.com/","description":"Cloud Analytics with R","license":"Saas"},{"name":"Quicksight","link":"https://quicksight.aws","description":"Cheap Cloud BI from Amazon","license":"Saas"},{"name":"Cartodb","link":"https://carto.com/","description":"BI for Maps Data","license":"Saas"},{"name":"Quoble","link":"https://www.qubole.com","description":"Integrated BIgData Analytics","license":"Saas"},{"name":"Opentext","link":"http://www.opentext.com","description":"BI focused on Oracle stack","license":"Saas"},{"name":"Logi Analytics","link":"https://www.logianalytics.com","description":"BI with aspect on Integration","license":"Saas"},{"name":"Yellow Fin","link":"https://www.yellowfinbi.com","description":"Easy to start BI","license":"Saas"},{"name":"Domo","link":"https://www.domo.com","description":"BI with focus on realtime","license":"Saas"},{"name":"Good Data","link":"https://www.gooddata.com","description":"Fortune 500 BI","license":"Saas"},{"name":"Dundas","link":"http://www.dundas.com","description":"BI with focus on Flexibility","license":"Saas"},{"name":"Jedox","link":"http://www.jedox.com/de/","description":"Excel like BI","license":"Saas"},{"name":"Dimensional Insight","link":"http://www.dimins.com","description":"Integrated BI","license":"Saas"},{"name":"Tibco","link":"http://www.tibco.com","description":"Integrated BI","license":"Saas"},{"name":"Birst","link":"https://www.birst.com","description":"Integrated BI","license":"Saas"},{"name":"BIME","link":"https://www.bimeanalytics.com","description":"BI with quite a lot of connectors","license":"Saas"},{"name":"1010Data","link":"https://1010data.com","description":"Integrated BI","license":"Saas"},{"name":"Adaptive Insights","link":"http://www.adaptiveinsights.com","description":"BI with focus on Finance","license":"Saas"},{"name":"Rosslyn Analytics","link":"http://www.rosslynanalytics.com","description":"Automated BI","license":"Saas"},{"name":"PeriscopeData","link":"https://www.periscopedata.com","description":"BI with focus on SQL queries","license":"Saas"},{"name":"Excel ","link":"https://en.wikipedia.org/wiki/Microsoft_Excel","description":"Great for prototyping ideas","license":"Saas/$"},{"name":"Excel Powerpivot","link":"http://www.powerpivotpro.com/get-the-software/","description":"Pivot Tables in Excel","license":"Saas"},{"name":"Pyramid Analytics","link":"http://go.pyramidanalytics.com","description":"Classic BI","license":"Saas"},{"name":"Information Builders","link":"http://www.informationbuilders.com","description":"BI with desktop UI","license":"Saas"},{"name":"SAP Analytics Cloud","link":"https://www.sapanalytics.cloud/","description":"Business Analytics by SAP","license":""}],"BI on Hadoop":[{"name":"Arcadia Data","link":"https://www.arcadiadata.com","description":"BI on Hadoop","license":"Saas"},{"name":"Datameer","link":"https://www.datameer.com","description":"BI on Hadoop","license":"Saas"},{"name":"Kyvos Insights","link":"http://www.kyvosinsights.com","description":"BI on Hadoop","license":"Saas"},{"name":"Attivio","link":"https://www.attivio.com","description":"BI on Hadoop","license":"Saas"},{"name":"Zoomdata","link":"https://www.zoomdata.com","description":"BI on Hadoop","license":"Saas"}],"Data Science Platforms":[{"name":"Hue","link":"https://github.com/cloudera/hue","description":"Cloudera Hue solution for haddop stack","license":"Opensource"},{"name":"Rapidminer","link":"https://rapidminer.com","description":"Java Data Modeling and Prediction","license":"Opensource"},{"name":"Orange","link":"http://orange.biolab.si","description":"Data Modeling and prediction","license":"Opensource"},{"name":"Graphlab","link":"https://turi.com","description":"Integrated Datascience","license":"Saas/Opensource"},{"name":"Knime","link":"https://www.knime.org","description":"BI for Datascientists","license":"Saas/Opensource"},{"name":"Azure Studio","link":"https://azure.microsoft.com/en-us/services/machine-learning/","description":"Click and Play Machine Learning Models","license":"Saas"},{"name":"Angoss","link":"http://www.angoss.com/predictive-analytics-software/software/knowledgestudio/","description":"Integrated Visual Platform","license":""},{"name":"Alpine Data","link":"http://alpinedata.com/product/","description":"ML, BigData in one platform","license":""},{"name":"Alteryx","link":"https://www.alteryx.com","description":"Leading Data Science platform","license":""},{"name":"TransmogrifAI","link":"https://transmogrif.ai","description":"AutoML Platform","license":""},{"name":"Kubeflow","link":"https://www.kubeflow.org","description":"DL on Kubernetes","license":""},{"name":"Auger.ai","link":"https://auger.ai","description":"Automated ML","license":""},{"name":"Tazi","link":"https://www.tazi.ai","description":"AI platform","license":""},{"name":"Modulos","link":"http://www.modulos.ai/","description":"Machine learning platform","license":""},{"name":"Datarobot","link":"https://www.datarobot.com","description":"Integrated Datascience","license":"Saas"},{"name":"Dominolab","link":"https://www.dominodatalab.com","description":"Integrated Datascience","license":"Saas"},{"name":"Yhat","link":"https://www.yhat.com","description":"Model deployment","license":"Saas"},{"name":"Modeanalytics","link":"https://modeanalytics.com","description":"Integrated Datascience","license":"Saas"},{"name":"Dataiku","link":"http://www.dataiku.com","description":"Integrated Datascience","license":"Saas"},{"name":"Continuum","link":"https://www.continuum.io","description":"Anaconda Datascience Suite","license":"Saas"},{"name":"Snowplow","link":"http://snowplowanalytics.com","description":"Integrated Event analysis","license":"Saas"},{"name":"Databricks","link":"https://databricks.com","description":"Unified analytics platform","license":""},{"name":"BigMl","link":"https://bigml.com","description":"Machine Learning Platform","license":"Saas"},{"name":"Siftscience","link":"https://siftscience.com","description":"Fraud detection system","license":"Saas"},{"name":"Windsor","link":"https://www.windsor.ai","description":"Integration of multiple sources for marketing with viz.","license":"Saas"},{"name":"SigOpt","link":"https://sigopt.com/industries/datascience","description":"Auto Hyperparameter tuning ML platform","license":"Saas"},{"name":"Datascience.com","link":"https://www.datascience.com","description":"Enterprise data science platform","license":""},{"name":"H2O","link":"https://www.h2o.ai","description":"Leading DS platform","license":""}]}}


TECH_STACK = []

for key in tech_stack.keys():
    for subject, techs in tech_stack[key].items():
        for tech in techs:
            TECH_STACK.append(tech['name'])
#             print(key, subject, tech['name'])


OCEANS = {
    'Openness':['Created','Changed', 'Researched', 'Improved',],
    'Conscientiousness': ['Managed', 'Achieved', 'Solved', 'Saved', 'Regulated', 'Tech_stack',],
    'Extraversion': ['Led', 'Communicated', 'Networked', 'Buzz',],
    'Agreebleness': ['Collaborated', 'Supported',],
    'Neurotism': ['Stressed',],
    'Self': ['Self',]
    }

# The Nine Enneagram Type Descriptions
ENNEAGRAM = {
            'REFORMER': ['Improved', 'Changed', 'Regulated',],
            # The Rational, Idealistic Type: Principled, Purposeful, Self-Controlled, and Perfectionistic

            'HELPER': ['Collaborated', ],
            # The Caring, Interpersonal Type: Demonstrative, Generous, People-Pleasing, and Possessive

            'ACHIEVER': ['Achieved', 'Result_driven', 'Solved',],
            # The Success-Oriented, Pragmatic Type: Adaptive, Excelling, Driven, and Image-Conscious

            'INDIVIDUALIST': ['Self', 'Tech_stack',],
            # The Sensitive, Withdrawn Type: Expressive, Dramatic, Self-Absorbed, and Temperamental

            'INVESTIGATOR': ['Created', 'Researched',],
            # The Intense, Cerebral Type: Perceptive, Innovative, Secretive, and Isolated

            'LOYALIST': ['Stressed', 'Saved',],
            # The Committed, Security-Oriented Type: Engaging, Responsible, Anxious, and Suspicious

            'ENTHUSIAST': ['Communicated', 'Buzz',],
            # The Busy, Fun-Loving Type: Spontaneous, Versatile, Distractible, and Scattered

            'CHALLENGER': ['Managed', 'Led',],
            # The Powerful, Dominating Type: Self-Confident, Decisive, Willful, and Confrontational

            'PEACEMAKER': ['Supported', 'Networked',],
            # The Easygoing, Self-Effacing Type: Receptive, Reassuring, Agreeable, and Complacent
            }

# CV headers
HEADERS = ['career', 'skill','competency', 'qualification', 'accomplishment', 'objective', 'summary',
           'education', 'experience', 'course', 'certificate', 'degree', 'interest', 'history',
          'activity', 'affiliation', 'volunteer', 'membership', 'honor', 'involvement',
          'background', 'association', 'training', 'academic', 'internship', 'project', 'program',
          'apprenticeship']
