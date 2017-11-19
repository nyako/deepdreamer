import os
import sys

def run(fn, *args, **kwargs):
  if kwargs.get('pidfile') is None:
    pidfile = "tmp/spawn.%s.pid" % fn.__name__
  else:
    pidfile = kwargs['pidfile']
    del kwargs['pidfile']

  try:
    pid = os.fork()
    if pid > 0:
      # write PID to file, then return
      #print "PID: %d" % pid
      f = open(pidfile, "w")
      f.write(str(pid))
      f.close
      return pid
  except OSError, e:
    print "fork failed: %d (%s)" % (e.errno, e.strerror)
    return -1

  # child process:
  os.setsid()
  os.umask(0)

  fn(*args, **kwargs)

  sys.exit(0)
