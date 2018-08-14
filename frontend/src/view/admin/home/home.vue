<template>
  <div>
    <Row :gutter="20">
      <i-col span="4" key="userCount" style="height: 120px;">
        <infor-card shadow color="#2d8cf0" icon="md-person-add" :icon-size="36">
          <count-to :end="newUsers" count-class="count-style"/>
          <p>今日新增用户</p>
        </infor-card>
      </i-col>
      <i-col span="4" key="DAU" style="height: 120px;">
        <infor-card shadow color="#19be6b" icon="md-body" :icon-size="36">
          <count-to :end="dayActiveUsers" count-class="count-style"/>
          <p>DAU(今日活跃用户)</p>
        </infor-card>
      </i-col>
      <i-col span="4" key="articieCount" style="height: 120px;">
        <infor-card shadow color="#ff9900" icon="md-paper" :icon-size="36">
          <count-to :end="newArticles" count-class="count-style"/>
          <p>今日新增文章</p>
        </infor-card>
      </i-col>
      <i-col span="4" key="viewCount" style="height: 120px;">
        <infor-card shadow color="#ed3f14" icon="md-eye" :icon-size="36">
          <count-to :end="newViews" count-class="count-style"/>
          <p>今日新增阅读量</p>
        </infor-card>
      </i-col>
      <i-col span="4" key="commentCount" style="height: 120px;">
        <infor-card shadow color="#E46CBB" icon="md-chatboxes" :icon-size="36">
          <count-to :end="newComments" count-class="count-style"/>
          <p>今日新增评论</p>
        </infor-card>
      </i-col>
      <i-col span="4" key="apiCallCount" style="height: 120px;">
        <infor-card shadow color="#9A66E4" icon="md-options" :icon-size="36">
          <count-to :end="apiCall" count-class="count-style"/>
          <p>今日服务调用量</p>
        </infor-card>
      </i-col>
    </Row>
    <Row :gutter="20" style="margin-top: 10px;">
      <Card shadow>
        <p slot="title">用户访问来源</p>
        <chart-pie style="height: 250px;" :value="pieData"/>
      </Card>
    </Row>
    <Row :gutter="20" style="margin-top: 10px;">
      <Card shadow>
        <p slot="title">上周用户活跃量</p>
        <chart-bar style="height: 250px;" :value="barData"/>
      </Card>
    </Row>
  </div>
</template>

<script>
import InforCard from '_c/info-card'
import CountTo from '_c/count-to'
import { ChartPie, ChartBar } from '_c/charts'
import { listUsers } from '@/api/user'
import { listArticles } from '@/api/article'

export default {
  name: 'home',
  components: {
    InforCard,
    CountTo,
    ChartPie,
    ChartBar
  },
  data () {
    return {
      newUsers: 0,
      dayActiveUsers: 0,
      newArticles: 0,
      newViews: 0,
      newComments: 0,
      apiCall: 0,
      pieData: [
        {value: 335, name: '直接访问'},
        {value: 310, name: '邮件营销'},
        {value: 234, name: '联盟广告'},
        {value: 135, name: '视频广告'},
        {value: 1548, name: '搜索引擎'}
      ],
      barData: {
        Mon: 13253,
        Tue: 34235,
        Wed: 26321,
        Thu: 12340,
        Fri: 24643,
        Sat: 1322,
        Sun: 1324
      }
    }
  },
  methods: {
    getNewUserCount () {
      let since = new Date()
      since.setHours(0, 0, 0, 0)
      since = since.toISOString()
      let params = { since }
      return new Promise((resolve, reject) => {
        listUsers(params).then(res => {
          this.newUsers = res.total
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    getNewArticleCount () {
      let since = new Date()
      since.setHours(0, 0, 0, 0)
      since = since.toISOString()
      let params = { since }
      return new Promise((resolve, reject) => {
        listArticles(params).then(res => {
          this.newArticles = res.total
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    getDayActiveUsers () {
      return new Promise((resolve, reject) => {
        let params = {}
        listUsers(params).then(res => {
          this.dayActiveUsers = res.total
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    }
  },
  mounted () {
    this.getNewUserCount()
    this.getNewArticleCount()
    this.getDayActiveUsers()
  }
}
</script>

<style lang="less">
.count-style{
  font-size: 50px;
}
</style>
