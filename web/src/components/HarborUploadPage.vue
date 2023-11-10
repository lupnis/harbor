<template>
<div>
  <div v-if="!uploaded && !uploading">
    <a id="back" href="/">{{ btnBackCaption }}</a>
    <h1>{{ pageTitle }}</h1>
    <div class="file-info-container">
        <img :src="getTypeIcon()" alt="no-image" id="file_type_icon">
        <div class="textual-info">
           <p class="file-title">{{fileName}}</p>
           <p>{{ fileSizeIndicator }}: {{ fileSize }}</p>
        </div>
        <img src="@/assets/images/upload.svg" alt="upload" id="upload" @click="uploadFile()">
        <img src="@/assets/images/remove.svg" alt="drop" id="drop" @click="dropUploaded()">
    </div>
    <p>{{ destroyBeforeText }} <input type="number" id="down_limit" min="1" max="32" value="1" outlined> {{ destroyDownText }}</p>
    <p>{{ destroyBeforeText }} <input type="number" id="day_limit" min="1" max="7" value="7" outlined> {{ destroyDayText }}</p>
    <button id="btn_create" @click="createLink()">{{ btnCreateCaption }}</button>
  </div>
  <div v-if="!uploaded && uploading">
    <a id="back" href="/">{{ btnBackCaption }}</a>
    <h1>{{ pageTitle }}</h1>
    <h2>{{ uploadingText }}</h2>
    <div class="detailed-info">
        <h3> {{ uploadProgress }} %</h3>
    </div>
    <el-progress :percentage="uploadProgress" :text-inside="true" :stroke-width="16" status="success"> </el-progress>
  </div>
  <div v-if="uploaded">
    <a id="back" href="/">{{ btnBackCaption }}</a>
    <h1>{{ pageTitle }}</h1>
    <h2>{{ uploadedText }}</h2>
    <div class="detailed-info">
        <h3> {{ fileCode }}</h3>
    </div>
    <button id="btn_copycode" @click="copyCode()">{{ btnCopyText }}</button>
  </div>
  <div class="invisible">
    <input type="file" id="file_container" @change="updateFile" single>
  </div>
</div>
</template>
<style scoped>
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
  opacity: 1;
}
input[type=number] {
    display: inline;
    background-color: transparent;
    text-decoration: none;
    outline: none;
    border: 1px solid transparent;
    border-bottom: 2px solid #33B5E5;
    padding: 0 0 0 0.5em;
    margin: 0 0.5em;
    width: 4em;
    font-size: 12pt;
}
#btn_create,#btn_copycode {
    width: calc(100% - 1.6em);
}
.detailed-info {
  background-color: #003f3f88;
}
.detailed-info h1 {
  margin: 0;
}
p {
  margin: 0.5em;
  text-align: justify;
  line-height: 1.5em;
  word-wrap: break-word;
}
h1,
h3 {
  margin-top: 0;
}
.file-info-container {
  background-color: #dae8fccc;
  border: 1px solid #6c8ebf;
  padding: 1em;
  margin: 1em;
  display: flex;
  align-items: center;
  max-width: 35em;
}

#file_type_icon {
  height: 45px;
  max-width: 55px;
}
#upload {
  width: 32px;
  height: 32px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
}
#drop {
  width: 32px;
  height: 32px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
}

#upload:hover,
#upload:focus {
  background-color: #00720433;
}
#drop:hover,
#drop:focus {
  background-color: #ec000033;
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
  word-wrap: break-word;
  word-break: break-all;
  overflow: hidden;
}
</style>
<style src="../assets/css/base.css"></style>
<script>
export default {
  name: 'HarborUploadPage',
  data () {
    return {
      pageTitle: 'littleDrive - Harbor Mode',
      btnBackCaption: '<Back',
      fileName: 'No file uploaded',
      fileSizeIndicator: 'Size',
      fileSize: '0 KiB',
      file: null,
      btnCreateCaption: 'Upload and create Harbor Link',
      selected: false,
      uploaded: false,
      uploading: false,
      destroyBeforeText: 'Destroy link after',
      destroyDownText: 'download(s).',
      destroyDayText: 'day(s).',
      uploadProgress: 0,
      uploadingText: 'File uploading...',
      fileCode: 'no code data',
      uploadedText: 'Upload succeeded!',
      btnCopyText: 'Copy Harbor Link'
    }
  },
  methods: {
    getTypeIcon: function () {
      try {
        let suffix = this.fileName.split('.')
        suffix = suffix[suffix.length - 1].toLowerCase()
        return require(`@/assets/images/${suffix}.svg`)
      } catch (error) {
        return require(`@/assets/images/other.svg`)
      }
    },
    uploadFile: function () {
      const fileUploader = document.getElementById('file_container')
      fileUploader.click()
    },
    updateFile: function (e) {
      this.file = e.target.files[0]
      this.fileName = this.file.name
      let dictSize = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', '!']
      let fileSize = this.file.size
      for (let i = 0; i < dictSize.length; i++) {
        if (fileSize < 1024.0) {
          fileSize = Math.round(fileSize * 100) / 100 + ' ' + dictSize[i]
          break
        }
        fileSize /= 1024.0
      }
      this.fileSize = fileSize
      this.selected = true
    },
    copyCode: function () {
      this.$copyText(this.fileCode).then(
        () => {
          this.$router.push(`/?code=${this.fileCode}`)
        },
        () => {
          alert('Failed to copy! Please select the code and manually copy it.')
        }
      )
    },
    createLink: function () {
      this.$http.post('http://papit.obelisync.com/api/ticket/get')
        .then(
          resp => {
            this.$cookies.set('ticket', resp.data.data)
            this.createLinkAction()
          }
        )
        .catch(
          err => {
            this.$cookies.set('err', err.response.data)
            this.$router.push('/error')
          }
        )
    },
    createLinkAction: function () {
      if (!this.selected) {
        return
      }
      const destroyD = document.getElementById('down_limit').value
      const destroyT = document.getElementById('day_limit').value * 60 * 60 * 24
      this.uploading = true
      const formData = new FormData()
      formData.append('file', this.file)
      this.$http.post(
        `http://papif.obelisync.com/file/upload?ticket=${this.$cookies.get('ticket')}&keep=${destroyT}&download=${destroyD}`,
        formData, {
          onUploadProgress: progress => {
            this.uploadProgress = (progress.loaded / progress.total) * 100
          }
        }
      ).then(resp => {
        this.uploaded = true
        resp = resp.data.data
        this.fileCode = `${resp.file_code.substring(0, 2).toUpperCase()}-${resp.file_code.substring(2, 6).toUpperCase()}-${resp.file_code.substring(6, 8).toUpperCase()}`
      })
        .catch(
          err => {
            this.$cookies.set('err', {
              data: null,
              ext: null,
              msg: err.message == null ? err.response.data.msg : err.message,
              res: err.message == null ? err.response.data.res : 100
            })
            this.$router.push('/error')
          }
        )
    },
    dropUploaded: function () {
      if (!this.selected) {
        return
      }
      const fileUploader = document.getElementById('file_container')
      fileUploader.value = ''
      this.fileName = 'No file uploaded'
      this.fileSize = '0 KiB'
      this.selected = false
    }
  }
}
</script>
