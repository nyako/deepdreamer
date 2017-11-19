from threading import Thread
from cStringIO import StringIO
import tensorflow as tf
import dream

graph = tf.get_default_graph()

class Dreamer(Thread):
  def __init__(self, img_file, name):
    self.img_file = img_file
    self.logger = StringIO()
    self.pos = 0
    Thread.__init__(self, group=None, target=None, name=name, args=(), kwargs={})

  def run(self):
    output_path = 'tmp/'+self.name
    print 'output = ' + output_path
    with graph.as_default():
      dream.start(self.img_file, output=output_path, stdout=self.logger)
      self.logger.close()

  def read_logger(self):
    buf = ''
    new_pos = self.logger.tell()
    if self.pos < new_pos:
      buf = self.logger.getvalue()[self.pos:]
      self.pos = new_pos
    return buf

