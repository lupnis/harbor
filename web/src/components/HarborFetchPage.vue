<template>
  <div>
    <a id="back" href="/">{{ btnBackCaption }}</a>
    <h1>{{ pageTitle }}</h1>
    <h3>{{ currentText }}: {{ harborLink }} </h3>
    <div class="file-info-container" v-if="fileValid">
        <img :src="getTypeIcon()" alt="no-image" id="file_type_icon">
        <div class="textual-info">
           <p class="file-title">{{fileName}}</p>
           <p>{{ fileSizeIndicator }}: {{ fileSize }}. {{ fileUploadIndicator }} {{ fileUpload }}</p>
        </div>
        <img src="@/assets/images/download.svg" alt="down" id="download" @click="downloadFile()">
    </div>
    <div class="detailed-info" v-if="!fileValid">
        <h2>{{ fetchingText }}</h2>
    </div>
  </div>
</template>
<style scoped>
.detailed-info {
  background-color: #003f3f88;
}
.detailed-info2{
  background-color: #003f3f88;
}
p {
  margin: 0;
  text-align: justify;
  line-height: 1.5em;
  word-wrap: break-word;
}
h1, h3{
    margin-top: 0;
}
.file-info-container {
  background-color: #dae8fccc;
  border: 1px solid #6c8ebf;
  padding: 1em;
  margin: 1em;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 35em;
}

#file_type_icon{
    height:45px;
    max-width: 55px;
}
#download{
    width: 32px;
    height: 32px;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
}
#download:hover,#download:focus{
    background-color: #00000033;
}

.textual-info {
  margin: -1em 1em;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  text-overflow: ellipsis;
  overflow: hidden;
  flex-grow: 1;
}
.file-title {
  font-weight: bold;
}
.textual-info p {
  color: #000;
  line-height: 1.5em;
  margin: 0.2em;
  text-align: start;
  text-overflow: ellipsis;
  overflow: hidden;
}
</style>
<style src="../assets/css/base.css"></style>
<script>
import axios from 'axios'

export default {
  name: 'HarborFetchPage',
  data () {
    return {
      pageTitle: 'littleDrive - Harbor Mode',
      btnBackCaption: '<Back',
      currentText: 'Current Harbor Link',
      harborLink: 'not specified',
      fetchingText: 'Fetching file...',
      fileValid: false,
      fileName: 'no file name',
      fileSizeIndicator: 'Size',
      fileSize: '? KiB',
      fileUploadIndicator: 'Uploaded on',
      fileUpload: '????/??/??'
    }
  },
  created () {
    this.$http.post('http://papit.obelisync.com/api/ticket/get')
      .then(
        resp => {
          this.$cookies.set('ticket', resp.data.data)
          this.loadFile()
        }
      )
      .catch(
        err => {
          this.$cookies.set('err', err.response.data)
          this.$router.push('/error')
        }
      )
  },
  methods: {
    loadFile: function () {
      this.fetchingText = 'Fetching file...'
      this.harborLink = this.$route.query.code.toUpperCase()
      let dictSize = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', '!']
      this.$http.post(`http://papif.obelisync.com/file/download?ticket=${this.$cookies.get('ticket')}&code=${this.harborLink.replaceAll('-', '').toLowerCase()}`)
        .then(resp => {
          this.fileValid = true
          resp = resp.data.data
          this.fileName = decodeURIComponent(resp.file_name)
          let fileSize = resp.size
          for (let i = 0; i < dictSize.length; i++) {
            if (fileSize < 1024.0) {
              fileSize = Math.round(fileSize * 100) / 100 + ' ' + dictSize[i]
              break
            }
            fileSize /= 1024.0
          }
          this.fileSize = fileSize
          this.fileUpload = resp.upload
        })
        .catch(
          err => {
            this.$cookies.set('err', err.response.data)
            this.$router.push('/error')
          }
        )
    },
    getTypeIcon: function () {
      try {
        let suffix = this.fileName.split('.')
        suffix = suffix[suffix.length - 1].toLowerCase()
        return require(`@/assets/images/${suffix}.svg`)
      } catch (error) {
        return require(`@/assets/images/other.svg`)
      }
    },
    downloadFile: async function () {
      const url = `http://papif.obelisync.com/file/download?ticket=${this.$cookies.get('ticket')}&code=${this.harborLink.replaceAll('-', '').toLowerCase()}`
      const resp = await axios({
        method: 'get',
        url: url,
        responseType: 'blob'
      })
      const link = document.createElement('a')
      const blob = new Blob([resp.data])
      link.href = window.URL.createObjectURL(blob)
      link.download = this.fileName
      link.click()
      this.$router.push('/')
    }
  }
}
</script>
