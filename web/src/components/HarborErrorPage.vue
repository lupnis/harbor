<template>
  <div>
    <a id="back" href="/">{{ btnBackCaption }}</a>
    <h1>{{ pageTitle }}</h1>
    <h2>{{ pageSub }}</h2>
    <div class="detailed-info">
        <p>Tickets: {{ sourceTicket }}</p>
        <p>ErrCode: {{ sourceErr.res }}</p>
        <p>Details: {{ sourceErr.msg }}</p>
    </div>
  </div>
</template>
<style scoped>
h1{
  margin: 0!important;
}
p{
    margin: 0;
    text-align: justify;
    line-height: 1.5em;
    word-wrap: break-word;
    word-break: break-all;
    overflow: hidden;
}
</style>
<style src="../assets/css/base.css"></style>
<script>
export default {
  name: 'HarborErrorPage',
  data () {
    return {
      pageTitle: 'OOps!',
      pageSub: 'Something went wrong...',
      sourceTicket: '',
      sourceErr: {
        data: null,
        ext: null,
        msg: null,
        res: null
      },
      btnBackCaption: '<Back'
    }
  },
  mounted () {
    this.initErr()
  },
  methods: {
    initErr: function () {
      this.sourceTicket = this.$cookies.get('ticket') == null ? 'no valid ticket' : this.$cookies.get('ticket')
      this.sourceErr = this.$cookies.get('err') == null ? null : this.$cookies.get('err')
      if (this.sourceTicket == null || this.sourceErr == null) {
        this.$router.push('/')
      }
      this.$cookies.remove('err')
    }
  }
}
</script>
