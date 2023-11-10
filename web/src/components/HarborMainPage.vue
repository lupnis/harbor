<template>
<div>
  <div v-if="!jumping">
    <h1>{{ pageTitle }}</h1>
    <p><input type="text" id="text_harborcode" :placeholder="harborCodeCaption" v-model="code" @keydown.enter="jumpToFile(code)" /></p>
    <p><button id="btn_jump" @click="jumpToFile(code)">{{ btnFetchCaption }}</button></p>
    <p class="or-cap">{{ orCaption }}</p>
    <p><button id="btn_create" @click="createLink()">{{ btnCreateCaption }}</button></p>
  </div>
  <div v-if="jumping">
    <h1>{{ pageTitle }}</h1>
    <div class="detailed-info" v-if="!fileValid">
        <h2>{{ jumpingText }}</h2>
    </div>
  </div>
</div>
</template>
<script>
export default {
  name: 'HarborMainPage',
  data () {
    return {
      pageTitle: 'littleDrive - Harbor Mode',
      harborCodeCaption: 'Harbor Code',
      btnFetchCaption: 'Jump to File',
      orCaption: ' - or - ',
      btnCreateCaption: 'Create Harbor Link',
      code: '',
      jumping: false,
      jumpingText: 'Fetching file...'
    }
  },
  mounted () {
    const code = this.$route.query.code.toUpperCase()
    if (code != null) {
      this.code = code
    }
  },
  methods: {
    jumpToFile: function (code) {
      if (code == null || code.length === 0) {
        return
      }
      if (code.length !== 10) {
        this.$cookies.set('err', {
          data: null,
          ext: null,
          msg: 'Harbor code format mismatched.',
          res: 0
        })
        this.$router.push('/error')
        return
      }
      this.jumping = true
      this.$http.post('http://papit.obelisync.com/api/ticket/get')
        .then(
          resp => {
            this.$cookies.set('ticket', resp.data.data)
            this.$router.replace(`/fetch?code=${code}`)
          }
        )
        .catch(
          err => {
            this.$cookies.set('err', err.response.data)
            this.$router.push('/error')
          }
        )
    },
    createLink: function () {
      this.$http.post('http://papit.obelisync.com/api/ticket/get')
        .then(
          resp => {
            this.$cookies.set('ticket', resp.data.data)
            this.$router.push('/create')
          }
        )
        .catch(
          err => {
            this.$cookies.set('err', err.response.data)
            this.$router.push('/error')
          }
        )
    }
  }
}
</script>
<style src="../assets/css/base.css"></style>
<style scoped>
.detailed-info {
  background-color: #003f3f88;
}
p{
  justify-content: center;
}
</style>
