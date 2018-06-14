# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings
from twisted.enterprise import adbapi
from scrapy import log

settings = get_project_settings() 

class ChemistPipeline(object):
    insert_sql = """insert into chemist (%s) values ( %s )"""    
 
    def __init__(self):    
        dbargs = settings.get('DB_CONNECT')    
        db_server = settings.get('DB_SERVER')    
        dbpool = adbapi.ConnectionPool(db_server, ** dbargs)    
        self.dbpool = dbpool    

    def __del__(self):    
        self.dbpool.close() 
        
    def process_item(self, item, spider):
#        return item
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        guid = self._get_guid(item)

        conn.execute("""SELECT EXISTS(
                SELECT site_chemist_url FROM chemist WHERE site_chemist_url = %s
            )""", (guid,))
        ret = conn.fetchone()[0]
        
        if ret and item['name']:
            conn.execute("""DELETE FROM chemist WHERE site_chemist_url = %s""", (guid,))
        
        keys = item.fields.keys()    
        fields = u','.join(keys)    
        qm = u','.join([u'%s'] * len(keys))    
        sql = self.insert_sql % (fields, qm)  
        data = [item[k] for k in keys]
        self.dbpool.runOperation(sql, data)

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        log.err(failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return item['site_chemist_url']
