import grpc

from etcd3.etcdrpc import rpc_pb2 as etcdrpc
import etcd3.exceptions as exceptions


class Etcd3Client(object):
    def __init__(self, host='localhost', port=2379):
        self.channel = grpc.insecure_channel('{host}:{port}'.format(
            host=host, port=port)
        )
        self.kvstub = etcdrpc.KVStub(self.channel)

    def get(self, key):
        '''
        Get the value of a key from etcd.

        :param key: key in etcd to get
        :returns: value of key
        :rtype: bytes
        '''
        range_request = etcdrpc.RangeRequest()
        range_request.key = key.encode('utf-8')
        range_response = self.kvstub.Range(range_request)

        if range_response.count < 1:
            raise exceptions.KeyNotFoundError(
                'the key "{}" was not found'.format(key))
        else:
            # smells funny - there must be a cleaner way to get the value?
            return range_response.kvs.pop().value

    def get_range(self, start_key, end_key='\0'):
        range_request = etcdrpc.RangeRequest()
        range_request.key = start_key.encode('utf-8')
        range_request.range_end = end_key.encode('utf-8')
        range_response = self.kvstub.Range(range_request)

        if range_response.count < 1:
            raise exceptions.KeyNotFoundError('no keys found')
        else:
            for kv in range_response.kvs:
                yield (kv.key, kv.value)


    def put(self, key, value):
        '''
        Save a value to etcd.

        :param key: key in etcd to set
        :param value: value to set key to
        :type value: bytes
        '''
        put_request = etcdrpc.PutRequest()
        put_request.key = key.encode('utf-8')
        put_request.value = value.encode('utf-8')
        self.kvstub.Put(put_request)

    def delete(self, key):
        delete_request = etcdrpc.DeleteRangeRequest()
        delete_request.key = key.encode('utf-8')
        self.kvstub.DeleteRange(delete_request)

    def compact(self):
        pass


def client():
    '''Return an instance of an Etcd3Client'''
    return Etcd3Client(host='localhost', port=2379)
