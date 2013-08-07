#! /usr/bin/env python

from time import sleep
from jsonrpclib import Server

class EiskaltDCPP(object):

    def __init__(self, host='127.0.0.1', port=3121, path=''):
        url = 'http://%s:%s/%s' % (host, port, path)
        self._http_client = Server(url)

    def getConnectedHubs(self):
        try:
            hub_list = self._http_client.hub.list(separator=';')
        except Exception as e:
            print 'connection error: %s' % str(e)
            return []

        return [hub for hub in hub_list.split(';') if hub != '']

    def getStatus(self):
        try:
            hub_list = self._http_client.hub.list(separator=';')
        except Exception as e:
            return 'connection error: %s' % str(e)

        hubs = [hub for hub in hub_list.split(';') if hub != '']
        if len(hubs) > 0:
            return 'connected'
        return 'not connected to any hubs'

    def getTransfers(self):
        try:
            transfer_list = self._http_client.queue.list()
        except Exception as e:
            print 'connection error:', str(e)
            return None

        transfers = {}
        if transfer_list is not None:
            for item in transfer_list.values():
                transfers[item['Target']] = {
                    'downloaded': item['Downloaded'],
                    'id': item['Target'],
                    'size': item['Size'],
                    'progress': float(item['Downloaded Sort']) / float(item['Size Sort']),
                    'filename': item['Filename'],
                    'status': item['Status']
                }
        return transfers

    def search(self, search_string):
        try:
            self._http_client.search.clear()
            self._http_client.search.send(searchstring=search_string)
        except Exception as e:
            print 'connection error:', str(e)
            return None

        sleep(2.0)

        try:
            result_list = self._http_client.search.getresults()
        except Exception as e:
            print 'connection error:', str(e)
            return None

        if result_list is None:
            result_list = []

        results = {}
        for result in result_list:
            if 'TTH' in result:
                tth = result['TTH']
                if tth not in results:
                    results[tth] = {
                        'count': 1,
                        'size': result['Size'],
                        'filename': result['Filename'],
                        'tth': tth,
                        'realsize': result['Real Size'],
                    }
                results[tth]['count'] += 1
        return results.values()

    def addDownload(self, search_result):
        try:
            self._http_client.queue.add(filename=search_result['filename'], tth=search_result['tth'], size=search_result['realsize'], directory='')
        except Exception as e:
            print 'connection error:', str(e)
            return None

    def removeTransfer(self, target):
        try:
            self._http_client.queue.remove(target=target)
        except Exception as e:
            print 'connection error:', str(e)
            return None


if __name__ == '__main__':
    import pprint
    eiskaltdcpp = EiskaltDCPP()
    pprint.pprint(eiskaltdcpp.getConnectedHubs())
    #pprint.pprint(eiskaltdcpp.search('dexter s08e04'))
