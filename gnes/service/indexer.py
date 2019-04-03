import zmq

from .base import BaseService as BS, Message, ComponentNotLoad, ServiceMode, ServiceError
from ..indexer.base import MultiheadIndexer


class IndexerService(BS):
    def _post_init(self):
        self.indexer = None
        try:
            self.indexer = MultiheadIndexer.load(self.args.dump_path)
            self.logger.info('load an indexer')
        except FileNotFoundError:
            if self.args.mode == ServiceMode.ADD:
                try:
                    self.indexer = MultiheadIndexer.load_yaml(self.args.yaml_path)
                    self.logger.info('load an uninitialized indexer, indexing is needed!')
                except FileNotFoundError:
                    raise ComponentNotLoad
            else:
                raise ComponentNotLoad

    @BS.handler.register(Message.typ_default)
    def _handler_default(self, msg: 'Message', out: 'zmq.Socket'):
        if self.args.mode == ServiceMode.ADD:
            self.indexer.add(*msg.msg_content, head_name='binary_indexer')
        elif self.args.mode == ServiceMode.QUERY:
            self.indexer.query(msg.msg_content, top_k=self.args.top_k)
        else:
            raise ServiceError('unknown service mode: %s' % self.args.mode)

    @BS.handler.register('SENT_ID_MAP')
    def _handler_sent_id(self, msg: 'Message', out: 'zmq.Socket'):
        self.indexer.add(*msg.msg_content, head_name='sent_doc_indexer')

    @BS.handler.register('DOC_ID_MAP')
    def _handler_doc_id(self, msg: 'Message', out: 'zmq.Socket'):
        self.indexer.add(*msg.msg_content, head_name='doc_content_indexer')

    def close(self):
        if self.indexer:
            self.indexer.close()
        super().close()
