<template>
  <div id="app">
    <div class="panel-container">
      <router-view />
      <p>
        <a>littleDrive Harbor {{ littleDriveHarborVersion }}</a>
        <span></span>
        <a :href="reportBugHref">{{ reportBugCaption }}</a>
      </p>
    </div>
  </div>
</template>
<style>
#app {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  max-width: 100vw;
  display: grid;
  place-items: center;
  overflow: hidden;
  background-image: url('./assets/images/back.jpg');

}
.panel-container{
  background-color: #64768788;
  border: 2px solid #314354;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  padding: 0;
  margin: 0;
  max-width: 100vw;
}
.panel-container > p {
  display: flex;
  justify-content: space-between;
  padding: 0 0.5em;
  margin: 1em 0 0.2em 0;
}
span{
  padding:0 1em;
}
a:link {
    color: #CCFFFF;
    text-decoration: none;
}

a:link:hover {
    color: #92e1e1;
    text-decoration: underline;
}
</style>
<script>
export default {
  name: 'App',
  data () {
    return {
      littleDriveHarborVersion: '1.0.0',
      reportBugCaption: 'Report Bugs',
      reportBugHref: 'mailto:lupnisj@gmail.com'
    }
  }
}
</script>
