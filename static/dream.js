var bus = new Vue()

Vue.component('files', {
  template: '<div class="d-flex"><select id="filesDropdown" class="form-control" v-model="selection"><option v-if="loading">Loading...</option><option v-for="file in file_list" v-bind:value="file" >{{ shorten(file) }}</option></select></div>',
  data: function() {
    return {
      loading: true,
      file_list: [],
      selection: '',
    }
  },
  created: function() {
    this.fetchFileList()
  },
  watch: {
    file_list: function(list) {
      var index = Math.round(Math.random() * list.length)
      this.selection = list[index]
    },
    selection: function(val) {
      // load image to container
      bus.$emit('file-selected', val)
    }
  },
  methods: {
    fetchFileList: function() {
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', '/files')
      xhr.onload = function() {
        self.file_list = JSON.parse(xhr.responseText)['files']
        self.loading = false
      }
      xhr.send()
    },
    shorten: function(s) {
      return s.split('/').slice(-2).join('/')
    }
  } // methods
})

Vue.component('logging', {
  template: '<textarea class="form-control" style="height:500px">{{ textdump }}</textarea>',
  props: [ 'id', 'socket' ],
  data: function() {
    return {
      logs: [ /* we start out empty */ ],
      textdump: '',
      is_running: false,
      emitter: null
    }
  },
  watch: {
    id: function(val) {
      if (val) {
        this.is_running = true
        this.logs = ["Let the dream begin!"]
        this.getstats() // kickstart the logging
      }
    },
    logs: function(val) {
      this.textdump = val.filter(function(e){ return e != ''}).join("\n")
      // scroll to bottom of textbox
      this.$el.scrollTop = this.$el.scrollHeight
      
    },
    is_running: function(val) {
      if (val == false) {
        // stop the logging
        clearInterval(this.emitter)
        this.textdump = "Done!"
        bus.$emit('fetch-dream', this.id)
      }
    }
  },
  methods: {
    getstats: function() {
      var self = this
      console.log('initiating stats collection')
      this.emitter = setInterval(function() {
        self.socket.emit('dreamstats', self.id)
      }, 1000) // query every second

      self.socket.on('dreamstats-ack-'+self.id, function(data) {
        //console.log('dreamstats ack', data)
          if (data.alive == false) {
            self.is_running = false
          } else {
            self.logs.push(data.log)
          }
      })
    }
  }
})

Vue.component('preview', {
  template: '<div class="d-flex"><img v-bind:src="url" /></div>',
  props: [ 'socket' ],
  data: function() {
    return { url: '' }
  },
  created: function() {
    var self = this
    bus.$on('file-selected', function(val) {
      self.url = val
    })
    bus.$on('fetch-dream', function(id) {
      self.url = "/fetch/" + id
      console.log('on fetch-dream', self.url)
    })
  }
})

