<template>
  <!--<div>-->
    <Row>
      <i-col span="5">
        <h4>
          <Icon type="ios-link"></Icon>
          网站说明
        </h4>
        <ul>
          <li>
            <router-link :to="{ name: 'login' }">{{ blogName }}</router-link>
          </li>
          <li>
            Powered by <Icon type="logo-github"></Icon><a :href="poweredBy.link" target="_blank">{{ poweredBy.name }}</a>
          </li>
        </ul>
      </i-col>
    </Row>
  <!--</div>-->
</template>

<script>
import config from '_conf/config'
export default {
  name: 'Footer',
  data () {
    return {
      blogName: config.blogName,
      poweredBy: config.poweredBy
    }
  }
}
</script>

<style scoped>

</style>
